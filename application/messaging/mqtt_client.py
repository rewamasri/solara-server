import sys
sys.path.append("/app")

import paho.mqtt.client as mqtt
import os
import json
from dotenv import load_dotenv
from ml.inference import predict
from api.routers.sensors import latest_sensor_data
from api.routers.predictions import latest_predictions
from data.database import insert_sensor_data, insert_prediction

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
    try:
        payload = json.loads(msg.payload.decode())
    except json.JSONDecodeError as e:
        print("[MQTT] Bad JSON payload, skipping: " + str(e), flush=True)
        return

    missing = validate_payload(payload)
    if missing:
        print("[MQTT] Missing required fields: " + str(missing) + ", skipping", flush=True)
        return

    print("[MQTT] Received: " + str(payload), flush=True)

    try:
        result = predict(payload)
        print("[ML] Result: " + str(result), flush=True)
        latest_sensor_data.update(payload)
        latest_predictions.update(result)
    except Exception as e:
        print("[ML] Failed: " + str(e), flush=True)
        result = {}

    raw_id = insert_sensor_data(payload)
    if raw_id and result:
        insert_prediction(raw_id, result)

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
