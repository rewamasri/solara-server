import paho.mqtt.client as mqtt
import json, yaml, os
from datetime import datetime

# NOTICE: WORKING INSIDE MQTT-SUBSCRIBER VIRTUAL ENV, NOT REGULAR VENV

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

broker  = config["broker"]
topics  = config["topics"]
QoS     = config["subscriber"]["qos"]

# OUTPUT FOLDER - for testing purposes but will have to change to route to database for ml and esri
DATA_DIR = config["subscriber"]["data_dir"]
os.makedirs(DATA_DIR, exist_ok=True)

# CALLBACKS 
def on_connect(client, userdata, flags, rc):
    print(f"[SUBSCRIBER] Connected rc={rc}")
    client.subscribe(topics["all"],    qos=QoS)
    client.subscribe(topics["status"], qos=QoS)

def on_message(client, userdata, msg):
    payload   = json.loads(msg.payload.decode())
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")

    # filename: topic levels joined with "_" + timestamp
    # e.g. sensors_all_2025-01-01T00-00-00Z.json
    topic_slug = msg.topic.replace("/", "_")
    filename   = f"{topic_slug}_{timestamp}.json"
    filepath   = os.path.join(DATA_DIR, filename)

    with open(filepath, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"[SUBSCRIBER] Saved → {filepath}")

# CLIENT 
client = mqtt.Client(client_id=broker["client_id"], clean_session=broker["clean_session"])
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker["host"], broker["port"], broker["keepalive"])
client.loop_forever()