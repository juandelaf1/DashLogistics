"""
OSRM routing — real driving distances & times between US state centroids.
"""
import requests
import pandas as pd
import logging
import time
from math import radians, sin, cos, sqrt, atan2

logger = logging.getLogger(__name__)

OSRM_URL = "https://router.project-osrm.org/route/v1/driving"

ST_CENTER = {
    "AL":(32.8,-86.9),"AK":(61.4,-152.5),"AZ":(34.0,-111.7),"AR":(34.8,-92.4),"CA":(36.1,-119.7),
    "CO":(39.0,-105.5),"CT":(41.6,-72.7),"DE":(39.0,-75.5),"FL":(27.8,-81.4),"GA":(32.6,-83.4),
    "HI":(19.7,-155.5),"ID":(44.4,-114.7),"IL":(40.0,-89.4),"IN":(39.8,-86.1),"IA":(42.0,-93.4),
    "KS":(38.5,-98.4),"KY":(37.5,-84.7),"LA":(30.9,-91.7),"ME":(45.3,-69.4),"MD":(39.0,-76.7),
    "MA":(42.4,-72.7),"MI":(44.3,-85.6),"MN":(46.1,-94.3),"MS":(32.8,-89.8),"MO":(38.5,-92.5),
    "MT":(47.0,-109.7),"NE":(41.5,-99.6),"NV":(38.5,-117.1),"NH":(43.6,-71.6),"NJ":(40.3,-74.5),
    "NM":(34.4,-106.1),"NY":(42.8,-75.0),"NC":(35.6,-79.4),"ND":(47.4,-100.4),"OH":(40.3,-82.8),
    "OK":(35.6,-97.1),"OR":(43.8,-120.6),"PA":(41.0,-77.7),"RI":(41.6,-71.5),"SC":(33.9,-80.9),
    "SD":(44.3,-100.2),"TN":(35.9,-86.5),"TX":(31.5,-99.4),"UT":(39.3,-111.7),"VT":(44.1,-72.7),
    "VA":(37.6,-78.4),"WA":(47.3,-120.4),"WV":(38.6,-80.6),"WI":(44.6,-89.9),"WY":(42.9,-107.5),"DC":(38.9,-77.0),
}


def haversine(lat1, lon1, lat2, lon2):
    """Great-circle distance in miles."""
    R = 3959
    dlat = radians(lat2 - lat1); dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))


def route_osrm(origin, destination, timeout=10):
    """Get driving distance (mi) and duration (hrs) via OSRM."""
    olat, olon = ST_CENTER[origin]
    dlat, dlon = ST_CENTER[destination]
    url = f"{OSRM_URL}/{olon},{olat};{dlon},{dlat}?overview=false&annotations=distance"
    headers = {"User-Agent": "DashLogistics/1.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        if data["code"] == "Ok":
            leg = data["routes"][0]
            dist_mi = round(leg["distance"] / 1609.34, 1)
            dur_hr = round(leg["duration"] / 3600, 2)
            return dist_mi, dur_hr
    except Exception as e:
        logger.debug(f"OSRM failed for {origin}→{destination}: {e}")
    return None, None


def route_with_fallback(origin, destination):
    """OSRM first, fallback to haversine distance. Duration estimated."""
    dist_mi, dur_hr = route_osrm(origin, destination)
    if dist_mi is not None:
        return dist_mi, dur_hr

    # Fallback: haversine + estimate 55 mph avg
    olat, olon = ST_CENTER[origin]
    dlat, dlon = ST_CENTER[destination]
    dist_mi = round(haversine(olat, olon, dlat, dlon), 1)
    dur_hr = round(dist_mi / 55, 2)
    return dist_mi, dur_hr


def compute_routes(origin_states, dest_states=None, rate_limit=1):
    """Compute routes for all pairs of origin→destination states.
    
    Args:
        origin_states: list of origin state codes
        dest_states: list of destination state codes (defaults to same as origins)
        rate_limit: seconds between API calls
    Returns:
        DataFrame with columns: origin, destination, driving_mi, driving_hr
    """
    if dest_states is None:
        dest_states = origin_states

    rows = []
    total = len(origin_states) * len(dest_states)
    count = 0

    for orig in origin_states:
        for dest in dest_states:
            if orig == dest:
                rows.append({"origin": orig, "destination": dest, "driving_mi": 0, "driving_hr": 0})
                continue

            # Check if we already computed the reverse
            existing = [r for r in rows if r["origin"] == dest and r["destination"] == orig]
            if existing:
                rows.append({"origin": orig, "destination": dest,
                             "driving_mi": existing[0]["driving_mi"],
                             "driving_hr": existing[0]["driving_hr"]})
                continue

            dist, dur = route_with_fallback(orig, dest)
            rows.append({"origin": orig, "destination": dest, "driving_mi": dist, "driving_hr": dur})
            count += 1
            if count % 10 == 0:
                logger.info(f"  Routes: {count}/{total}")

            time.sleep(rate_limit)

    return pd.DataFrame(rows)


def store_routes(engine, top_states=None):
    """Compute and store routes. If top_states provided, only compute for those."""
    from src.database import write_df_to_sql

    if top_states is None:
        top_states = sorted(ST_CENTER.keys())

    logger.info(f"Computing routes for {len(top_states)} states...")
    df = compute_routes(top_states, rate_limit=0.5)
    write_df_to_sql(df, "state_routes", engine, if_exists="replace")
    logger.info(f"Stored {len(df)} routes")
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Quick test: top 5 states
    test = compute_routes(["CA", "TX", "FL", "NY", "IL"], rate_limit=0)
    print(test.to_string(index=False))
