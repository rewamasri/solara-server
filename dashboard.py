from arcgis.gis import GIS
from arcgis.features import FeatureLayer, Feature
import pandas as pd
import pyodbc
import os
import json

# 1. AUTH
gis = GIS("https://ucr.maps.arcgis.com", client_id=os.environ.get("ARCGIS_CLIENT_ID"), client_secret=os.environ.get("ARCGIS_CLIENT_SECRET"))

def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=azure-sql-edge;"
        "UID=sa;"
        f"PWD={os.environ.get('SA_PASSWORD')};"
        "TrustServerCertificate=yes"
    )

def push_sensor_data(layer_url):
    try:
        conn = get_connection()
        df = pd.read_sql("SELECT TOP 100 * FROM raw_sensor_data ORDER BY id DESC", conn)
        conn.close()
        print(f"📦 Pulled {len(df)} rows from raw_sensor_data")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return

    if df.empty:
        print("⚠️  No sensor data to upload")
        return

    # Parse JSON payload into columns
    parsed = df['json_payload'].apply(json.loads)
    df = pd.json_normalize(parsed)

    # Rename columns to match ArcGIS field names
    rename_map = {
        'timestamp': 'timestamps',
        'soil_temp_c': 'soil_temp',
        'soil_moisture_pct': 'soil_moisture',
    }
    df = df.rename(columns=rename_map)

    # Connect to Feature Layer
    fl = FeatureLayer(layer_url, gis)
    esri_fields = [f.name for f in fl.properties.fields]
    print(f"Esri fields: {esri_fields}")

    # Delete old features
    try:
        fl.delete_features(where="1=1")
        print("🗑️  Deleted old features")
    except Exception as e:
        print(f"⚠️  Delete warning: {e}")

    # Format features
    features_to_add = []
    for _, row in df.iterrows():
        attributes = row.to_dict()
        lon = round(float(attributes.pop('longitude', 0)), 6)
        lat = round(float(attributes.pop('latitude', 0)), 6)

        for field in ['OBJECTID', 'soil_ph', 'water_recommendation']:
            attributes.pop(field, None)

        if 'timestamps' in attributes:
            try:
                ts = pd.to_datetime(attributes['timestamps'])
                attributes['timestamps'] = ts.strftime('%Y-%m-%d %H:%M:%S')
            except:
                attributes['timestamps'] = None

        for key, value in attributes.items():
            if isinstance(value, float):
                attributes[key] = round(value, 2)

        attributes = {k: v for k, v in attributes.items() if k in esri_fields}

        feature = Feature(
            geometry={"x": lon, "y": lat, "spatialReference": {"wkid": 4326}},
            attributes=attributes
        )
        features_to_add.append(feature)

    try:
        result = fl.edit_features(adds=features_to_add)
        success_count = sum(1 for r in result['addResults'] if r['success'])
        print(f"✅ Uploaded {success_count}/{len(features_to_add)} sensor records")
        errors = [r for r in result['addResults'] if not r['success']]
        if errors:
            print(f"⚠️  {len(errors)} errors:")
            for err in errors[:3]:
                print(f"   {err}")
    except Exception as e:
        print(f"❌ Upload failed for raw_sensor_data: {e}")


def push_prediction_data(layer_url):
    try:
        conn = get_connection()
        df = pd.read_sql("SELECT TOP 100 * FROM predictions ORDER BY prediction_id DESC", conn)
        conn.close()
        print(f"📦 Pulled {len(df)} rows from predictions")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return

    if df.empty:
        print("⚠️  No prediction data to upload")
        return

    # Connect to Feature Layer
    fl = FeatureLayer(layer_url, gis)
    esri_fields = [f.name for f in fl.properties.fields]
    print(f"Esri fields: {esri_fields}")

    # Delete old features
    try:
        fl.delete_features(where="1=1")
        print("🗑️  Deleted old features")
    except Exception as e:
        print(f"⚠️  Delete warning: {e}")

    # Format features
    features_to_add = []
    for _, row in df.iterrows():
        attributes = row.to_dict()

        for field in ['prediction_id', 'OBJECTID']:
            attributes.pop(field, None)

        if 'created_at' in attributes:
            try:
                ts = pd.to_datetime(attributes['created_at'])
                attributes['created_at'] = ts.strftime('%Y-%m-%d %H:%M:%S')
            except:
                attributes['created_at'] = None

        for key, value in attributes.items():
            if isinstance(value, float):
                attributes[key] = round(value, 2)

        attributes = {k: v for k, v in attributes.items() if k in esri_fields}

        feature = Feature(
            geometry={"x": 0, "y": 0, "spatialReference": {"wkid": 4326}},
            attributes=attributes
        )
        features_to_add.append(feature)

    if not features_to_add:
        print("⚠️  No features to upload after filtering")
        return

    try:
        result = fl.edit_features(adds=features_to_add)
        success_count = sum(1 for r in result['addResults'] if r['success'])
        print(f"✅ Uploaded {success_count}/{len(features_to_add)} prediction records")
        errors = [r for r in result['addResults'] if not r['success']]
        if errors:
            print(f"⚠️  {len(errors)} errors:")
            for err in errors[:3]:
                print(f"   {err}")
    except Exception as e:
        print(f"❌ Upload failed for predictions: {e}")


# --- EXECUTION ---
sensor_layer_url = "https://services1.arcgis.com/RCT9RCgW4FY2e7Dk/arcgis/rest/services/Sensor_Data_Layer/FeatureServer/0"
ml_layer_url = "https://services1.arcgis.com/RCT9RCgW4FY2e7Dk/arcgis/rest/services/ml_predictions/FeatureServer/0"

print("="*60)
print("SYNCING DATA TO ESRI FEATURE LAYERS")
print("="*60)

push_sensor_data(sensor_layer_url)
push_prediction_data(ml_layer_url)

print("="*60)
print("✓ SYNC COMPLETE")
print("="*60)