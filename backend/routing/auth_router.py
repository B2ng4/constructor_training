from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    Body,
    Form,
    BackgroundTasks,
    Query,
)
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from starlette.requests import Request

from schemas.users import UserRegister
from depends import get_user_service
from schemas.users import UserRegister, UserLogin, User
from services.user_service import UserService
from utils.security import get_password_hash
from core.config import configs
from fastapi.responses import RedirectResponse


router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/register")
async def register_user(
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    user_service: UserService = Depends(get_user_service),
) -> dict:
    if await user_service.register(user_data, background_tasks):
        raise HTTPException(
            status_code=200,
            detail= "Вы успешно зарегистрированы! На ваш email отправлено письмо.",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует!",
        )


@router.post("/login")
async def login_user(
    username: Optional[str] = Form(default=None),
    password: Optional[str] = Form(default=None),
    user_data: Optional[UserLogin] = Body(default=None),
    user_service: UserService = Depends(get_user_service),
) -> dict:
    if user_data:
        final_user_data = user_data
    elif username and password:
        final_user_data = UserLogin(username=username, password=password)
    else:
        raise HTTPException(
            status_code=400,
            detail="Некорректные данные",
        )
    access_token = await user_service.login(final_user_data)
    if access_token is None:
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me/")
async def get_me(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> User:
    current_user = await user_service.get_current_user(token)
    return current_user


