from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as SessionType
from sqlalchemy import update, delete
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import bcrypt, os

from app.dependencies import get_db, get_current_user
from app.models import UserModel
from app.schemas import UserCreate, UserOut, LoginData

load_dotenv()

router = APIRouter(prefix="/user", tags=["users"])

@router.post("/login")
async def login(data: LoginData, db: SessionType = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    if not bcrypt.checkpw(data.password.encode("utf-8"), user.password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    payload = {
        "user_id": user.id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}

@router.get("/{user_id}", response_model=UserOut)
async def read_user(user_id: int, db: SessionType = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@router.post("/")
async def create_user(user: UserCreate, db: SessionType = Depends(get_db)):
    hashed = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user_data = user.model_dump()
    user_data["password"] = hashed
    new_user = UserModel(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"success": "OK"}

@router.put("/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserCreate,
    db: SessionType = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if db_user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    stmt = update(UserModel).where(UserModel.id == user_id).values(**user_data.model_dump())
    db.execute(stmt)
    db.commit()
    return {"success": "OK"}

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: SessionType = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if db_user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    stmt = delete(UserModel).where(UserModel.id == user_id)
    db.execute(stmt)
    db.commit()
    return {"success": "OK"}