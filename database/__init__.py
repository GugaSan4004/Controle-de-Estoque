from sqlalchemy.orm import (
    declarative_base, 
    sessionmaker
)

from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///./stock.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


# ------------------ #
#       Models       #
# ------------------ #


from database.models import * 


# ------------------ #
#       Schema       #
# ------------------ #


from database.schema import *


Base.metadata.create_all(bind=engine)