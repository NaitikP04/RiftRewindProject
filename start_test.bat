@echo off
echo Starting Rift Rewind Backend...
echo.
echo API will be available at: http://127.0.0.1:8000
echo Health check: http://127.0.0.1:8000/api/health
echo API docs: http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000