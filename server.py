import database

from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Controle de Estoque",
    version="1.0"
)

@app.get("/")
def home():
    return "Hello World!"


@app.get("/items")
def list_items():
    db = database.SessionLocal()

    items = db.query(database.Item).all()

    result = []

    for item in items:
        result.append({
            "id": item.id,
            "name": item.name,
            "quantity": item.quantity,
            "price": item.price,
            "min_quantity": item.min_quantity,
            "ideal_quantity": item.ideal_quantity
        })

    db.close()

    return result


# @app.get("/items/{item_id}")
# def search_wwitem(item_id: int):
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


# @app.post("/item")
# def create_item(dados: ItemCreate):
#     db = SessionLocal()

#     item = ItemsDB(
#         name=dados.name,
#         quantity=dados.quantity,
#         price=dados.price,
#         min_quantity=dados.min_quantity,
#         ideal_quantity=dados.ideal_quantity
#     )

#     db.add(item)
#     db.commit()
#     db.refresh(item)
#     db.close()

#     return {
#         "message": "item criado",
#         "id": item.id
#     }


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