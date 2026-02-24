import paho.mqtt.client as mqtt
import json, yaml

# NOTICE: WORKING INSIDE PAHO-SUBSCRIBER VIRTUAL ENV, NOT REGULAR VENV


with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

broker = config["broker"]
topics = config["topics"]
QoS    = config["subscriber"]["qos"]

def on_connect(client, userdata, flags, rc):
    print(f"[SUBSCRIBER] Connected rc={rc}")
    client.subscribe(topics["all"],    qos=QoS)
    client.subscribe(topics["status"], qos=QoS)

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    print(f"[{msg.topic}] {json.dumps(payload, indent=2)}")

client = mqtt.Client(client_id=broker["client_id"], clean_session=broker["clean_session"])
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker["host"], broker["port"], broker["keepalive"])
client.loop_forever()