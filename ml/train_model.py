import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
import joblib

#loads the csv
df = pd.read_csv("mock_rover_sustainability_data.csv", parse_dates=["timestamp"])

#checks if data is corrupted
df.info()
df.describe()

#separates columns
non_numeric_cols = ["timestamp"]
numeric_cols = df.select_dtypes(include="number").columns



#removes extreme outliers
def remove_outliers_iqr(df, columns, k=1.5):
    filtered_df = df.copy()
    for col in columns:
        Q1 = filtered_df[col].quantile(0.25)
        Q3 = filtered_df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - k * IQR
        upper = Q3 + k * IQR

        filtered_df = filtered_df[
            (filtered_df[col] >= lower) &
            (filtered_df[col] <= upper)
        ]
    return filtered_df

#apply removing extreme outliers to numeric features only (not time stamps)
df_clean = remove_outliers_iqr(df, numeric_cols)

print(f"Rows before: {len(df)}, after: {len(df_clean)}")



#normalzies features using minmax scaling
#(making every value between 0 and 1)
scaler = MinMaxScaler()

df_scaled = df_clean.copy()
df_scaled[numeric_cols] = scaler.fit_transform(df_clean[numeric_cols])

#implementing isolationforesting

iso = IsolationForest(
    n_estimators=200,
    contamination=0.05,
    random_state=42
)

df_scaled["anomaly_score"] = iso.fit_predict(
    df_scaled[numeric_cols]
)

# Convert {-1, 1} → {1 = anomaly, 0 = normal}
df_scaled["anomaly_score"] = (df_scaled["anomaly_score"] == -1).astype(int)


#implementing kmeans

kmeans = KMeans(
    n_clusters=2,
    random_state=42,
    n_init=10
)

df_scaled["cluster_label"] = kmeans.fit_predict(
    df_scaled[numeric_cols]
)

#tests if scaling worked (all cols are between 0 and 1)
assert np.all(df_scaled[numeric_cols].min() >= -1e-9)
assert np.all(df_scaled[numeric_cols].max() <= 1 + 1e-9)

print("Scaling Test Passed!!")


#health rules (subject to change)
def label_health(row):
    if row["soil_moisture_pct"] < 0.3:
        return "Needs watering"
    elif row["surface_temp_max_c"] > 0.8:
        return "Heat stress"
    elif row["soil_ph"] < 0.4 or row["soil_ph"] > 0.7:
        return "pH issue"
    else:
        return "Healthy"

df_scaled["health_status"] = df_scaled.apply(label_health, axis=1)

#adding extra "noise" to take into account imperfect sensors
df_scaled["soil_moisture_pct"] += np.random.normal(0, 0.05, len(df_scaled))
df_scaled["surface_temp_max_c"] += np.random.normal(0, 0.05, len(df_scaled))



#begin random foresting
target_col = "health_status"


#define x -> features and y -> columns
X = df_scaled[
    list(numeric_cols) +
    ["cluster_label", "anomaly_score"]
]

y = df_scaled["health_status"]

#Train test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

#training the random forest
rf = RandomForestClassifier(
    n_estimators=200, #num of trees
    max_depth=None,   #trees can fully grow, won't get cut off
    min_samples_split=2,
    random_state=42,
    n_jobs=-1       #uses all CPU cores
)



rf.fit(X_train, y_train)

#evaluation
y_pred = rf.predict(X_test)

#how accurate the predictions were 
print("Accuracy:", accuracy_score(y_test, y_pred))

#precision = true pos/(true pos+ false pos) (accuracy of positive predictions)
#recall = true pos/(true pos + false neg) (ability to find all positives)
#f1 score = mean of precision and recall
#support -> actual numbe of real occurances (true positives, true negatives)

print("\nClassification Report: \n", classification_report(y_test, y_pred))

#confusion matrices show the false postives(bottom left), false negatives(top right), 
# true positives(top left), true negatives(bottom right)
print("\n Confusion Matrix: \n ", confusion_matrix(y_test, y_pred))



#pickles -> convert python objects to bytes so we can load it later
#trains model saves it to a pickle so we can load it later for inference
#Joblib is a library built on top of pickle where it actually compresses it and loads it
joblib.dump(rf, "rf_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(kmeans, "kmeans.pkl")
joblib.dump(iso, "iso.pkl")
joblib.dump(list(numeric_cols), "numeric_cols.pkl")
