FROM python:3.11-slim

WORKDIR /app

# Copiamos el requirements.txt de la raíz
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos solo la carpeta de la API
COPY api /app

EXPOSE 5000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
