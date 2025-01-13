import logging
import os
import sys

import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логгирования
logging.basicConfig(
    filename="telegram_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Функция для обработки сообщений с ID товара
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает сообщения, содержащие ID товара.

    :param update: Объект Update от Telegram API
    :param context: Контекст команды
    """
    product_id = update.message.text.strip()

    # Проверяем, является ли введенное сообщение числом
    if not product_id.isdigit():
        logging.warning(f"Получен некорректный ID: {product_id}")
        await update.message.reply_text("Пожалуйста, введите корректный ID товара (число).")
        return

    url = f"http://127.0.0.1:8000/category-item/{product_id}"
    logging.info(f"Запрос на получение данных по ID товара: {product_id}")

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            logging.info(f"Данные успешно получены для ID товара {product_id}: {data}")
            data_str = ""
            for key, value in data.items():
                data_str += f"\t{key}: {value}\n\n"
            await update.message.reply_text(f"Данные по товару: {data_str}")
        elif response.status_code == 404 and response.json().get("detail") == "CategoryItem not found":
            logging.warning(f"Товар с ID {product_id} не найден.")
            await update.message.reply_text("Ничего не найдено для данного ID.")
        else:
            logging.error(f"Ошибка сервера: {response.status_code} {response.text}")
            await update.message.reply_text(f"Произошла ошибка: {response.status_code} {response.text}")
    except requests.RequestException as e:
        logging.error(f"Ошибка при выполнении HTTP-запроса для ID {product_id}: {e}")
        await update.message.reply_text(f"Ошибка при запросе: {e}")

# Функция для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отправляет приветственное сообщение пользователю при вводе команды /start.

    :param update: Объект Update от Telegram API
    :param context: Контекст команды
    """
    logging.info("Получена команда /start.")
    await update.message.reply_text("Добро пожаловать! Введите ID товара, чтобы получить данные о нем.")

# Основной код для запуска бота
def main():
    """
    Основная функция для настройки и запуска Telegram-бота.
    """
    # Вставьте сюда токен вашего бота
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7970568882:AAHhmjdO5TqtD_zMmBzN2PxZsS-TBvw29ZM")

    if not TELEGRAM_BOT_TOKEN:
        logging.critical("Токен Telegram-бота не указан. Завершение работы.")
        sys.exit("Ошибка: токен Telegram-бота не указан.")

    logging.info("Запуск Telegram-бота.")
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Обработка команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    try:
        application.run_polling()
    except Exception as e:
        logging.critical(f"Критическая ошибка при запуске бота: {e}")
        sys.exit(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
