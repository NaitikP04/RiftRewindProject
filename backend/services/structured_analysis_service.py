"""
Structured Analysis Service
Generates AI-powered analysis using Claude Sonnet 4 with accurate stats from match history.
"""
import asyncio
import os
import json
import httpx
import boto3
import statistics
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError
from langchain_aws import ChatBedrock
from . import agent_tools, profile_service
from .rate_limiter import rate_limiter
from .bedrock_rate_limiter import bedrock_rate_limiter
from .progress_tracker import progress_tracker

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

# Initialize Bedrock client for Claude Sonnet 4 (via inference profile)
bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
)

# Shared Haiku LLM for lightweight analysis tasks
haiku_llm = getattr(agent_tools, "haiku_llm", None)
if haiku_llm is None:
    try:
        internal_bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )

        haiku_llm = ChatBedrock(
            client=internal_bedrock_client,
            model_id="anthropic.claude-3-haiku-20240307-v1:0",
            model_kwargs={"temperature": 0.3, "max_tokens": 1000},
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
    except Exception as e:
        print(f"Warning: Could not initialize Haiku LLM for structured analysis. Error: {e}")
        haiku_llm = None


async def generate_structured_analysis(
    game_name: str,
    tag_line: str,
    num_matches: int = 100,
    analysis_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate complete structured analysis for frontend dashboard.
    Uses accurate stats from match history + deep AI analysis with Claude Sonnet 4.
    """
    try:
        print(f"\n{'='*60}")
        print(f"🤖 Generating Deep AI Analysis with Claude Sonnet 4")
        print(f"   Player: {game_name}#{tag_line}")
        print(f"   Analyzing: {num_matches} matches")
        print(f"{'='*60}\n")
        
        # Step 1: Get profile data
        print("📋 Step 1/5: Fetching profile...")
        if analysis_id:
            await progress_tracker.update(
                analysis_id, 
                "profile", 
                10, 
                f"Loading profile for {game_name}#{tag_line}..."
            )
        
        profile_result = await profile_service.get_player_profile(game_name, tag_line)
        
        if not profile_result.get('success'):
            if analysis_id:
                await progress_tracker.update(analysis_id, "error", 0, f"Failed to load profile: {profile_result.get('error', 'Unknown error')}")
            return profile_result
        
        profile = profile_result['profile']
        puuid = profile['puuid']
        
        # Step 2: Fetch comprehensive match history
        print(f"\n📥 Step 2/5: Fetching match history...")
        if analysis_id:
            await progress_tracker.update(
                analysis_id, 
                "matches", 
                25, 
                f"Finding {num_matches} recent matches..."
            )
        
        match_ids, metadata = await agent_tools.fetch_matches_intelligently(
            puuid=puuid,
            target_matches=num_matches,
            max_age_days=365
        )
        
        if not match_ids:
            if analysis_id:
                await progress_tracker.update(analysis_id, "error", 0, "No recent matches found")
            return {"success": False, "error": "No recent matches found"}
        
        print(f"   Found {len(match_ids)} matches to analyze")
        
        # Step 3: Get detailed match data
        print(f"\n📊 Step 3/5: Analyzing match details...")
        if analysis_id:
            await progress_tracker.update(
                analysis_id, 
                "details", 
                50, 
                f"Analyzing {len(match_ids)} match details..."
            )
        
        matches_data = await agent_tools.get_match_details_batch(match_ids)
        
        if not matches_data:
            if analysis_id:
                await progress_tracker.update(analysis_id, "error", 0, "Failed to fetch match details")
            return {"success": False, "error": "Failed to fetch match details"}
        
        print(f"   Successfully analyzed {len(matches_data)} matches")
        
        # Step 4: Calculate comprehensive performance metrics
        print(f"\n🔢 Step 4/5: Calculating detailed statistics...")
        if analysis_id:
            await progress_tracker.update(
                analysis_id, 
                "statistics", 
                75, 
                "Calculating performance trends and champion stats..."
            )
        performance = agent_tools.calculate_performance_trends(matches_data, puuid)
        champion_pool = agent_tools.analyze_champion_pool(matches_data, puuid)
        playstyle = agent_tools.identify_playstyle_personality(matches_data, puuid)
        
        # Get accurate top champions from match data
        top_champions = _extract_top_champions(champion_pool)
        
        # Extract detailed challenge data
        detailed_stats = _extract_detailed_stats(matches_data, puuid)
        
        # Step 5: Use AI to generate complete analysis
        # ========== NEW: DEEP DIVE ANALYSIS (STEPS 4.1 - 4.3) ==========

        # Step 4.1: Use AI (Haiku) to select 3 key matches
        print(f"\n🔍 Step 4.1/5: Selecting key matches for deep dive...")
        if analysis_id:
            await progress_tracker.update(
                analysis_id, 
                "deep_dive", 
                80, 
                "Selecting key matches for timeline analysis..."
            )

        key_matches_to_analyze = await _select_key_matches(
            matches_data=matches_data,
            champion_pool=champion_pool,
            performance=performance,
            puuid=puuid
        )
        print(f"   Selected {len(key_matches_to_analyze)} matches for timeline analysis.")

        # Step 4.2: Fetch and analyze timeline data for *only* those key matches
        print(f"\n🔎 Step 4.2/5: Performing deep dive timeline analysis...")
        if analysis_id:
            await progress_tracker.update(
                analysis_id, 
                "timeline", 
                85, 
                f"Analyzing {len(key_matches_to_analyze)} match timelines..."
            )

        deep_analysis_results: List[Dict[str, Any]] = []
        timeline_tasks = []
        for match_info in key_matches_to_analyze:
            timeline_tasks.append(
                agent_tools.get_timeline_analysis_for_match(
                    match_id=match_info['matchId'],
                    puuid=puuid,
                    player_champion=match_info['champion'],
                    context_reason=match_info['context']
                )
            )

        timeline_results = await asyncio.gather(*timeline_tasks, return_exceptions=True) if timeline_tasks else []

        for i, result in enumerate(timeline_results):
            if isinstance(result, Exception):
                print(f"   ⚠️ Timeline analysis failed for match {key_matches_to_analyze[i]['matchId']}: {result}")
                continue
            if result:
                deep_analysis_results.append({
                    "context": key_matches_to_analyze[i]['context'],
                    "analysis": result
                })

        # Step 4.3: Rename old Step 5 to Step 5
        print(f"\n🤖 Step 5/5: Generating AI insights with Claude Sonnet 4...")
        if analysis_id:
            await progress_tracker.update(
                analysis_id, 
                "ai_analysis", 
                90, 
                "Generating AI insights with Claude Sonnet 4..."
            )
        # ========== END OF NEW SECTION ==========
        ai_result = await _generate_deep_ai_analysis(
            performance=performance,
            champion_pool=champion_pool,
            playstyle=playstyle,
            detailed_stats=detailed_stats,
            rank_info=profile['rank'],
            matches_analyzed=len(matches_data),
            deep_analysis_results=deep_analysis_results
        )
        
        if analysis_id:
            await progress_tracker.update(
                analysis_id, 
                "complete", 
                100, 
                "Analysis complete!"
            )
        
        print(f"\n{'='*60}")
        print(f"✅ Deep Analysis Complete!")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "data": {
                "displayName": profile['display_name'],
                "profilePicture": profile['profile_icon_url'],
                "mainRole": profile['main_role'],
                "topChampions": top_champions[:3],
                "highlights": ai_result['highlights'],
                "aiInsight": ai_result['insight'],
                "personality": ai_result['personality'],
                "rank": profile['rank']['display'],
                "matchesAnalyzed": len(matches_data)
            }
        }
        
    except Exception as e:
        print(f"\n❌ Error in structured analysis: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": f"Analysis failed: {str(e)}"}


def _extract_top_champions(champion_pool: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract top champions with accurate stats from match data."""
    top_champs = champion_pool.get('top_champions', [])[:5]
    
    return [
        {
            "name": champ['name'],
            "games": champ['games'],
            "winRate": round(champ['win_rate'], 1)
        }
        for champ in top_champs
    ]


def _extract_detailed_stats(matches_data: List[Dict[str, Any]], puuid: str) -> Dict[str, Any]:
    """
    Extract detailed stats including challenges, timeline patterns.
    This provides the deep data for AI analysis.
    """
    detailed = {
        "challenge_stats": {},
        "timeline_patterns": {},
        "consistency_metrics": {}
    }
    
    all_player_stats = []
    
    for match in matches_data:
        player_data = agent_tools.extract_comprehensive_player_data(match, puuid)
        if player_data:
            all_player_stats.append(player_data)
            
            # Extract challenge data
            participants = match['info']['participants']
            player = next((p for p in participants if p['puuid'] == puuid), None)
            if player and 'challenges' in player:
                challenges = player['challenges']
                
                # Key challenges for analysis
                for key in ['laneMinionsFirst10Minutes', 'maxCsAdvantageOnLaneOpponent', 
                           'soloKills', 'takedownsFirst25Minutes', 'visionScoreAdvantageLaneOpponent',
                           'controlWardsPlaced', 'stealthWardsPlaced']:
                    if key in challenges:
                        if key not in detailed['challenge_stats']:
                            detailed['challenge_stats'][key] = []
                        detailed['challenge_stats'][key].append(challenges[key])
    
    # Calculate averages (iterate over a copy to avoid modification during iteration)
    for key, values in list(detailed['challenge_stats'].items()):
        if values and isinstance(values, list):
            detailed['challenge_stats'][f'{key}_avg'] = sum(values) / len(values)
            detailed['challenge_stats'][f'{key}_max'] = max(values)
    
    # Timeline patterns
    early_game_deaths = []
    late_game_deaths = []
    
    for stats in all_player_stats:
        duration = stats['game_duration']
        deaths = stats['deaths']
        
        if duration < 25:
            early_game_deaths.append(deaths)
        elif duration > 35:
            late_game_deaths.append(deaths)
    
    if early_game_deaths and late_game_deaths:
        detailed['timeline_patterns'] = {
            'early_avg_deaths': sum(early_game_deaths) / len(early_game_deaths),
            'late_avg_deaths': sum(late_game_deaths) / len(late_game_deaths)
        }
    
    # Consistency metrics
    if len(all_player_stats) >= 10:
        kda_values = [s['kda'] for s in all_player_stats]
        cs_values = [s['cs_per_min'] for s in all_player_stats]
        
        detailed['consistency_metrics'] = {
            'kda_std_dev': statistics.stdev(kda_values) if len(kda_values) > 1 else 0,
            'cs_std_dev': statistics.stdev(cs_values) if len(cs_values) > 1 else 0
        }
    
    return detailed


async def _select_key_matches(
    matches_data: List[Dict[str, Any]],
    champion_pool: Dict[str, Any],
    performance: Dict[str, Any],
    puuid: str
) -> List[Dict[str, str]]:
    """
    Uses a fast AI (Haiku) to select 3-5 interesting matches for deep analysis.
    """
    if not haiku_llm: # Use the internal Haiku LLM
        print("Key match selection disabled: internal LLM not initialized.")
        return []

    # 1. Find top 3 champs
    top_champs = [c['name'] for c in champion_pool.get('top_champions', [])[:3]]
    
    # 2. Extract simplified match list
    simplified_matches = []
    for match in matches_data:
        player_data = agent_tools.extract_comprehensive_player_data(match, puuid)
        if player_data:
            simplified_matches.append({
                "matchId": match['metadata']['matchId'],
                "champion": player_data['champion'],
                "kda": player_data['kda'],
                "win": player_data['win'],
                "duration_mins": player_data['game_duration']
            })
    
    if not simplified_matches:
        return []

    # 3. Create prompt for Haiku
    prompt = f"""
    You are a match analyst. Your goal is to select 3-5 key matches from a list for deeper timeline analysis.
    The player's top champions are: {', '.join(top_champs)}
    
    From the following list of matches, select:
    1.  **"Best Performance"**: A recent game with a very high KDA or on a main champion.
    2.  **"Worst Defeat"**: A recent game on a main champion with a low KDA and a loss.
    3.  **"Most ARAM"**: A long game (> 35 mins) with a very high number of deaths.

    Respond *only* with a JSON list in this exact format:
    [
      {{"matchId": "MATCH_ID_HERE", "champion": "CHAMPION_NAME", "context": "Best Performance"}},
      {{"matchId": "MATCH_ID_HERE", "champion": "CHAMPION_NAME", "context": "Worst Defeat"}},
      {{"matchId": "MATCH_ID_HERE", "champion": "CHAMPION_NAME", "context": "Most ARAM"}}
    ]

    MATCH LIST:
    {json.dumps(simplified_matches, default=str)}
    """

    # 4. Invoke Haiku
    try:
        await bedrock_rate_limiter.wait_if_needed(is_retry=False)
        bedrock_rate_limiter.record_request(success=False)

        result = await haiku_llm.ainvoke(prompt)
        response_text = result.content
        
        bedrock_rate_limiter.record_request(success=True)

        # Extract JSON from response
        import re
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if json_match:
            return json.loads(json_match.group())
        else:
            print(f"   [Deep Dive] Failed to parse key matches JSON: {response_text}")
            return []
            
    except Exception as e:
        print(f"   [Deep Dive] Key match selection LLM failed: {e}")
        bedrock_rate_limiter.record_request(success=False)
        return []


async def _generate_deep_ai_analysis(
    performance: Dict[str, Any],
    champion_pool: Dict[str, Any],
    playstyle: Dict[str, Any],
    detailed_stats: Dict[str, Any],
    rank_info: Dict[str, Any],
    matches_analyzed: int,
    deep_analysis_results: List[Dict[str, Any]]  # <-- ADD THIS
) -> Dict[str, Any]:
    """
    Use Claude Sonnet 4 to generate deep, personalized analysis.
    Full AI-generated narrative with specific insights and benchmarks.
    """
    
    # Prepare comprehensive data for AI
    prompt = f"""You are an expert League of Legends analyst. Provide a deep, personalized analysis for this player.

PLAYER PROFILE:
- Rank: {rank_info['display']}
- Matches Analyzed: {matches_analyzed}
- Main Role: {champion_pool.get('primary_role', 'Unknown')}

AGGREGATE PERFORMANCE ("Wide" Data):
- Win Rate: {performance.get('overall_win_rate', 0):.1f}%
- Average KDA: {performance.get('avg_kda', 0):.2f} (K:{performance.get('avg_kills', 0):.1f} / D:{performance.get('avg_deaths', 0):.1f} / A:{performance.get('avg_assists', 0):.1f})
- CS/min: {performance.get('avg_cs_per_min', 0):.1f}
- Vision Score/min: {performance.get('avg_vision_per_min', 0):.2f}
- Top Champions: {json.dumps([f"{c['name']}: {c['games']} games, {c['win_rate']:.1f}% WR" for c in champion_pool.get('top_champions', [])[:3]], indent=2)}
- Playstyle: {playstyle.get('primary_trait', 'Unknown')}
- Advanced Stats: {json.dumps(detailed_stats, indent=2)}

DEEP DIVE TIMELINE ANALYSIS ("Deep" Data):
{json.dumps(deep_analysis_results, indent=2) if deep_analysis_results else "No deep analysis available."}

BENCHMARKS (for context):
- {rank_info.get('tier', 'GOLD')} Average KDA: 2.8-3.2
- {rank_info.get('tier', 'GOLD')} Average CS/min: 6.0-6.5
- {rank_info.get('tier', 'GOLD')} Average Vision/min: 0.8-1.2

YOUR TASK:
Generate 3 Stat Highlights, 1 Deep Insight, and 1 Personality.

1.  **Select 3 Best Stat Highlights**: Choose from the "Wide" Data. Be specific with numbers.

2.  **Write Deep AI Insight (4-5 sentences)**: This is the most important part.
    -   **You MUST use the "Deep" Data.**
    -   Find a connection between the "Wide" data and "Deep" data.
    -   Example: If "Wide" data shows a 30% WR on Vayne, and "Deep" data says "In this match, player died 3 times solo in the side lane," then your insight should be:
        "Your stats show you struggle on Vayne (30% WR), and we found a 'gameplay bug' that might be the cause: we analyzed a key loss and found a pattern of you getting caught farming solo in a side-lane post-20 minutes. Fixing this one habit could be the key to climbing."
    -   Identify 1 critical weakness *with evidence from the timeline analysis*.
    -   Provide 1 actionable improvement.

3.  **Determine Personality**: Pick ONE that best fits:
    - "Aggressive Playmaker"
    - "Teamfight Specialist"  
    - "Vision Master"
    - "Carry Player"
    - "Consistent Performer"
    - "Strategic Player"

IMPORTANT: 
- No generic statements.
- The "Deep AI Insight" MUST be based on the "Deep Dive Timeline Analysis". If that data is empty, just report on the aggregate stats.
- Connect the timeline event to a broader pattern.

RESPOND IN EXACT JSON FORMAT:
{{
  "highlights": [
    {{"stat": "descriptive title", "value": "number with unit"}},
    {{"stat": "descriptive title", "value": "number with unit"}},
    {{"stat": "descriptive title", "value": "number with unit"}}
  ],
  "insight": "your 4-5 sentence deep analysis here, using the deep dive data",
  "personality": "chosen personality"
}}"""
    
    try:
        await bedrock_rate_limiter.wait_if_needed(is_retry=False)
        
        # Call Claude Sonnet 4 via US inference profile
        # Use inference profile ID instead of direct model ID
        response = bedrock_client.invoke_model(
            modelId="us.anthropic.claude-sonnet-4-20250514-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        bedrock_rate_limiter.record_request(success=True)
        
        # Parse response
        response_body = json.loads(response['body'].read())
        ai_text = response_body['content'][0]['text']
        
        # Extract JSON
        import re
        json_match = re.search(r'\{[\s\S]*\}', ai_text)
        if json_match:
            ai_result = json.loads(json_match.group())
            print(f"   ✓ AI generated deep insights successfully")
            return ai_result
        else:
            print(f"   ⚠ Could not parse AI response, using fallback")
            return _fallback_insights(performance, playstyle)
            
    except Exception as e:
        print(f"   ⚠ AI generation failed: {e}, using fallback")
        import traceback
        traceback.print_exc()
        return _fallback_insights(performance, playstyle)


def _fallback_insights(performance: Dict[str, Any], playstyle: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback insights if AI fails."""
    highlights = []
    
    kda = performance.get('avg_kda', 0)
    if kda >= 3.0:
        highlights.append({"stat": "Strong KDA", "value": f"{kda:.1f}"})
    
    wr = performance.get('overall_win_rate', 0)
    if wr >= 50:
        highlights.append({"stat": "Positive Win Rate", "value": f"{wr:.0f}%"})
    
    cs = performance.get('avg_cs_per_min', 0)
    if cs >= 6.0:
        highlights.append({"stat": "Good Farming", "value": f"{cs:.1f} CS/min"})
    
    while len(highlights) < 3:
        highlights.append({"stat": "Games Played", "value": str(performance.get('total_games', 0))})
    
    return {
        "highlights": highlights[:3],
        "insight": f"{playstyle.get('primary_trait', 'Player')} with {kda:.1f} KDA across {performance.get('total_games', 0)} games. Focus on consistency and reducing deaths to climb further.",
        "personality": playstyle.get('primary_trait', 'Consistent Performer')
    }
