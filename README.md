# 🎵 BeatPush - AI-Powered Music Promotion Platform

## Overview
BeatPush is an AI-powered platform that helps African music creators (Artists, DJs, Producers) distribute music, automate promotion, track analytics, and earn money - all in one place.

## Tech Stack

### Backend (Python)
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Cache/Queue**: Redis
- **Background Tasks**: Celery
- **ORM**: SQLAlchemy
- **Server**: Gunicorn + Uvicorn (on Linux)

### Frontend
- **Framework**: Next.js 14+ (TypeScript)
- **Styling**: Tailwind CSS
- **UI Components**: Shadcn UI

### Server
- **OS**: Ubuntu Server 22.04 LTS
- **Reverse Proxy**: Nginx
- **SSL**: Let's Encrypt
- **Deployment**: Docker + Docker Compose

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 20+ (for frontend)
- Git

### Backend Setup (Local Development)

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/beatpush.git
cd beatspush/backend
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Run database migrations**
```bash
alembic upgrade head
```

6. **Start the development server**
```bash
python main.py
```

The API will be available at `http://localhost:8000`
API Documentation: `http://localhost:8000/api/v1/docs`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Project Structure

```
beatspush/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Config, security
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   ├── ai/          # AI services
│   │   └── tasks/       # Celery tasks
│   ├── tests/           # Pytest tests
│   └── main.py          # Entry point
├── frontend/            # Next.js frontend
├── scripts/             # Deployment scripts
└── docs/               # Documentation
```

## Development Status

✅ **Phase 0: Project Setup** - COMPLETED
- ✓ Project structure created
- ✓ FastAPI backend initialized
- ✓ Core configuration setup
- ✓ Environment variables configured

⏳ **Phase 1: Authentication & User Management** - NEXT
- User registration
- Login/logout
- JWT authentication
- User profiles

## Deployment (Linux Server)

Deployment instructions will be provided for Ubuntu 22.04 LTS with security hardening.

## Contributing

This is a private project. Contact the project owner for contribution guidelines.

## License

Proprietary - All rights reserved

## Contact

For questions or support, contact: [your-email@beatpush.com]
