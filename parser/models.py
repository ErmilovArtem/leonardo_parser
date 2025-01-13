from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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

    Category.items = relationship("CategoryItem", back_populates="category", cascade="all, delete", lazy="selectin")
