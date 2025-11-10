# Quick Reference Guide - Rift Rewind

## ⚡ NEW: Improvements Added (November 2025)

### What's New:
- ✅ **JSON Caching** - 80-90% faster repeat analyses!
- ✅ **Config Validation** - Clear error messages
- ✅ **Type Safety** - Pydantic models for all APIs
- ✅ **Enhanced Logging** - Better debugging
- ✅ **Health Monitoring** - Check cache & rate limit stats

### Quick Test New Features:
```powershell
# Check health with cache stats
curl http://localhost:8000/api/health

# Watch for cache hits in logs:
# "💾 Cache hits: 95/100 (95%)"
```

### Performance: First analysis = 3-6min, Repeat = 30-60s (⚡**80-90% faster!**)

See **IMPROVEMENTS.md** for full details!

---

## Daily Startup

### Start Application
```bash
# Terminal 1 - Backend
start_backend.bat

# Terminal 2 - Frontend
start_frontend.bat
```

### Access Points
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Testing

### Test Accounts (NA Region)
- `i will int#akali` - Emerald IV
- `kinuryu#amphy` - Test account 2

### Run Tests
```bash
cd tests

# Test profile service
python test_profile.py

# Test structured analysis
python test_structured_analysis.py

# Test rate limiting
python test_rate_limits.py
```

---

## Key Files to Edit

### Backend - AI Analysis
**File**: `backend/services/structured_analysis_service.py`
- Line ~270: `_generate_deep_ai_analysis()` function
- Contains AI prompt for Claude Sonnet 4
- Modify prompt to improve insight quality

**File**: `backend/services/agent_tools.py`
- Data extraction functions
- Champion pool analysis
- Playstyle identification
- Add new metrics here

### Frontend - UI/UX
**File**: `frontend/features/dashboard/DashboardContainer.tsx`
- Main dashboard layout
- Card arrangement and styling

**File**: `frontend/components/ui/`
- Reusable UI components
- Modify for visual changes

### Configuration
**Backend**: `backend/.env`
```env
RIOT_API_KEY=your_key
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
```

**Frontend**: `frontend/.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Architecture Quick View

### Data Flow
```
User Input → LandingContainer
           ↓
API Client (api-client.ts)
           ↓
FastAPI Backend (main.py)
           ↓
Profile Service (fast) → Structured Analysis (slow)
           ↓                      ↓
Frontend Dashboard (DashboardContainer)
```

### API Endpoints
- `GET /api/profile/{name}/{tag}` - Profile data (<5s)
- `POST /api/analysis/{name}/{tag}` - AI analysis (3-6 min)
- `GET /api/health` - Service health

---

## Common Tasks

### Improve AI Insights
1. Edit `backend/services/structured_analysis_service.py`
2. Find `_generate_deep_ai_analysis()` function (line ~270)
3. Modify the `prompt` variable
4. Save and backend auto-reloads (if using --reload flag)
5. Test with: http://localhost:3000

### Add New Stat
1. Extract in `agent_tools.py` → `extract_comprehensive_player_data()`
2. Calculate in `structured_analysis_service.py` → `_extract_detailed_stats()`
3. Include in AI prompt → `_generate_deep_ai_analysis()`
4. Display in frontend → `DashboardContainer.tsx`

### Change UI Styling
1. Edit components in `frontend/components/`
2. Modify layouts in `frontend/features/dashboard/`
3. Update global styles in `frontend/styles/globals.css`
4. Save and frontend auto-reloads

---

## Troubleshooting

### Backend Errors
```bash
# Check logs in Terminal 1
# Common issues:
- Missing .env file → Create backend/.env
- AWS credentials → Verify Bedrock access
- Riot API key → Check validity
```

### Frontend Errors
```bash
# Check browser console (F12)
# Common issues:
- API not reachable → Check backend is running
- CORS errors → Backend should allow localhost:3000
- Type errors → Check lib/types.ts matches backend response
```

### Analysis Takes Too Long
- Expected: 3-6 minutes for 100 matches
- Check rate limiter: http://localhost:8000/api/health
- Reduce matches: Add `?num_matches=50` to analysis endpoint

---

## Git Workflow

### Before Commit
```bash
# Verify .env files are NOT tracked
git status

# Should NOT see:
# - backend/.env
# - frontend/.env.local
```

### Clean Commit
```bash
git add .
git commit -m "feat: your feature description"
git push origin main
```

---

## Next Steps (Post-Hackathon)

1. **AI Quality** - Refine prompts and add more context
2. **Performance** - Optimize match fetching and caching
3. **Multi-Region** - Add support for other regions
4. **Historical Data** - Implement rank timeline tracking
5. **Share Feature** - Export as image functionality

---

## Important Notes

- **Region**: Only NA is supported right now
- **Rate Limits**: 20 req/s, 100 req/2min for Riot API
- **AI Model**: Claude Sonnet 4 (expensive but high quality)
- **Analysis Time**: 3-6 minutes is normal
- **Mock Data**: Progress charts use mock data (not implemented yet)

---

## Useful Commands

### Backend
```bash
# Check syntax errors
cd backend
python -m py_compile services/structured_analysis_service.py

# Run specific test
python tests/test_structured_analysis.py

# Check rate limiter stats
curl http://localhost:8000/api/health
```

### Frontend
```bash
cd frontend

# Install new package
npm install package-name

# Build for production
npm run build

# Check TypeScript errors
npx tsc --noEmit
```

---

**Last Updated**: Step 3 Complete - Frontend/Backend Connected
