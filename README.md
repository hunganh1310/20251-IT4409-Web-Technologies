# 🎵 Music Streaming Platform

A modern, full-stack **music streaming application** built with **React**, **FastAPI**, **PostgreSQL**, **Apache Airflow**, and **Docker**. Features intelligent music recommendations, playlist management, and a beautiful glassmorphic UI.

## ✨ Features

### 🎧 Core Functionality
- **Stream & Discover** - Browse and play thousands of songs with smooth playback
- **Smart Recommendations** - AI-powered music suggestions based on your listening habits
- **Playlist Management** - Create, edit, and share custom playlists
- **Search & Filter** - Advanced search across songs, artists, and albums
- **User Authentication** - Secure JWT-based auth with refresh tokens

### 🛠️ Technical Highlights
- **FastAPI Backend** - High-performance async Python API
- **React Frontend** - Modern, responsive UI with glassmorphic design
- **PostgreSQL Database** - Robust relational data storage
- **Apache Airflow** - Automated data pipeline for music catalog updates
- **Docker Compose** - Containerized microservices architecture
- **MinIO/S3** - Scalable object storage for audio files
- **Music Recommender** - Machine learning-based recommendation engine

---

## 🚀 Quick Start

### Prerequisites
- **Docker** and **Docker Compose** installed
- **Node.js** (v14+) and **npm**
- **Python** (v3.9+)
- **Git**

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/hunganh1310/20251-IT4409-Web-Technologies.git
cd 20251-IT4409-Web-Technologies
```

### 2️⃣ Environment Configuration

Create a `.env` file in the `backend/` directory:

```bash
cd backend
touch .env  # or create manually on Windows
```

Add the following configuration:

```ini
# PostgreSQL Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=music_streaming

# MinIO/S3 Object Storage
S3_ACCESS_KEY=minio
S3_SECRET_KEY=minio123
S3_BUCKET=music
S3_PREFIX=tracks
S3_ENDPOINT=http://localhost:9000

# JWT Authentication
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3️⃣ Launch with Docker (Recommended)

From the project root directory:

```bash
docker compose up --build
```

This will start all services:
- **PostgreSQL** - Database on `localhost:5432`
- **Backend API** - FastAPI on `http://localhost:8001`
- **Frontend** - React app on `http://localhost:3000`
- **Airflow** - Scheduler on `http://localhost:8080`
- **MinIO** - Object storage on `http://localhost:9000`

### 4️⃣ Manual Setup (Development)

#### Backend Setup
```bash
cd backend
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

The app will open at `http://localhost:3000`

---

## 📁 Project Structure

```
├── airflow/              # Apache Airflow DAGs and scripts
│   ├── dags/            # Workflow definitions
│   ├── scripts/         # Data processing scripts
│   └── data/            # Datasets and audio files
├── backend/              # FastAPI backend
│   ├── models/          # SQLAlchemy ORM models
│   ├── routes/          # API endpoint handlers
│   ├── schemas/         # Pydantic data schemas
│   ├── utils/           # Helper functions
│   └── main.py          # Application entry point
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page-level components
│   │   ├── styles/      # CSS stylesheets
│   │   └── context/     # React context providers
│   └── public/          # Static assets
├── music-recommender/    # ML recommendation engine
│   ├── recommender.py   # Core recommendation logic
│   └── loader.py        # Model loading utilities
└── docker-compose.yml    # Multi-container orchestration
```

---

## 🔧 Tech Stack

### Frontend
- **React** - UI framework
- **React Router** - Client-side routing
- **Context API** - State management
- **Axios** - HTTP client

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation
- **JWT** - Secure authentication
- **PostgreSQL** - Primary database
- **MinIO** - S3-compatible object storage

### Data Pipeline
- **Apache Airflow** - Workflow orchestration
- **Spotify API** - Music metadata crawler
- **Pandas** - Data processing

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-service orchestration
- **Nginx** - Reverse proxy (production)

---

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

### Key Endpoints

#### Authentication
- `POST /auth/register` - Create new account
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token

#### Music
- `GET /music/tracks` - List all tracks
- `GET /music/track/{id}` - Get track details
- `GET /music/stream/{id}` - Stream audio file
- `GET /music/recommendations` - Get personalized recommendations

#### Playlists
- `GET /playlists` - List user playlists
- `POST /playlists` - Create new playlist
- `PUT /playlists/{id}` - Update playlist
- `DELETE /playlists/{id}` - Delete playlist

---

## 🎨 Features in Detail

### Music Recommendation Engine
The system uses collaborative filtering and content-based algorithms to suggest songs based on:
- Listening history
- Playlist composition
- Similar user preferences
- Audio features (tempo, energy, danceability)

### Data Pipeline with Airflow
Automated workflows handle:
- Fetching new songs from external APIs
- Processing and enriching metadata
- Uploading audio files to storage
- Database synchronization

### Glassmorphic UI Design
A modern, visually appealing interface featuring:
- Frosted glass effect backgrounds
- Smooth animations and transitions
- Responsive layout for all screen sizes
- Accessible color contrast

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**IT4409 - Web Technologies (2025.1)**  
**University of Engineering and Technology, VNU**

- **Hung Anh** - [@hunganh1310](https://github.com/hunganh1310)

---

## 🙏 Acknowledgments

- Spotify API for music metadata
- FastAPI and React communities
- Apache Airflow for workflow management
- Open-source contributors

---

## 📧 Contact

For questions or support, please open an issue on [GitHub Issues](https://github.com/hunganh1310/20251-IT4409-Web-Technologies/issues).
