import sys
sys.path.append("/app")

import os
import json
import pyodbc
from dotenv import load_dotenv

load_dotenv()

SERVER = os.getenv("DB_HOST", "azure-sql-edge")
DATABASE = os.getenv("DB_NAME", "master")
USERNAME = "sa"
PASSWORD = os.getenv("SA_PASSWORD", "")

def get_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={SERVER},1433;"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def insert_sensor_data(payload: dict, sensor_id: str = "rover_01") -> int:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO raw_sensor_data (sensor_id, json_payload) OUTPUT INSERTED.id VALUES (?, ?)",
            sensor_id,
            json.dumps(payload)
        )
        row_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        print("[DB] Inserted sensor data, id: " + str(row_id), flush=True)
        return row_id
    except Exception as e:
        print("[DB] Failed to insert sensor data: " + str(e), flush=True)
        return None

def insert_prediction(raw_data_id: int, prediction: dict) -> None:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        prediction_value = 1.0 if prediction.get("is_anomaly") else 0.0
        model_version = "1.0"
        cursor.execute(
            "INSERT INTO predictions (raw_data_id, prediction_value, model_version) VALUES (?, ?, ?)",
            raw_data_id,
            prediction_value,
            model_version
        )
        conn.commit()
        conn.close()
        print("[DB] Inserted prediction for raw_data_id: " + str(raw_data_id), flush=True)
    except Exception as e:
        print("[DB] Failed to insert prediction: " + str(e), flush=True)
