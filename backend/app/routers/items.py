from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as SessionType
from sqlalchemy import update, delete
from typing import Optional

from app.dependencies import get_db, get_current_user
from app.models import UserModel, ItemModel
from app.schemas import ItemCreate

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/")
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
    return {"items": query.all(), "success": "OK"}

@router.post("/")
async def create_item(
    item: ItemCreate,
    db: SessionType = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    new_item = ItemModel(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"success": "OK"}

@router.put("/{item_id}")
async def update_item(
    item_id: int,
    item_data: ItemCreate,
    db: SessionType = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Товар не найден")
    if db_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    stmt = update(ItemModel).where(ItemModel.id == item_id).values(**item_data.model_dump())
    db.execute(stmt)
    db.commit()
    return {"success": "OK"}

@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    db: SessionType = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Товар не найден")
    if db_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    stmt = delete(ItemModel).where(ItemModel.id == item_id)
    db.execute(stmt)
    db.commit()
    return {"success": "OK"}