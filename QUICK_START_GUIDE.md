# 🚀 BeatPush Quick Start Guide

**For Developers continuing the project**

---

## 📋 What's Been Built

✅ **8 Tasks Complete** (Phase 0 → Phase 3.1)
- Complete authentication system
- User profiles (4 types: Artist, DJ, Producer, Fan)
- Image upload (avatars, covers)
- Audio upload (tracks with metadata)
- AI content generation (5 features)

---

## 🏃 Quick Start

### **1. Start the Server**
```bash
cd backend
.\venv\Scripts\activate
python main.py
```

Server runs at: `http://localhost:8000`

### **2. Test Users**
Already registered and ready to use:

| Email | Password | Role |
|-------|----------|------|
| `wizkid@beatpush.com` | `Password123` | Artist |
| `djspinall@beatpush.com` | `Password123` | DJ |
| `pheelz@beatpush.com` | `Password123` | Producer |

### **3. Test an Endpoint**
```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={
        "email": "wizkid@beatpush.com",
        "password": "Password123"
    }
)

token = response.json()["access_token"]

# Get profile
profile = requests.get(
    "http://localhost:8000/api/v1/profiles/me",
    headers={"Authorization": f"Bearer {token}"}
)

print(profile.json())
```

---

## 🗂️ Project Structure

```
backend/
├── app/
│   ├── ai/              # AI content generation
│   ├── api/v1/          # API endpoints
│   ├── core/            # Config, security, dependencies
│   ├── db/              # Database connection
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── utils/           # File storage, helpers
├── uploads/             # Local file storage
├── main.py              # FastAPI application
├── beatpush.db          # SQLite database
├── .env                 # Environment config
└── requirements.txt     # Dependencies
```

---

## 📚 API Endpoints (41 total)

### **Authentication (7)**
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh-token` - Refresh token
- `POST /api/v1/auth/forgot-password` - Request reset
- `POST /api/v1/auth/reset-password` - Reset password
- `POST /api/v1/auth/verify-email` - Verify email
- `POST /api/v1/auth/logout` - Logout

### **Users (4)**
- `GET /api/v1/users/me` - Get my profile
- `PUT /api/v1/users/me` - Update profile
- `DELETE /api/v1/users/me` - Delete account
- `GET /api/v1/users/{user_id}/public` - Public profile

### **Profiles (11)**
- `GET /api/v1/profiles/me` - Get my profile
- `PUT /api/v1/profiles/me` - Update profile
- `GET /api/v1/profiles/{user_id}` - Get user profile
- `POST /api/v1/profiles/upload-avatar` - Upload avatar
- `DELETE /api/v1/profiles/avatar` - Delete avatar
- `POST /api/v1/profiles/upload-cover` - Upload cover
- `DELETE /api/v1/profiles/cover` - Delete cover
- + Role-specific endpoints

### **Tracks (7)**
- `POST /api/v1/tracks/upload` - Upload track
- `GET /api/v1/tracks/{track_id}` - Get track
- `PUT /api/v1/tracks/{track_id}` - Update track
- `DELETE /api/v1/tracks/{track_id}` - Delete track
- `GET /api/v1/tracks/my-tracks` - My tracks
- `GET /api/v1/tracks/user/{user_id}` - User's tracks
- `POST /api/v1/tracks/{track_id}/cover` - Upload cover

### **AI Content (5)**
- `POST /api/v1/ai/generate-captions` - Social captions
- `POST /api/v1/ai/generate-hashtags` - Hashtags
- `POST /api/v1/ai/generate-press-release` - Press release
- `POST /api/v1/ai/suggest-posting-times` - Posting times
- `POST /api/v1/ai/generate-bio` - Artist bio

---

## 🧪 Running Tests

```bash
cd backend

# Test auth
python test_auth.py

# Test profiles
python test_profiles.py

# Test uploads
python test_uploads.py

# Test tracks
python test_tracks.py

# Verify AI endpoints
python verify_ai_endpoints.py
```

**All tests should pass ✅**

---

## ⚙️ Configuration

### **Environment Variables (`.env`)**

Key settings to configure:

```env
# Database
DATABASE_URL=sqlite:///./beatpush.db

# JWT Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# OpenAI (for AI features)
OPENAI_API_KEY=sk-your-key-here

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

### **OpenAI Setup (Optional)**
1. Get API key: https://platform.openai.com/api-keys
2. Update `OPENAI_API_KEY` in `.env`
3. Restart server
4. AI endpoints will generate real content

---

## 📊 Database

**SQLite Database:** `backend/beatpush.db`

**Tables:**
- `users` - User accounts
- `artist_profiles` - Artist data
- `dj_profiles` - DJ data
- `producer_profiles` - Producer data
- `fan_profiles` - Fan data
- `tracks` - Music tracks

**Inspect Database:**
```bash
python check_db.py
```

---

## 🔧 Common Tasks

### **Create New User**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/auth/register",
    json={
        "email": "newartist@beatpush.com",
        "password": "SecurePass123",
        "role": "artist",
        "full_name": "New Artist",
        "username": "newartist"
    }
)
```

### **Upload Avatar**
```python
import requests

token = "your-token-here"

with open("avatar.png", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/profiles/upload-avatar",
        files={"file": f},
        headers={"Authorization": f"Bearer {token}"}
    )
```

### **Upload Track**
```python
import requests

token = "your-token-here"

with open("track.mp3", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/tracks/upload",
        files={"file": f},
        data={
            "title": "My New Track",
            "genre": "Afrobeats",
            "status": "draft"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
```

---

## 📝 Next Tasks

**Immediate:**
- [ ] Task 3.2 - Audio Analysis Service
- [ ] Task 3.3 - Track Recommendations
- [ ] Task 3.4 - Content Personalization

**Upcoming:**
- [ ] Phase 4 - Social Media Integration
- [ ] Phase 5 - Analytics Dashboard
- [ ] Phase 6 - Payment Integration

---

## 🐛 Troubleshooting

### **Server won't start**
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <process-id> /F

# Restart server
python main.py
```

### **Database errors**
```bash
# Delete and recreate database
del beatpush.db
python main.py
# Database will be recreated automatically
```

### **Module not found errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📚 Documentation

**Detailed Task Documentation:**
- `TASK_0.1_COMPLETED.md` - Environment setup
- `TASK_0.3_COMPLETED.md` - Database setup
- `TASK_1.1_COMPLETED.md` - Authentication
- `TASK_1.5_COMPLETED.md` - Profiles
- `TASK_2.1_IMAGE_UPLOAD_COMPLETED.md` - Image uploads
- `TASK_2.2_AUDIO_UPLOAD_COMPLETED.md` - Audio uploads
- `TASK_3.1_AI_CONTENT_GENERATION_COMPLETED.md` - AI features

**Progress Summary:**
- `PROGRESS_SUMMARY_PHASE_0_TO_3.1.md` - Full progress report

**Roadmap:**
- `BEATPUSH_EXECUTION_ROADMAP.txt` - Complete project plan

---

## 🎯 Development Workflow

1. **Check roadmap** - See what's next
2. **Read task docs** - Understand requirements
3. **Implement feature** - Write code
4. **Write tests** - Verify functionality
5. **Update docs** - Document completion
6. **Commit changes** - Git commit with clear message
7. **Move to next task**

---

## 🚀 Quick Commands

```bash
# Start server
python main.py

# Run all tests
python test_auth.py && python test_profiles.py && python test_uploads.py

# Check database
python check_db.py

# Verify AI endpoints
python verify_ai_endpoints.py

# Install new package
pip install <package>
pip freeze > requirements.txt
```

---

## 💡 Tips

1. **Always test** after implementing a feature
2. **Use test users** for development (credentials above)
3. **Check logs** if something fails
4. **Read task docs** before starting new tasks
5. **Commit often** with descriptive messages

---

**Happy Coding! 🎉**

For questions or issues, check the detailed task documentation files.
