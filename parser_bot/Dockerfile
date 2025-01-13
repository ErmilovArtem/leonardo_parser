FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV TELEGRAM_BOT_TOKEN="7970568882:AAHhmjdO5TqtD_zMmBzN2PxZsS-TBvw29ZM"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

# Команда для запуска бота
CMD ["python", "tg_bot.py"]
