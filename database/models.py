from datetime import datetime, timezone
import enum

from sqlalchemy import (
    Column,
    Integer,
    Float,
    DECIMAL,
    ForeignKey,
    Boolean,
    DateTime,
    Date,
    Text,
    Enum,
)

from sqlalchemy.orm import relationship

from database import Base

class MovementType(enum.Enum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    TRANSFER = "TRANSFER"
    ADJUSTMENT = "ADJUSTMENT"


class TimestampMixin:
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class Item(TimestampMixin, Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(Text, nullable=False)
    place = Column(Text, nullable=False, default="ALMOX")
    unityType = Column(Text)

    unityPrice = Column(
        DECIMAL(10, 2),
        nullable=False,
        default=0
    )

    quantity = Column(
        Float,
        nullable=False,
        default=0
    )

    minimum = Column(
        Float,
        nullable=False,
        default=0
    )

    ideal = Column(
        Float,
        nullable=False,
        default=0
    )

    category = Column(Text)

    movements = relationship(
        "MovementItem",
        back_populates="item"
    )

    purchases = relationship(
        "PurchaseItem",
        back_populates="item"
    )


class Movement(TimestampMixin, Base):
    __tablename__ = "movements"

    id = Column(Integer, primary_key=True, index=True)

    date = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        nullable=False
    )

    type = Column(
        Enum(MovementType),
        nullable=False
    )

    responsible = Column(
        Text,
        nullable=False
    )

    locale = Column(Text)

    cc = Column(
        Text,
        nullable=False
    )

    items = relationship(
        "MovementItem",
        back_populates="movement",
        cascade="all, delete-orphan"
    )


class MovementItem(Base):
    __tablename__ = "movements_items"

    id = Column(Integer, primary_key=True)

    movementsId = Column(
        Integer,
        ForeignKey(
            "movements.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    itemsId = Column(
        Integer,
        ForeignKey(
            "items.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    quantity = Column(
        Float,
        nullable=False,
        default=0
    )

    movement = relationship(
        "Movement",
        back_populates="items"
    )

    item = relationship(
        "Item",
        back_populates="movements"
    )


class Purchase(TimestampMixin, Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True)

    date = Column(
        Date,
        default=datetime.utcnow,
        nullable=False
    )

    received = Column(
        Boolean,
        nullable=False,
        default=False
    )

    shippingNoteId = Column(Integer)

    items = relationship(
        "PurchaseItem",
        back_populates="purchase",
        cascade="all, delete-orphan"
    )


class PurchaseItem(Base):
    __tablename__ = "purchases_items"

    id = Column(Integer, primary_key=True)

    itemsId = Column(
        Integer,
        ForeignKey(
            "items.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    purchasesId = Column(
        Integer,
        ForeignKey(
            "purchases.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    quantity = Column(
        Float,
        nullable=False,
        default=0
    )

    purchase = relationship(
        "Purchase",
        back_populates="items"
    )

    item = relationship(
        "Item",
        back_populates="purchases"
    )