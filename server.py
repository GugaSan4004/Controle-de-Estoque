import os
os.environ['TZ'] = 'UTC'

from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends

import database
# from database.models import *
# from database.schema import *
import database.audit


app = FastAPI(
    title="Controle de Estoque",
    version="1.0"
)

@app.on_event("startup")
def on_startup():
    database.Base.metadata.create_all(bind=database.engine)

@app.get("/")
def home():
    return "Hello World!"


@app.get("/items")
def list_items(db: Session = Depends(database.get_db)):
    items = db.query(database.Item).all()
    return [
        {
            "id": i.id,
            "name": i.name,
            "quantity": i.quantity,
            "unityPrice": i.unityPrice,
            "minimum": i.minimum,
            "ideal": i.ideal,
        }
        for i in items
    ]


# @app.get("/items/{item_id}")
# def search_item(item_id: int):
#     db = SessionLocal()

#     item = db.query(ItemsDB).filter(
#         ItemsDB.id == item_id
#     ).first()

#     db.close()

#     if not item:
#         raise HTTPException(
#             status_code=404,
#             detail="Item não encontrado"
#         )

#     return {
#         "id": item.id,
#         "name": item.name,
#         "quantity": item.quantity,
#         "price": item.price,
#         "min_quantity": item.min_quantity,
#         "ideal_quantity": item.ideal_quantity
#     }


@app.post("/item", response_model=database.ItemResponse, status_code=201)
def create_item(data: database.ItemCreate, db: Session = Depends(database.get_db)):
    item = database.Item(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# @app.put("/item/{item_id}")
# def update_item(
#     item_id: int,
#     data: ItemUpdate
# ):
#     db = SessionLocal()

#     item = db.query(ItemsDB).filter(
#         ItemsDB.id == item_id
#     ).first()

#     if not item:
#         db.close()
#         raise HTTPException(
#             status_code=404,
#             detail="item não encontrado"
#         )

#     item.quantity = data.quantity

#     db.commit()
#     db.close()

#     return {"message": "Estoque atualizado"}


# @app.delete("/item/{item_id}")
# def remover_item(item_id: int):
#     db = SessionLocal()

#     item = db.query(ItemsDB).filter(
#         ItemsDB.id == item_id
#     ).first()

#     if not item:
#         db.close()
#         raise HTTPException(
#             status_code=404,
#             detail="item não encontrado"
#         )

#     db.delete(item)
#     db.commit()
#     db.close()

#     return {"message": "item removido"}