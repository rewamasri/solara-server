from fastapi import FastAPI
from pydantic import BaseModel, Field, ConfigDict
from inference import predict

app = FastAPI()


class SensorPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")  # rejects extra fields

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

    ambient_temp_c: float = Field(..., ge=-50, le=100)
    surface_temp_avg_c: float = Field(..., ge=-50, le=120)
    surface_temp_max_c: float = Field(..., ge=-50, le=150)

    humidity_pct: float = Field(..., ge=0, le=100)
    iaq_index: float = Field(..., ge=0, le=500)
    lux: float = Field(..., ge=0, le=200000)

    soil_temp_c: float = Field(..., ge=-20, le=60)
    soil_moisture_pct: float = Field(..., ge=0, le=100)
    soil_ph: float = Field(..., ge=0, le=14)

    pitch_deg: float = Field(..., ge=-180, le=180)
    roll_deg: float = Field(..., ge=-180, le=180)

    battery_pct: float = Field(..., ge=0, le=100)
    power_draw_w: float = Field(..., ge=0)


@app.post("/predict")
def run_model(payload: SensorPayload):
    return predict(payload.model_dump())
