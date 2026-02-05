FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /data

COPY requirements.txt /data/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /data

EXPOSE 5000 8501

CMD ["python3", "main.py"]