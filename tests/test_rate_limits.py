#!/usr/bin/env python3
"""
Test script to find your actual Riot API rate limits.
"""
import asyncio
import httpx
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load .env from backend directory
load_dotenv('backend/.env')
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

# Test endpoint (lightweight)
TEST_URL = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Faker/KR1"


async def test_burst_requests(requests_per_second: int, duration_seconds: int = 5):
    """
    Test burst requests to find the actual per-second limit.
    """
    print(f"\n🧪 Testing {requests_per_second} requests per second for {duration_seconds} seconds...")
    
    successful_requests = 0
    rate_limited_requests = 0
    errors = 0
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        start_time = time.time()
        
        for second in range(duration_seconds):
            second_start = time.time()
            
            # Send requests for this second
            tasks = []
            for i in range(requests_per_second):
                tasks.append(make_request(client))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count results
            for result in results:
                if isinstance(result, Exception):
                    errors += 1
                elif result == 200:
                    successful_requests += 1
                elif result == 429:
                    rate_limited_requests += 1
                else:
                    errors += 1
            
            # Wait for the rest of the second
            elapsed = time.time() - second_start
            if elapsed < 1.0:
                await asyncio.sleep(1.0 - elapsed)
            
            print(f"   Second {second + 1}: {successful_requests} success, {rate_limited_requests} rate limited, {errors} errors")
    
    total_time = time.time() - start_time
    
    print(f"\n📊 Results after {total_time:.1f} seconds:")
    print(f"   ✅ Successful: {successful_requests}")
    print(f"   ⚠️  Rate limited: {rate_limited_requests}")
    print(f"   ❌ Errors: {errors}")
    print(f"   📈 Effective rate: {successful_requests / total_time:.1f} req/s")
    
    return successful_requests, rate_limited_requests, errors


async def make_request(client):
    """Make a single API request."""
    try:
        response = await client.get(TEST_URL, headers=HEADERS)
        return response.status_code
    except Exception:
        return "error"


async def test_sustained_requests(target_rate: int, duration_minutes: int = 2):
    """
    Test sustained requests to find the 2-minute limit.
    """
    print(f"\n🧪 Testing sustained {target_rate} req/s for {duration_minutes} minutes...")
    
    successful_requests = 0
    rate_limited_requests = 0
    errors = 0
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        request_interval = 1.0 / target_rate  # Time between requests
        next_request_time = start_time
        
        while time.time() < end_time:
            current_time = time.time()
            
            if current_time >= next_request_time:
                # Make request
                result = await make_request(client)
                
                if result == 200:
                    successful_requests += 1
                elif result == 429:
                    rate_limited_requests += 1
                    print(f"   ⚠️  Rate limited at {successful_requests} requests ({(current_time - start_time):.1f}s)")
                else:
                    errors += 1
                
                next_request_time = current_time + request_interval
                
                # Progress update every 10 seconds
                if successful_requests % (target_rate * 10) == 0:
                    elapsed = current_time - start_time
                    print(f"   Progress: {successful_requests} requests in {elapsed:.1f}s ({successful_requests/elapsed:.1f} req/s)")
            else:
                # Small sleep to avoid busy waiting
                await asyncio.sleep(0.01)
    
    total_time = time.time() - start_time
    
    print(f"\n📊 Sustained test results:")
    print(f"   ✅ Successful: {successful_requests}")
    print(f"   ⚠️  Rate limited: {rate_limited_requests}")
    print(f"   ❌ Errors: {errors}")
    print(f"   📈 Average rate: {successful_requests / total_time:.1f} req/s")
    print(f"   📊 Total in 2min window: {successful_requests}")
    
    return successful_requests, rate_limited_requests, errors


async def find_optimal_limits():
    """
    Find your actual API limits by testing progressively.
    """
    global RIOT_API_KEY
    
    print("🚀 Finding your actual Riot API rate limits...")
    print("=" * 60)
    
    if not RIOT_API_KEY:
        print("❌ No RIOT_API_KEY found in environment variables!")
        print("💡 Make sure your .env file is in the backend/ directory")
        print("💡 And contains: RIOT_API_KEY=your_key_here")
        
        # Try to load from backend/.env directly
        try:
            with open('backend/.env', 'r') as f:
                content = f.read()
                if 'RIOT_API_KEY' in content:
                    print("✅ Found RIOT_API_KEY in backend/.env file")
                    for line in content.split('\n'):
                        if line.startswith('RIOT_API_KEY='):
                            key = line.split('=', 1)[1].strip()
                            print(f"🔑 Found key: {key[:8]}...")
                            RIOT_API_KEY = key
                            break
                else:
                    print("❌ No RIOT_API_KEY found in backend/.env file")
        except FileNotFoundError:
            print("❌ backend/.env file not found!")
        
        if not RIOT_API_KEY:
            return
    
    print(f"🔑 Using API key: {RIOT_API_KEY[:8]}...")
    
    # Test per-second limits
    print("\n📈 TESTING PER-SECOND LIMITS")
    print("=" * 40)
    
    for rate in [20, 30, 40, 50]:
        success, rate_limited, errors = await test_burst_requests(rate, 3)
        
        if rate_limited > 0:
            print(f"❌ {rate} req/s: Hit rate limit")
            optimal_per_second = rate - 10
            break
        elif errors > success:
            print(f"❌ {rate} req/s: Too many errors")
            optimal_per_second = rate - 10
            break
        else:
            print(f"✅ {rate} req/s: Success!")
            optimal_per_second = rate
    
    # Test 2-minute limits
    print(f"\n📈 TESTING 2-MINUTE LIMITS (using {optimal_per_second} req/s)")
    print("=" * 40)
    
    success, rate_limited, errors = await test_sustained_requests(optimal_per_second, 2)
    
    if rate_limited > 0:
        optimal_per_2min = success
        print(f"⚠️  Hit 2-minute limit at {success} requests")
    else:
        optimal_per_2min = success
        print(f"✅ Completed {success} requests without hitting 2-minute limit")
    
    # Recommendations
    print(f"\n🎯 RECOMMENDED SETTINGS")
    print("=" * 40)
    print(f"requests_per_second = {max(optimal_per_second - 2, 20)}  # Conservative")
    print(f"requests_per_2min = {max(optimal_per_2min - 10, 100)}    # Conservative")
    
    print(f"\n📝 Update your rate_limiter.py:")
    print(f"rate_limiter = RateLimiter(")
    print(f"    requests_per_second={max(optimal_per_second - 2, 20)},")
    print(f"    requests_per_2min={max(optimal_per_2min - 10, 100)}")
    print(f")")


async def main():
    """Run rate limit tests."""
    print("⚠️  WARNING: This will make many API requests!")
    print("⚠️  Only run this if you want to test your rate limits.")
    print("⚠️  Make sure you have a valid RIOT_API_KEY in your .env file.")
    
    user_input = input("\nProceed with rate limit testing? (y/N): ")
    
    if user_input.lower() in ['y', 'yes']:
        await find_optimal_limits()
    else:
        print("⏭️  Skipping rate limit tests")
        print("\n💡 Manual rate limit increases you can try:")
        print("   Personal Key (safe): 30/s, 200/2min")
        print("   Personal Key (aggressive): 50/s, 300/2min")
        print("   Production Key: 500/s, 30000/10min")


if __name__ == "__main__":
    asyncio.run(main())