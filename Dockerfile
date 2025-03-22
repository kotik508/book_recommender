FROM python:3.12.9-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libatlas-base-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /bookie

ENV FLASK_RUN_HOST=0.0.0.0

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN flask --app main.py db migrate

EXPOSE 5000

CMD ["python", "./main.py"]