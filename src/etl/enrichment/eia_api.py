import os
import sys
import logging
from pathlib import Path
import time

import pandas as pd
import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.database import get_engine, write_df_to_sql, read_sql_query

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[3]
LOG_PATH = BASE_DIR / "logs" / "eia_api.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

EIA_API_KEY = os.getenv("EIA_API_KEY")
BASE_URL = "https://api.eia.gov/v2/petroleum/pri/gnd/data/"

STATE_AREA_MAP = {
    "CA": "SCA", "CO": "SCO", "MA": "SMA",
    "NY": "SNY", "TX": "STX",
}

def fetch_eia_data(product: str, area: str = "NUS") -> list:
    params = {
        "api_key": EIA_API_KEY,
        "frequency": "weekly",
        "data[0]": "value",
        "facets[duoarea][]": area,
        "facets[product][]": product,
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "length": 10,
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        return r.json()["response"]["data"]
    except Exception as e:
        logger.warning(f"EIA fetch error ({product}, {area}): {e}")
        return []

def fetch_fuel_prices():
    if not EIA_API_KEY:
        logger.error("EIA_API_KEY no configurada en .env")
        return pd.DataFrame()

    run_id = os.getenv("PIPELINE_RUN_ID", "unknown")

    products = {
        "EPM0R": "regular",
        "EPM0M": "mid_grade",
        "EPM0P": "premium",
        "EPD2D": "diesel",
    }

    records = []

    for product, name in products.items():
        data = fetch_eia_data(product, "NUS")
        for row in data:
            records.append({
                "state": "US",
                "fuel_type": name,
                "price": float(row["value"]),
                "period": row["period"],
                "product_code": product,
                "area_name": row.get("area-name", "U.S."),
                "data_source": "EIA",
                "pipeline_run_id": run_id,
            })

        for state_code, area_code in STATE_AREA_MAP.items():
            data = fetch_eia_data(product, area_code)
            for row in data:
                records.append({
                    "state": state_code,
                    "fuel_type": name,
                    "price": float(row["value"]),
                    "period": row["period"],
                    "product_code": product,
                    "area_name": row.get("area-name", state_code),
                    "data_source": "EIA",
                    "pipeline_run_id": run_id,
                })
            time.sleep(0.2)

    if not records:
        logger.warning("No EIA data fetched")
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df = df.drop_duplicates(subset=["state", "fuel_type", "period"])

    engine = get_engine()
    write_df_to_sql(df, "eia_fuel_prices", engine, if_exists="replace")
    logger.info(f"{len(df)} EIA fuel price records saved")
    return df


if __name__ == "__main__":
    fetch_fuel_prices()
