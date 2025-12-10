FROM apache/airflow:2.7.2-python3.11

WORKDIR /opt/airflow

# Install system dependencies
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER airflow

# Pre-create expected directories
RUN mkdir -p /opt/airflow/data /opt/airflow/logs

# Copy DAGs and scripts
COPY dags/ /opt/airflow/dags/
COPY data_enrich.py upload_pg.py upload_mp3.py /opt/airflow/
COPY requirements.txt /requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /requirements.txt