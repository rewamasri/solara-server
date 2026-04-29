#!/bin/bash
# scripts/test_deploy.sh

PASS=0
FAIL=0

green() { echo -e "\033[32m✔ $1\033[0m"; }
red()   { echo -e "\033[31m✘ $1\033[0m"; }

check() {
  if eval "$2" &>/dev/null; then
    green "$1"
    ((PASS++))
  else
    red "$1"
    ((FAIL++))
  fi
}

echo ""
echo "=============================="
echo "  Container Integration Tests"
echo "=============================="
echo ""

echo "[ Containers Running ]"
check "mosquitto is running"      "docker ps --filter name=mosquitto --filter status=running | grep mosquitto"
check "azure-sql-edge is running" "docker ps --filter name=azure-sql-edge --filter status=running | grep azure-sql-edge"
check "fastapi-app is running"    "docker ps --filter name=fastapi-app --filter status=running | grep fastapi-app"
echo ""

echo "[ MQTT (Mosquitto) ]"
check "port 1883 is open on host" "nc -z localhost 1883"
check "can publish and subscribe via MQTT" \
  "docker exec mosquitto sh -c 'mosquitto_sub -h localhost -t test/ping -C 1 -W 2 & sleep 0.3 && mosquitto_pub -h localhost -t test/ping -m hello && wait'"
echo ""

echo "[ Azure SQL Edge ]"
check "port 1433 is open on host" "nc -z localhost 1433"
check "SQL Edge responds to query" \
  "docker exec fastapi-app python3 -c 'import pyodbc; pyodbc.connect(\"DRIVER={ODBC Driver 18 for SQL Server};SERVER=azure-sql-edge;UID=sa;PWD=${SA_PASSWORD};TrustServerCertificate=yes\")'"
echo ""

echo "[ FastAPI Application ]"
check "port 8000 is open on host"   "nc -z localhost 8000"
check "health endpoint returns 200" "curl -sf http://localhost:8000/"
check "app can reach SQL Edge"      "docker exec fastapi-app python3 -c 'import socket; socket.create_connection((\"azure-sql-edge\", 1433), timeout=3)'"
echo ""

echo "[ Inter-container Networking ]"
check "fastapi-app can reach mosquitto by name"      "docker exec fastapi-app python3 -c 'import socket; socket.create_connection((\"mosquitto\", 1883), timeout=3)'"
check "fastapi-app can reach azure-sql-edge by name" "docker exec fastapi-app python3 -c 'import socket; socket.create_connection((\"azure-sql-edge\", 1433), timeout=3)'"
check "azure-sql-edge can reach mosquitto by name"   "docker exec azure-sql-edge bash -c 'echo > /dev/tcp/mosquitto/1883'"
echo ""

echo "=============================="
echo "  Results: ${PASS} passed, ${FAIL} failed"
echo "=============================="
echo ""

[ $FAIL -eq 0 ] && exit 0 || exit 1