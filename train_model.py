
import json, joblib, pandas as pd, numpy as np, os
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic_data.csv"
SCHEMA = ROOT / "utils" / "features_schema.json"
OUT_MODEL = ROOT / "models" / "pipeline.pkl"
OUT_REPORT = ROOT / "models" / "model_report.json"

def main():
    df = pd.read_csv(DATA)
    with open(SCHEMA, "r", encoding="utf-8") as f:
        schema = json.load(f)

    feature_names = [f["name"] for f in schema["fields"]]
    target_name = schema["target"]["name"]

    X = df[feature_names].copy()
    y = df[target_name].copy()

    # Identify categorical vs numeric
    cat_cols = [f["name"] for f in schema["fields"] if f["type"] == "category"]
    num_cols = [f["name"] for f in schema["fields"] if f["type"] in ["int", "float"]]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
            ("num", "passthrough", num_cols)
        ]
    )

    model = RandomForestRegressor(
        n_estimators=400,
        max_depth=None,
        random_state=42,
        n_jobs=-1
    )

    pipe = Pipeline(steps=[("prep", preprocessor), ("model", model)])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)

    mae = float(mean_absolute_error(y_test, preds))
    rmse = float(mean_squared_error(y_test, preds, squared=False))
    r2 = float(r2_score(y_test, preds))

    os.makedirs(OUT_MODEL.parent, exist_ok=True)
    joblib.dump(pipe, OUT_MODEL)

    report = {
        "samples": len(df),
        "features": feature_names,
        "metrics": {"MAE": mae, "RMSE": rmse, "R2": r2}
    }
    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("Saved:", OUT_MODEL)
    print("Report:", report)

if __name__ == "__main__":
    main()
