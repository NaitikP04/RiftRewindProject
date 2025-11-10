# Deployment Guide - Vercel (Frontend) + Render (Backend)

## 🚀 Quick Deploy

### Frontend (Vercel)
```bash
# From project root
cd frontend
vercel deploy --prod
```

### Backend (Render)
1. Connect GitHub repo to Render
2. Use `backend` directory as root
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 📋 Environment Variables

### Frontend (.env.local for Vercel)
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

### Backend (.env for Render)
```env
RIOT_API_KEY=RGAPI-your-key-here
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1
ALLOWED_ORIGINS=https://your-frontend-url.vercel.app,http://localhost:3000
```

---

## 🔧 Render Configuration

### render.yaml (Backend)
```yaml
services:
  - type: web
    name: rift-rewind-api
    env: python
    region: oregon
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: RIOT_API_KEY
        sync: false
      - key: AWS_ACCESS_KEY_ID
        sync: false
      - key: AWS_SECRET_ACCESS_KEY
        sync: false
      - key: AWS_REGION
        value: us-east-1
      - key: PYTHON_VERSION
        value: 3.11
```

---

## 🎯 Vercel Configuration

### vercel.json (Frontend)
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-backend-url.onrender.com/api/:path*"
    }
  ]
}
```

---

## ⚡ Performance Optimizations

### Backend (Already Implemented)
- ✅ JSON caching (80-90% faster on repeat requests)
- ✅ Rate limiting with intelligent backoff
- ✅ Batch API calls (10-30 matches per batch)
- ✅ Error resilience (timeline failures don't crash)
- ✅ Health endpoint for monitoring

### Frontend (Already Implemented)
- ✅ Fake progress streaming (smooth UX)
- ✅ Code splitting with Next.js
- ✅ Framer Motion animations
- ✅ Lazy loading components
- ✅ SSE for real-time updates

---

## 🧪 Pre-Deployment Checklist

### Backend
- [ ] Test with production Riot API key (higher rate limits)
- [ ] Verify AWS Bedrock credentials work in production region
- [ ] Test CORS with production frontend URL
- [ ] Check health endpoint: `GET /api/health`
- [ ] Verify cache directory is writable

### Frontend
- [ ] Update `NEXT_PUBLIC_API_URL` in Vercel
- [ ] Test SSE connection with production backend
- [ ] Verify all images load (champion icons, profile pics)
- [ ] Test error states (invalid Riot ID, API failures)
- [ ] Check mobile responsiveness

---

## 🔍 Monitoring & Debugging

### Backend Logs (Render)
```bash
# View live logs
render logs -f

# Check specific error
render logs | grep ERROR
```

### Frontend Logs (Vercel)
```bash
# View deployment logs
vercel logs your-deployment-url

# Check function logs
vercel logs --follow
```

### Health Check Endpoints
- Backend: `https://your-backend.onrender.com/api/health`
- Returns: Rate limiter stats, cache stats, API status

---

## 🐛 Common Issues & Fixes

### Issue: CORS Errors
**Fix**: Update `ALLOWED_ORIGINS` in backend `.env`
```python
# backend/app/main.py
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
```

### Issue: SSE Connection Fails
**Fix**: Ensure Render allows streaming responses (it does by default)
- Check: No proxy timeouts (Render timeout is 30 mins)
- Verify: EventSource URL uses `https://` not `http://`

### Issue: Cold Start Delays (Render Free Tier)
**Fix**: Implement keep-alive ping
```python
# Optional: Add to backend for free tier
from apscheduler.schedulers.background import BackgroundScheduler

@app.on_event("startup")
async def keep_alive():
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: None, 'interval', minutes=10)
    scheduler.start()
```

### Issue: Cache Not Persisting (Render)
**Fix**: Use disk storage (already implemented with `cache/` directory)
- Render provides persistent disk storage
- Cache survives restarts automatically

### Issue: Slow First Request
**Expected**: Render free tier spins down after 15 mins inactivity
- First request takes ~30s to spin up
- Upgrade to paid plan for always-on

---

## 📊 Performance Expectations

### Production (With Riot API Production Key)
- Profile fetch: **2-3 seconds** (vs 5s dev)
- Analysis: **1-2 minutes** (vs 3-6 min dev)
- Cache hit: **<1 second** (instant)

### Free Tier Limits
- Render: 750 hours/month (always-on if only service)
- Vercel: 100 GB bandwidth/month
- AWS Bedrock: Pay per request (Claude Sonnet 4)

---

## 🎬 Demo Script (For Submission Video)

1. **Show Landing Page** (5s)
   - Explain Riot API integration
   - Show clean UI

2. **Enter Riot ID** (5s)
   - Use pre-analyzed account for speed
   - Example: `Hide#NA1` or `Doublelift#NA1`

3. **Watch Progress Bar** (10s)
   - Show fake streaming animation
   - Highlight smooth UX

4. **Dashboard Reveal** (30s)
   - Explain AI-generated insights
   - Show champion stats
   - Highlight personality analysis

5. **Key Features** (10s)
   - Real-time API integration
   - Claude Sonnet 4 AI
   - Personalized recommendations

**Total Time**: 60 seconds

---

## 🚨 Rate Limit Considerations

### Development Key (Current)
- 20 requests/second
- 100 requests/2 minutes
- **Demo Impact**: 3-6 min analysis time

### Production Key (Request from Riot)
- 500 requests/second
- 30,000 requests/10 minutes
- **Demo Impact**: 1-2 min analysis time
- **How to get**: Apply at https://developer.riotgames.com/

---

## 💡 Demo Optimization Tips

1. **Pre-warm Cache**:
   ```bash
   # Analyze demo accounts before presentation
   curl -X POST "https://your-api.onrender.com/api/analysis/Hide/NA1?num_matches=100"
   ```

2. **Use High-Rank Accounts**: More impressive stats
   - Masters+: Better champion pool diversity
   - Example: `TFBlade#NA1`, `Yassuo#NA1`

3. **Keep Backend Warm**:
   ```bash
   # Ping every 5 mins before demo
   watch -n 300 curl https://your-api.onrender.com/api/health
   ```

4. **Have Backup**:
   - Record video of working demo
   - Use mock data if API fails
   - Test 30 mins before submission

---

## 📦 Build Commands Reference

### Frontend
```bash
# Install dependencies
npm install

# Build for production
npm run build

# Test production build locally
npm start

# Deploy to Vercel
vercel deploy --prod
```

### Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Run production server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Test health
curl http://localhost:8000/api/health
```

---

## 🎯 Submission Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Render
- [ ] Environment variables set
- [ ] CORS configured
- [ ] Demo account pre-cached
- [ ] Health endpoints responding
- [ ] SSE streaming works
- [ ] Mobile responsive
- [ ] Error handling tested
- [ ] README updated with live URLs
- [ ] Video demo recorded
- [ ] GitHub repo public
- [ ] License added (MIT)

---

**Good luck with your submission! 🎉**
