"""
LangChain agent for generating Year-End Reviews.
"""
from typing import Dict, Any
import boto3
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_aws import ChatBedrock
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
import json
import os
import asyncio
import time
from botocore.exceptions import ClientError

from . import agent_tools
from .bedrock_rate_limiter import bedrock_rate_limiter


bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
)

# Initialize Bedrock LLM with minimal retries (we handle retries ourselves)
llm = ChatBedrock(
    client=bedrock_client,
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    model_kwargs={
        "temperature": 0.7,
        "max_tokens": 4000
    },
    region_name=os.getenv('AWS_REGION', 'us-west-2')
)


async def invoke_llm_with_rate_limit(agent_executor, input_dict: Dict, max_retries: int = 5) -> Dict[str, Any]:
    """
    Invoke the LLM with rate limiting and exponential backoff for throttling.
    
    Args:
        agent_executor: The LangChain agent executor
        input_dict: Input dictionary for the agent
        max_retries: Maximum number of retry attempts
    
    Returns:
        Agent execution result
    
    Raises:
        Exception: If all retries are exhausted
    """
    for attempt in range(max_retries):
        try:
            # Wait based on rate limiter
            is_retry = attempt > 0
            await bedrock_rate_limiter.wait_if_needed(is_retry=is_retry)
            
            # Record the request attempt
            bedrock_rate_limiter.record_request(success=False)
            
            # Invoke the agent
            result = await agent_executor.ainvoke(input_dict)
            
            # Success! Record it and return
            bedrock_rate_limiter.record_request(success=True)
            return result
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            
            # Check if it's a throttling error
            if error_code in ['ThrottlingException', 'TooManyRequestsException']:
                bedrock_rate_limiter.record_throttle()
                
                if attempt < max_retries - 1:
                    print(f"⚠️  Bedrock throttled (attempt {attempt + 1}/{max_retries}), retrying with backoff...")
                    # The next wait_if_needed call will handle the backoff
                    continue
                else:
                    print(f"❌ Bedrock throttled after {max_retries} attempts, giving up")
                    raise
            else:
                # Not a throttling error, re-raise
                print(f"❌ Bedrock error: {error_code} - {e}")
                raise
                
        except Exception as e:
            # Check if the error message contains throttling keywords
            error_str = str(e).lower()
            if 'throttl' in error_str or 'too many requests' in error_str or 'rate limit' in error_str:
                bedrock_rate_limiter.record_throttle()
                
                if attempt < max_retries - 1:
                    print(f"⚠️  Bedrock throttled (attempt {attempt + 1}/{max_retries}), retrying with backoff...")
                    continue
                else:
                    print(f"❌ Bedrock throttled after {max_retries} attempts, giving up")
                    raise
            else:
                # Not a throttling error, re-raise
                print(f"❌ Unexpected error: {e}")
                raise
    
    raise Exception(f"Failed to invoke Bedrock after {max_retries} attempts")

# Global state for current analysis
_current_matches_data = []
_current_puuid = None

# ========== AGENT TOOLS ==========

@tool
async def fetch_player_matches(puuid: str, target_count: int = 50) -> str:
    """
    Fetch match IDs for a player. Always call this FIRST.
    
    This automatically:
    - Prioritizes ranked matches for competitive players
    - Adapts to players with few or many matches
    - Focuses on last year's matches only
    
    Args:
        puuid: Player's PUUID
        target_count: Desired number of matches (default 50)
    
    Returns:
        JSON string with match IDs and metadata
    """
    match_ids, metadata = await agent_tools.fetch_matches_intelligently(
        puuid=puuid,
        target_matches=target_count,
        max_age_days=365
    )
    
    return json.dumps({
        "match_ids": match_ids,
        "count": len(match_ids),
        "metadata": metadata,
        "status": "success" if match_ids else "no_matches_found"
    })


@tool
async def get_detailed_match_data(match_ids_json: str) -> str:
    """
    Fetch detailed data for matches. Call this AFTER fetching match IDs.
    
    This fetches full match details and stores them for analysis.
    Rate limited to 100 req/2min, so this may take a few minutes.
    
    Args:
        match_ids_json: JSON string or list containing match IDs
    
    Returns:
        JSON string confirming data was fetched
    """
    global _current_matches_data
    
    try:
        # Handle both string JSON and direct list input
        if isinstance(match_ids_json, str):
            # Try to parse as JSON
            try:
                data = json.loads(match_ids_json)
            except json.JSONDecodeError:
                # If it fails, assume it's already been parsed or is malformed
                return json.dumps({
                    "status": "error", 
                    "message": f"Invalid JSON format: {match_ids_json[:100]}"
                })
        else:
            data = match_ids_json
        
        # Extract match IDs from various formats
        if isinstance(data, dict):
            match_ids = data.get('match_ids', [])
        elif isinstance(data, list):
            match_ids = data
        else:
            return json.dumps({
                "status": "error",
                "message": f"Unexpected data type: {type(data)}"
            })
        
        if not match_ids:
            return json.dumps({
                "status": "error",
                "message": "No match IDs provided"
            })
        
        print(f"\n📥 Fetching details for {len(match_ids)} matches...")
        
        # Fetch all match details
        matches = await agent_tools.get_match_details_batch(match_ids)
        _current_matches_data = matches
        
        return json.dumps({
            "status": "success",
            "matches_fetched": len(matches),
            "message": f"Successfully loaded {len(matches)} matches for analysis"
        })
        
    except Exception as e:
        print(f"❌ Error in get_detailed_match_data: {e}")
        import traceback
        traceback.print_exc()
        return json.dumps({
            "status": "error",
            "message": f"Error processing match data: {str(e)}"
        })


@tool
def analyze_performance_trends(puuid: str) -> str:
    """
    Analyze performance trends over time (KDA, CS, vision, win rate improvements).
    
    Call this to identify if the player is improving or declining.
    
    Args:
        puuid: Player's PUUID
    
    Returns:
        JSON string with comprehensive trend analysis
    """
    global _current_matches_data
    
    if not _current_matches_data:
        return json.dumps({"error": "No match data loaded. Call get_detailed_match_data first."})
    
    trends = agent_tools.calculate_performance_trends(_current_matches_data, puuid)
    return json.dumps(trends, default=str)


@tool
def analyze_champion_pool(puuid: str) -> str:
    """
    Analyze champion preferences, win rates, and role distribution.
    
    Call this to understand what champions they play and how well.
    
    Args:
        puuid: Player's PUUID
    
    Returns:
        JSON string with champion pool analysis
    """
    global _current_matches_data
    
    if not _current_matches_data:
        return json.dumps({"error": "No match data loaded. Call get_detailed_match_data first."})
    
    champion_data = agent_tools.analyze_champion_pool(_current_matches_data, puuid)
    return json.dumps(champion_data, default=str)


@tool
def identify_playstyle(puuid: str) -> str:
    """
    Determine the player's unique playstyle personality.
    
    Returns a personality type like "Duelist", "Carry", "Vision Master", etc.
    
    Args:
        puuid: Player's PUUID
    
    Returns:
        JSON string with playstyle personality profile
    """
    global _current_matches_data
    
    if not _current_matches_data:
        return json.dumps({"error": "No match data loaded. Call get_detailed_match_data first."})
    
    playstyle = agent_tools.identify_playstyle_personality(_current_matches_data, puuid)
    return json.dumps(playstyle, default=str)


# ========== AGENT SETUP ==========

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert League of Legends analyst creating personalized Year-End Reviews.

**Your Analysis Process:**
1. ALWAYS start by calling fetch_player_matches to get match IDs
2. Then call get_detailed_match_data to load full match details
3. Call analyze_performance_trends to see improvement patterns
4. Call analyze_champion_pool to understand their champion mastery
5. Call identify_playstyle to determine their unique personality
6. Synthesize all findings into an engaging year-end review

**Important Guidelines:**
- Adapt to sample size: <50 games = general advice, 50-200 = trends, 200+ = deep patterns
- Prioritize ranked matches for competitive insights
- Be encouraging but honest about areas for improvement
- Use gaming and league of legends specific terminology as required
- Structure the review like Spotify Wrapped - fun and shareable
- Include specific numbers and percentages to make it concrete
- Highlight unique achievements (pentakills, high KDAs, improvement streaks)

**Review Structure:**
1. **Playstyle Personality** - Their unique identity
2. **Year in Numbers** - Key stats and totals
3. **Performance Trends** - Are they improving?
4. **Champion Mastery** - Top picks and win rates
5. **Standout Moments** - Best games and achievements
6. **Growth Areas** - 2-3 very specific tips for improvement (e.g itemization, matchup specifics, macro play, etc.)

Make it engaging, data-driven, and personal!"""),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create the agent
tools = [
    fetch_player_matches,
    get_detailed_match_data,
    analyze_performance_trends,
    analyze_champion_pool,
    identify_playstyle
]

agent = create_tool_calling_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=10,
    handle_parsing_errors=True
)

# ========== PUBLIC API ==========

async def generate_year_rewind(puuid: str, riot_id: str) -> Dict[str, Any]:
    """
    Generate a complete year-end review using the agent.
    
    Args:
        puuid: Player's PUUID
        riot_id: Player's Riot ID (for display)
    
    Returns:
        Complete year-end review
    """
    global _current_matches_data, _current_puuid
    
    try:
        # Reset state
        _current_matches_data = []
        _current_puuid = puuid
        
        print(f"\n{'='*60}")
        print(f"🎮 Generating Year Rewind for {riot_id}")
        print(f"{'='*60}\n")
        
        # Run the agent with rate limiting
        result = await invoke_llm_with_rate_limit(
            agent_executor,
            {
                "input": f"""Create a comprehensive Year-End Review for player {riot_id} (PUUID: {puuid}).

Follow the analysis process step by step:
1. Fetch their match history
2. Load detailed match data
3. Analyze performance trends
4. Examine champion pool
5. Identify playstyle personality
6. Create an engaging, personalized review

Focus on ranked matches when available. Make it fun and motivational!"""
            }
        )
        
        print(f"\n{'='*60}")
        print(f"✅ Year Rewind Complete!")
        print(f"{'='*60}\n")
        
        # Extract review text from result
        review_text = result.get('output', '')
        
        # Handle various LangChain response formats
        if isinstance(review_text, dict):
            review_text = review_text.get('text', str(review_text))
        elif isinstance(review_text, list):
            # If it's a list of message objects, extract text from each
            text_parts = []
            for item in review_text:
                if isinstance(item, dict):
                    text_parts.append(item.get('text', str(item)))
                else:
                    text_parts.append(str(item))
            review_text = '\n'.join(text_parts)
        elif not isinstance(review_text, str):
            review_text = str(review_text)
        
        return {
            "success": True,
            "review": review_text,
            "puuid": puuid,
            "riot_id": riot_id,
            "matches_analyzed": len(_current_matches_data)
        }
        
    except Exception as e:
        print(f"\n❌ Error generating rewind: {e}\n")
        return {
            "success": False,
            "error": str(e)
        }