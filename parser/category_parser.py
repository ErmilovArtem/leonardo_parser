import time
import logging
from typing import List, Optional, Dict
from bs4 import BeautifulSoup
import cloudscraper
from config import HEADERS, COOKIES, BASE_URL, BLOCKED_CATEGORY, DB_URL
from sqlalchemy import create_engine, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Category, CategoryItem
from parser.sku_parser import SKUParser

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("sku_parser.log"),
        logging.StreamHandler()
    ]
)
logging.getLogger().setLevel(logging.INFO)
# Создание подключения к базе данных
engine = create_engine(DB_URL)
SessionLocal = scoped_session(sessionmaker(bind=engine))


class CategoryParser:
    """
    Класс для парсинга информации о SKU с веб-сайта и записи данных в базу данных.
    """

    def __init__(self):
        """Инициализирует скрейпер и сессию базы данных."""
        self.scraper = cloudscraper.create_scraper()

    def fetch_page(self, url: str, retries: int = 5) -> Optional[str]:
        """
        Загружает HTML-страницу по заданному URL с помощью CloudScraper.

        :param url: URL страницы для загрузки
        :param retries: Количество попыток при ошибке загрузки
        :return: Содержимое HTML-страницы или None в случае неудачи
        """
        for attempt in range(retries):
            try:
                response = self.scraper.get(url, headers=HEADERS, cookies=COOKIES)
                if response.status_code == 200:
                    logging.info(f"Страница {url} успешно загружена.")
                    return response.text
                elif response.status_code == 503:
                    logging.warning(f"Ошибка 503. Попытка {attempt + 1} из {retries}...")
                    time.sleep(5)
            except Exception as e:
                logging.error(f"Ошибка при загрузке страницы {url}: {e}")
        logging.error(f"Не удалось загрузить страницу {url} после {retries} попыток.")
        return None

    def get_categories(self) -> List[dict]:
        """
        Получает список категорий с сайта.

        :return: Список словарей с именами категорий и их URL
        """
        html = self.fetch_page(f"{BASE_URL}/ishop/")
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        categories = []

        for category in soup.select(".main-widgets .widgets__link"):
            category_name = category.text.strip()
            if category_name in BLOCKED_CATEGORY:
                logging.info(f"Пропускаем категорию: {category_name}")
                continue

            href = category.get("href")
            if href:
                categories.append({"name": category_name, "url": BASE_URL + href})

        return categories

    def save_category(self, category_names: List[str]) -> List[int]:
        """
        Сохраняет список имен категорий в базу данных единой транзакцией.

        :param category_names: Список имен категорий
        :return: Список ID сохраненных категорий
        """
        if not category_names:
            return []

        categories = [{"name": name} for name in category_names]
        stmt = insert(Category).values(categories).on_conflict_do_nothing(index_elements=["name"])

        with SessionLocal() as db_session:
            try:
                with db_session.begin():
                    db_session.execute(stmt)
                logging.info(f"Сохранено {len(categories)} категорий.")
            except Exception as e:
                logging.error(f"Ошибка сохранения категорий: {e}")
                raise

            return [row.id for row in db_session.execute(select(Category.id))]

    def get_subcategories(self, category_url: str) -> List[str]:
        """
        Получает список подкатегорий для заданной категории.

        :param category_url: URL категории
        :return: Список URL подкатегорий
        """
        html = self.fetch_page(category_url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        return [
            BASE_URL + subcategory.get("href")
            for subcategory in soup.select(".widgets__item .widgets__link")
            if subcategory.get("href")
        ]

    def get_product_ids(self, subcategory_url: str, sku_list: List[str]) -> List[str]:
        """
        Получает список идентификаторов товаров из подкатегории.

        :param subcategory_url: URL подкатегории
        :param sku_list: Список уже сохраненных SKU
        :return: Список идентификаторов товаров
        """
        products_list = []
        html = self.fetch_page(f"{subcategory_url}/?pages=1")
        if not html:
            return products_list

        soup = BeautifulSoup(html, "html.parser")
        page_numbers = soup.select(".page-number")
        max_page = int(page_numbers[-1].text) if page_numbers else 1

        for page in range(1, max_page + 1):
            html = self.fetch_page(f"{subcategory_url}/?pages={page}")
            if not html:
                break

            soup = BeautifulSoup(html, "html.parser")
            products = soup.select(".goods .goods__link")
            for product in products:
                href = product.get("href")
                if href and "/ishop/good_" in href:
                    product_id = href.split("good_")[1].strip("/")
                    if product_id in sku_list:
                        return products_list
                    products_list.append(product_id)

        return products_list

    def save_products(self, products: List[Dict]) -> None:
        """
        Сохраняет список продуктов в базу данных.

        :param products: Список словарей с данными о продуктах
        """
        if not products:
            return

        stmt = insert(CategoryItem).values(products)

        with SessionLocal() as db_session:
            try:
                with db_session.begin():
                    db_session.execute(stmt)
            except Exception as e:
                logging.error(f"Ошибка сохранения продуктов: {e}")
                raise

    def update_category_parse_status(self, category_id: int) -> None:
        """
        Обновляет статус парсинга категории в базе данных.

        :param category_id: ID категории
        """
        with SessionLocal() as db_session:
            try:
                with db_session.begin():
                    db_session.query(Category).filter_by(id=category_id).update({"parse": True})
            except Exception as e:
                logging.error(f"Ошибка обновления статуса парсинга: {e}")
                raise

    def get_sku_by_category(self, category_id: int) -> List[str]:
        """
        Получает список SKU для заданной категории.

        :param category_id: ID категории
        :return: Список SKU
        """
        stmt = select(CategoryItem.sku).where(CategoryItem.category_id == category_id)

        with SessionLocal() as db_session:
            try:
                with db_session.begin():
                    return [row[0] for row in db_session.execute(stmt)]
            except Exception as e:
                logging.error(f"Ошибка получения SKU: {e}")
                raise

    def parse_all_product_ids(self) -> None:
        """
        Основной метод для парсинга всех идентификаторов товаров и записи их в базу данных.
        """
        categories = self.get_categories()
        id_list = self.save_category([category["name"] for category in categories])

        for category, category_id in zip(categories, id_list):
            sku_list = self.get_sku_by_category(category_id)
            category_name = category["name"]
            category_url = category["url"]

            logging.info(f"Обрабатываем категорию: {category_name} ({category_url})")

            subcategories = self.get_subcategories(category_url)
            if not subcategories:
                subcategories = [category_url]

            products = set()
            for subcategory_url in subcategories:
                logging.info(f"  Обрабатываем подкатегорию: {subcategory_url}")
                products.update(self.get_product_ids(subcategory_url, sku_list))

            sku_parser = SKUParser()
            products = list(products)
            for i in range(0, len(products), 10):
                batch = products[i:i + 10]
                parsed_data = sku_parser.process_skus(batch)
                parsed_data = [item for item in parsed_data if item['category_name'] != category_name]

                for item in parsed_data:
                    item.pop('category_name', None)
                    item['category_id'] = category_id

                self.save_products(parsed_data)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    parser = CategoryParser()
    parser.parse_all_product_ids()
