#!/usr/bin/env python3
"""
Test script for the year rewind agent with retry-safe caching.
"""
import asyncio
import httpx
import json
import time
from datetime import datetime

# Test configuration
TEST_PLAYERS = [
    # Add your own Riot ID here for testing
    # {"game_name": "YourName", "tag_line": "NA1"},
    #{"game_name": "i will int", "tag_line": "akali"},
    {"game_name": "kinuryu ", "tag_line": "amphy"}

]

BASE_URL = "http://127.0.0.1:8000"


async def test_basic_endpoint():
    """Test the basic player lookup endpoint."""
    print("🧪 Testing basic player endpoint...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for player in TEST_PLAYERS:
            try:
                url = f"{BASE_URL}/api/player/{player['game_name']}/{player['tag_line']}"
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {player['game_name']}#{player['tag_line']}: {data['puuid'][:8]}...")
                else:
                    print(f"❌ {player['game_name']}#{player['tag_line']}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {player['game_name']}#{player['tag_line']}: {e}")


async def test_year_rewind_agent():
    """Test the year rewind agent with retry-safe caching."""
    print("\n🧪 Testing year rewind agent...")
    
    player = TEST_PLAYERS[0]  # Use first player
    
    async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minute timeout
        try:
            url = f"{BASE_URL}/api/year-rewind/{player['game_name']}/{player['tag_line']}"
            
            print(f"📡 Calling: {url}")
            start_time = time.time()
            
            response = await client.post(url)
            
            elapsed = time.time() - start_time
            print(f"⏱️  Request took: {elapsed:.1f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Year rewind agent success!")
                print(f"   Matches analyzed: {data.get('matches_analyzed', 'unknown')}")
                print(f"   Review length: {len(data.get('review', ''))} characters")
                
                # Save the review to a file for inspection
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"year_review_{player['game_name']}_{timestamp}.txt"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Year Rewind for {player['game_name']}#{player['tag_line']}\n")
                    f.write(f"Generated at: {datetime.now()}\n")
                    f.write("="*60 + "\n\n")
                    f.write(data.get('review', ''))
                
                print(f"📄 Review saved to: {filename}")
                
            else:
                print(f"❌ Year rewind agent failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Year rewind agent error: {e}")


async def test_health_check():
    """Test the health check endpoint."""
    print("\n🧪 Testing health check...")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/api/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed")
                print(f"   Status: {data.get('status')}")
                
                rate_limiter = data.get('rate_limiter', {})
                print(f"   Rate limiter stats:")
                print(f"     Requests made: {rate_limiter.get('requests_made', 0)}")
                print(f"     Throttles: {rate_limiter.get('throttles', 0)}")
                print(f"     Current delay: {rate_limiter.get('current_delay', 0):.1f}s")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Health check error: {e}")


async def main():
    """Run all tests."""
    print("🚀 Starting Rift Rewind Agent Tests")
    print("=" * 60)
    
    # Test basic functionality first
    await test_health_check()
    await test_basic_endpoint()
    
    # Test agent (comment out if you don't want to use Bedrock credits)
    print("\n" + "=" * 60)
    print("🤖 AGENT TEST (Uses Bedrock - costs money!)")
    print("=" * 60)
    
    user_input = input("\nRun agent test? This will use AWS Bedrock credits. (y/N): ")
    
    if user_input.lower() in ['y', 'yes']:
        # Test the year rewind agent
        await test_year_rewind_agent()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
    else:
        print("⏭️  Skipping agent test")


if __name__ == "__main__":
    asyncio.run(main())