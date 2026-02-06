FROM python:3.11-slim

WORKDIR /app

# Copiamos el requirements.txt de la raíz
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos solo la carpeta del dashboard
COPY dashboard /app

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
