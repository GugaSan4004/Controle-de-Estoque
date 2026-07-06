from typing import Optional
from pydantic import BaseModel
from datetime import datetime, date

class ItemBase(BaseModel):
    name: Optional[str] = None
    place: str = "ALMOX"
    unityType: Optional[str] = None
    unityPrice: int = 0
    quantity: int = 0
    minimum: int = 0
    ideal: int = 0
    category: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int

    class Config:
        from_attributes = True
