FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV DB_URL="postgresql://postgres:2525@localhost/leonardo_parser"

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "-m", "category_parser.py"]
