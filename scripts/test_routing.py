import sys; from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.etl.enrichment.osrm_routing import route_with_fallback, compute_routes

# Quick test
r = route_with_fallback("CA", "NY")
print(f"CA -> NY: {r[0]} mi, {r[1]} hrs")

r2 = route_with_fallback("TX", "IL")
print(f"TX -> IL: {r2[0]} mi, {r2[1]} hrs")

r3 = route_with_fallback("FL", "WA")
print(f"FL -> WA: {r3[0]} mi, {r3[1]} hrs")

# Test batch for top 5
from src.etl.enrichment.faf_loader import load_faf, lanes_aggregation
df = load_faf()
lanes = lanes_aggregation(df)
top_origins = lanes["origin"].value_counts().head(10).index.tolist()
print(f"\nTop 10 origin states: {top_origins}")

# Compute for top 10 states
routes = compute_routes(top_origins, rate_limit=0.3)
print(routes.to_string(index=False))
