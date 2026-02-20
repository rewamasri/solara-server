JSON Payload Format

i believe pramika&ava had set up a mock of what each sensor would send
https://www.canva.com/design/DAG-KXmNVsM/1lnrymI0xT_G0XZDV70miQ/edit

Prediction Output Format

i believe pramika set up a JSON file for how predictions would get sent
https://www.canva.com/design/DAG4pUPh-_A/98jDkEkC9qkrWZFNiWIGVg/edit

Sensors

http://canva.com/design/DAG_Fu_jHp8/U7Q-HHgsM6rNJf1nduWNrw/edit

MQTT Topic

will not be getting live data yet
a test data set is in the Slack

Papalexakis doc: https://docs.google.com/document/d/1_Ps2i-MGEfcOUYO9aAsantR3GI5riLDpk6exeTsaa1c/edit?tab=t.0


ML Data Expectations
- timestamp
- latitude
- longitude
- ambient_temp_c
- surface_temp_avg_c
- surface_temp_max_c
- humidity_pct
- iaq_index
- lux
- soil_temp_c
- soil_moisture_pct
- soil_ph
- pitch_deg
- roll_deg
- battery_pct
- power_draw_w

Create branches as follows:

- ava/ml
- sanvi/dataingestion
- ananya/api
- tanisha/infrastructure
- pramika/database
