# -*- coding: utf-8 -*-
import logging
import time
from typing import Optional, Dict, List

import cloudscraper
from bs4 import BeautifulSoup

from parser.config import HEADERS, COOKIES

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class SKUParser:
    def __init__(self):
        """Инициализация объекта парсера с использованием CloudScraper."""
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

    def parse_item_data(self, sku: str, html: str) -> Dict[str, Optional[str]]:
        """
        Парсинг данных о товаре с HTML-страницы.

        :param sku: SKU товара
        :param html: HTML-страница товара
        :return: Словарь с данными о товаре
        """
        soup = BeautifulSoup(html, 'html.parser')

        product_name_tag = soup.select_one('h1.f24.card__title')
        product_name = product_name_tag.text.strip() if product_name_tag else None

        brand_tag = soup.select_one('div.card__about-td a.blue-link')
        brand = brand_tag.text.strip() if brand_tag else None

        description_tag = soup.select_one('div.tabs__content > div.text-page-wrapper')
        description = description_tag.text.strip() if description_tag else "нет описания"

        photo_tag = soup.select_one('a.big-image-wrapper img.big-image')
        photo = photo_tag['src'] if photo_tag else None

        delivery_tag = soup.select_one('div.delivery-table')
        stock = 1 if delivery_tag and ("сегодня" in delivery_tag.text or "завтра" in delivery_tag.text) else 0

        price_tag = soup.select_one('p.price')
        price = int(float(price_tag.text.strip().split()[0])) if price_tag else None

        category_name_tag = soup.select_one('breadcrumb-link blue-link')
        category_name = category_name_tag.text.strip() if category_name_tag else None

        logging.info(f"Данные для SKU {sku} успешно распознаны.")

        return {
            "sku": sku[:20],
            "product_name": product_name[:45] if product_name else None,
            "brand": str(brand)[:45] if brand else None,
            "description": description,
            "photo": photo,
            "stock": stock,
            "price": price,
            "category_name": category_name,
        }

    def parse_features(self, html: str) -> Dict[str, str]:
        """
        Парсинг характеристик товара.

        :param html: HTML-страница товара
        :return: Словарь характеристик товара
        """
        soup = BeautifulSoup(html, 'html.parser')
        features = {}
        features_table = soup.select('#tabs .card__about-th, #tabs .card__about-td')

        if features_table:
            for th, td in zip(features_table[0::2], features_table[1::2]):
                key = th.text.strip()
                value = td.text.strip()
                features[key] = value

        logging.info(f"Характеристики успешно извлечены.")
        return features

    def process_skus(self, skus: List[str]) -> List[Dict[str, Optional[str]]]:
        """
        Обработка списка SKU и извлечение данных о товарах.

        :param skus: Список SKU
        :return: Список словарей с данными о товарах
        """
        items = []
        for sku in skus:
            url_desc = f"https://leonardo.ru/ishop/good_{sku}/#itemdesc"
            url_feat = f"https://leonardo.ru/ishop/good_{sku}/#itemfeatures"

            desc_html = self.fetch_page(url_desc)
            feat_html = self.fetch_page(url_feat)

            if desc_html:
                item_data = self.parse_item_data(sku, desc_html)
                if feat_html:
                    item_data["features"] = self.parse_features(feat_html)
                else:
                    item_data["features"] = {}
                items.append(item_data)
            else:
                logging.warning(f"Пропуск SKU {sku} из-за недоступности страницы описания.")

        logging.info(f"Обработка SKU завершена. Обработано {len(items)} товаров.")
        return items
