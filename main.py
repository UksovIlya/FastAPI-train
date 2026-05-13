from typing import Optional
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy.orm import Session as SessionType
from sqlalchemy import update, delete
from db import Session, engine, ItemModel, UserModel, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()


# Зависимость: получаем сессию БД на время запроса и закрываем после
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


# Схемы (Pydantic-модели) — описывают форму данных в запросах/ответах
class Item(BaseModel):
    name: str
    price: float
    author: str
    available: bool
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    name: str
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserOut(BaseModel):
    """Схема ответа для пользователя — без пароля."""
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


# Эндпоинты для Items
@app.get("/items")
async def read_items(
    name: Optional[str] = None,
    price: Optional[float] = None,
    db: SessionType = Depends(get_db)
):
    query = db.query(ItemModel)

    if name:
        query = query.filter(ItemModel.name == name)
    if price:
        query = query.filter(ItemModel.price == price)

    results = query.all()
    return {"items": results, "success": "OK"}


@app.post("/items")
async def create_item(item: Item, db: SessionType = Depends(get_db)):
    new_item = ItemModel(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"success": "OK"}


@app.put("/items/{item_id}")
async def update_item(item_id: int, item_data: Item, db: SessionType = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    stmt = update(ItemModel).where(ItemModel.id == item_id).values(**item_data.model_dump())
    db.execute(stmt)
    db.commit()
    db.refresh(db_item)
    return {"success": "OK"}


@app.delete("/items/{item_id}")
async def delete_item(item_id: int, db: SessionType = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    stmt = delete(ItemModel).where(ItemModel.id == item_id)
    db.execute(stmt)
    db.commit()
    return {"success": "OK"}


# Эндпоинты для Users

@app.get("/user/{user_id}", response_model=UserOut)
async def read_user(user_id: int, db: SessionType = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/user")
async def create_user(user: User, db: SessionType = Depends(get_db)):
    import bcrypt
    user_data = user.model_dump()
    user_data["password"] = bcrypt.hashpw(
        user_data["password"].encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    new_user = UserModel(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"success": "OK"}


@app.put("/user/{user_id}")
async def update_user(user_id: int, user_data: User, db: SessionType = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    stmt = update(UserModel).where(UserModel.id == user_id).values(**user_data.model_dump())
    db.execute(stmt)
    db.commit()
    db.refresh(db_user)
    return {"success": "OK"}


@app.delete("/user/{user_id}")
async def delete_user(user_id: int, db: SessionType = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    stmt = delete(UserModel).where(UserModel.id == user_id)
    db.execute(stmt)
    db.commit()
    return {"success": "OK"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)