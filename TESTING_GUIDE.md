# Quick Testing Guide 🚀

## Test the Improvements (5 minutes)

### 1. Start Backend
```powershell
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**You should see**:
```
🚀 Rift Rewind API Starting...
════════════════════════════════════════════════════════════

🔧 Configuration:
   Riot API: ✓ Configured
   AWS Bedrock: ✓ Configured
   Region: us-east-1
   Cache: Enabled
   Rate Limits: 20/s, 100/2min

📦 Cache Status:
   Matches: 0 (0 fresh)
   Profiles: 0
   Size: 0.00 MB
════════════════════════════════════════════════════════════

INFO:     Application startup complete.
```

If you see ❌ errors, check your `.env` file!

---

### 2. Test Health Endpoint
```powershell
# New terminal
curl http://localhost:8000/api/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "rate_limiter": {
    "requests_last_second": 0,
    "requests_last_2_minutes": 0,
    "capacity_1s": "0/20",
    "capacity_2min": "0/100"
  },
  "cache": {
    "total_matches": 0,
    "fresh_matches": 0,
    "total_profiles": 0,
    "cache_size_mb": 0.0
  },
  "config_valid": true
}
```

---

### 3. Test Profile Fetch (Quick)
```powershell
# Replace with any NA summoner
curl "http://localhost:8000/api/profile/Doublelift/NA1"
```

**Should complete in ~5 seconds**

---

### 4. Test Full Analysis (First Time - No Cache)
```powershell
# This will take 3-6 minutes
$response = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/analysis/Doublelift/NA1" -Body '{"num_matches":50}' -ContentType "application/json"
$response | ConvertTo-Json -Depth 10
```

**Watch the logs** - you'll see:
```
📥 Fetching details for 50 matches...
   💾 Cache hits: 0/50 (0%)
   🌐 Fetching 50 new matches from API...
   Progress: 100% (50/50)
   ✅ Successfully fetched 50/50 matches
```

---

### 5. Test Again (With Cache) ⚡
```powershell
# Same request - should be MUCH faster!
$response = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/analysis/Doublelift/NA1" -Body '{"num_matches":50}' -ContentType "application/json"
```

**Watch the logs** - you'll see:
```
📥 Fetching details for 50 matches...
   💾 Cache hits: 50/50 (100%)
   ✅ All matches loaded from cache!
```

**Result**: ~80-90% faster! 🚀

---

### 6. Check Cache Stats
```powershell
curl http://localhost:8000/api/health
```

**Now you'll see**:
```json
{
  "cache": {
    "total_matches": 50,
    "fresh_matches": 50,
    "total_profiles": 1,
    "cache_size_mb": 0.45
  }
}
```

---

## Test with Frontend

### 1. Start Frontend
```powershell
# New terminal
cd frontend
npm run dev
```

### 2. Open Browser
Navigate to: http://localhost:3000

### 3. Test Flow
1. Enter Riot ID: `Doublelift#NA1`
2. Click "Generate Review"
3. Watch profile load (~5 seconds)
4. Wait for analysis (~3-6 minutes first time)
5. **Try the same player again** - should be much faster!

---

## Verify Cache Files

```powershell
# Check cache was created
dir backend\cache

# View cache contents (pretty printed)
Get-Content backend\cache\matches.json | ConvertFrom-Json | ConvertTo-Json -Depth 5
```

---

## Performance Benchmark

Test the same player twice:

```powershell
# First run (no cache)
Measure-Command {
  Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/analysis/Doublelift/NA1" -Body '{"num_matches":50}' -ContentType "application/json"
}

# Second run (with cache)
Measure-Command {
  Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/analysis/Doublelift/NA1" -Body '{"num_matches":50}' -ContentType "application/json"
}
```

**Expected**:
- First run: ~180-360 seconds (3-6 min)
- Second run: ~30-60 seconds
- **Improvement**: 80-90% faster! ⚡

---

## Troubleshooting

### "Config validation failed"
```powershell
# Copy example env
Copy-Item backend\.env.example backend\.env

# Edit with your keys
notepad backend\.env

# Restart backend
```

### "Module not found"
```powershell
cd backend
pip install -r requirements.txt
```

### Cache not working
```powershell
# Check cache folder exists
New-Item -ItemType Directory -Path backend\cache -Force

# Check logs for cache hits
# You should see: "💾 Cache hits: X/Y"
```

### Clear cache to test fresh
```powershell
Remove-Item backend\cache\*.json
```

---

## What to Look For (Demo Points)

### ✅ Config Validation
- Clear startup messages
- Helpful error messages if keys missing

### ✅ Cache Performance
- First analysis: "💾 Cache hits: 0/50 (0%)"
- Second analysis: "💾 Cache hits: 50/50 (100%)"
- Massive speed improvement

### ✅ Type Safety
- All responses have proper structure
- No more generic dict returns

### ✅ Better Logging
- Clear progress indicators
- Emoji-enhanced readability
- Performance metrics

### ✅ Health Monitoring
- Cache statistics
- Rate limiter stats
- Config validation status

---

## Next Steps

After testing improvements:

1. ✅ **Commit changes**: All improvements are in place
2. 🎨 **Polish frontend**: Add loading states, better error messages
3. 📊 **Add more stats**: Leverage the cached data for richer insights
4. 🎥 **Record demo**: Show cache performance difference
5. 🏆 **Submit to hackathon**: You're ready!

---

## Questions?

Check these files:
- `IMPROVEMENTS.md` - Full documentation
- `backend/services/cache_manager.py` - Cache implementation
- `backend/services/config.py` - Config validation
- `backend/app/schemas.py` - Type definitions
