# Getting Started: Card-Based Review System

## Quick Start Guide

### What You Have Now

✓ Working year-end review system with AI agent  
✓ Riot API integration with rate limiting  
✓ AWS Bedrock (Claude) integration  
✓ Comprehensive match analysis tools

### What We're Building

A 3-page user flow with card-based UI:

1. **Home** → Enter Riot ID
2. **Profile** → Shows rank, icon, unique stat
3. **Dashboard** → Cards with champion mastery, stat highlights, coaching insights

---

## Phase 1: Core Cards (Start Here!)

### Step 1: Create Profile Service (Day 1-2)

**File:** `backend/services/profile_service.py`

**Key functions to implement:**

```python
async def get_player_profile(game_name: str, tag_line: str)
    # 1. Get PUUID
    # 2. Get summoner data (icon, level)
    # 3. Get rank data
    # 4. Generate unique stat from 50 matches
    # 5. Return structured profile

async def _generate_unique_stat(puuid: str)
    # Analyze 50 matches for interesting stats
    # Categories: pentakills, one-trick, vision, solo kills, high KDA
    # Pick most interesting based on rarity score
```

**Start with this template:** See `FEATURE_SPEC_COMPLETE.md` lines 440-630 for full implementation

**Test it:**

```bash
# Start backend
cd backend
python -m uvicorn app.main:app --reload

# Test endpoint
curl http://localhost:8000/api/profile/Doublelift/NA1
```

---

### Step 2: Add Structured Output to Agent (Day 3-4)

**File:** `backend/services/year_rewind_agent.py`

**Changes needed:**

1. **Add output_format parameter:**

```python
async def generate_year_rewind(
    puuid: str,
    riot_id: str,
    output_format: str = "text"  # Add this
) -> Dict[str, Any]:
```

2. **Create new prompt for structured output:**

```python
STRUCTURED_ANALYSIS_PROMPT = """
You are an expert League of Legends analyst creating structured JSON reviews.

OUTPUT FORMAT (strict JSON):
{
  "highest_wr_champion": {...},
  "stat_highlights": [{...}, {...}, {...}],
  "coaching_insights": [{...}, {...}]
}

REQUIREMENTS:
- Cite specific numbers in every insight
- Compare to rank benchmarks
- Make action items concrete and measurable
...
"""
```

3. **Add tool for stat highlight selection:**

```python
@tool
def select_best_stat_highlights(puuid: str) -> str:
    """
    Pick 3 most interesting stats from 6-7 categories.

    Selection criteria:
    - Percentile ranking (prioritize top/bottom 10%)
    - Improvement trends
    - Uniqueness (rare achievements)
    - Balance (2 strengths + 1 area to improve)
    """
    # Implementation in agent_tools.py
```

---

### Step 3: Enhance Agent Tools (Day 4-5)

**File:** `backend/services/agent_tools.py`

**Add these functions:**

```python
def calculate_all_stat_highlights(matches_data: List[Dict], puuid: str) -> Dict:
    """
    Calculate all possible stat highlights across categories.

    Categories:
    1. Combat (KDA, kills, multikills)
    2. Economy (gold/min, CS/min)
    3. Vision (vision score, control wards)
    4. Objectives (tower damage, dragon participation)
    5. Champion mastery (games, win rate, consistency)
    6. Improvement trends (KDA improvement, etc.)
    7. Unique achievements (pentakills, solo kills)

    Returns dict with all calculated stats + percentiles
    """
    pass

def _rank_stat_highlights(all_stats: Dict) -> List[Dict]:
    """
    Rank stats by interestingness.

    Scoring factors:
    - Percentile (top/bottom 10% = high score)
    - Rarity (pentakills > high KDA)
    - Story value (improving > static)
    """
    pass

def _select_balanced_highlights(ranked_stats: List[Dict]) -> List[Dict]:
    """
    Pick top 3 stats with balance.

    Balance rules:
    - Mix categories (not all combat)
    - Prefer 2 strengths + 1 improvement area
    - If all strong, pick 3 strengths
    """
    pass
```

**See:** `FEATURE_SPEC_COMPLETE.md` lines 200-350 for selection logic details

---

### Step 4: Add New Endpoints (Day 5)

**File:** `backend/app/main.py`

**Add these endpoints:**

```python
@app.get("/api/profile/{game_name}/{tag_line}")
async def get_player_profile(game_name: str, tag_line: str):
    """Get profile with rank, icon, unique stat."""
    from services import profile_service

    profile = await profile_service.get_player_profile(game_name, tag_line)

    if not profile.get('success'):
        raise HTTPException(status_code=404, detail=profile.get('error'))

    return profile


@app.post("/api/analysis/structured/{game_name}/{tag_line}")
async def generate_structured_analysis(game_name: str, tag_line: str):
    """Generate card-based analysis."""
    from services import riot_api, year_rewind_agent

    puuid = await riot_api.get_puuid_by_riot_id(game_name, tag_line)
    if not puuid:
        raise HTTPException(status_code=404, detail="Player not found")

    result = await year_rewind_agent.generate_year_rewind(
        puuid=puuid,
        riot_id=f"{game_name}#{tag_line}",
        output_format="structured"
    )

    return result
```

---

### Step 5: Test Everything (Day 6-7)

**Create:** `tests/test_profile_endpoint.py`

```python
import pytest
from backend.services import profile_service

@pytest.mark.asyncio
async def test_valid_player_profile():
    """Test profile generation for valid player."""
    result = await profile_service.get_player_profile("Doublelift", "NA1")

    assert result['success'] is True
    assert 'profile' in result
    assert 'unique_stat' in result['profile']
    assert result['profile']['unique_stat']['percentile'] > 0

@pytest.mark.asyncio
async def test_unique_stat_categories():
    """Test that unique stats are interesting."""
    # Test with multiple players
    # Verify stats are in valid categories
    # Check percentile calculations
    pass
```

**Create:** `tests/test_structured_analysis.py`

```python
@pytest.mark.asyncio
async def test_structured_output_format():
    """Test structured analysis returns valid JSON."""
    # Mock match data
    # Generate structured review
    # Validate JSON schema
    # Check coaching insights have specific numbers
    pass
```

---

## Implementation Checklist

### Week 1: Backend Core

- [ ] Day 1-2: Create `profile_service.py`
  - [ ] Implement summoner/rank fetching
  - [ ] Implement unique stat generation (all 6-7 categories)
  - [ ] Test with 5+ different players
- [ ] Day 3-4: Modify `year_rewind_agent.py`
  - [ ] Add `output_format` parameter
  - [ ] Create `STRUCTURED_ANALYSIS_PROMPT`
  - [ ] Test structured JSON output
- [ ] Day 4-5: Enhance `agent_tools.py`
  - [ ] Implement `calculate_all_stat_highlights()`
  - [ ] Implement stat ranking logic
  - [ ] Implement balanced selection logic
- [ ] Day 5: Update `main.py`
  - [ ] Add `/api/profile` endpoint
  - [ ] Add `/api/analysis/structured` endpoint
  - [ ] Test endpoints with curl/Postman
- [ ] Day 6-7: Testing
  - [ ] Write unit tests for profile service
  - [ ] Write unit tests for structured analysis
  - [ ] Test with 10+ diverse player profiles
  - [ ] Refine prompts based on output quality

### Week 2: Integration & Polish

- [ ] Day 8-9: Frontend Integration (your teammate)
  - [ ] Build profile page UI
  - [ ] Build card components
  - [ ] Connect to backend APIs
- [ ] Day 10-11: Refinement
  - [ ] Improve coaching insight specificity
  - [ ] Add more unique stat categories
  - [ ] Optimize performance
- [ ] Day 12-14: Testing & Deployment
  - [ ] End-to-end testing
  - [ ] Fix bugs
  - [ ] Deploy to development environment
  - [ ] Gather feedback

---

## Key Files Reference

### Existing Files to Modify

1. `backend/services/year_rewind_agent.py` - Add structured output mode
2. `backend/services/agent_tools.py` - Add stat highlight functions
3. `backend/app/main.py` - Add new endpoints

### New Files to Create

1. `backend/services/profile_service.py` - Profile + unique stat generation
2. `backend/services/structured_analysis_service.py` - Wrapper for structured analysis
3. `tests/test_profile_endpoint.py` - Profile tests
4. `tests/test_structured_analysis.py` - Structured analysis tests

---

## Common Issues & Solutions

### Issue 1: Unique Stat Not Interesting

**Problem:** Generated unique stat is boring (e.g., "League Enthusiast")  
**Solution:**

- Lower thresholds for "interesting" stats
- Add more stat categories (comeback wins, late-game specialist, etc.)
- Prioritize rarity score in selection logic

### Issue 2: Coaching Insights Too Generic

**Problem:** AI says "farm better" instead of specific advice  
**Solution:**

- Add more examples to prompt (good vs. bad insights)
- Enforce data point requirement (3+ specific numbers)
- Add validation: reject insights without numbers

### Issue 3: Structured Output Invalid JSON

**Problem:** Agent returns malformed JSON  
**Solution:**

- Add JSON parsing validation in agent
- Retry with "fix JSON" prompt if parsing fails
- Use LangChain's structured output parser

### Issue 4: Rate Limits Hit

**Problem:** Too many Riot API requests during testing  
**Solution:**

- Cache match data aggressively (24 hours)
- Use smaller sample size for testing (20 matches)
- Add delays between test runs

### Issue 5: Bedrock Throttling

**Problem:** Getting ThrottlingException during testing  
**Solution:**

- Your rate limiter should handle this automatically
- Add longer delays between requests (already implemented)
- Use smaller match samples during development

---

## Testing Strategy

### Manual Testing Flow

1. **Test Profile Endpoint:**

```bash
# Test valid player
curl http://localhost:8000/api/profile/Doublelift/NA1

# Test invalid player
curl http://localhost:8000/api/profile/InvalidPlayer/NA1

# Test unranked player
curl http://localhost:8000/api/profile/UnrankedPlayer/NA1
```

2. **Test Structured Analysis:**

```bash
# Test with POST request
curl -X POST http://localhost:8000/api/analysis/structured/Doublelift/NA1

# Should return JSON with:
# - highest_wr_champion
# - stat_highlights (array of 3)
# - coaching_insights (array of 2-3)
```

3. **Validate Output Quality:**

- Check coaching insights cite specific numbers
- Verify stat highlights are diverse (not all combat)
- Confirm action items are concrete and specific
- Ensure percentiles make sense (pentakills = 99th, etc.)

### Test Cases to Cover

**Player Types:**

- [ ] Ranked player (Gold, Plat, Diamond)
- [ ] Unranked player
- [ ] One-trick player (45+ games on one champ)
- [ ] Low-game count player (<20 games)
- [ ] High-game count player (200+ games)
- [ ] Support main (high vision score)
- [ ] ADC main (high CS)
- [ ] Pentakill achiever

**Edge Cases:**

- [ ] Player with no matches in last 365 days
- [ ] Player with only normal games (no ranked)
- [ ] Player with only ARAM games
- [ ] Player not found (404)
- [ ] API timeout/error (500)

---

## Performance Targets

### Response Times

- Profile endpoint: **<5 seconds**
  - 2-3 Riot API calls
  - Unique stat uses cached matches if available
- Structured analysis: **3-6 minutes**
  - 50 matches: ~2-3 minutes
  - 100 matches: ~4-5 minutes
  - Mostly limited by Riot API rate limits

### Success Criteria

- ✓ 95%+ requests succeed
- ✓ Valid JSON returned 100% of time
- ✓ Coaching insights cite specific numbers (manual review)
- ✓ Unique stats are interesting (not generic)
- ✓ Stat highlights are diverse (not all same category)

---

## Quick Win Tips

### Start Small

1. Implement just **pentakills** for unique stat first
2. Test with **one player** you know has pentakills
3. Once working, add other unique stat categories
4. Iterate based on output quality

### Use Existing Code

- Copy match fetching logic from `agent_tools.py`
- Reuse `extract_comprehensive_player_data()` for stats
- Leverage existing rate limiters (don't rebuild)
- Use existing agent architecture (just add structured mode)

### Debug Effectively

- Add verbose logging to profile service
- Print intermediate results (stat candidates, rankings)
- Test unique stat generation separately from full API
- Use small match samples during development (20-30)

---

## Next Steps After Phase 1

### Phase 2: Timeline Analysis (Week 3)

- Parse match timelines for critical moments
- Identify gold swings, teamfight outcomes
- Generate timestamp-specific coaching notes
- Add timeline endpoint: `/api/match/{match_id}/timeline/{puuid}`

### Phase 3: OPGG Integration (Week 4)

- Research OPGG MCP availability
- Fetch meta builds and rank benchmarks
- Compare player builds to meta
- Add meta comparison to coaching insights

### Phase 4: Charts & Polish (Week 5)

- Generate chart data for frontend
- Implement rank progression tracking
- Add KDA trend calculations
- Polish UI/UX with your frontend teammate

---

## Resources

### Documentation

- **Full Feature Spec:** `FEATURE_SPEC_COMPLETE.md`
- **Steering Docs Review:** `STEERING_DOCS_REVIEW.md`
- **Analysis Quality Guide:** `analysis_quality.md`

### Code References

- **Existing Agent:** `backend/services/year_rewind_agent.py`
- **Existing Tools:** `backend/services/agent_tools.py`
- **Existing Riot API:** `backend/services/riot_api.py`

### External APIs

- **Riot API Docs:** https://developer.riotgames.com/apis
- **Data Dragon:** https://developer.riotgames.com/docs/lol#data-dragon
- **AWS Bedrock Docs:** https://docs.aws.amazon.com/bedrock/

---

## Questions Before Starting?

Before you start coding, make sure you understand:

1. **Unique Stat Logic:** How to prioritize rare/interesting stats
2. **Structured Output:** How agent generates JSON vs. text
3. **Stat Highlights:** How AI picks best 3 from 6-7 categories
4. **Coaching Quality:** What makes insights "good" vs. "generic"
5. **Caching Strategy:** When to cache, what to cache, TTLs

If anything is unclear, review:

- `FEATURE_SPEC_COMPLETE.md` for detailed implementation
- `STEERING_DOCS_REVIEW.md` for architecture guidance
- Existing code in `backend/services/` for patterns

---

## Success Checklist

Before considering Phase 1 complete:

**Functionality:**

- [ ] Profile endpoint returns valid data
- [ ] Unique stat is generated correctly
- [ ] Structured analysis returns valid JSON
- [ ] Stat highlights are diverse and interesting
- [ ] Coaching insights cite specific numbers
- [ ] Action items are concrete and actionable

**Quality:**

- [ ] Manual review of 10+ player analyses shows good quality
- [ ] No generic advice like "farm better" without specifics
- [ ] Percentiles are realistic (not all 99th percentile)
- [ ] Unique stats match player profile (one-tricks get one-trick stat)

**Technical:**

- [ ] Error handling covers all cases
- [ ] Rate limiting works under load
- [ ] Caching reduces redundant API calls
- [ ] Tests pass (unit + integration)
- [ ] Documentation is updated

---

## Final Tips

1. **Start with one player:** Pick someone you know (or yourself) and test thoroughly
2. **Iterate on prompts:** The AI output quality depends heavily on prompt engineering
3. **Test edge cases:** Low games, unranked, one-tricks, pentakills, etc.
4. **Ask for help:** If stuck, reference the full spec or ask questions
5. **Have fun:** This is a hackathon - prioritize working features over perfection!

**Good luck! 🚀**

Once Phase 1 is done, your frontend teammate can build the UI and you'll have a solid foundation for Phases 2-4.
