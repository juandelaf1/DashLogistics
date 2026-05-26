import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from src.database import read_sql_query, write_df_to_sql


def train_cost_predictor(engine):
    """Train a linear regression model to predict total_cost from route features."""
    
    df = read_sql_query("SELECT * FROM route_costs", engine)
    if df.empty or len(df) < 50:
        print("[ML] Insufficient route data, skipping")
        return

    features = ["driving_mi", "driving_hr"]
    target = "total_cost"

    X = df[features].copy()
    y = df[target].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    metrics = {
        "r2": round(r2_score(y_test, y_pred), 4),
        "mae": round(mean_absolute_error(y_test, y_pred), 2),
        "rmse": round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }
    print(f"[ML] R² = {metrics['r2']}  |  MAE = ${metrics['mae']}  |  RMSE = ${metrics['rmse']}")

    coef_df = pd.DataFrame({
        "feature": ["intercept"] + features,
        "coefficient": [round(model.intercept_, 2)] + [round(c, 6) for c in model.coef_],
    })
    write_df_to_sql(coef_df, "ml_coefficients", engine, if_exists="replace")

    metrics_df = pd.DataFrame([metrics])
    write_df_to_sql(metrics_df, "ml_metrics", engine, if_exists="replace")

    test_df = X_test.copy()
    test_df["actual_cost"] = y_test.values
    test_df["predicted_cost"] = y_pred.round(2)
    test_df["error"] = test_df["predicted_cost"] - test_df["actual_cost"]
    test_df["error_pct"] = (test_df["error"] / test_df["actual_cost"] * 100).round(1)
    test_df = test_df.reset_index(drop=True)
    write_df_to_sql(test_df, "ml_predictions", engine, if_exists="replace")

    print(f"[ML] Predictions saved: {len(test_df)} test routes")

    return metrics


if __name__ == "__main__":
    from src.database import get_engine
    eng = get_engine()
    train_cost_predictor(eng)
