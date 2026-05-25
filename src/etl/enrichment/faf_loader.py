import zipfile
import pandas as pd
from pathlib import Path
import requests

RAW_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"

FAF_DOWNLOAD_URL = "https://faf.ornl.gov/faf5/data/FAF5.7.1_State_2018-2024.zip"
FAF_FILENAME = "FAF5.7.1_State_2018-2024.zip"

STATE_FIPS = {
    1: "AL", 2: "AK", 4: "AZ", 5: "AR", 6: "CA", 8: "CO", 9: "CT", 10: "DE",
    11: "DC", 12: "FL", 13: "GA", 15: "HI", 16: "ID", 17: "IL", 18: "IN", 19: "IA",
    20: "KS", 21: "KY", 22: "LA", 23: "ME", 24: "MD", 25: "MA", 26: "MI", 27: "MN",
    28: "MS", 29: "MO", 30: "MT", 31: "NE", 32: "NV", 33: "NH", 34: "NJ", 35: "NM",
    36: "NY", 37: "NC", 38: "ND", 39: "OH", 40: "OK", 41: "OR", 42: "PA", 44: "RI",
    45: "SC", 46: "SD", 47: "TN", 48: "TX", 49: "UT", 50: "VT", 51: "VA", 53: "WA",
    54: "WV", 55: "WI", 56: "WY",
}

SCTG_NAMES = {
    1: "Animals & Fish", 2: "Grains", 3: "Other Ag", 4: "Basic Food", 5: "Milled Food",
    6: "Alcoholic Beverages", 7: "Tobacco", 8: "Building Stone", 9: "Nonmetallic Minerals",
    10: "Metallic Ores", 11: "Crude Petroleum", 12: "Gravel & Sand",
    13: "Phosphate Fertilizers", 14: "Basic Chemicals", 15: "Pharmaceuticals",
    16: "Fertilizer Mixes", 17: "Plastic Products", 18: "Logs & Wood",
    19: "Wood Products", 20: "Pulp & Paper", 21: "Paper Articles",
    22: "Printed Products", 23: "Textiles & Leather", 24: "Nonmetal Mineral Products",
    25: "Base Metal Products", 26: "Machinery", 27: "Electronic Equipment",
    28: "Motor Vehicles", 29: "Transport Equipment", 30: "Precision Instruments",
    31: "Furniture", 32: "Misc. Products", 33: "Waste & Scrap", 34: "Mixed Freight",
    35: "Unknown", 36: "Other", 37: "Tobacco (seperate)",
    38: "Alcohol (seperate)", 39: "Fish (seperate)", 40: "Vegetable Oils",
    41: "Meat", 42: "Live Animals",
}

MODE_NAMES = {1: "Truck", 2: "Rail", 3: "Water", 4: "Air", 5: "Pipeline", 6: "Other", 7: "Multiple", 8: "Parcel"}


def load_faf(filename=FAF_FILENAME):
    faf_path = RAW_DIR / filename
    if not faf_path.exists():
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        print(f"[FAF] Downloading {FAF_DOWNLOAD_URL} ...")
        try:
            r = requests.get(FAF_DOWNLOAD_URL, timeout=600, stream=True)
            r.raise_for_status()
            downloaded = 0
            with open(faf_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
            print(f"[FAF] Downloaded {downloaded / 1024 / 1024:.0f} MB")
        except Exception as e:
            print(f"[FAF] Download failed: {e}")
            print("[FAF] Please manually download from:")
            print("      https://www.bts.gov/faf")
            print(f"      and place the zip at: {faf_path}")
            raise
    zf = zipfile.ZipFile(faf_path)
    csv_name = [n for n in zf.namelist() if n.endswith(".csv")][0]
    cols = [
        "dms_origst", "dms_destst", "dms_mode", "sctg2", "trade_type",
    ]
    year_cols = [f"tons_{y}" for y in range(2018, 2025)]
    val_cols = [f"value_{y}" for y in range(2018, 2025)]
    use_cols = cols + year_cols + val_cols

    print(f"[FAF] Loading {csv_name}...")
    df = pd.read_csv(
        zf.open(csv_name), usecols=use_cols, low_memory=False,
        dtype={c: "float32" for c in year_cols + val_cols},
    )
    print(f"[FAF] Loaded {len(df):,} rows")

    # Filter domestic only
    df = df[df["trade_type"] == 1].copy()
    print(f"[FAF] Domestic: {len(df):,} rows")

    # Filter state-to-state only (no foreign)
    df = df.dropna(subset=["dms_origst", "dms_destst"])
    df["dms_origst"] = df["dms_origst"].astype(int)
    df["dms_destst"] = df["dms_destst"].astype(int)
    # Filter to known FIPS codes
    df = df[df["dms_origst"].isin(STATE_FIPS) & df["dms_destst"].isin(STATE_FIPS)]
    print(f"[FAF] State-to-state: {len(df):,} rows")

    # Map codes
    df["origin"] = df["dms_origst"].map(STATE_FIPS)
    df["destination"] = df["dms_destst"].map(STATE_FIPS)
    df["mode"] = df["dms_mode"].map(MODE_NAMES).fillna("Other")
    df["commodity"] = df["sctg2"].map(SCTG_NAMES).fillna("Unknown")

    return df


def aggregate_yearly(df):
    """Return a yearly summary: total tons and value by year."""
    rows = []
    for y in range(2018, 2025):
        t = df[f"tons_{y}"].sum()
        v = df[f"value_{y}"].sum()
        rows.append({"year": y, "tons_m": round(t / 1e3, 2), "value_b": round(v / 1e3, 2)})
    return pd.DataFrame(rows)


def state_aggregation(df):
    """Aggregate tons and value for each state (origin perspective)."""
    rows = []
    for y in range(2018, 2025):
        t_col, v_col = f"tons_{y}", f"value_{y}"
        by_orig = df.groupby("origin")[[t_col, v_col]].sum().reset_index()
        by_orig.columns = ["state", "tons", "value"]
        by_orig["year"] = y
        rows.append(by_orig)

    result = pd.concat(rows, ignore_index=True)
    # Add latest (2024) per state
    latest = result[result["year"] == 2024].copy()
    latest["tons_m"] = (latest["tons"] / 1e3).round(2)
    latest["value_b"] = (latest["value"] / 1e3).round(2)
    return result, latest


def lanes_aggregation(df, year=2024):
    """Get top origin-destination lanes by tonnage."""
    t_col = f"tons_{year}"
    lanes = df.groupby(["origin", "destination", "commodity", "mode"])[[t_col]].sum().reset_index()
    lanes = lanes.sort_values(t_col, ascending=False)
    lanes["tons_m"] = (lanes[t_col] / 1e3).round(2)
    return lanes.head(100)


def mode_split(df, year=2024):
    """Tons by mode for a given year."""
    t_col = f"tons_{year}"
    return df.groupby("mode")[[t_col]].sum().sort_values(t_col, ascending=False).reset_index()


def commodity_split(df, year=2024):
    """Tons by commodity for a given year."""
    t_col = f"tons_{year}"
    return df.groupby("commodity")[[t_col]].sum().sort_values(t_col, ascending=False).reset_index()


def trade_balance(df, year=2024):
    """Compute net flow (outbound - inbound) for each state."""
    t_col = f"tons_{year}"
    out = df.groupby("origin")[[t_col]].sum().rename(columns={t_col: "outbound"})
    inn = df.groupby("destination")[[t_col]].sum().rename(columns={t_col: "inbound"})
    bal = out.join(inn, how="outer").fillna(0)
    bal["net_tons"] = bal["outbound"] - bal["inbound"]
    bal["net_tons_m"] = (bal["net_tons"] / 1e3).round(2)
    bal = bal.reset_index()
    bal = bal.rename(columns={bal.columns[0]: "state"})
    return bal


def avg_haul(df, year=2024):
    """Average haul distance (ton-miles / tons) by origin state."""
    t_col, tm_col = f"tons_{year}", f"tmiles_{year}"
    if tm_col not in df.columns:
        return pd.DataFrame()
    haul = df.groupby("origin")[[t_col, tm_col]].sum().reset_index()
    haul["avg_miles"] = (haul[tm_col] / haul[t_col]).round(1)
    haul = haul.rename(columns={"origin": "state"})
    return haul[["state", "avg_miles"]]


def top_lanes_by_mode(df, year=2024, mode_name="Truck"):
    """Top lanes for a specific mode."""
    t_col = f"tons_{year}"
    sub = df[df["mode"] == mode_name]
    lanes = sub.groupby(["origin", "destination"])[[t_col]].sum().reset_index()
    lanes = lanes.sort_values(t_col, ascending=False).head(20)
    lanes["tons_m"] = (lanes[t_col] / 1e3).round(2)
    return lanes


def store_freight_data(engine):
    """Load FAF data and store aggregate tables in DB."""
    from src.database import write_df_to_sql

    df = load_faf()

    # State aggregates
    _, state_latest = state_aggregation(df)
    write_df_to_sql(state_latest, "freight_by_state", engine, if_exists="replace")

    # Top lanes
    lanes = lanes_aggregation(df)
    write_df_to_sql(lanes, "freight_lanes", engine, if_exists="replace")

    # Mode split
    modes = mode_split(df)
    write_df_to_sql(modes, "freight_mode_split", engine, if_exists="replace")

    # Commodity split
    commodities = commodity_split(df)
    write_df_to_sql(commodities, "freight_commodities", engine, if_exists="replace")

    # Yearly trends
    yearly = aggregate_yearly(df)
    write_df_to_sql(yearly, "freight_yearly", engine, if_exists="replace")

    # Trade balance
    bal = trade_balance(df)
    write_df_to_sql(bal, "freight_trade_balance", engine, if_exists="replace")

    # Avg haul distance
    haul = avg_haul(df)
    if not haul.empty:
        write_df_to_sql(haul, "freight_avg_haul", engine, if_exists="replace")

    # Top lanes by mode
    for mode_name in ["Truck", "Rail", "Water", "Air"]:
        ml = top_lanes_by_mode(df, mode_name=mode_name)
        if not ml.empty:
            write_df_to_sql(ml, f"freight_lanes_{mode_name.lower()}", engine, if_exists="replace")

    return {
        "state_rows": len(state_latest),
        "lane_rows": len(lanes),
        "total_tons": yearly[yearly["year"] == 2024]["tons_m"].values[0],
        "total_value": yearly[yearly["year"] == 2024]["value_b"].values[0],
    }


if __name__ == "__main__":
    df = load_faf()
    print(f"\nTotal domestic state-to-state rows: {len(df):,}")
    yearly = aggregate_yearly(df)
    print("\nYearly totals:")
    print(yearly.to_string(index=False))

    modes = mode_split(df)
    print("\nMode split (2024):")
    print(modes.to_string(index=False))

    top = lanes_aggregation(df)
    print("\nTop lanes (2024):")
    print(top.head(10).to_string(index=False))
