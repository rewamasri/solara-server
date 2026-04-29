import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler

# Load data
df = pd.read_csv("mock_rover_sustainability_data.csv", parse_dates=["timestamp"])

#selecting numeric columns
numeric_cols = df.select_dtypes(include="number").columns
X = df[numeric_cols]

#scaling data
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

#train
iso = IsolationForest(
    n_estimators=200,
    contamination=0.05,  # assume ~5% anomalies
    random_state=42
)

df["anomaly_flag"] = iso.fit_predict(X_scaled)
# -1 = anomaly, 1 = normal

#filter anomalies from the data frame
df_clean = df[df["anomaly_flag"] == 1]

print(f"Rows before: {len(df)}, after removing anomalies: {len(df_clean)}")
