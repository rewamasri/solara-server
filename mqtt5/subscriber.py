import paho.mqtt.client as mqtt
import json, yaml, os
from datetime import datetime
import requests

# NOTICE: WORKING INSIDE MQTT-SUBSCRIBER VIRTUAL ENV, NOT REGULAR VENV

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

API_URL = config["api"]["url"]
broker  = config["broker"]
topics  = config["topics"]
QoS     = config["subscriber"]["qos"]

# OUTPUT FOLDER - for testing purposes but will have to change to route to database for ml and esri
DATA_DIR = config["subscriber"]["data_dir"]
os.makedirs(DATA_DIR, exist_ok=True)

# CALLBACKS 
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[SUBSCRIBER] Connected rc={reason_code}")
    result1 = client.subscribe(topics["ML"],     qos=QoS)
    result2 = client.subscribe(topics["ESRI"],   qos=QoS)
    result3 = client.subscribe(topics["status"], qos=QoS)
    print(f"[SUBSCRIBER] Subscribe results: {result1}, {result2}, {result3}")

def on_message(client, userdata, msg):
    try:
        payload   = json.loads(msg.payload.decode())
    except json.JSONDecodeError as e:
        print(f"[SUBSCRIBER] Bad JSON on {msg.topic}: {e}")
        return
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
    topic_slug = msg.topic.replace("/", "_")
    filename   = f"{topic_slug}_{timestamp}.json"
    filepath   = os.path.join(DATA_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"[SUBSCRIBER] Saved --> {filepath}")

# CLIENT 
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id=broker["client_id"],
    clean_session=broker["clean_session"]
)
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker["host"], broker["port"], broker["keepalive"])
client.loop_forever()