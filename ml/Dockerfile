# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy ML folder
COPY ml/ ./ml/

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "ml.MLEndpoint:app", "--host", "0.0.0.0", "--port", "8000"]