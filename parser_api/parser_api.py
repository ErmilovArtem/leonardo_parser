# -*- coding: utf-8 -*-
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from db import CategoryItem, CategoryItemResponse, DB_URL

# Настройка логгирования
logging.basicConfig(
    filename="api.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Создание объекта приложения FastAPI
app = FastAPI()

# Настройка асинхронного движка базы данных и сессии
engine = create_async_engine(DB_URL)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Функция для получения объекта из базы данных
async def get_category_item_by_sku(sku: str, db: AsyncSession) -> Optional[CategoryItem]:
    """
    Получение объекта CategoryItem из базы данных по его SKU.

    :param sku: SKU объекта
    :param db: Асинхронная сессия базы данных
    :return: Объект CategoryItem или None, если объект не найден
    """
    try:
        query = select(CategoryItem).where(CategoryItem.sku == sku)
        result = await db.execute(query)
        item = result.scalars().first()
        if item:
            logging.info(f"CategoryItem найден для SKU: {sku}.")
        else:
            logging.warning(f"CategoryItem не найден для SKU: {sku}.")
        return item
    except Exception as e:
        logging.error(f"Ошибка при получении CategoryItem для SKU {sku}: {e}")
        raise

# Зависимость для получения сессии базы данных
async def get_db() -> AsyncSession:
    """
    Генератор асинхронной сессии базы данных.

    :yield: Асинхронная сессия базы данных
    """
    try:
        async with async_session() as session:
            yield session
            logging.debug("Асинхронная сессия базы данных успешно завершена.")
    except Exception as e:
        logging.error(f"Ошибка при создании сессии базы данных: {e}")
        raise

# FastAPI эндпоинт
@app.get("/category-item/{sku}", response_model=CategoryItemResponse)
async def read_category_item(sku: str, db: AsyncSession = Depends(get_db)):
    """
    Эндпоинт для получения данных CategoryItem по SKU.

    :param sku: SKU объекта
    :param db: Асинхронная сессия базы данных, передаваемая через Depends
    :return: Объект CategoryItemResponse
    :raises HTTPException: Если объект не найден
    """
    try:
        item = await get_category_item_by_sku(sku, db)
        if not item:
            logging.warning(f"Запрос на SKU {sku}: CategoryItem не найден.")
            raise HTTPException(status_code=404, detail="CategoryItem not found")
        logging.info(f"Успешно возвращён объект для SKU {sku}.")
        return item
    except HTTPException as e:
        logging.error(f"HTTP ошибка для SKU {sku}: {e.detail}")
        raise
    except Exception as e:
        logging.error(f"Необработанная ошибка для SKU {sku}: {e}")
        raise
