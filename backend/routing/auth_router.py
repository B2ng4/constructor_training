import time
from collections import defaultdict, deque
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, Body, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from loguru import logger
from pydantic import BaseModel
from starlette import status

from core.config import configs
from depends import get_user_service, oauth2_scheme
from schemas.users import UserLogin, UserRegister, UserResponse
from services.user_service import UserService
from services.yandex_oauth_service import (
    exchange_code_for_token,
    fetch_yandex_profile,
    build_yandex_authorize_url,
)
from utils.security import create_access_token, decode_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


_RATE_BUCKETS: dict = defaultdict(deque)


def _throttle(request: Request, bucket: str, limit: int, window_sec: int) -> None:
    """Простой rate-limit по IP (X-Forwarded-For за прокси)."""
    fwd = request.headers.get("x-forwarded-for")
    ip = (
        fwd.split(",")[0].strip()
        if fwd
        else (request.client.host if request.client else "unknown")
    )
    key = (bucket, ip)
    now = time.monotonic()
    dq = _RATE_BUCKETS[key]
    while dq and now - dq[0] > window_sec:
        dq.popleft()
    if len(dq) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Слишком много попыток. Попробуйте позже.",
        )
    dq.append(now)


def _sanitize_oauth_next(raw: Optional[str]) -> str:
    default = "/personal"
    if not raw or not isinstance(raw, str):
        return default
    s = raw.strip()
    if not s.startswith("/") or s.startswith("//"):
        return default
    if "\n" in s or "\r" in s or "\x00" in s:
        return default
    return s[:512]


@router.get("/yandex/start", name="Старт OAuth Яндекс ID")
async def yandex_oauth_start(next: str = "/personal") -> RedirectResponse:
    missing = []
    if not (configs.YANDEX_CLIENT_ID or "").strip():
        missing.append("YANDEX_CLIENT_ID")
    if not (configs.YANDEX_REDIRECT_URI or "").strip():
        missing.append("YANDEX_REDIRECT_URI")
    if missing:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Яндекс OAuth не настроен: задайте в backend/.env (или env_file Docker): "
                + ", ".join(missing)
                + ". Значения в config.py по умолчанию не подставляют client_id."
            ),
        )
    n = _sanitize_oauth_next(next)
    state = create_access_token(
        data={
            "sub": "__yandex_oauth__",
            "yandex_oauth_state": "1",
            "yandex_next": n,
        },
        expires_minutes=15,
    )
    url = build_yandex_authorize_url(state=state)
    return RedirectResponse(url, status_code=302)


@router.get("/yandex/callback", name="OAuth Яндекс ID: callback")
async def yandex_oauth_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    user_service: UserService = Depends(get_user_service),
) -> RedirectResponse:
    fe = configs.FRONTEND_PUBLIC_URL.rstrip("/")
    err_url = f"{fe}/login?yandex_error=1"

    if error or not code or not state:
        return RedirectResponse(err_url, status_code=302)

    try:
        payload = decode_access_token(state)
    except Exception:
        return RedirectResponse(err_url, status_code=302)

    if payload.get("sub") != "__yandex_oauth__" or payload.get(
        "yandex_oauth_state"
    ) not in ("1", 1, True):
        return RedirectResponse(err_url, status_code=302)

    next_path = _sanitize_oauth_next(payload.get("yandex_next"))

    try:
        ya_token = await exchange_code_for_token(code)
        profile = await fetch_yandex_profile(ya_token)
        user = await user_service.get_or_create_yandex_user(
            yandex_id=profile.yandex_id,
            email_from_yandex=profile.email,
            first_name=profile.first_name,
            last_name=profile.last_name,
            photo=profile.photo,
        )
        access_token = create_access_token(data={"sub": user.email})
    except Exception:
        logger.exception("Yandex OAuth error")
        return RedirectResponse(err_url, status_code=302)

    q = f"token={quote(access_token, safe='')}&redirect={quote(next_path, safe='')}"
    return RedirectResponse(
        f"{fe}/login/yandex/callback?{q}",
        status_code=302,
    )


@router.get("/yandex/config", name="Конфиг Яндекс OAuth")
async def yandex_oauth_config() -> dict:
    fe = configs.FRONTEND_PUBLIC_URL.rstrip("/")
    return {
        "client_id": configs.YANDEX_CLIENT_ID,
        "redirect_uri": f"{fe}/login/yandex/callback",
    }


class YandexTokenRequest(BaseModel):
    access_token: str


@router.post("/yandex/token", name="Авторизация по токену Яндекса")
async def yandex_oauth_token(
    data: YandexTokenRequest,
    user_service: UserService = Depends(get_user_service),
) -> dict:
    try:
        profile = await fetch_yandex_profile(data.access_token)
        user = await user_service.get_or_create_yandex_user(
            yandex_id=profile.yandex_id,
            email_from_yandex=profile.email,
            first_name=profile.first_name,
            last_name=profile.last_name,
            photo=profile.photo,
        )
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.exception("Yandex OAuth token error")
        raise HTTPException(status_code=400, detail="Invalid Yandex token")


@router.post("/register", name="регистрация пользователя")
async def register_user(
    user_data: UserRegister,
    request: Request,
    user_service: UserService = Depends(get_user_service),
) -> dict:
    _throttle(request, "register", limit=5, window_sec=60)
    if await user_service.register(user_data):
        return {"detail": "Вы успешно зарегистрированы! На ваш email отправлено письмо."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует!",
        )


@router.post("/login", name="Логин")
async def login_user(
    request: Request,
    username: Optional[str] = Form(default=None),
    password: Optional[str] = Form(default=None),
    user_data: Optional[UserLogin] = Body(default=None),
    user_service: UserService = Depends(get_user_service),
) -> dict:
    _throttle(request, "login", limit=10, window_sec=60)
    if user_data:
        final_user_data = user_data
    elif username and password:
        final_user_data = UserLogin(
            username=username.strip().lower(),
            password=password.strip(),
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Некорректные данные",
        )
    access_token = await user_service.login(final_user_data)
    if access_token is None:
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль, либо срок действия учётной записи истёк",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me/", name="Получение данных текущего пользователя")
async def get_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    current_user = await user_service.get_current_user(token)
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось загрузить пользователя",
        )
    return current_user
