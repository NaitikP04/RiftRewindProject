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
from . import agent_tools, profile_service
from .rate_limiter import rate_limiter
from .bedrock_rate_limiter import bedrock_rate_limiter

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

# Initialize Bedrock client for Claude Sonnet 4 (via inference profile)
bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
)


async def generate_structured_analysis(
    game_name: str,
    tag_line: str,
    num_matches: int = 100
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
        profile_result = await profile_service.get_player_profile(game_name, tag_line)
        
        if not profile_result.get('success'):
            return profile_result
        
        profile = profile_result['profile']
        puuid = profile['puuid']
        
        # Step 2: Fetch comprehensive match history
        print(f"\n📥 Step 2/5: Fetching match history...")
        match_ids, metadata = await agent_tools.fetch_matches_intelligently(
            puuid=puuid,
            target_matches=num_matches,
            max_age_days=365
        )
        
        if not match_ids:
            return {"success": False, "error": "No recent matches found"}
        
        print(f"   Found {len(match_ids)} matches to analyze")
        
        # Step 3: Get detailed match data
        print(f"\n📊 Step 3/5: Analyzing match details...")
        matches_data = await agent_tools.get_match_details_batch(match_ids)
        
        if not matches_data:
            return {"success": False, "error": "Failed to fetch match details"}
        
        print(f"   Successfully analyzed {len(matches_data)} matches")
        
        # Step 4: Calculate comprehensive performance metrics
        print(f"\n🔢 Step 4/5: Calculating detailed statistics...")
        performance = agent_tools.calculate_performance_trends(matches_data, puuid)
        champion_pool = agent_tools.analyze_champion_pool(matches_data, puuid)
        playstyle = agent_tools.identify_playstyle_personality(matches_data, puuid)
        
        # Get accurate top champions from match data
        top_champions = _extract_top_champions(champion_pool)
        
        # Extract detailed challenge data
        detailed_stats = _extract_detailed_stats(matches_data, puuid)
        
        # Step 5: Use AI to generate complete analysis
        print(f"\n🤖 Step 5/5: Generating AI insights with Claude Sonnet 4...")
        ai_result = await _generate_deep_ai_analysis(
            performance=performance,
            champion_pool=champion_pool,
            playstyle=playstyle,
            detailed_stats=detailed_stats,
            rank_info=profile['rank'],
            matches_analyzed=len(matches_data)
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


async def _generate_deep_ai_analysis(
    performance: Dict[str, Any],
    champion_pool: Dict[str, Any],
    playstyle: Dict[str, Any],
    detailed_stats: Dict[str, Any],
    rank_info: Dict[str, Any],
    matches_analyzed: int
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

PERFORMANCE METRICS:
- Win Rate: {performance.get('overall_win_rate', 0):.1f}%
- Average KDA: {performance.get('avg_kda', 0):.2f} (K:{performance.get('avg_kills', 0):.1f} / D:{performance.get('avg_deaths', 0):.1f} / A:{performance.get('avg_assists', 0):.1f})
- CS/min: {performance.get('avg_cs_per_min', 0):.1f}
- Vision Score/min: {performance.get('avg_vision_per_min', 0):.2f}
- Damage/min: {performance.get('avg_damage_per_min', 0):.0f}
- Gold/min: {performance.get('avg_gold_per_min', 0):.0f}
- Multikills: {performance.get('total_multikills', 0)}
- Pentakills: {performance.get('total_penta_kills', 0)}

TOP CHAMPIONS:
{json.dumps([f"{c['name']}: {c['games']} games, {c['win_rate']:.1f}% WR, {c['avg_kda']:.1f} KDA" for c in champion_pool.get('top_champions', [])[:3]], indent=2)}

PLAYSTYLE ANALYSIS:
- Primary Trait: {playstyle.get('primary_trait', 'Unknown')}
- Aggression Score: {playstyle.get('scores', {}).get('aggression_score', 0):.0f}/100
- Carry Potential: {playstyle.get('scores', {}).get('carry_potential', 0):.0f}/100
- Vision Mastery: {playstyle.get('scores', {}).get('vision_mastery', 0):.0f}/100
- Teamfight Prowess: {playstyle.get('scores', {}).get('teamfight_prowess', 0):.0f}/100

ADVANCED METRICS:
{json.dumps(detailed_stats, indent=2)}

IMPROVEMENT TRENDS:
{json.dumps({
    'has_trends': performance.get('has_trends', False),
    'first_half_wr': performance.get('first_half_wr', 0),
    'second_half_wr': performance.get('second_half_wr', 0),
    'kda_improvement': performance.get('kda_improvement', 0)
}, indent=2)}

YOUR TASK:
1. **Select 3 Best Stat Highlights**: Choose the most impressive, unique, or notable stats. Be specific with numbers.

2. **Write Deep AI Insight (4-5 sentences)**: 
   - Start with playstyle personality and what defines their play
   - Highlight 1-2 key strengths with SPECIFIC numbers and context
   - Identify 1 critical weakness with data (compare to rank benchmarks)
   - Provide actionable improvement with measurable goals
   - Use League-specific terminology and insights that show deep understanding

3. **Determine Personality**: Pick ONE that best fits:
   - "Aggressive Playmaker"
   - "Teamfight Specialist"  
   - "Vision Master"
   - "Carry Player"
   - "Consistent Performer"
   - "Strategic Player"

BENCHMARKS (for context):
- {rank_info.get('tier', 'GOLD')} Average KDA: 2.8-3.2
- {rank_info.get('tier', 'GOLD')} Average CS/min: 6.0-6.5
- {rank_info.get('tier', 'GOLD')} Average Vision/min: 0.8-1.2

IMPORTANT: 
- No generic statements or templates
- Every insight must reference specific numbers
- Compare to rank-appropriate benchmarks
- Be encouraging but honest about weaknesses
- Make recommendations measurable and actionable

RESPOND IN EXACT JSON FORMAT:
{{
  "highlights": [
    {{"stat": "descriptive title", "value": "number with unit"}},
    {{"stat": "descriptive title", "value": "number with unit"}},
    {{"stat": "descriptive title", "value": "number with unit"}}
  ],
  "insight": "your 4-5 sentence deep analysis here",
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
