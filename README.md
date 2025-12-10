# Music Streaming App

This project is a **Music Streaming Application** using **Python**, **PostgreSQL**, **Docker**, and **MinIO**.

## 🚀 Features
- **FastAPI** for high-performance backend API
- **PostgreSQL** for database management
- **Docker Compose** for easy setup
- **React** for frontend

---

## 🛠 Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/hunganh1310/KIS-2025-Music-Streaming-Web
cd KIS-2025-Music-Streaming-Web
```
### 2️⃣ Create a Python Virtual Environment
```bash
cd backend
```
```bash
python -m venv venv
source venv/bin/activate  # For Mac/Linux
venv\Scripts\activate  # For Windows
```
```bash
pip install -r requirements.txt
```
### 3️⃣ Run Docker Containers (PostgreSQL, Backend, Frontend)
Return to the main directory
```bash
docker compose up --build
```
This will start:

- PostgreSQL database on `localhost:5432`
- Backend API on `localhost:8001`
- Frontend (React) on `localhost:3000`
### 4️⃣ Set Up Environment Variables
Create a `.env` file in the `backend/` directory:
```bash
cd backend
touch .env
```
Then add:
```ini
# pg credentials
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=music_streaming

# s3 credentials (MinIO)
S3_ACCESS_KEY=minio
S3_SECRET_KEY=minio123
S3_BUCKET=music
S3_PREFIX=tracks
S3_ENDPOINT=http://localhost:9000

# JWT Auth
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```
### 5️⃣ Run the Application
#### Run the backend
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```
#### Run the frontend
```bash
cd frontend
npm install
npm start
```
