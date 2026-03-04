from fastapi import FastAPI
from pydantic import BaseModel
from inference import predict

app = FastAPI()

class SensorPayload(BaseModel):
    latitude: float
    longitude: float
    ambient_temp_c: float
    surface_temp_avg_c: float
    surface_temp_max_c: float
    humidity_pct: float
    iaq_index: float
    lux: float
    soil_temp_c: float
    soil_moisture_pct: float
    soil_ph: float
    pitch_deg: float
    roll_deg: float
    battery_pct: float
    power_draw_w: float


@app.post("/predict")
def run_model(payload: SensorPayload):
    result = predict(payload.dict())
    return result