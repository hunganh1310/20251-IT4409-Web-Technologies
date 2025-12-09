# Use Python 3.11 slim image with PySpark installed via pip
FROM python:3.11-slim-bookworm

# Install system dependencies including Java (required for Spark)
RUN apt-get update && apt-get install -y \
    default-jdk-headless \
    postgresql-client \
    libpq-dev \
    gcc \
    g++ \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set Java environment
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY data/ ./data/

# Create directories for Spark
RUN mkdir -p /tmp/spark_checkpoints && \
    chmod -R 777 /tmp/spark_checkpoints

# Set Python path
ENV PYTHONPATH=/app

# Default command (this will be overridden in K8s manifests)
CMD ["echo", "Please specify a command to run. Example: python3 scripts/run_realtime_hanoi.py"]
