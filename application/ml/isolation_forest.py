import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

FEATURES = [
    "latitude", "longitude", "ambient_temp_c", "surface_temp_avg_c",
    "surface_temp_max_c", "humidity_pct", "iaq_index", "lux",
    "soil_temp_c", "soil_moisture_pct", "soil_ph",
    "pitch_deg", "roll_deg", "battery_pct", "power_draw_w"
]

def run_isolation_forest(payload: dict) -> dict:
    try:
        df = pd.DataFrame([payload])
        available = [f for f in FEATURES if f in df.columns]
        X = df[available].fillna(0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model = IsolationForest(contamination=0.1, random_state=42)
        result = model.fit_predict(X_scaled)[0]
        is_outlier = bool(result == -1)
        return {"is_outlier": is_outlier, "features_used": available}
    except Exception as e:
        return {"error": str(e)}
