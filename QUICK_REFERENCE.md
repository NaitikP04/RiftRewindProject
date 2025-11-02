# Quick Reference Card

## 🚀 Start Here

**Current Status:** Ready to implement Phase 1 (Card-Based UI)  
**First Task:** Create `backend/services/profile_service.py`  
**Timeline:** 7-10 days for Phase 1  

---

## 📖 Documentation Map

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **PROJECT_STATUS_SUMMARY.md** | High-level overview of project status | Start here for big picture |
| **GETTING_STARTED.md** | Day-by-day implementation guide | When starting to code |
| **FEATURE_SPEC_COMPLETE.md** | Complete technical specification | When implementing features |
| **STEERING_DOCS_REVIEW.md** | Architecture and design guidance | When making design decisions |

---

## 🎯 Phase 1 Checklist

### Week 1: Implementation
- [ ] **Day 1-2:** Create profile service
  - File: `backend/services/profile_service.py`
  - Functions: `get_player_profile()`, `_generate_unique_stat()`
  
- [ ] **Day 3-4:** Modify agent for structured output
  - File: `backend/services/year_rewind_agent.py`
  - Add: `output_format` parameter, structured prompt
  
- [ ] **Day 4-5:** Enhance agent tools
  - File: `backend/services/agent_tools.py`
  - Add: `calculate_all_stat_highlights()`, selection logic
  
- [ ] **Day 5:** Add endpoints
  - File: `backend/app/main.py`
  - Add: `/api/profile`, `/api/analysis/structured`
  
- [ ] **Day 6-7:** Test everything
  - Files: `tests/test_profile_*.py`
  - Test with 10+ diverse players

---

## 🔧 Key Code Changes

### 1. Profile Service (NEW FILE)
```python
# backend/services/profile_service.py

async def get_player_profile(game_name: str, tag_line: str):
    """Main entry point for profile data."""
    # 1. Get PUUID
    # 2. Get summoner (icon, level)
    # 3. Get rank
    # 4. Generate unique stat
    # 5. Return structured profile
```

### 2. Agent Modification
```python
# backend/services/year_rewind_agent.py

async def generate_year_rewind(
    puuid: str, 
    riot_id: str,
    output_format: str = "text"  # ADD THIS
):
    # If structured, use different prompt
    # Return JSON instead of markdown
```

### 3. Agent Tools Enhancement
```python
# backend/services/agent_tools.py

def calculate_all_stat_highlights(matches, puuid):
    """Calculate all 6-7 stat categories."""
    # Combat, economy, vision, objectives,
    # mastery, trends, achievements
    
def _select_balanced_highlights(ranked_stats):
    """Pick top 3 with diversity."""
    # Mix categories, balance strengths/weaknesses
```

### 4. New Endpoints
```python
# backend/app/main.py

@app.get("/api/profile/{game_name}/{tag_line}")
async def get_player_profile(...):
    """Profile with rank, icon, unique stat."""

@app.post("/api/analysis/structured/{game_name}/{tag_line}")
async def generate_structured_analysis(...):
    """Card-based analysis."""
```

---

## 🧪 Testing Commands

```bash
# Start backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Test profile endpoint
curl http://localhost:8000/api/profile/Doublelift/NA1

# Test structured analysis
curl -X POST http://localhost:8000/api/analysis/structured/Doublelift/NA1

# Run tests
python tests/test_profile_endpoint.py
python tests/test_structured_analysis.py
```

---

## 📊 API Schemas

### Profile Response
```json
{
  "success": true,
  "profile": {
    "puuid": "...",
    "riot_id": "Doublelift#NA1",
    "summoner_icon_url": "https://...",
    "rank": {
      "tier": "GOLD",
      "division": "II",
      "lp": 57,
      "win_rate": 52.5
    },
    "unique_stat": {
      "title": "Pentakill Artist",
      "description": "6 pentakills - Top 1%",
      "icon": "🌟",
      "percentile": 99
    }
  }
}
```

### Structured Analysis Response
```json
{
  "success": true,
  "analysis": {
    "highest_wr_champion": {
      "name": "Jinx",
      "win_rate": 66.7,
      "avg_kda": 5.8
    },
    "stat_highlights": [
      {
        "title": "Vision Master",
        "value": "1.8",
        "unit": "vision/min",
        "percentile": 95
      }
      // ... 2 more
    ],
    "coaching_insights": [
      {
        "title": "Close Games Faster",
        "summary": "Wins avg 32 min vs. 28 for rank...",
        "action_items": [
          {
            "action": "Setup Baron at 20-25 min",
            "reasoning": "...",
            "difficulty": "medium"
          }
        ]
      }
      // ... 1-2 more
    ]
  }
}
```

---

## 🎯 Success Criteria

### Phase 1 Complete When:
- ✅ Profile endpoint works (<5 seconds)
- ✅ Unique stat is interesting (not generic)
- ✅ Structured analysis returns valid JSON
- ✅ Stat highlights are diverse (3 different categories)
- ✅ Coaching insights cite specific numbers
- ✅ Action items are concrete and actionable
- ✅ 10+ test players analyzed successfully
- ✅ Frontend teammate can build UI with API

---

## 🔥 Unique Stat Categories

1. **Pentakills** (rarity: 99th percentile)
   - "Pentakill Artist: 6 pentakills - Top 1%"
   
2. **One-Trick** (45+ games on one champ)
   - "Jinx Specialist: 87 games, 62% WR"
   
3. **Vision Master** (top 5% vision score)
   - "Vision Excellence: 1.8 vision/min - Top 5%"
   
4. **Solo Kill Master** (2+ solo kills/game)
   - "Mechanical Outplays: 2.3 solo kills/game"
   
5. **High KDA** (4.5+ KDA)
   - "Consistent Performer: 5.8 KDA - Top tier"
   
6. **Comeback King** (high WR when behind)
   - "Never Surrender: 58% WR in comeback games"
   
7. **Late Game Specialist** (KDA improves after 25 min)
   - "Scales to Victory: +2.1 KDA late game"

---

## 💡 Quality Checklist

### Good Coaching Insight Example
```json
{
  "title": "Reduce Early Deaths",
  "summary": "Deaths 0-15 min: 2.1/game vs. 1.3 Master avg. 73% from jungle ganks.",
  "data_points": [
    "Deaths 0-15 min: 2.1 (Master avg: 1.3)",
    "73% from enemy jungle ganks",
    "Gold deficit after death: -520g"
  ],
  "action_items": [
    {
      "action": "Ward tribush at 2:45 (before first gank)",
      "reasoning": "Your avg ward time is 3:15, missing early ganks",
      "difficulty": "easy"
    }
  ]
}
```

### Bad Example (Too Generic)
```json
{
  "title": "Die Less",
  "summary": "You die too much. Position better.",
  "action_items": [
    {
      "action": "Don't die",
      "reasoning": "Dying is bad"
    }
  ]
}
```

**Key Differences:**
- ✅ Specific numbers (2.1 vs. 1.3)
- ✅ Context (73% from ganks)
- ✅ Concrete action (ward at 2:45)
- ✅ Clear reasoning (3:15 is too late)

---

## ⚠️ Common Pitfalls

1. **Generic unique stats**
   - ❌ "League Enthusiast: Active player"
   - ✅ "Pentakill Artist: 6 pentas - Top 1%"

2. **Non-specific coaching**
   - ❌ "Farm better"
   - ✅ "CS drops from 7.2/min to 5.1/min after 20 min"

3. **Invalid JSON**
   - Add validation and retry logic
   - Test JSON parsing before returning

4. **Rate limit issues**
   - Cache aggressively (24-hour TTL)
   - Use small samples during testing

5. **All stat highlights same category**
   - Enforce diversity in selection logic
   - Mix combat, vision, mastery

---

## 🚦 Development Workflow

### Daily Cycle
1. **Morning:** Review spec for day's tasks
2. **Code:** Implement feature with tests
3. **Test:** Validate with real API calls
4. **Iterate:** Refine based on output quality
5. **Document:** Update any changes

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/phase1-cards

# Commit frequently
git add backend/services/profile_service.py
git commit -m "feat: add profile service with unique stats"

# Push when ready
git push origin feature/phase1-cards
```

---

## 📞 When to Reference Full Docs

- **Stuck on implementation?** → `GETTING_STARTED.md`
- **Need schema details?** → `FEATURE_SPEC_COMPLETE.md`
- **Architecture questions?** → `STEERING_DOCS_REVIEW.md`
- **Want big picture?** → `PROJECT_STATUS_SUMMARY.md`

---

## 🎉 You Got This!

**Remember:**
- Start small (one feature at a time)
- Test early and often
- Iterate on quality (especially prompts)
- Ask for help when stuck
- Have fun! This is a hackathon 🚀

**Current Phase:** Phase 1 - Card-Based UI  
**Next Milestone:** Working profile + structured analysis  
**Timeline:** 7-10 days  
**Goal:** Demo-ready for hackathon  

---

## 📋 Daily Standup Template

```markdown
### Day X Progress

**Completed:**
- [ ] Task 1
- [ ] Task 2

**In Progress:**
- [ ] Task 3

**Blockers:**
- None / [describe blocker]

**Next Steps:**
- [ ] Task for tomorrow

**Notes:**
- Any observations or decisions made
```

---

## 🔗 Quick Links

- **Riot API Docs:** https://developer.riotgames.com/apis
- **Data Dragon:** https://developer.riotgames.com/docs/lol#data-dragon
- **AWS Bedrock:** https://docs.aws.amazon.com/bedrock/
- **LangChain:** https://python.langchain.com/docs/

---

**Last Updated:** December 2024  
**Phase:** 1 (Card-Based UI)  
**Status:** Ready to Code ✅
