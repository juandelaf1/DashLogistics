FROM python:3.11-slim

# --- System dependencies ---
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    libxml2 \
    libxslt1-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- Working directory ---
WORKDIR /data

# --- Install Python dependencies ---
COPY requirements.txt /data/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Copy project ---
COPY . /data

# --- Expose ports ---
EXPOSE 5000 8501

# --- Run app ---
CMD ["python3", "main.py"]
