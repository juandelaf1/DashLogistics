FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN printf '#!/bin/bash\n\
if [ ! -f data/dashlogistics.db ]; then\n\
  echo "[DashLogistics] Running pipeline to initialize database..."\n\
  python main.py 2>&1\n\
  echo "[DashLogistics] Pipeline complete"\n\
fi\n\
exec streamlit run dashboard/dashboard.py --server.port=8502 --server.address=0.0.0.0\n\
' > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 8502

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8502/_stcore/health')" || exit 1

ENTRYPOINT ["/entrypoint.sh"]
