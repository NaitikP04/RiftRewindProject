# Analysis Quality Guidelines

## What Makes Good Coaching Insights?

### Principles

1. **Specific, not generic**: "Your CS drops from 7.2/min to 5.1/min after 20 minutes" > "Farm better"
2. **Contextual**: Consider champion, role, rank, and meta
3. **Actionable**: Clear steps to improve, not just observations
4. **Data-driven**: Always reference actual stats
5. **Encouraging**: Balance criticism with recognition of strengths

### Bad vs. Good Examples

**❌ Bad:**
"You die a lot. Try to position better."

**✅ Good:**
"Your average deaths (5.2/game) are high for Gold ADCs (avg 4.1). Key issue: 68% of deaths occur after 25 minutes in teamfights. Focus on: staying behind your frontline, tracking enemy engage cooldowns (Malphite R, Leona E), and avoiding face-checks."

### Insight Categories

#### 1. Macro Play (Game Understanding)

- **What to analyze**: Objective control, map rotations, game pacing
- **Data sources**: Turret takedowns, damage to objectives, game duration patterns
- **Example insight**: "You excel in early game (67% first tower rate) but struggle to close games (avg 32 min in wins vs. 28 min for your rank). Work on: Baron setup at 20-25 minutes, inhibitor trading, and avoiding ARAM mid after winning lane."

#### 2. Micro Mechanics

- **What to analyze**: Trading patterns, solo kills, damage output
- **Data sources**: Solo kills, damage per minute, team damage %, CS per min
- **Example insight**: "Your Yasuo mechanics are strong (6.1 KDA, 3.2 solo kills/game) but you're leaving farm on the table. At 8.2 CS/min, you're missing ~40 CS per game compared to high Diamond Yasuo players (9.8 CS/min). Practice: wave manipulation drills, jungle camp timing, and recall timings."

#### 3. Vision & Information

- **What to analyze**: Warding patterns, map awareness
- **Data sources**: Vision score, wards placed/killed, control ward purchases
- **Example insight**: "Vision score of 1.2/min is excellent for support (90th percentile). However, ward placement concentration shows 73% of wards are in bot river. Diversify: deep ward enemy jungle at 1:15, contest scuttle vision at 3:15, sweep pixel brush before Baron."

#### 4. Itemization

- **What to analyze**: Build adaptation, situational items
- **Data sources**: Build paths (requires OPGG/meta data integration)
- **Example insight**: [Future feature - requires meta build comparison]

#### 5. Mental Game & Consistency

- **What to analyze**: Performance variance, tilt patterns
- **Data sources**: KDA standard deviation, win/loss streaks, performance trends
- **Example insight**: "Your performance is volatile (KDA range: 1.2-11.3). After losses, your next-game KDA drops 42%. Consistency tip: take 5-minute break after losses, review one mistake (don't dwell), queue with a clear plan."

### Prompt Engineering for Quality

**Current Prompt Issues:**

- Too general ("analyze performance trends")
- Doesn't enforce specificity
- No examples of good coaching

**Improved Prompt Structure:**

```
You are an expert League coach analyzing {riot_id}'s season.

TONE: Encouraging but honest, like a personal coach reviewing film.

SPECIFICITY REQUIREMENT:
- Every insight must cite specific numbers (e.g., "Your KDA improved from 2.8 to 3.9")
- Compare to benchmarks when possible (e.g., "Gold average is 3.2 KDA")
- Give 1-2 concrete action items per insight

COACHING FOCUS AREAS (pick top 3 based on data):
1. Early game: First 15 minutes (CS, kills, map control)
2. Mid game: 15-25 minutes (objectives, rotations, teamfight positioning)
3. Late game: 25+ minutes (closing games, decision-making under pressure)
4. Vision control: Warding patterns, vision denial
5. Champion mastery: Win rates, consistency, one-tricks vs. variety

AVOID:
- Generic advice ("improve CS", "die less")
- Comparing to pro players unless player is Diamond+
- More than 3 coaching points (overwhelming)

STRUCTURE:
[Playstyle Personality]
[Year in Numbers - key stats]
[Performance Trends - improvement or decline]
[Champion Mastery - top picks and performance]
[Top 3 Coaching Insights with specific action items]
```

### Data Enrichment Checklist

To improve analysis quality, add these data points:

**High Priority (Next Sprint):**

- [ ] Match timelines (early/mid/late game splits)
- [ ] Item builds (requires static data or OPGG)
- [ ] First blood participation, first tower rates
- [ ] Objective control stats (dragons, barons, heralds)

**Medium Priority:**

- [ ] Champion matchup analysis (win rate vs. specific champions)
- [ ] Rank progression tracking (show climb/fall over time)
- [ ] Duo vs. solo queue performance splits
- [ ] Champion mastery curves (performance over time on a champion)

**Low Priority (Polish):**

- [ ] Clip highlighting (API for remarkable moments)
- [ ] Meta comparison (your build vs. current meta builds)
- [ ] Peer comparison (your rank vs. similar players)
