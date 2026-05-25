import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)

URL = "https://agtransport.usda.gov/resource/qm5q-5r5f.json"
REGION_MAP = {
    "CALIFORNIA": "CA", "ARIZONA": "AZ", "FLORIDA": "FL",
    "TEXAS": "TX", "NEW YORK": "NY", "GREAT LAKES": "IL,IN,MI,OH,WI",
    "SOUTHEAST": "GA,NC,SC,AL,MS,TN", "PNW": "OR,WA,ID,MT",
    "MID-ATLANTIC": "PA,NJ,MD,DE,VA,WV", "OTHER": None,
}


def fetch_truck_rates(year=2025):
    """Fetch real refrigerated truck rates per mile from USDA."""
    params = {
        "$where": f"year={year}",
        "$order": "quarter, region, destination",
        "$limit": 10000,
    }
    headers = {"User-Agent": "DashLogistics/1.0"}

    try:
        r = requests.get(URL, params=params, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        logger.info(f"USDA: fetched {len(data)} rate records for {year}")
    except Exception as e:
        logger.warning(f"USDA API error: {e}")
        return pd.DataFrame()

    rows = []
    for row in data:
        dest = row.get("destination", "").upper().strip()
        rows.append({
            "year": int(row.get("year", year)),
            "quarter": int(row.get("quarter", 1)),
            "origin_state": REGION_MAP.get(row.get("region", ""), row.get("region")),
            "destination": dest,
            "rate_per_mile": round(float(row.get("rate_per_mile", 0)), 4),
            "rate_per_truckload": round(float(row.get("rate_per_truckload", 0)), 2),
        })

    return pd.DataFrame(rows)


def store_usda_rates(engine):
    """Fetch and store USDA truck rates."""
    from src.database import write_df_to_sql
    df = fetch_truck_rates()
    if not df.empty:
        write_df_to_sql(df, "truck_rates", engine, if_exists="replace")
        logger.info(f"USDA: stored {len(df)} records")
    return len(df)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parents[3]))
    logging.basicConfig(level=logging.INFO)
    df = fetch_truck_rates()
    print(f"Records: {len(df)}")
    if not df.empty:
        print(df.head(10).to_string(index=False))
        print(f"\nRate per mile stats: min={df['rate_per_mile'].min():.2f} max={df['rate_per_mile'].max():.2f} avg={df['rate_per_mile'].mean():.2f}")
