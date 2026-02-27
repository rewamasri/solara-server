from inference import predict

#healthy payload
payload = {
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
}

result = predict(payload)

print(result)

#testing anomoly
anomaly_payload = {
    "latitude": 95.0,                 # Impossible latitude
    "longitude": -250.0,              # Impossible longitude
    "ambient_temp_c": -40.0,          # Extremely low
    "surface_temp_avg_c": 85.0,       # Extremely high
    "surface_temp_max_c": 120.0,      # Unrealistic heat
    "humidity_pct": 0.5,              # Near zero humidity
    "iaq_index": 500.0,               # Extremely poor air
    "lux": 50000.0,                   # Extremely bright
    "soil_temp_c": -15.0,             # Frozen soil
    "soil_moisture_pct": 2.0,         # Extremely dry
    "soil_ph": 12.0,                  # Highly alkaline (almost caustic)
    "pitch_deg": 45.0,                # Steep tilt
    "roll_deg": 50.0,                 # Extreme roll
    "battery_pct": 150.0,             # Impossible battery
    "power_draw_w": 200.0             # Very high draw
}

anomaly_result = predict(anomaly_payload)
print(anomaly_result)