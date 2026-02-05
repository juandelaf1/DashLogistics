import requests
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

RAW_PATH = Path(os.getenv("RAW_DATA_PATH"))
DATA_URL = os.getenv("DATA_URL")

def download_dataset():
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(DATA_URL)
    response.raise_for_status()

    RAW_PATH.write_bytes(response.content)
    print(f"Dataset descargado en: {RAW_PATH}")

if __name__ == "__main__":
    download_dataset()