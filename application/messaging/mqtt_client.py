import sys
sys.path.append("/app")

import paho.mqtt.client as mqtt
import os
import json
from dotenv import load_dotenv
from ml.kmeans import run_kmeans
from ml.isolation_forest import run_isolation_forest
from ml.random_forest import run_random_forest
from api.routers.sensors import latest_sensor_data
from api.routers.predictions import latest_predictions

load_dotenv()

BROKER = os.getenv("MQTT_BROKER", "mosquitto")
TOPIC = os.getenv("MQTT_TOPIC", "solara/sensors")

REQUIRED_FIELDS = ["timestamp", "latitude", "longitude"]

_client = None

def validate_payload(payload: dict) -> list:
    return [f for f in REQUIRED_FIELDS if f not in payload]

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[MQTT] Connected. Subscribed to " + TOPIC, flush=True)
        client.subscribe(TOPIC)
    else:
        print("[MQTT] Connection failed, code " + str(rc), flush=True)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("[MQTT] Unexpected disconnect, will auto-reconnect...", flush=True)

def on_message(client, userdata, msg):
    # parse JSON
    try:
        payload = json.loads(msg.payload.decode())
    except json.JSONDecodeError as e:
        print("[MQTT] Bad JSON payload, skipping: " + str(e), flush=True)
        return

    # validate required fields
    missing = validate_payload(payload)
    if missing:
        print("[MQTT] Missing required fields: " + str(missing) + ", skipping", flush=True)
        return

    print("[MQTT] Received: " + str(payload), flush=True)

    # run ML with individual error handling
    try:
        kmeans_result = run_kmeans(payload)
    except Exception as e:
        kmeans_result = {"error": str(e)}
        print("[ML] KMeans failed: " + str(e), flush=True)

    try:
        iso_result = run_isolation_forest(payload)
    except Exception as e:
        iso_result = {"error": str(e)}
        print("[ML] Isolation Forest failed: " + str(e), flush=True)

    try:
        rf_result = run_random_forest(payload)
    except Exception as e:
        rf_result = {"error": str(e)}
        print("[ML] Random Forest failed: " + str(e), flush=True)

    print("[ML] KMeans: " + str(kmeans_result), flush=True)
    print("[ML] Isolation Forest: " + str(iso_result), flush=True)
    print("[ML] Random Forest: " + str(rf_result), flush=True)

    # store results
    latest_sensor_data.update(payload)
    latest_predictions.update({
        "kmeans": kmeans_result,
        "isolation_forest": iso_result,
        "random_forest": rf_result
    })

def start_mqtt():
    global _client
    _client = mqtt.Client()
    _client.on_connect = on_connect
    _client.on_disconnect = on_disconnect
    _client.on_message = on_message
    try:
        _client.connect(BROKER, 1883, keepalive=60)
        _client.loop_start()
    except Exception as e:
        print("[MQTT] Failed to connect: " + str(e), flush=True)

def stop_mqtt():
    global _client
    if _client:
        _client.loop_stop()
        _client.disconnect()
