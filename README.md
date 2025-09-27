# Rift Rewind - League Match Tracker

A simple web application to track recent League of Legends matches using the Riot Games API.

## Features

- Search for any player by Riot ID (Name#TAG)
- View the last 10 matches for any player
- Clean, responsive interface
- Real-time match data from Riot Games API

## Prerequisites

- Node.js (v18 or higher)
- Python (v3.8 or higher)
- Riot Games API Key

## Setup Instructions

### 1. Get a Riot API Key

1. Go to [Riot Developer Portal](https://developer.riotgames.com/)
2. Sign in with your Riot account
3. Create a new app or use the development key
4. Copy your API key

### 2. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd RiftRewindProject

# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the `backend` directory:

```env
RIOT_API_KEY=your_riot_api_key_here
```

### 4. Run the Application

**Terminal 1 - Backend:**

```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend:**

```bash
npm run dev
```

### 5. Access the App

- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8000

## Usage

1. Enter a Riot ID in the format `PlayerName#TAG` (e.g., `Faker#KR1`)
2. Click "Search" to fetch recent matches
3. View the list of match IDs for the last 10 games

## API Endpoints

- `GET /api/matches/{game_name}/{tag_line}` - Get recent matches for a player

## Troubleshooting

- Make sure both frontend and backend are running
- Verify your Riot API key is valid and not expired
- Check that the player name and tag are correct
- Development API keys have rate limits (100 requests per 2 minutes)

## Project Structure

```
RiftRewindProject/
├── app/                    # Next.js app directory
│   ├── globals.css        # Global styles with Tailwind
│   ├── layout.tsx         # Root layout component
│   └── page.tsx           # Main page component
├── backend/               # Python FastAPI backend
│   ├── app/
│   │   └── main.py        # FastAPI application
│   ├── services/
│   │   └── riot_api.py    # Riot API service functions
│   ├── .env.example       # Environment variables template
│   └── requirements.txt   # Python dependencies
├── .gitignore             # Git ignore rules
├── package.json           # Node.js dependencies and scripts
├── setup.bat              # Windows setup script
└── README.md              # This file
```

## Tech Stack

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Python, httpx
- **API:** Riot Games League of Legends API
