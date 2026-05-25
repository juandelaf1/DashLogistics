"""
Cost estimation & congestion proxy from existing data sources.
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

TRUCK_MPG = 6.5
DRIVER_RATE = 35.0
MAINTENANCE_PER_MI = 0.15
SPEED_BASELINE = 55.0


def estimate_route_costs(df_routes, fuel_prices=None):
    """Estimate operating costs for each route.
    
    Args:
        df_routes: DataFrame with origin, destination, driving_mi, driving_hr
        fuel_prices: dict of {state: {"diesel": price}}
    Returns:
        DataFrame with cost estimates
    """
    if fuel_prices is None:
        fuel_prices = {}

    rows = []
    for _, r in df_routes.iterrows():
        mi = r["driving_mi"]
        hr = r["driving_hr"]
        orig = r["origin"]

        if mi == 0:
            rows.append({"origin": orig, "destination": r["destination"],
                         "driving_mi": 0, "driving_hr": 0,
                         "fuel_cost": 0, "driver_cost": 0, "maint_cost": 0,
                         "total_cost": 0, "cost_per_mi": 0})
            continue

        diesel_price = fuel_prices.get(orig, {}).get("diesel", 3.50)

        fuel_cost = (mi / TRUCK_MPG) * diesel_price
        driver_cost = hr * DRIVER_RATE
        maint_cost = mi * MAINTENANCE_PER_MI
        total = fuel_cost + driver_cost + maint_cost

        rows.append({
            "origin": orig,
            "destination": r["destination"],
            "driving_mi": round(mi, 1),
            "driving_hr": round(hr, 2),
            "diesel_price": round(diesel_price, 2),
            "fuel_cost": round(fuel_cost, 2),
            "driver_cost": round(driver_cost, 2),
            "maint_cost": round(maint_cost, 2),
            "total_cost": round(total, 2),
            "cost_per_mi": round(total / mi, 4),
            "fuel_pct": round(fuel_cost / total * 100, 1) if total > 0 else 0,
        })

    return pd.DataFrame(rows)


def congestion_proxy(df_routes):
    """Compute congestion proxy: ratio of actual time to free-flow time.
    A ratio > 1.3 suggests notable congestion.
    """
    df = df_routes.copy()
    theoretical_hr = df["driving_mi"] / SPEED_BASELINE
    theoretical_hr = theoretical_hr.replace(0, np.nan)
    df["congestion_ratio"] = (df["driving_hr"] / theoretical_hr).round(3)
    df["congestion_ratio"] = df["congestion_ratio"].fillna(0)
    # Tier: low (<1.1), moderate (1.1-1.3), high (>1.3)
    df["congestion_tier"] = pd.cut(
        df["congestion_ratio"],
        bins=[0, 1.1, 1.3, float("inf")],
        labels=["Low", "Moderate", "High"]
    )
    return df


def combined_lane_analysis(df_lanes, df_congested):
    """Merge lane volume with cost+congestion estimates.
    Ranks routes by: volume per dollar of cost.
    """
    merged = df_lanes.merge(
        df_congested[["origin", "destination", "driving_mi", "total_cost",
                      "cost_per_mi", "fuel_pct", "congestion_ratio", "congestion_tier"]],
        on=["origin", "destination"], how="inner"
    )

    if not merged.empty:
        vol_col = "tons_m"
        if vol_col not in merged.columns:
            # Try tons_2024
            vol_col = [c for c in merged.columns if "tons" in c][0]
        merged["tons_per_dollar"] = (merged[vol_col] / merged["total_cost"]).replace([np.inf, -np.inf], 0).round(6)
        merged["tons_per_mile"] = (merged[vol_col] / merged["driving_mi"]).replace([np.inf, -np.inf], 0).round(2)
        merged = merged.sort_values(vol_col, ascending=False)

    return merged


def build_cost_features(engine):
    """Full pipeline: load routes, estimate costs, merge with lanes, store results."""
    from src.database import read_sql_query, write_df_to_sql

    # Load data
    df_routes = read_sql_query("SELECT * FROM state_routes", engine)
    df_lanes = read_sql_query("SELECT * FROM freight_lanes", engine)
    df_fuel = read_sql_query(
        "SELECT state, diesel FROM fuel_prices "
        "WHERE scraped_at = (SELECT MAX(scraped_at) FROM fuel_prices)", engine
    )

    if df_routes.empty:
        logger.warning("No routes data. Run OSRM routing first.")
        return {}

    # Fuel price lookup
    fuel_prices = {}
    if not df_fuel.empty:
        for _, r in df_fuel.iterrows():
            fuel_prices[r["state"]] = {"diesel": r["diesel"]}

    # Cost estimates
    costs = estimate_route_costs(df_routes, fuel_prices)
    write_df_to_sql(costs, "route_costs", engine, if_exists="replace")
    logger.info(f"Stored {len(costs)} route cost estimates")

    # Congestion proxy
    congested = congestion_proxy(costs)
    write_df_to_sql(congested, "route_congestion", engine, if_exists="replace")
    logger.info(f"Stored {len(congested)} congestion proxies")

    # Combined analysis
    if not df_lanes.empty:
        combined = combined_lane_analysis(df_lanes, congested)
        write_df_to_sql(combined, "lane_efficiency", engine, if_exists="replace")
        logger.info(f"Stored {len(combined)} lane efficiency rankings")

        return {
            "routes": len(costs),
            "high_congestion": len(congested[congested["congestion_tier"] == "High"]),
            "top_efficient": combined.head(5)[["origin", "destination", "tons_per_dollar"]].to_dict("records") if not combined.empty else [],
            "avg_cost_per_mi": costs["cost_per_mi"].mean(),
            "avg_fuel_pct": costs["fuel_pct"].mean(),
        }

    return {"routes": len(costs)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from pathlib import Path
    import sys
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from src.database import get_engine
    e = get_engine()
    r = build_cost_features(e)
    print(f"Results: {r}")
