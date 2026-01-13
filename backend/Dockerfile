FROM python:3.10-slim

WORKDIR /app

# Install dependencies with retry and alternative mirrors
RUN apt-get update --fix-missing || \
    (echo "deb http://ftp.us.debian.org/debian trixie main" > /etc/apt/sources.list && \
     echo "deb http://ftp.us.debian.org/debian trixie-updates main" >> /etc/apt/sources.list && \
     apt-get update) && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        python3-dev \
        cargo \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code vào container
COPY . .

# Pre-load models during build time
RUN python preload_models.py

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
