# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all ML files directly into /app
COPY ml/ ./

# Install FastAPI and Uvicorn
RUN pip install --no-cache-dir fastapi uvicorn

# Expose FastAPI port
EXPOSE 8000
# Use official Python image
FROM python:3.11-slim

WORKDIR /app
COPY ml/ ./

# Install FastAPI, Uvicorn, and ML dependencies
RUN pip install --no-cache-dir fastapi uvicorn joblib numpy pandas scikit-learn

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "MLEndpoint:app", "--host", "0.0.0.0", "--port", "8000"]
# Start FastAPI (no ml. prefix because files are in /app)
CMD ["uvicorn", "MLEndpoint:app", "--host", "0.0.0.0", "--port", "8000"]