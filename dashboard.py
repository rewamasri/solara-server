from arcgis.gis import GIS
from arcgis.features import FeatureLayer, Feature
import sqlite3
import pandas as pd

# 1. AUTH
gis = GIS("https://ucr.maps.arcgis.com", client_id="ZvGniMfMxSg54T2T", client_secret="0ae338c02ccf4a9f8f1916dc80e566ff")

def push_data_to_esri(db_path, layer_url, table_name):
    # 1. Pull data from SQLite
    try:
        conn = sqlite3.connect(db_path)
        query = f"SELECT * FROM {table_name} WHERE timestamp >= datetime('now', '-24 hours')"
        df = pd.read_sql_query(query, conn)
        conn.close()
        print(f"📦 Pulled {len(df)} rows from {table_name}")

        if df.empty:
            print(f"⚠️  No recent data, falling back to all data...")
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 10", conn)
            conn.close()
            print(f"📦 Pulled {len(df)} rows (fallback)")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return

    if df.empty:
        print(f"⚠️  No data to upload for {table_name}")
        return

    # 2. Rename columns to match ArcGIS field names
    rename_map = {
        'timestamp': 'timestamps',
        'soil_temp_c': 'soil_temp',
    }
    df = df.rename(columns=rename_map)

    # 3. Connect to Feature Layer
    fl = FeatureLayer(layer_url, gis)
    esri_fields = [f.name for f in fl.properties.fields]
    print(f"Esri fields: {esri_fields}")

    # 4. Delete old features
    try:
        fl.delete_features(where="1=1")
        print(f"🗑️  Deleted old features")
    except Exception as e:
        print(f"⚠️  Delete warning: {e}")

    # 5. Format Features
    features_to_add = []
    for _, row in df.iterrows():
        attributes = row.to_dict()

        # Extract geometry
        lon = round(float(attributes.pop('longitude', 0)), 6)
        lat = round(float(attributes.pop('latitude', 0)), 6)

        # Remove fields ArcGIS auto-generates or that don't exist in the layer
        for field in ['id', 'OBJECTID', 'soil_ph', 'water_recommendation']:
            attributes.pop(field, None)

        # Convert timestamp to milliseconds
        if 'timestamps' in attributes:
            try:
                ts = pd.to_datetime(attributes['timestamps'])
                attributes['timestamps'] = ts.strftime('%Y-%m-%d %H:%M:%S')
            except:
                attributes['timestamps'] = None

        # Round floats
        for key, value in attributes.items():
            if isinstance(value, float):
                attributes[key] = round(value, 2)

        # Only keep fields that exist in ArcGIS layer
        attributes = {k: v for k, v in attributes.items() if k in esri_fields}

        feature = Feature(
            geometry={"x": lon, "y": lat, "spatialReference": {"wkid": 4326}},
            attributes=attributes
        )
        features_to_add.append(feature)

    # 6. Push to ArcGIS
    try:
        result = fl.edit_features(adds=features_to_add)
        success_count = sum(1 for r in result['addResults'] if r['success'])
        print(f"✅ Uploaded {success_count}/{len(features_to_add)} records from {table_name}")

        errors = [r for r in result['addResults'] if not r['success']]
        if errors:
            print(f"⚠️  {len(errors)} errors:")
            for err in errors[:3]:
                print(f"   {err}")
    except Exception as e:
        print(f"❌ Upload failed for {table_name}: {e}")

        # Remove timestamp — ArcGIS will use its own time
        attributes.pop('timestamps', None)

# --- EXECUTION ---
DB_PATH = "rover_data.db"
sensor_layer_url = "https://services1.arcgis.com/RCT9RCgW4FY2e7Dk/arcgis/rest/services/Sensor_Data_Layer/FeatureServer/0"
ml_layer_url = "https://services1.arcgis.com/RCT9RCgW4FY2e7Dk/arcgis/rest/services/ml_layer/FeatureServer/0"

print("="*60)
print("SYNCING DATA TO ESRI FEATURE LAYERS")
print("="*60)

push_data_to_esri(DB_PATH, sensor_layer_url, "sensor_readings")
push_data_to_esri(DB_PATH, ml_layer_url, "recommendations")

print("="*60)
print("✓ SYNC COMPLETE")
print("="*60)