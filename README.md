# Deploying and Testing:

## Set Environment Variables
```
export SA_PASSWORD="password"
```

## First-Time Setup (from root)
```
docker compose -f infrastructure/compose/docker-compose.yml up -d --build
./scripts/test_deploy.sh
./scripts/test_pipeline.sh
```

## Normal Development (not first time)
```
./scripts/deploy.sh
```
> this pulls all new changes from the repo, sets up deployment, and runs both test scripts

## Restart Containers (Without Wiping Database)
```
docker compose -f infrastructure/compose/docker-compose.yml down
docker compose -f infrastructure/compose/docker-compose.yml up -d
```

## Deleting Test Data from Database
```
./scripts/reset_db.sh
```
#### Example ####

```
Pulling latest code...
From https://github.com/rewamasri/solara-server
 * branch            main       -> FETCH_HEAD
Already up to date.
Building and starting containers...
[+] Building 1.1s (14/14) FINISHED                                                                               
 => [internal] load local bake definitions                                                                  0.0s
 => => reading from stdin 534B                                                                              0.0s
 => [internal] load build definition from Dockerfile                                                        0.0s
 => => transferring dockerfile: 901B                                                                        0.0s
 => [internal] load metadata for docker.io/library/python:3.11-slim                                         0.8s
 => [internal] load .dockerignore                                                                           0.0s
 => => transferring context: 2B                                                                             0.0s
 => [1/7] FROM docker.io/library/python:3.11-slim@sha256:92c262cbb2e99cdc16218338d74fbe518055c13d224d94270  0.0s
 => => resolve docker.io/library/python:3.11-slim@sha256:92c262cbb2e99cdc16218338d74fbe518055c13d224d94270  0.0s
 => [internal] load build context                                                                           0.0s
 => => transferring context: 1.61kB                                                                         0.0s
 => CACHED [2/7] WORKDIR /app                                                                               0.0s
 => CACHED [3/7] RUN apt-get update && apt-get install -y     curl     gnupg2     apt-transport-https       0.0s
 => CACHED [4/7] COPY application/requirements.txt .                                                        0.0s
 => CACHED [5/7] RUN pip install --upgrade pip                                                              0.0s
 => CACHED [6/7] RUN pip install -r requirements.txt                                                        0.0s
 => CACHED [7/7] COPY application/ ./application/                                                           0.0s
 => exporting to image                                                                                      0.0s
 => => exporting layers                                                                                     0.0s
 => => exporting manifest sha256:98a42491324f8fa3d6b0c5646856d180f6e43c26358b05c7f71a8085c7bda1c2           0.0s
 => => exporting config sha256:79ec8e35400a6add25bb84d6381eb17e8e1019cf5b6f76c2b628e11e816766b1             0.0s
 => => exporting attestation manifest sha256:923a471a851883ab4eef90ab28092ba255f985c9cf16a4f462c3a5212f803  0.0s
 => => exporting manifest list sha256:525d40483d6d3bfc3d090440887652b1afbe6e6d7a05fc12ad798f08df3c68e8      0.0s
 => => naming to docker.io/library/compose-application:latest                                               0.0s
 => => unpacking to docker.io/library/compose-application:latest                                            0.0s
 => resolving provenance for metadata file                                                                  0.0s
[+] up 4/4
 ✔ Image compose-application Built                                                                           1.2s
 ✔ Container azure-sql-edge  Running                                                                         0.0s
 ✔ Container mosquitto       Running                                                                         0.0s
 ✔ Container fastapi-app     Recreated                                                                       1.0s
Waiting for containers to initialise...
Running integration tests...

==============================
  Container Integration Tests
==============================

[ Containers Running ]
✔ mosquitto is running
✔ azure-sql-edge is running
✔ fastapi-app is running

[ MQTT (Mosquitto) ]
✔ port 1883 is open on host
✔ can publish and subscribe via MQTT

[ Azure SQL Edge ]
✔ port 1433 is open on host
✔ SQL Edge responds to query

[ FastAPI Application ]
✔ port 8000 is open on host
✔ health endpoint returns 200
✔ app can reach SQL Edge

[ Inter-container Networking ]
✔ fastapi-app can reach mosquitto by name
✔ fastapi-app can reach azure-sql-edge by name
✔ azure-sql-edge can reach mosquitto by name

==============================
  Results: 13 passed, 0 failed
==============================

Running pipeline tests...

==============================
  Pipeline Integration Test
==============================

[ Step 1: Publish MQTT Message ]
✔ publish sensor payload to solara/sensors

ℹ Waiting 3s for API to process message...

[ Step 2: API Received Message ]
✔ GET /sensors/latest returns 200
✔ sensor data contains latitude
ℹ Response: {"timestamp":"2026-04-14T00:00:00Z","latitude":33.97350496714153,"longitude":-117.32810678494731,"ambient_temp_c":23.696572495333637,"surface_temp_avg_c":26.838114650347794,"surface_temp_max_c":32.034526941705906,"humidity_pct":50.78837759668136,"iaq_index":86.59741961775525,"lux":7077.712129758373,"soil_temp_c":20.735677929836026,"soil_moisture_pct":39.900483217915166,"soil_ph":7.120349543359651,"pitch_deg":-0.6559507995563203,"roll_deg":3.3525977591851497,"battery_pct":99.73446271947512,"power_draw_w":20.076330543858848}

[ Step 3: ML Prediction ]
✔ GET /predictions/latest returns 200
✔ prediction result received
ℹ Response: {"health_prediction":"Healthy","confidence_scores":{"Healthy":0.99,"Heat stress":0.0,"Needs watering":0.0,"pH issue":0.01},"cluster_label":1,"is_anomaly":false}

[ Step 4: Database Write ]
✔ raw_sensor_data inserted into DB
✔ predictions inserted into DB
[ Step 5: Log Confirmation ]
✔ MQTT received log present
✔ ML result log present

==============================
  Results: 7 passed, 0 failed
==============================
```
**Notes:**
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
