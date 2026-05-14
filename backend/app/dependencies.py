from sqlalchemy.orm import Session as SessionType
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.db import Session
from app.models import UserModel
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: SessionType = Depends(get_db)
):
    credentials_exception = HTTPException(status_code=401, detail="Токен недействителен")
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user