-- 1. Simulate the Aggregator Node inserting data
-- Simulate the Aggregator Node inserting actual Rover Sustainability data
INSERT INTO raw_sensor_data (sensor_id, json_payload)
VALUES ('ROVER_01', '{
    "ambient_temp_c": 23.69,
    "humidity_pct": 50.78,
    "soil_moisture_pct": 39.90,
    "battery_pct": 99.73,
    "location": {"lat": 33.97, "long": -117.32}
}');

-- 2. Simulate the ML Module creating a prediction based on that data
-- (This uses SCOPE_IDENTITY() to get the ID of the row we just inserted)
INSERT INTO predictions (raw_data_id, prediction_value, model_version)
VALUES (SCOPE_IDENTITY(), 0.95, 'v1.0-beta');

-- 3. The Query Test: Join the tables to see the result
SELECT 
    r.timestamp, 
    r.sensor_id, 
    r.json_payload, 
    p.prediction_value
FROM raw_sensor_data r
JOIN predictions p ON r.id = p.raw_data_id;