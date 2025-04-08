from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from core.config import get_auth_data, configs

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=configs.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, configs.SECRET_KEY, algorithm=configs.ALGORITHM)

    return encode_jwt


def decode_access_token(token: str):
    decode_jwt = jwt.decode(token, configs.SECRET_KEY, algorithms=[configs.ALGORITHM])
    return decode_jwt