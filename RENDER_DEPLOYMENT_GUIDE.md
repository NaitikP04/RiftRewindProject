# 🚀 Render Backend Deployment Guide

## Step-by-Step Render Setup

### Prerequisites
- ✅ GitHub account with your repository pushed
- ✅ Render account (free tier works!) - Sign up at https://render.com
- ✅ Your API keys ready (Riot API, AWS credentials)

---

## 📋 Step 1: Prepare Your Repository

### 1.1 Verify render.yaml exists
Check that `render.yaml` is in your project root. It should look like this:

```yaml
services:
  - type: web
    name: rift-rewind-api
    env: python
    region: oregon
    plan: starter
    rootDir: backend
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
      - key: ALLOWED_ORIGINS
        value: https://rift-rewind.vercel.app,http://localhost:3000
    healthCheckPath: /api/health
```

### 1.2 Verify requirements.txt
Make sure `backend/requirements.txt` has all dependencies:

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
httpx==0.26.0
python-dotenv==1.0.0
langchain==0.1.0
langchain-aws==0.1.0
boto3==1.34.0
pydantic==2.5.0
```

### 1.3 Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

---

## 🔧 Step 2: Create Render Web Service

### 2.1 Sign in to Render
1. Go to https://render.com
2. Click "Sign Up" or "Log In"
3. Connect your GitHub account

### 2.2 Create New Web Service
1. Click **"New +"** in the top right
2. Select **"Web Service"**
3. Choose **"Build and deploy from a Git repository"**
4. Click **"Connect GitHub"** (if not already connected)

### 2.3 Select Your Repository
1. Find **"RiftRewindProject"** in the list
2. Click **"Connect"**

### 2.4 Configure Service Settings

**Basic Settings:**
- **Name**: `rift-rewind-api` (or your preferred name)
- **Region**: `Oregon (US West)` (recommended for low latency)
- **Branch**: `main`
- **Root Directory**: `backend` ⚠️ **IMPORTANT!**
- **Runtime**: `Python 3`

**Build & Deploy Settings:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- **Plan**: `Free` (or `Starter` if you need more power)
  - Free: 750 hours/month, spins down after 15 min inactivity
  - Starter: $7/month, always on, faster

---

## 🔐 Step 3: Add Environment Variables

Scroll down to **"Environment Variables"** section and add these:

### Required Variables:

1. **RIOT_API_KEY**
   - Click **"Add Environment Variable"**
   - Key: `RIOT_API_KEY`
   - Value: `RGAPI-your-key-here`
   - ⚠️ Get your key from: https://developer.riotgames.com/

2. **AWS_ACCESS_KEY_ID**
   - Key: `AWS_ACCESS_KEY_ID`
   - Value: Your AWS access key
   - ⚠️ Create IAM user with `bedrock:InvokeModel` permission

3. **AWS_SECRET_ACCESS_KEY**
   - Key: `AWS_SECRET_ACCESS_KEY`
   - Value: Your AWS secret key
   - 🔒 Keep this secret!

4. **AWS_REGION**
   - Key: `AWS_REGION`
   - Value: `us-east-1`

5. **ALLOWED_ORIGINS**
   - Key: `ALLOWED_ORIGINS`
   - Value: `http://localhost:3000`
   - ⚠️ Update later with your Vercel URL

### Optional (Render sets automatically):
- `PORT` - Render provides this
- `PYTHON_VERSION` - Defaults to 3.11

---

## 🚀 Step 4: Deploy

1. Click **"Create Web Service"** at the bottom
2. Render will start building your service
3. Watch the logs in the **"Logs"** tab

### Expected Build Process:
```
==> Cloning from https://github.com/NaitikP04/RiftRewindProject...
==> Checking out commit 1a2b3c4...
==> Downloading cache...
==> Building with pip...
==> Installing dependencies from requirements.txt
==> Build complete!
==> Starting service...
INFO:     Uvicorn running on http://0.0.0.0:10000
INFO:     Application startup complete.
```

**First deploy takes 2-5 minutes**

---

## ✅ Step 5: Verify Deployment

### 5.1 Get Your Render URL
Once deployed, you'll see your service URL:
```
https://rift-rewind-api.onrender.com
```
Or similar (Render assigns a unique URL)

### 5.2 Test Health Endpoint
Open in browser or use curl:
```bash
curl https://your-app-name.onrender.com/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "riot_api": "configured",
  "bedrock": "configured",
  "rate_limiter": {
    "requests_this_second": 0,
    "requests_this_2min": 0,
    "capacity_2min": 100
  },
  "cache": {
    "total_matches": 0,
    "fresh_matches": 0,
    "total_profiles": 0,
    "cache_size_mb": 0
  }
}
```

### 5.3 Test Profile Endpoint
```bash
curl https://your-app-name.onrender.com/api/profile/Hide/NA1
```

If you see player data, **you're live!** 🎉

---

## 🔄 Step 6: Update Frontend

### 6.1 Update .env.local
In your `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=https://your-app-name.onrender.com
```

### 6.2 Update ALLOWED_ORIGINS on Render
1. Go to Render dashboard
2. Select your service
3. Go to **"Environment"** tab
4. Edit `ALLOWED_ORIGINS`
5. Change to: `https://your-frontend.vercel.app,http://localhost:3000`
6. Click **"Save Changes"** (triggers auto-redeploy)

---

## 🐛 Troubleshooting

### Issue: Build Failed - "No module named 'services'"
**Fix**: Make sure `Root Directory` is set to `backend`

### Issue: "Internal Server Error" on API calls
**Solution**:
1. Check Render logs: Dashboard → Your Service → Logs tab
2. Look for Python errors
3. Common causes:
   - Missing environment variable
   - Wrong AWS region
   - Invalid Riot API key

### Issue: Free tier spins down (slow first request)
**Symptoms**: First request takes 30+ seconds

**Solutions**:
1. **Upgrade to Starter plan** ($7/month, always on)
2. **Keep-alive script** (ping every 10 mins):
   ```bash
   # Run locally before demos
   watch -n 600 curl https://your-app.onrender.com/api/health
   ```
3. **Pre-warm before demo** (5 mins before):
   ```bash
   curl https://your-app.onrender.com/api/health
   ```

### Issue: CORS errors in browser
**Fix**:
1. Check `ALLOWED_ORIGINS` includes your frontend URL
2. Make sure no trailing slashes
3. Restart service after changing env vars

### Issue: Rate limit errors
**Expected**: Development Riot API key has low limits (20/s, 100/2min)
**Solution**: 
- Apply for production key at https://developer.riotgames.com/
- Production key: 500/s, 30k/10min (much better!)

---

## 📊 Monitoring Your Service

### View Logs
1. Go to Render dashboard
2. Click your service
3. **"Logs"** tab shows live logs
4. Look for:
   ```
   INFO:     Application startup complete.
   📋 Step 1/5: Fetching profile...
   ✅ Profile fetched successfully!
   ```

### Check Metrics
**"Metrics"** tab shows:
- CPU usage
- Memory usage
- Request count
- Response times

**Free tier**: 512 MB RAM, 0.1 CPU
**Starter tier**: 512 MB RAM, 0.5 CPU (faster)

### Health Check
Render automatically pings `/api/health` every minute
- Green checkmark = healthy
- Red X = unhealthy (check logs)

---

## 💰 Cost Breakdown

### Free Tier
- **Cost**: $0
- **Hours**: 750/month (enough for one service always on)
- **Limits**: Spins down after 15 min inactivity
- **Best for**: Development, testing, low-traffic demos

### Starter Tier
- **Cost**: $7/month
- **Features**: Always on, faster CPU, no spin-down
- **Best for**: Hackathon demos, production

### Recommended for Hackathon
**Start with Free**, upgrade to Starter ($7) if:
- You're doing live demos (no spin-down delay)
- Expecting multiple users
- Want consistent performance

---

## 🎯 Pre-Demo Checklist

**30 Minutes Before Demo:**
- [ ] Ping health endpoint to wake up service
- [ ] Test profile fetch with demo account
- [ ] Check Render logs - no errors
- [ ] Verify frontend can reach backend
- [ ] Pre-cache 1-2 demo accounts (optional but recommended)

**5 Minutes Before Demo:**
```bash
# Wake up Render service
curl https://your-app.onrender.com/api/health

# Test full flow
curl -X POST "https://your-app.onrender.com/api/analysis/Hide/NA1?num_matches=100"
```

---

## 🔗 Quick Reference

### Your URLs After Deployment
```
Backend:  https://your-app-name.onrender.com
Health:   https://your-app-name.onrender.com/api/health
Profile:  https://your-app-name.onrender.com/api/profile/{name}/{tag}
Analysis: https://your-app-name.onrender.com/api/analysis/{name}/{tag}
```

### Environment Variables Needed
```
RIOT_API_KEY=RGAPI-xxx
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=us-east-1
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

### Common Commands
```bash
# Wake up service
curl https://your-app.onrender.com/api/health

# Test profile
curl https://your-app.onrender.com/api/profile/Hide/NA1

# View logs (on Render dashboard)
Dashboard → Service → Logs tab

# Redeploy
Dashboard → Service → Manual Deploy → "Clear build cache & deploy"
```

---

## 🎓 Next Steps

1. ✅ Deploy backend to Render (you're doing this now!)
2. Deploy frontend to Vercel (see DEPLOYMENT.md)
3. Update CORS settings with Vercel URL
4. Test full flow end-to-end
5. Pre-cache demo accounts
6. Record demo video
7. Submit to hackathon! 🎉

---

## 📞 Need Help?

**Render Support:**
- Docs: https://render.com/docs
- Community: https://community.render.com/

**Project Issues:**
- Check `backend/app/main.py` for CORS settings
- Verify all environment variables are set
- Look at Render logs for Python errors
- Test locally first: `uvicorn app.main:app --reload`

**Common Error Solutions:**
1. "Module not found" → Check `Root Directory = backend`
2. "CORS error" → Update `ALLOWED_ORIGINS`
3. "Unhealthy service" → Check logs, verify env vars
4. "Slow first request" → Free tier spin-down (normal)

---

**You're almost there! 🚀**

Once you see "Application startup complete" in the logs and `/api/health` returns 200, **your backend is live!**
