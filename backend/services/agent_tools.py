"""
Tools that the AI agent can use to analyze player data.
"""
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import httpx
import os
import json
import boto3
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from . import riot_api
from .rate_limiter import rate_limiter
from .bedrock_rate_limiter import bedrock_rate_limiter

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

# Internal LLM for smart tool summarization
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
    print(f"Warning: Could not initialize internal Haiku LLM for agent_tools. Timeline analysis will be disabled. Error: {e}")
    haiku_llm = None

# Queue IDs
RANKED_SOLO = 420
RANKED_FLEX = 440
NORMAL_DRAFT = 400
NORMAL_BLIND = 430

RANKED_QUEUES = [RANKED_SOLO, RANKED_FLEX]
NORMAL_QUEUES = [NORMAL_DRAFT, NORMAL_BLIND]
VALID_QUEUES = RANKED_QUEUES + NORMAL_QUEUES


# ========== SMART MATCH FETCHING ==========

async def fetch_matches_intelligently(
    puuid: str,
    target_matches: int = 50,
    max_age_days: int = 100
) -> Tuple[List[str], Dict[str, Any]]:
    """
    Intelligently fetch match IDs prioritizing ranked matches.
    
    Args:
        puuid: Player's PUUID
        target_matches: Desired number of matches
        max_age_days: Only fetch matches from last N days
    
    Returns:
        Tuple of (match_ids, metadata)
    """
    print("\n🔍 Analyzing player match history...")
    
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    start_time = int(cutoff_date.timestamp())
    
    all_match_ids = []
    start_index = 0
    batch_size = 100
    max_discovery = 300  # Fetch up to 300 IDs to discover patterns
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        while len(all_match_ids) < max_discovery:
            await rate_limiter.wait_if_needed()
            
            url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
            params = {
                "start": start_index,
                "count": batch_size,
                "startTime": start_time
            }
            
            try:
                response = await client.get(url, headers=HEADERS, params=params)
                rate_limiter.record_request()
                
                if response.status_code == 200:
                    batch = response.json()
                    
                    if not batch:
                        print(f"   Reached end of history at {len(all_match_ids)} matches")
                        break
                    
                    all_match_ids.extend(batch)
                    start_index += len(batch)
                    
                    if len(batch) < batch_size:
                        print(f"   Found all {len(all_match_ids)} available matches")
                        break
                        
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 10))
                    print(f"   ⏳ Rate limited, waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    continue
                else:
                    print(f"   ❌ API error {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                break
    
    total_available = len(all_match_ids)
    
    if total_available == 0:
        return [], {"error": "No matches found"}
    
    print(f"   Total matches found: {total_available}")
    
    # Now categorize and select best matches
    selected, metadata = await _select_best_matches(
        all_match_ids=all_match_ids,
        target=target_matches
    )
    
    return selected, metadata


async def _select_best_matches(
    all_match_ids: List[str],
    target: int
) -> Tuple[List[str], Dict[str, Any]]:
    """
    Select best matches to analyze (prioritize ranked).
    
    Args:
        all_match_ids: All available match IDs
        target: How many matches we want
    
    Returns:
        Tuple of (selected_ids, metadata)
    """
    total_available = len(all_match_ids)
    
    # If player has fewer matches than target, use all
    if total_available <= target:
        print(f"   Strategy: Using ALL {total_available} matches\n")
        return all_match_ids, {
            "total_available": total_available,
            "selected": total_available,
            "strategy": "all_available"
        }
    
    # Need to categorize - sample first 50 to understand game types
    print(f"   Strategy: Selecting best {target} from {total_available} matches")
    print(f"   🔍 Categorizing match types (sampling 50)...")
    
    sample_size = min(50, total_available)
    sample_ids = all_match_ids[:sample_size]
    
    ranked_ids = []
    normal_ids = []
    other_ids = []
    
    # Categorize sample in batches
    batch_size = 10
    for i in range(0, len(sample_ids), batch_size):
        batch = sample_ids[i:i + batch_size]
        
        tasks = [_get_match_queue_id(mid) for mid in batch]
        results = await asyncio.gather(*tasks)
        
        for match_id, queue_id in results:
            if queue_id in RANKED_QUEUES:
                ranked_ids.append(match_id)
            elif queue_id in NORMAL_QUEUES:
                normal_ids.append(match_id)
            else:
                other_ids.append(match_id)
    
    ranked_ratio = len(ranked_ids) / sample_size if sample_size > 0 else 0
    normal_ratio = len(normal_ids) / sample_size if sample_size > 0 else 0
    
    print(f"      Found in sample: {len(ranked_ids)} ranked, {len(normal_ids)} normal")
    print(f"      Estimated split: {ranked_ratio*100:.0f}% ranked, {normal_ratio*100:.0f}% normal")
    
    # Select matches based on patterns
    selected = []
    
    if ranked_ratio >= 0.5:
        # Player plays mostly ranked - prioritize ranked
        # Estimate total ranked matches
        estimated_ranked = int(total_available * ranked_ratio)
        
        if estimated_ranked >= target:
            # Enough ranked matches - use only ranked
            print(f"      ✅ Using ranked matches only (~{estimated_ranked} available)")
            
            # Take ranked from sample, then fetch more if needed
            selected.extend(ranked_ids)
            
            # If we need more, continue fetching and filtering
            if len(selected) < target:
                remaining_ids = [mid for mid in all_match_ids if mid not in ranked_ids]
                additional_needed = target - len(selected)
                
                # Fetch more in batches to find ranked
                for i in range(0, min(len(remaining_ids), additional_needed * 2), batch_size):
                    if len(selected) >= target:
                        break
                    
                    batch = remaining_ids[i:i + batch_size]
                    tasks = [_get_match_queue_id(mid) for mid in batch]
                    results = await asyncio.gather(*tasks)
                    
                    for match_id, queue_id in results:
                        if queue_id in RANKED_QUEUES:
                            selected.append(match_id)
                            if len(selected) >= target:
                                break
            
            strategy = "ranked_only"
        else:
            # Not enough ranked - use all ranked + some normal
            print(f"      ✅ Using all ranked + normal matches")
            selected.extend(ranked_ids)
            needed = target - len(selected)
            selected.extend(normal_ids[:needed])
            
            # If still need more, take from unsampled
            if len(selected) < target:
                unsampled = [mid for mid in all_match_ids if mid not in sample_ids]
                selected.extend(unsampled[:target - len(selected)])
            
            strategy = "ranked_priority"
    else:
        # Player plays mostly normal - just take most recent
        print(f"      ✅ Using most recent matches (mixed modes)")
        selected = all_match_ids[:target]
        strategy = "most_recent"
    
    metadata = {
        "total_available": total_available,
        "selected": len(selected),
        "estimated_ranked_ratio": ranked_ratio,
        "strategy": strategy
    }
    
    print(f"      Selected {len(selected)} matches for analysis\n")
    
    return selected, metadata


async def _get_match_queue_id(match_id: str) -> Tuple[str, Optional[int]]:
    """Helper to get queue ID for a match."""
    await rate_limiter.wait_if_needed()
    
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=HEADERS)
            rate_limiter.record_request()
            
            if response.status_code == 200:
                data = response.json()
                return match_id, data['info']['queueId']
    except:
        pass
    
    return match_id, None


# ========== DATA FETCHING ==========

async def get_match_details_batch(match_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch match details in batches with rate limiting.
    
    Args:
        match_ids: List of match IDs
    
    Returns:
        List of match data dicts
    """
    print(f"📥 Fetching details for {len(match_ids)} matches...")
    
    results = []
    total = len(match_ids)
    
    # Process in small batches to respect rate limits
    batch_size = 10
    
    for i in range(0, len(match_ids), batch_size):
        batch = match_ids[i:i + batch_size]
        
        tasks = []
        for match_id in batch:
            tasks.append(_fetch_match_with_retry(match_id))
        
        batch_results = await asyncio.gather(*tasks)
        valid_results = [r for r in batch_results if r is not None]
        results.extend(valid_results)
        
        progress = min((i + batch_size) / total * 100, 100)
        print(f"   Progress: {progress:.0f}% ({len(results)}/{total})", end='\r')
    
    print(f"\n   ✅ Successfully fetched {len(results)}/{total} matches\n")
    
    return results


async def _fetch_match_with_retry(match_id: str) -> Optional[Dict]:
    """Fetch a single match with rate limiting."""
    await rate_limiter.wait_if_needed()
    
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=HEADERS)
            rate_limiter.record_request()
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 5))
                await asyncio.sleep(retry_after)
                # Don't retry to avoid infinite loops
                return None
    except:
        pass
    
    return None


# ========== DATA ANALYSIS ==========

def extract_comprehensive_player_data(match_data: Dict, puuid: str) -> Optional[Dict]:
    """Extract all relevant player stats from match."""
    participants = match_data['info']['participants']
    player = next((p for p in participants if p['puuid'] == puuid), None)
    
    if not player:
        return None
    
    challenges = player.get('challenges', {})
    game_duration = match_data['info']['gameDuration'] / 60  # minutes
    
    return {
        # Basic
        'timestamp': match_data['info']['gameCreation'],
        'champion': player['championName'],
        'role': player['teamPosition'],
        'win': player['win'],
        'game_duration': game_duration,
        'queue_id': match_data['info']['queueId'],
        
        # Combat
        'kills': player['kills'],
        'deaths': player['deaths'],
        'assists': player['assists'],
        'kda': (player['kills'] + player['assists']) / max(player['deaths'], 1),
        'solo_kills': challenges.get('soloKills', 0),
        'double_kills': player['doubleKills'],
        'triple_kills': player['tripleKills'],
        'quadra_kills': player['quadraKills'],
        'penta_kills': player['pentaKills'],
        
        # Damage
        'damage_dealt': player['totalDamageDealtToChampions'],
        'damage_per_min': player['totalDamageDealtToChampions'] / game_duration,
        'damage_taken': player['totalDamageTaken'],
        'team_damage_pct': challenges.get('teamDamagePercentage', 0),
        
        # Economy
        'gold_earned': player['goldEarned'],
        'gold_per_min': challenges.get('goldPerMinute', 0),
        'cs_total': player['totalMinionsKilled'] + player['neutralMinionsKilled'],
        'cs_per_min': (player['totalMinionsKilled'] + player['neutralMinionsKilled']) / game_duration,
        
        # Vision
        'vision_score': player['visionScore'],
        'vision_per_min': challenges.get('visionScorePerMinute', 0),
        'control_wards': challenges.get('controlWardsBought', 0),
        'wards_placed': challenges.get('stealthWardsPlaced', 0),
        'wards_killed': challenges.get('wardTakedowns', 0),
        
        # Objectives
        'turret_kills': player.get('turretTakedowns', 0),
        'damage_to_objectives': player['damageDealtToObjectives'],
    }


def calculate_performance_trends(matches_data: List[Dict], puuid: str) -> Dict[str, Any]:
    """
    Calculate comprehensive performance metrics and trends.
    
    Args:
        matches_data: List of match data
        puuid: Player's PUUID
    
    Returns:
        Dictionary with performance analysis
    """
    player_stats = []
    
    for match in matches_data:
        stats = extract_comprehensive_player_data(match, puuid)
        if stats:
            player_stats.append(stats)
    
    if not player_stats:
        return {"error": "No valid match data"}
    
    df = pd.DataFrame(player_stats)
    df = df.sort_values('timestamp')
    
    total_games = len(df)
    
    # Basic stats
    analysis = {
        'total_games': total_games,
        'overall_win_rate': (df['win'].sum() / total_games * 100),
        
        # Averages
        'avg_kda': df['kda'].mean(),
        'avg_kills': df['kills'].mean(),
        'avg_deaths': df['deaths'].mean(),
        'avg_assists': df['assists'].mean(),
        'avg_cs_per_min': df['cs_per_min'].mean(),
        'avg_vision_per_min': df['vision_per_min'].mean(),
        'avg_damage_per_min': df['damage_per_min'].mean(),
        'avg_gold_per_min': df['gold_per_min'].mean(),
        
        # Totals
        'total_multikills': (
            df['double_kills'].sum() + 
            df['triple_kills'].sum() + 
            df['quadra_kills'].sum() + 
            df['penta_kills'].sum()
        ),
        'total_penta_kills': df['penta_kills'].sum(),
        
        # Best game
        'best_kda': df['kda'].max(),
        'highest_kills': df['kills'].max(),
    }
    
    # Trend analysis (if enough games)
    if total_games >= 40:
        first_half = df.iloc[:total_games//2]
        second_half = df.iloc[total_games//2:]
        
        analysis.update({
            'first_half_wr': (first_half['win'].sum() / len(first_half) * 100),
            'second_half_wr': (second_half['win'].sum() / len(second_half) * 100),
            'kda_improvement': (second_half['kda'].mean() - first_half['kda'].mean()),
            'cs_improvement': (second_half['cs_per_min'].mean() - first_half['cs_per_min'].mean()),
            'vision_improvement': (second_half['vision_per_min'].mean() - first_half['vision_per_min'].mean()),
            'has_trends': True
        })
    else:
        analysis['has_trends'] = False
    
    # Queue distribution
    queue_counts = df['queue_id'].value_counts().to_dict()
    ranked_games = sum(count for qid, count in queue_counts.items() if qid in RANKED_QUEUES)
    
    analysis['ranked_games'] = ranked_games
    analysis['ranked_percentage'] = (ranked_games / total_games * 100)
    
    return analysis


def analyze_champion_pool(matches_data: List[Dict], puuid: str) -> Dict[str, Any]:
    """Analyze champion preferences and performance."""
    champion_stats = {}
    role_stats = {}
    
    for match in matches_data:
        player_data = extract_comprehensive_player_data(match, puuid)
        if not player_data:
            continue
        
        champ = player_data['champion']
        role = player_data['role']
        win = player_data['win']
        kda = player_data['kda']
        
        # Champion stats
        if champ not in champion_stats:
            champion_stats[champ] = {
                'games': 0,
                'wins': 0,
                'total_kda': 0,
                'roles': []
            }
        
        champion_stats[champ]['games'] += 1
        champion_stats[champ]['wins'] += 1 if win else 0
        champion_stats[champ]['total_kda'] += kda
        champion_stats[champ]['roles'].append(role)
        
        # Role stats
        if role and role != 'NONE':
            if role not in role_stats:
                role_stats[role] = {'games': 0, 'wins': 0}
            role_stats[role]['games'] += 1
            role_stats[role]['wins'] += 1 if win else 0
    
    # Calculate final stats
    for champ, stats in champion_stats.items():
        stats['win_rate'] = (stats['wins'] / stats['games'] * 100) if stats['games'] > 0 else 0
        stats['avg_kda'] = stats['total_kda'] / stats['games'] if stats['games'] > 0 else 0
        stats['primary_role'] = max(set(stats['roles']), key=stats['roles'].count) if stats['roles'] else 'UNKNOWN'
    
    # Sort and format
    top_champions = sorted(
        champion_stats.items(),
        key=lambda x: x[1]['games'],
        reverse=True
    )[:10]
    
    # Role distribution
    for role, stats in role_stats.items():
        stats['win_rate'] = (stats['wins'] / stats['games'] * 100) if stats['games'] > 0 else 0
    
    primary_role = max(role_stats.items(), key=lambda x: x[1]['games'])[0] if role_stats else 'UNKNOWN'
    
    return {
        'total_unique_champions': len(champion_stats),
        'top_champions': [
            {
                'name': champ,
                'games': stats['games'],
                'win_rate': stats['win_rate'],
                'avg_kda': stats['avg_kda'],
                'primary_role': stats['primary_role']
            }
            for champ, stats in top_champions
        ],
        'role_distribution': role_stats,
        'primary_role': primary_role,
    }


def identify_playstyle_personality(matches_data: List[Dict], puuid: str) -> Dict[str, Any]:
    """Determine player's unique playstyle personality."""
    all_stats = []
    
    for match in matches_data:
        player_data = extract_comprehensive_player_data(match, puuid)
        if player_data:
            all_stats.append(player_data)
    
    if not all_stats:
        return {"error": "No data"}
    
    df = pd.DataFrame(all_stats)
    
    # Calculate personality scores
    avg_solo_kills = df['solo_kills'].mean()
    avg_team_damage = df['team_damage_pct'].mean()
    avg_vision = df['vision_per_min'].mean()
    avg_multikills = (df['double_kills'] + df['triple_kills'] + df['quadra_kills'] + df['penta_kills']).mean()
    overall_kda = df['kda'].mean()
    
    personality = {
        'aggression_score': min(100, avg_solo_kills * 20),
        'carry_potential': min(100, avg_team_damage * 2),
        'vision_mastery': min(100, avg_vision * 15),
        'teamfight_prowess': min(100, avg_multikills * 25),
        'overall_kda': overall_kda,
    }
    
    # Determine primary personality
    if personality['aggression_score'] > 60:
        primary_trait = "Duelist"
        description = "You thrive in 1v1 outplays and mechanical skill"
    elif personality['carry_potential'] > 70:
        primary_trait = "Carry"
        description = "You consistently deal massive damage for your team"
    elif personality['vision_mastery'] > 70:
        primary_trait = "Vision Master"
        description = "Your map awareness and vision control are exceptional"
    elif personality['teamfight_prowess'] > 60:
        primary_trait = "Teamfight Monster"
        description = "You excel in coordinated 5v5 engagements"
    elif overall_kda > 4:
        primary_trait = "Consistent Performer"
        description = "Reliable and steady across all games"
    else:
        primary_trait = "Adaptive Player"
        description = "Flexible playstyle that adjusts to team needs"
    
    return {
        'primary_trait': primary_trait,
        'description': description,
        'scores': personality,
        'notable_stats': {
            'avg_solo_kills': avg_solo_kills,
            'avg_team_damage_pct': avg_team_damage,
            'avg_vision_per_min': avg_vision,
            'total_multikills': df['double_kills'].sum() + df['triple_kills'].sum() + df['quadra_kills'].sum() + df['penta_kills'].sum()
        }
    }


async def get_timeline_analysis_for_match(
    match_id: str,
    puuid: str,
    player_champion: str,
    context_reason: str
) -> Optional[str]:
    """
    Analyzes a single match timeline for a player using an internal, fast LLM (Haiku).
    This function now pre-processes the timeline to create a summarized log of events
    to avoid exceeding the LLM's context window.
    """
    if not haiku_llm:
        print("Timeline analysis tool disabled: internal LLM not initialized.")
        return None

    print(f"   [Deep Dive] Analyzing timeline for match {match_id} ({context_reason})...")

    try:
        timeline = await riot_api.get_match_timeline(match_id)
        if not timeline or "info" not in timeline or "frames" not in timeline:
            print(f"   [Deep Dive] Could not retrieve a valid timeline for match {match_id}")
            return f"Could not retrieve a valid timeline for match {match_id}."

        # Find the participantId for the given puuid
        participant_id = -1
        for p in timeline["info"]["participants"]:
            if p["puuid"] == puuid:
                participant_id = p["participantId"]
                break
        
        if participant_id == -1:
            print(f"   [Deep Dive] Could not find participant with puuid {puuid} in match {match_id}")
            return f"Could not find participant with puuid {puuid} in match {match_id}."

        # Pre-process the timeline to create a summarized event log
        event_log = _create_player_event_log(timeline, participant_id)
        
        if not event_log:
            print(f"   [Deep Dive] No significant events found for this player in {match_id}")
            return "No significant events found for this player in the match."

        prompt = f"""
You are a League of Legends analyst. Given the following summarized event log for a player playing {player_champion} in a single match (analyzed as a '{context_reason}' game), provide a concise (2-4 sentences) narrative summary of their performance and game progression. Focus on their key moments and overall impact that explain why this game fits the context.

Event Log:
{event_log}

Narrative Summary:
"""
        await bedrock_rate_limiter.wait_if_needed(is_retry=False)
        response = await haiku_llm.ainvoke(prompt)
        bedrock_rate_limiter.record_request(success=True)
        
        analysis_text = response.content
        print(f"   [Deep Dive] Insight found: {analysis_text[:100]}...")
        return analysis_text

    except Exception as e:
        print(f"   [Deep Dive] Internal LLM failed for {match_id}: {e}")
        bedrock_rate_limiter.record_request(success=False)
        return f"AI analysis failed for match {match_id}."


def _create_player_event_log(timeline: Dict[str, Any], participant_id: int) -> str:
    """
    Parses a raw match timeline and creates a simplified, human-readable log of events
    for a specific participant. This reduces the token count for the LLM.
    """
    event_log = []
    
    # Get champion names for all participants for richer logs
    participant_champions = {p['participantId']: p.get('championName', 'Unknown') for p in timeline['info']['participants']}

    for frame in timeline['info']['frames']:
        for event in frame['events']:
            timestamp_min = int(event['timestamp'] / 60000)
            
            # ITEM AND SKILL EVENTS (Simplified)
            if event.get('participantId') == participant_id:
                if event['type'] == 'SKILL_LEVEL_UP' and event['levelUpType'] == 'NORMAL':
                    skill_map = {1: 'Q', 2: 'W', 3: 'E', 4: 'R'}
                    event_log.append(f"[{timestamp_min}m] Leveled up {skill_map.get(event['skillSlot'], 'Skill')}")
                elif event['type'] == 'ITEM_PURCHASED':
                    event_log.append(f"[{timestamp_min}m] Purchased an item.")

            # KILLS, DEATHS, ASSISTS
            if event['type'] == 'CHAMPION_KILL':
                killer_id = event.get('killerId', 0)
                victim_id = event['victimId']
                
                assisting_ids = event.get('assistingParticipantIds', [])
                
                if killer_id == participant_id:
                    victim_champ = participant_champions.get(victim_id, 'Unknown')
                    event_log.append(f"[{timestamp_min}m] KILLED {victim_champ}")
                elif victim_id == participant_id:
                    killer_champ = participant_champions.get(killer_id, 'Unknown')
                    event_log.append(f"[{timestamp_min}m] DIED to {killer_champ}")
                elif participant_id in assisting_ids:
                    victim_champ = participant_champions.get(victim_id, 'Unknown')
                    event_log.append(f"[{timestamp_min}m] ASSISTED in killing {victim_champ}")

            # OBJECTIVE EVENTS
            if event['type'] in ['ELITE_MONSTER_KILL', 'BUILDING_KILL']:
                killer_id = event.get('killerId', 0)
                assisting_ids = event.get('assistingParticipantIds', [])
                if killer_id == participant_id or participant_id in assisting_ids:
                    if event['type'] == 'ELITE_MONSTER_KILL':
                        monster_type = event.get('monsterType', 'Monster').replace('_', ' ')
                        event_log.append(f"[{timestamp_min}m] Helped take {monster_type}")
                    elif event['type'] == 'BUILDING_KILL':
                        building_type = event.get('buildingType', 'Building').replace('_', ' ').title()
                        lane = event.get('laneType', '').replace('_LANE', '')
                        event_log.append(f"[{timestamp_min}m] Helped destroy a {lane} {building_type}")

    # To keep the log concise, remove duplicate consecutive messages
    if not event_log:
        return ""
        
    deduplicated_log = [event_log[0]]
    for i in range(1, len(event_log)):
        # Only add if it's different from the last message
        if event_log[i] != event_log[i-1]:
            deduplicated_log.append(event_log[i])
            
    return "\n".join(deduplicated_log)