import joblib
import numpy as np
import pandas as pd

#loads trained models
rf = joblib.load("rf_model.pkl")
scaler = joblib.load("scaler.pkl")
kmeans = joblib.load("kmeans.pkl")
iso = joblib.load("iso.pkl")
numeric_cols = joblib.load("numeric_cols.pkl")


#checks for a valid payload
def validate_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary.")

    missing = [col for col in numeric_cols if col not in payload]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")


#
def predict(payload):
    """
    payload: dict of feature_name -> value
    returns: dict with prediction results
    """
    try:
        validate_payload(payload)

        #converts payload to a dataframe
        df = pd.DataFrame([payload])

        #scales features
        df[numeric_cols] = scaler.transform(df[numeric_cols])

        #Add a cluster label for the kmeans prediction and an aomoly score for
        #isolation foresting prediction
        df["cluster_label"] = kmeans.predict(df[numeric_cols])
        df["anomaly_score"] = (iso.predict(df[numeric_cols]) == -1).astype(int)




        #builds a feature matrix to ensure order of features
        # is the same as the training order
        feature_order = numeric_cols + ["cluster_label", "anomaly_score"]
        X = df[feature_order]



        #predicts using random forest
        prediction = rf.predict(X)[0]
        probabilities = rf.predict_proba(X)[0]


        #matches each class with its probability
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
    except Exception as e:
        return {"error":str(e)}
