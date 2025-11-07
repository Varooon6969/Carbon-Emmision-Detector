
from flask import Flask, request, jsonify
import joblib, json
from pathlib import Path

app = Flask(__name__)

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "pipeline.pkl"
SCHEMA_PATH = ROOT / "utils" / "features_schema.json"

pipe = None
schema = None

def load():
    global pipe, schema
    pipe = joblib.load(MODEL_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)

load()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    # Expect either a dict (single) or list of dicts (batch)
    if isinstance(data, dict):
        instances = [data]
    elif isinstance(data, list):
        instances = data
    else:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Ensure all fields exist; fill N/A if missing
    fields = [f["name"] for f in schema["fields"]]
    cleaned = []
    for row in instances:
        rec = {}
        for name in fields:
            rec[name] = row.get(name, None)
        cleaned.append(rec)

    import pandas as pd
    X = pd.DataFrame(cleaned)

    try:
        yhat = pipe.predict(X)
        return jsonify({"predictions_monthly_co2_kg": [float(v) for v in yhat]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
