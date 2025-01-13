FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV DB_URL="postgresql+asyncpg://postgres:2525@localhost/leonardo_parser"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "parser_api:app", "--host", "0.0.0.0", "--port", "8000"]
