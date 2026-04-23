#!/bin/bash

echo "Wiping test data (keeping tables)..."

docker exec -i azure-sql-edge /opt/mssql-tools18/bin/sqlcmd \
  -S localhost \
  -U sa \
  -P "$SA_PASSWORD" \
  -Q "
  DELETE FROM predictions;
  DELETE FROM raw_sensor_data;
"

echo "Database cleared."