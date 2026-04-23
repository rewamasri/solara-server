FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    apt-transport-https \
    unixodbc \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft.gpg \
    && echo "deb [arch=amd64,arm64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

COPY application/requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY application/ ./application/

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:/app/application

CMD ["uvicorn", "application.api.main:app", "--host", "0.0.0.0", "--port", "8000"]