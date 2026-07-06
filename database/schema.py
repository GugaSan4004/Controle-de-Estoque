from typing import Optional
from pydantic import BaseModel
from datetime import datetime, date

class ItemBase(BaseModel):
    name: Optional[str] = None
    place: Optional[str] = None
    unityType: Optional[str] = None
    unityPrice: Optional[int] = None
    quantity: Optional[int] = None
    minimum: Optional[int] = None
    ideal: Optional[int] = None
    category: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int

    class Config:
        from_attributes = True
