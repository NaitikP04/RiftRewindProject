@echo off
echo Starting Rift Rewind Backend...
echo.

cd backend

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found in backend directory
    echo Please create backend/.env with your API keys
    echo See backend/.env.example for reference
    pause
    exit /b 1
)

echo Starting FastAPI server on http://localhost:8000
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
