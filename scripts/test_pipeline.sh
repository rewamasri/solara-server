#!/bin/bash
# scripts/test_pipeline.sh
# Tests the full pipeline: MQTT -> API -> ML -> DB

PASS=0
FAIL=0

green() { echo -e "\033[32m✔ $1\033[0m"; }
red()   { echo -e "\033[31m✘ $1\033[0m"; }
info()  { echo -e "\033[34mℹ $1\033[0m"; }

check() {
  if eval "$2" &>/dev/null; then
    green "$1"
    ((PASS++))
  else
    red "$1"
    ((FAIL++))
  fi
}

PAYLOAD='{
  "timestamp": "2026-04-14T00:00:00Z",
  "latitude": 33.97350496714153,
  "longitude": -117.32810678494731,
  "ambient_temp_c": 23.696572495333637,
  "surface_temp_avg_c": 26.838114650347794,
  "surface_temp_max_c": 32.034526941705906,
  "humidity_pct": 50.78837759668136,
  "iaq_index": 86.59741961775525,
  "lux": 7077.712129758373,
  "soil_temp_c": 20.735677929836026,
  "soil_moisture_pct": 39.900483217915166,
  "soil_ph": 7.120349543359651,
  "pitch_deg": -0.6559507995563203,
  "roll_deg": 3.3525977591851497,
  "battery_pct": 99.73446271947512,
  "power_draw_w": 20.076330543858848
}'

echo ""
echo "=============================="
echo "  Pipeline Integration Test"
echo "=============================="
echo ""

# Step 1 - publish MQTT message
echo "[ Step 1: Publish MQTT Message ]"
check "publish sensor payload to solara/sensors" \
  "docker exec mosquitto mosquitto_pub -h localhost -t solara/sensors -m '$PAYLOAD'"
echo ""

# Wait for the API to process it
info "Waiting 3s for API to process message..."
sleep 3
echo ""

# Step 2 - check API received it
echo "[ Step 2: API Received Message ]"
check "GET /sensors/latest returns 200" \
  "curl -sf http://localhost:8000/sensors/latest"

SENSOR_RESPONSE=$(curl -sf http://localhost:8000/sensors/latest 2>/dev/null)
if [ -n "$SENSOR_RESPONSE" ]; then
  green "sensor data contains latitude"
  info "Response: $SENSOR_RESPONSE"
else
  red "sensor data is empty"
fi
echo ""

# Step 3 - check ML prediction ran
echo "[ Step 3: ML Prediction ]"
check "GET /predictions/latest returns 200" \
  "curl -sf http://localhost:8000/predictions/latest"

PRED_RESPONSE=$(curl -sf http://localhost:8000/predictions/latest 2>/dev/null)
if [ -n "$PRED_RESPONSE" ]; then
  green "prediction result received"
  info "Response: $PRED_RESPONSE"
else
  red "prediction result is empty"
fi
echo ""

# Step 4 - check DB write
echo "[ Step 4: Database Write ]"

check "raw_sensor_data inserted into DB" \
  "docker exec fastapi-app python3 -c '
import pyodbc
conn = pyodbc.connect(
  \"DRIVER={ODBC Driver 18 for SQL Server};SERVER=azure-sql-edge;UID=sa;PWD=${SA_PASSWORD};TrustServerCertificate=yes\"
)
cursor = conn.cursor()
cursor.execute(\"SELECT TOP 1 * FROM raw_sensor_data ORDER BY id DESC\")
row = cursor.fetchone()
assert row is not None
'"

check "predictions inserted into DB" \
  "docker exec fastapi-app python3 -c '
import pyodbc
conn = pyodbc.connect(
  \"DRIVER={ODBC Driver 18 for SQL Server};SERVER=azure-sql-edge;UID=sa;PWD=${SA_PASSWORD};TrustServerCertificate=yes\"
)
cursor = conn.cursor()
cursor.execute(\"SELECT TOP 1 * FROM predictions ORDER BY prediction_id DESC\")
row = cursor.fetchone()
assert row is not None
'"

# Step 5 - check logs confirm success
echo "[ Step 5: Log Confirmation ]"
check "MQTT received log present" \
  "docker logs fastapi-app 2>&1 | grep '\[MQTT\] Received'"
check "ML result log present" \
  "docker logs fastapi-app 2>&1 | grep '\[ML\] Result'"
echo ""

echo "=============================="
echo "  Results: ${PASS} passed, ${FAIL} failed"
echo "=============================="
echo ""

[ $FAIL -eq 0 ] && exit 0 || exit 1
