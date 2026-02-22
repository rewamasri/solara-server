from fastapi import APIRouter, HTTPException
from api.routers.sensors import latest_sensor_data
from api.routers.predictions import latest_predictions

router = APIRouter()

def format_geojson(sensor: dict, predictions: dict) -> dict:
    if not sensor:
        return {}
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        sensor.get("longitude"),
                        sensor.get("latitude")
                    ]
                },
                "properties": {
                    "timestamp": sensor.get("timestamp"),
                    "ambient_temp_c": sensor.get("ambient_temp_c"),
                    "humidity_pct": sensor.get("humidity_pct"),
                    "soil_moisture_pct": sensor.get("soil_moisture_pct"),
                    "soil_ph": sensor.get("soil_ph"),
                    "battery_pct": sensor.get("battery_pct"),
                    "kmeans_cluster": predictions.get("kmeans", {}).get("cluster"),
                    "is_outlier": predictions.get("isolation_forest", {}).get("is_outlier"),
                    "rf_prediction": predictions.get("random_forest", {}).get("prediction"),
                }
            }
        ]
    }

@router.get("/esri/geojson")
def get_geojson():
    if not latest_sensor_data:
        raise HTTPException(status_code=404, detail="No data available yet")
    return format_geojson(latest_sensor_data, latest_predictions)
