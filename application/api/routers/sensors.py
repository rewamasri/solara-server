from fastapi import APIRouter, HTTPException

router = APIRouter()

latest_sensor_data = {}

@router.get("/sensors/latest")
def get_latest_sensor():
    if not latest_sensor_data:
        raise HTTPException(status_code=404, detail="No sensor data received yet")
    return latest_sensor_data
