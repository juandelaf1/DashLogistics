import sys; from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.database import get_engine
from src.analysis.cost_estimator import build_cost_features

e = get_engine()
r = build_cost_features(e)
print(f"Routes: {r['routes']}")
print(f"High congestion: {r['high_congestion']}")
print(f"Avg cost/mi: ${r['avg_cost_per_mi']:.2f}")
print(f"Avg fuel %: {r['avg_fuel_pct']:.1f}%")
print(f"Top efficient: {r['top_efficient'][:2]}")
