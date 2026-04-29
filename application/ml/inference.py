import joblib
import numpy as np
import pandas as pd
import os

# load from same directory as this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

rf = joblib.load(os.path.join(BASE_DIR, "rf_model.pkl"))
scaler = joblib.load(os.path.join(BASE_DIR, "scaler.pkl"))
kmeans = joblib.load(os.path.join(BASE_DIR, "kmeans.pkl"))
iso = joblib.load(os.path.join(BASE_DIR, "iso.pkl"))
numeric_cols = joblib.load(os.path.join(BASE_DIR, "numeric_cols.pkl"))

def validate_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary.")
    missing = [col for col in numeric_cols if col not in payload]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

def predict(payload):
    validate_payload(payload)
    df = pd.DataFrame([payload])
    df[numeric_cols] = scaler.transform(df[numeric_cols])
    df["cluster_label"] = kmeans.predict(df[numeric_cols])
    df["anomaly_score"] = (iso.predict(df[numeric_cols]) == -1).astype(int)
    feature_order = list(numeric_cols) + ["cluster_label", "anomaly_score"]
    X = df[feature_order]
    prediction = rf.predict(X)[0]
    probabilities = rf.predict_proba(X)[0]
    confidence_dict = {
        cls: float(prob)
        for cls, prob in zip(rf.classes_, probabilities)
    }
    return {
        "health_prediction": str(prediction),
        "confidence_scores": confidence_dict,
        "cluster_label": int(df["cluster_label"][0]),
        "is_anomaly": bool(df["anomaly_score"][0])
    }
