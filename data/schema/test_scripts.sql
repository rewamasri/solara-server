-- 1. Simulate the Aggregator Node inserting data
INSERT INTO raw_sensor_data (sensor_id, json_payload)
VALUES ('SOLAR_PANEL_TEST', '{"voltage": 24.5, "current": 1.1}');

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