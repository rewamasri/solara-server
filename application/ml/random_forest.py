import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

FEATURES = [
    "latitude", "longitude", "ambient_temp_c", "surface_temp_avg_c",
    "surface_temp_max_c", "humidity_pct", "iaq_index", "lux",
    "soil_temp_c", "soil_moisture_pct", "soil_ph",
    "pitch_deg", "roll_deg", "battery_pct", "power_draw_w"
]

def run_random_forest(payload: dict) -> dict:
    try:
        df = pd.DataFrame([payload])
        available = [f for f in FEATURES if f in df.columns]
        X = df[available].fillna(0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        X_mock = np.random.rand(20, len(available))
        y_mock = np.random.randint(0, 3, 20)
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_mock, y_mock)
        prediction = int(model.predict(X_scaled)[0])
        probabilities = model.predict_proba(X_scaled)[0].tolist()
        return {"prediction": prediction, "probabilities": probabilities, "features_used": available}
    except Exception as e:
        return {"error": str(e)}
