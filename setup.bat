@echo off
echo Setting up Rift Rewind Project...
echo.

echo Installing frontend dependencies...
npm install
if %errorlevel% neq 0 (
    echo Failed to install frontend dependencies
    pause
    exit /b 1
)

echo.
echo Installing backend dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install backend dependencies
    pause
    exit /b 1
)

cd ..
echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Add your Riot API key to backend/.env
echo 2. Run 'npm run dev' in one terminal
echo 3. Run 'python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000' in backend directory in another terminal
echo.
pause