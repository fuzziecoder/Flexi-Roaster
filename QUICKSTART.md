# FlexiRoaster - Quick Start Guide

## Prerequisites

1. **Node.js** (for frontend) - Already installed ✓
2. **Python 3.8+** (for backend) - Need to verify

---

## Frontend (Already Running)

Your frontend is already running at: **http://localhost:5173**

If it's not loading:
1. Check if `npm run dev` is still running
2. Try refreshing the browser
3. Clear browser cache

---

## Backend Setup (Step-by-Step)

### 1. Check Python Installation

```powershell
python --version
# or
python3 --version
# or
py --version
```

If Python is not found, download from: https://www.python.org/downloads/

### 2. Install Backend Dependencies

```powershell
cd d:\Desktop\Flexi-Roaster\backend
pip install fastapi uvicorn sqlalchemy pyyaml pydantic
```

### 3. Initialize Database

```powershell
cd d:\Desktop\Flexi-Roaster
python backend/db/init_db.py
```

### 4. Start Backend Server

```powershell
cd d:\Desktop\Flexi-Roaster
python backend/main.py
```

The API will start at: **http://127.0.0.1:8000**

---

## Verify Everything Works

### Frontend
- Open: http://localhost:5173
- You should see the FlexiRoaster dashboard

### Backend API
- Open: http://127.0.0.1:8000/api/docs
- You should see the Swagger API documentation

### Test API Connection
```powershell
curl http://127.0.0.1:8000/health
```

---

## Common Issues

### Issue 1: Python not found
**Solution:** Install Python from python.org or use `py` instead of `python`

### Issue 2: Module not found errors
**Solution:** Install dependencies:
```powershell
pip install -r backend/requirements.txt
```

### Issue 3: Port already in use
**Solution:** Kill the process or use a different port:
```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue 4: Frontend not connecting to backend
**Solution:** Make sure both are running:
- Frontend: http://localhost:5173
- Backend: http://127.0.0.1:8000

---

## What to Test

1. **Create a Pipeline** (via API docs)
2. **Execute Pipeline** (via API)
3. **View in Dashboard** (frontend should show data)

---

## Need Help?

Tell me specifically what error you're seeing:
- Error message?
- Which step failed?
- Screenshot of the issue?
