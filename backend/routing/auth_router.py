
from fastapi import APIRouter, Depends, HTTPException, Response, Body
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from backend.schemas.users import UserRegister
from backend.schemas.books import Book
from backend.depends import get_book_service, get_user_service
from backend.schemas.users import UserRegister, UserLogin, User
from backend.services.books import BookService
from backend.services.users import UserService
from backend.utils.security import get_password_hash


router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")



@router.post("/register")
async def register_user(user_data: UserRegister,
                        user_service: UserService = Depends(get_user_service)) -> dict:

    if await user_service.register(user_data):
        return {'message': 'Вы успешно зарегистрированы!'}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует!"
        )



@router.post("/login")
async def login_user(
    user_data: UserLogin = Body(...),
    user_service: UserService = Depends(get_user_service)
) -> dict:
    access_token = await user_service.login(user_data)
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": access_token, "token_type": "bearer"}




@router.get("/me/")
async def get_me(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    current_user = await user_service.get_current_user(token)
    return current_user



