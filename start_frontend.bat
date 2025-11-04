@echo off
echo Starting Rift Rewind Frontend...
echo.

cd frontend

REM Check if .env.local exists
if not exist .env.local (
    echo WARNING: .env.local not found, creating from .env.example
    copy .env.example .env.local
)

echo Installing dependencies...
call npm install

echo.
echo Starting Next.js dev server on http://localhost:3000
echo.
call npm run dev
