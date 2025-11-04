"""
Test script for structured analysis service with real data.
Tests accurate champion stats and AI-generated insights with Claude Sonnet 4.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from services.structured_analysis_service import generate_structured_analysis


async def test_structured_analysis():
    """Test structured analysis with real player data."""
    
    print("\n" + "="*70)
    print("🧪 TESTING STRUCTURED ANALYSIS SERVICE")
    print("="*70)
    
    # Test with your account
    game_name = "i will int"
    tag_line = "akali"
    
    print(f"\n📊 Testing with: {game_name}#{tag_line}")
    print(f"   This should show accurate Akali stats from match history")
    print(f"   AI insights should be unique and reference specific numbers\n")
    
    try:
        result = await generate_structured_analysis(
            game_name=game_name,
            tag_line=tag_line,
            num_matches=50  # Smaller sample for testing
        )
        
        if not result.get('success'):
            print(f"\n❌ FAILED: {result.get('error')}")
            return
        
        data = result['data']
        
        print("\n" + "="*70)
        print("✅ ANALYSIS COMPLETE")
        print("="*70)
        
        print(f"\n👤 PROFILE:")
        print(f"   Display Name: {data['displayName']}")
        print(f"   Main Role: {data['mainRole']}")
        print(f"   Rank: {data['rank']}")
        print(f"   Matches Analyzed: {data['matchesAnalyzed']}")
        
        print(f"\n🏆 TOP CHAMPIONS (from match history):")
        for i, champ in enumerate(data['topChampions'], 1):
            print(f"   {i}. {champ['name']}: {champ['games']} games, {champ['winRate']}% WR")
        
        print(f"\n⭐ STAT HIGHLIGHTS:")
        for i, highlight in enumerate(data['highlights'], 1):
            print(f"   {i}. {highlight['stat']}: {highlight['value']}")
        
        print(f"\n🤖 AI INSIGHT (Claude Sonnet 4):")
        print(f"   {data['aiInsight']}")
        
        print(f"\n🎭 PERSONALITY:")
        print(f"   {data['personality']}")
        
        print("\n" + "="*70)
        print("✅ VALIDATION CHECKS:")
        print("="*70)
        
        # Validate champion stats accuracy
        akali_found = any('Akali' in c['name'] for c in data['topChampions'])
        print(f"   {'✓' if akali_found else '✗'} Akali in top champions: {akali_found}")
        
        # Validate AI insight quality
        insight = data['aiInsight']
        has_numbers = any(char.isdigit() for char in insight)
        print(f"   {'✓' if has_numbers else '✗'} AI insight contains specific numbers: {has_numbers}")
        
        long_enough = len(insight) > 200
        print(f"   {'✓' if long_enough else '✗'} AI insight is detailed (>200 chars): {long_enough} ({len(insight)} chars)")
        
        # Check for template strings (should NOT contain these)
        template_phrases = [
            "preset sentence",
            "template",
            "placeholder",
            "for now",
            "temporary"
        ]
        has_templates = any(phrase in insight.lower() for phrase in template_phrases)
        print(f"   {'✓' if not has_templates else '✗'} No template strings: {not has_templates}")
        
        print("\n" + "="*70)
        if akali_found and has_numbers and long_enough and not has_templates:
            print("✅ ALL CHECKS PASSED! Analysis is working correctly.")
        else:
            print("⚠️ Some checks failed. Review the output above.")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_structured_analysis())
