#!/usr/bin/env python3
"""
Demo Prep Script
Pre-warm cache with demo accounts for smooth presentation.
"""
import asyncio
import httpx
import sys
import os
from datetime import datetime

# Demo accounts (high-rank players for impressive stats)
DEMO_ACCOUNTS = [
    ("Hide", "NA1"),
    ("Doublelift", "NA1"),
    ("Yassuo", "NA1"),
    ("TFBlade", "NA1"),
]

API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")

async def warm_cache(game_name: str, tag_line: str):
    """Pre-fetch and cache analysis for demo account."""
    print(f"\n{'='*60}")
    print(f"🔥 Warming cache for {game_name}#{tag_line}")
    print(f"{'='*60}\n")
    
    start_time = datetime.now()
    
    async with httpx.AsyncClient(timeout=600.0) as client:
        try:
            # Step 1: Fetch profile (fast)
            print(f"📋 Step 1/2: Fetching profile...")
            profile_url = f"{API_BASE_URL}/api/profile/{game_name}/{tag_line}"
            profile_response = await client.get(profile_url)
            
            if profile_response.status_code != 200:
                print(f"❌ Profile fetch failed: {profile_response.text}")
                return False
            
            print(f"✅ Profile cached")
            
            # Step 2: Generate full analysis (slow, but caches matches)
            print(f"\n🤖 Step 2/2: Generating analysis (this takes 3-6 minutes)...")
            analysis_url = f"{API_BASE_URL}/api/analysis/{game_name}/{tag_line}?num_matches=100"
            analysis_response = await client.post(analysis_url)
            
            if analysis_response.status_code != 200:
                print(f"❌ Analysis failed: {analysis_response.text}")
                return False
            
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"✅ Analysis cached in {elapsed:.1f}s")
            print(f"\n{'='*60}")
            print(f"🎉 {game_name}#{tag_line} ready for demo!")
            print(f"{'='*60}\n")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

async def main():
    """Warm cache for all demo accounts."""
    print("\n" + "="*60)
    print("🎬 Demo Prep: Warming Cache")
    print("="*60)
    print(f"API: {API_BASE_URL}")
    print(f"Accounts: {len(DEMO_ACCOUNTS)}")
    print("="*60 + "\n")
    
    # Check if backend is alive
    print("🔍 Checking backend health...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            health_response = await client.get(f"{API_BASE_URL}/api/health")
            if health_response.status_code == 200:
                print("✅ Backend is alive!\n")
            else:
                print(f"⚠️ Backend health check returned {health_response.status_code}")
                return
        except Exception as e:
            print(f"❌ Backend is not responding: {e}")
            print(f"Make sure backend is running at {API_BASE_URL}")
            return
    
    # Warm cache sequentially (to avoid rate limits)
    results = []
    for game_name, tag_line in DEMO_ACCOUNTS:
        success = await warm_cache(game_name, tag_line)
        results.append((f"{game_name}#{tag_line}", success))
        
        # Wait between accounts to avoid rate limits
        if success:
            print("⏳ Waiting 30s before next account...\n")
            await asyncio.sleep(30)
    
    # Summary
    print("\n" + "="*60)
    print("📊 Demo Prep Summary")
    print("="*60)
    for account, success in results:
        status = "✅ Ready" if success else "❌ Failed"
        print(f"{status} - {account}")
    print("="*60 + "\n")
    
    successful = sum(1 for _, success in results if success)
    print(f"🎯 {successful}/{len(DEMO_ACCOUNTS)} accounts cached\n")
    
    if successful > 0:
        print("🚀 Demo is ready! These accounts will load instantly:\n")
        for account, success in results:
            if success:
                print(f"   • {account}")
        print()

if __name__ == "__main__":
    # Usage: python demo_prep.py
    # Or: API_URL=https://your-api.onrender.com python demo_prep.py
    asyncio.run(main())
