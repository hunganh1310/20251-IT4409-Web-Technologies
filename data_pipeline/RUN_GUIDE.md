# 🚀 Running the Air Quality Data Pipeline

This guide explains how to run the complete data pipeline with your setup:
- **Kafka**: Confluent Cloud
- **Producers**: Digital Ocean
- **Consumers/Processing**: Local Docker

## 📋 Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────────────────┐
│   AQICN API     │────▶│  Digital Ocean  │────▶│     Confluent Cloud         │
│   (Data Source) │     │  (Producers)    │     │     (Kafka Topics)          │
└─────────────────┘     └─────────────────┘     └─────────────┬───────────────┘
                                                              │
                        ┌─────────────────────────────────────┘
                        ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                       LOCAL DOCKER ENVIRONMENT                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ TimescaleDB │  │  ClickHouse │  │    MinIO    │  │   Grafana   │      │
│  │  (Realtime) │  │ (Analytics) │  │  (Archive)  │  │ (Dashboard) │      │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │                     SPARK STREAMING JOBS                              │ │
│  │  • run_realtime_*.py  → Kafka → TimescaleDB                         │ │
│  │  • run_archive_*.py   → Kafka → MinIO (S3)                          │ │
│  │  • run_analytics_*.py → TimescaleDB → ClickHouse                    │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Step 1: Setup Local Environment

### 1.1 Configure Environment Variables

Copy the template and fill in your Confluent Cloud credentials:

```cmd
copy .env.local .env
```

Edit `.env` with your actual values:
- `AQICN_TOKEN`: Your AQICN API token
- `KAFKA_BOOTSTRAP_SERVERS`: Your Confluent Cloud bootstrap server
- `KAFKA_SASL_USERNAME`: Confluent API Key
- `KAFKA_SASL_PASSWORD`: Confluent API Secret

### 1.2 Install Python Dependencies

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 1.3 Start Docker Infrastructure

```cmd
docker-compose up -d
```

This starts:
- **TimescaleDB** (port 5432) - Real-time data storage
- **ClickHouse** (port 8123) - Analytics database
- **MinIO** (ports 9000, 9001) - Local S3-compatible storage
- **Grafana** (port 3000) - Visualization dashboards

### 1.4 Create MinIO Bucket

Access MinIO Console: http://localhost:9001
- Username: `minioadmin`
- Password: `minioadmin`
- Create bucket: `airquality-archive`

Or via CLI:
```cmd
docker exec minio1 mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec minio1 mc mb local/airquality-archive
```

---

## 🚀 Step 2: Run Data Pipeline Components

### 2.1 Producers (Running on Digital Ocean)

Your producers on Digital Ocean should be configured with:
```env
KAFKA_BOOTSTRAP_SERVERS=your-confluent-cluster:9092
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_SASL_USERNAME=your_api_key
KAFKA_SASL_PASSWORD=your_api_secret
```

The producers run continuously fetching data from AQICN API:
```bash
# On Digital Ocean
python scripts/produce_hanoi.py
python scripts/produce_danang.py
python scripts/produce_cantho.py
```

### 2.2 Real-time Consumers (Local)

These read from Confluent Kafka and write to local TimescaleDB:

```cmd
REM Terminal 1 - Hanoi
python scripts/run_realtime_hanoi.py

REM Terminal 2 - Da Nang
python scripts/run_realtime_danang.py

REM Terminal 3 - Can Tho
python scripts/run_realtime_cantho.py
```

### 2.3 Archive Jobs (Local)

Archive data from Kafka to MinIO (local S3):

```cmd
REM Run in separate terminals
python scripts/run_archive_hanoi.py
python scripts/run_archive_danang.py
python scripts/run_archive_cantho.py
```

### 2.4 Analytics Jobs (Local)

Run analytics to aggregate data in ClickHouse:

```cmd
REM Hourly analytics
python scripts/run_analytics_hourly_hanoi.py
python scripts/run_analytics_hourly_danang.py
python scripts/run_analytics_hourly_cantho.py

REM Daily analytics
python scripts/run_analytics_daily.py
```

---

## ☸️ Step 3: Kubernetes Deployment

### 3.1 Prerequisites

- Kubernetes cluster (EKS, AKS, GKE, or local minikube/kind)
- kubectl configured
- Docker image pushed to registry

### 3.2 Build and Push Docker Image

```cmd
REM Build image
docker build -t hunganh1310/airquality:latest .

REM Login to Docker Hub
docker login

REM Push to registry
docker push hunganh1310/airquality:latest
```

### 3.3 Update K8s Manifests

Update image references in deployment files (already done):
```yaml
image: hunganh1310/airquality:latest
```

### 3.4 Create Kubernetes Secret

```cmd
cd k8s

REM Edit secret-template.yaml with your credentials
REM Then apply:
kubectl apply -f namespace.yaml
kubectl apply -f secret-template.yaml
```

Or create secret imperatively:
```cmd
kubectl create secret generic airquality-secrets -n airquality ^
  --from-literal=AQICN_TOKEN=your_token ^
  --from-literal=KAFKA_BOOTSTRAP_SERVERS=your-confluent:9092 ^
  --from-literal=KAFKA_SECURITY_PROTOCOL=SASL_SSL ^
  --from-literal=KAFKA_SASL_MECHANISM=PLAIN ^
  --from-literal=KAFKA_SASL_USERNAME=your_key ^
  --from-literal=KAFKA_SASL_PASSWORD=your_secret ^
  --from-literal=DB_HOST=your-timescaledb ^
  --from-literal=DB_PORT=5432 ^
  --from-literal=DB_NAME=airquality ^
  --from-literal=DB_USER=airquality ^
  --from-literal=DB_PASSWORD=your_password ^
  --from-literal=CLICKHOUSE_HOST=your-clickhouse ^
  --from-literal=CLICKHOUSE_PORT=8123 ^
  --from-literal=CLICKHOUSE_DB=airquality ^
  --from-literal=CLICKHOUSE_USER=airquality ^
  --from-literal=CLICKHOUSE_PASSWORD=your_password ^
  --from-literal=AWS_ACCESS_KEY_ID=your_key ^
  --from-literal=AWS_SECRET_ACCESS_KEY=your_secret ^
  --from-literal=AWS_S3_BUCKET=airquality-archive ^
  --from-literal=AWS_REGION=us-east-1 ^
  --from-literal=SPARK_CHECKPOINT_LOCATION=/tmp/spark_checkpoints
```

### 3.5 Deploy All Components

Using the deployment script:
```bash
cd k8s
chmod +x deploy-to-eks.sh
./deploy-to-eks.sh
```

Or deploy manually:
```cmd
REM Namespace
kubectl apply -f namespace.yaml

REM Real-time streaming deployments
kubectl apply -f deployment-realtime-hanoi.yaml
kubectl apply -f deployment-realtime-danang.yaml
kubectl apply -f deployment-realtime-cantho.yaml

REM Archive streaming deployments
kubectl apply -f deployment-archive-hanoi.yaml
kubectl apply -f deployment-archive-danang.yaml
kubectl apply -f deployment-archive-cantho.yaml

REM Analytics CronJobs
kubectl apply -f cronjob-analytics-hourly-hanoi.yaml
kubectl apply -f cronjob-analytics-hourly-danang.yaml
kubectl apply -f cronjob-analytics-hourly-cantho.yaml
kubectl apply -f cronjob-analytics-daily.yaml
```

### 3.6 Verify Deployment

```cmd
REM Check pods
kubectl get pods -n airquality

REM Check logs
kubectl logs -f deployment/realtime-hanoi -n airquality

REM Check CronJobs
kubectl get cronjobs -n airquality
```

---

## 📊 Step 4: Access Dashboards

### Grafana
- URL: http://localhost:3000
- Username: `admin`
- Password: `admin`

Configure data sources:
1. **TimescaleDB**: PostgreSQL connection to `localhost:5432`
2. **ClickHouse**: ClickHouse connection to `localhost:8123`

### MinIO Console
- URL: http://localhost:9001
- Username: `minioadmin`
- Password: `minioadmin`

---

## 🔍 Troubleshooting

### Check Kafka Connectivity
```python
from kafka import KafkaConsumer
consumer = KafkaConsumer(
    bootstrap_servers='your-confluent:9092',
    security_protocol='SASL_SSL',
    sasl_mechanism='PLAIN',
    sasl_plain_username='your_key',
    sasl_plain_password='your_secret'
)
print(consumer.topics())
```

### Check TimescaleDB
```cmd
docker exec -it timescaledb psql -U airquality -d airquality
\dt
SELECT * FROM hanoi_measurements LIMIT 5;
```

### Check ClickHouse
```cmd
docker exec -it clickhouse clickhouse-client -u airquality --password airquality123
SHOW TABLES FROM airquality;
SELECT * FROM airquality.hanoi_analytics LIMIT 5;
```

### Check MinIO
```cmd
docker exec minio1 mc ls local/airquality-archive/
```

---

## 📝 Summary of Components

| Component | Purpose | Local Port | K8s Resource |
|-----------|---------|------------|--------------|
| Producers | Fetch AQICN → Kafka | Digital Ocean | N/A |
| Realtime | Kafka → TimescaleDB | Local/K8s | Deployment |
| Archive | Kafka → S3/MinIO | Local/K8s | Deployment |
| Analytics Hourly | TimescaleDB → ClickHouse | Local/K8s | CronJob |
| Analytics Daily | TimescaleDB → ClickHouse | Local/K8s | CronJob |
| TimescaleDB | Real-time storage | 5432 | External |
| ClickHouse | Analytics storage | 8123 | External |
| MinIO | Archive storage | 9000/9001 | External |
| Grafana | Visualization | 3000 | External |
