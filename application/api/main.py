import sys
sys.path.append("/app")

from fastapi import FastAPI
from contextlib import asynccontextmanager
from messaging.mqtt_client import start_mqtt, stop_mqtt
from api.routers import sensors, predictions
from api import esri

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_mqtt()
    yield
    stop_mqtt()

app = FastAPI(title="Solara Edge Server", lifespan=lifespan)

app.include_router(sensors.router)
app.include_router(predictions.router)
app.include_router(esri.router)

@app.get("/")
def root():
    return {"service": "solara-edge-server", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}
