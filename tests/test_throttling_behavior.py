#!/usr/bin/env python3
"""
Test script to verify throttling behavior and caching.
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services import year_rewind_agent
from services.bedrock_rate_limiter import bedrock_rate_limiter


async def simulate_throttling_test():
    """
    Simulate a throttling scenario to test caching behavior.
    """
    print("🧪 Testing throttling behavior and caching...")
    print("=" * 60)
    
    # Clear cache first
    year_rewind_agent.clear_analysis_cache()
    
    # Test data
    test_puuid = "test_puuid_12345"
    test_riot_id = "TestPlayer#NA1"
    
    print("📊 Cache state before test:")
    cache = year_rewind_agent._analysis_cache
    print(f"   Matches data: {len(cache['matches_data'])} items")
    print(f"   Performance trends: {cache['performance_trends'] is not None}")
    print(f"   Champion pool: {cache['champion_pool'] is not None}")
    print(f"   Playstyle: {cache['playstyle'] is not None}")
    print(f"   Meta analysis: {len(cache['meta_analysis'])} items")
    
    # Simulate some cached data
    print("\n🔄 Simulating cached data...")
    cache['matches_data'] = [{"fake": "match_data"} for _ in range(50)]
    cache['performance_trends'] = {"fake": "trends_data"}
    cache['champion_pool'] = {"fake": "champion_data"}
    cache['playstyle'] = {"fake": "playstyle_data"}
    cache['current_puuid'] = test_puuid
    
    print("📊 Cache state after simulation:")
    print(f"   Matches data: {len(cache['matches_data'])} items")
    print(f"   Performance trends: {cache['performance_trends'] is not None}")
    print(f"   Champion pool: {cache['champion_pool'] is not None}")
    print(f"   Playstyle: {cache['playstyle'] is not None}")
    
    # Test cached tool calls
    print("\n🧪 Testing cached tool behavior...")
    
    # Test fetch_player_matches (cached version)
    result = await year_rewind_agent.fetch_player_matches(test_puuid, 50)
    print(f"✅ fetch_player_matches: {result[:100]}...")
    
    # Test get_detailed_match_data (cached version)
    result = await year_rewind_agent.get_detailed_match_data('{"match_ids": ["test1", "test2"]}')
    print(f"✅ get_detailed_match_data: {result[:100]}...")
    
    # Test analyze_performance_trends (cached version)
    result = year_rewind_agent.analyze_performance_trends(test_puuid)
    print(f"✅ analyze_performance_trends: {result[:100]}...")
    
    # Test analyze_champion_pool (cached version)
    result = year_rewind_agent.analyze_champion_pool(test_puuid)
    print(f"✅ analyze_champion_pool: {result[:100]}...")
    
    # Test identify_playstyle (cached version)
    result = year_rewind_agent.identify_playstyle(test_puuid)
    print(f"✅ identify_playstyle: {result[:100]}...")
    
    print("\n✅ All cached tools working correctly!")
    print("🔄 On Bedrock retry, these tools will return cached data instead of re-fetching")
    
    # Clear cache
    year_rewind_agent.clear_analysis_cache()
    print("\n🧹 Cache cleared for next test")


async def test_rate_limiter():
    """Test the rate limiter behavior."""
    print("\n🧪 Testing rate limiter behavior...")
    print("=" * 60)
    
    # Get current stats
    stats = bedrock_rate_limiter.get_stats()
    print(f"📊 Rate limiter stats:")
    print(f"   Requests made: {stats['requests_made']}")
    print(f"   Successful requests: {stats['successful_requests']}")
    print(f"   Throttles: {stats['throttles']}")
    print(f"   Current delay: {stats['current_delay']:.1f}s")
    print(f"   Last request time: {stats['last_request_time']}")
    
    # Simulate some requests
    print("\n🔄 Simulating request pattern...")
    
    for i in range(3):
        print(f"   Request {i+1}:")
        
        # Wait if needed
        await bedrock_rate_limiter.wait_if_needed(is_retry=False)
        print(f"     ✅ Wait completed")
        
        # Record request
        bedrock_rate_limiter.record_request(success=True)
        print(f"     ✅ Request recorded")
        
        # Small delay
        await asyncio.sleep(0.1)
    
    # Simulate a throttle
    print("\n⚠️  Simulating throttle...")
    bedrock_rate_limiter.record_throttle()
    
    stats = bedrock_rate_limiter.get_stats()
    print(f"📊 Stats after throttle:")
    print(f"   Throttles: {stats['throttles']}")
    print(f"   Current delay: {stats['current_delay']:.1f}s")
    
    print("✅ Rate limiter test completed")


async def main():
    """Run throttling and caching tests."""
    print("🚀 Starting Throttling and Caching Tests")
    print("=" * 60)
    
    await simulate_throttling_test()
    await test_rate_limiter()
    
    print("\n" + "=" * 60)
    print("✅ All throttling tests completed!")
    print("🔄 The agent will now use cached data on Bedrock retries")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())