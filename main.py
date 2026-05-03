from typing import List, Optional
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import update, delete
from db import Session, engine, ItemModel, UserModel, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

class Item(BaseModel):
    name: str
    price: float
    author: str
    available: bool
    owner_id: int

    class Config:
        from_attributes = True

class User(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)

@app.get("/items")
async def read_items(name: Optional[str] = None,
                     price: Optional[float] = None,
                     db: Session = Depends(get_db)
                     ):
    query = db.query(ItemModel)
    if name:
        query = db.query(ItemModel).where(ItemModel.name == name)
    if price:
        query = db.query(ItemModel).where(ItemModel.price == price)

    results = query
    return {"items": results, "success": "OK"}

@app.post("/items")
async def create_item(item: Item, db: Session = Depends(get_db)):
    new_item = ItemModel(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"success": "OK"}

@app.put("/items/{item_id}")
async def update_item(item_id: int, item_data: Item, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    stmt = update(ItemModel).where(ItemModel.id == item_id).values(**item_data.model_dump())
    db.execute(stmt)
    db.commit()
    db.refresh(db_item)
    return {"success": "OK"}

@app.delete("/items/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    stmt = delete(db_item)
    db.execute(stmt)
    db.commit()
    return {"success": "OK"}



@app.get("/user/{user_id}")
async def read_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(UserModel).filter(UserModel.id == user_id).first(), {"success": "OK"}

@app.post("/user")
async def create_user(user: User, db: Session = Depends(get_db)):
    new_user = UserModel(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"success": "OK"}

@app.put("/user/{user_id}")
async def update_user(user_id: int, user_data: User, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    stmt = update(UserModel).where(UserModel.id == user_id).values(**user_data.model_dump())
    db.execute(stmt)
    db.commit()
    db.refresh(db_user)
    return {"success": "OK"}

@app.delete("/user/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    stmt = delete(UserModel).where(UserModel.id == user_id)
    db.execute(stmt)
    db.commit()
    return {"success": "OK"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)