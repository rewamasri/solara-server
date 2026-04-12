import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

FEATURES = [
    "ambient_temp_c", "surface_temp_avg_c", "surface_temp_max_c",
    "humidity_pct", "iaq_index", "lux", "soil_temp_c",
    "soil_moisture_pct", "soil_ph"
]

def run_kmeans(payload: dict, n_clusters: int = 3) -> dict:
    try:
        df = pd.DataFrame([payload])
        available = [f for f in FEATURES if f in df.columns]
        X = df[available].fillna(0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        n = min(n_clusters, len(X))
        model = KMeans(n_clusters=n, random_state=42, n_init=10)
        cluster = int(model.fit_predict(X_scaled)[0])
        return {"cluster": cluster, "features_used": available}
    except Exception as e:
        return {"error": str(e)}
