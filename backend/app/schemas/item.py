from pydantic import BaseModel, ConfigDict

class ItemCreate(BaseModel):
    name: str
    price: float
    author: str
    available: bool
    owner_id: int
    model_config = ConfigDict(from_attributes=True)