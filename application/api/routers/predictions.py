from fastapi import APIRouter, HTTPException

router = APIRouter()

latest_predictions = {}

@router.get("/predictions/latest")
def get_latest_predictions():
    if not latest_predictions:
        raise HTTPException(status_code=404, detail="No predictions available yet")
    return latest_predictions
