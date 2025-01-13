import os
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, Integer, Boolean, String, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

# Настройка базы данных
DB_URL = os.getenv("DB_URL", "postgresql+asyncpg://postgres:2525@localhost/leonardo_parser")

Base = declarative_base()

class CategoryItemResponse(BaseModel):
    id: int
    product_name: Optional[str]
    category_id: int
    brand: Optional[str]
    sku: str
    features: Optional[dict]
    description: Optional[str]
    photo: Optional[str]
    stock: bool
    price: Optional[int]

    class Config:
        orm_mode = True

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=False, unique=True)
    parse = Column(Boolean, default=False)


class CategoryItem(Base):
    __tablename__ = 'category_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(45), nullable=True)
    category_id = Column(Integer, ForeignKey('category.id', ondelete="CASCADE"), nullable=False)
    brand = Column(String(45), nullable=True)
    sku = Column(String(20), unique=True, nullable=False)
    features = Column(JSON, nullable=True)
    description = Column(String, nullable=True)
    photo = Column(String, nullable=True)
    stock = Column(Boolean, nullable=False, default=False)
    price = Column(Integer, nullable=True)

    category = relationship("Category", back_populates="items")

    Category.items = relationship("CategoryItem", back_populates="category", cascade="all, delete")