"""
JSON-based cache manager for match data.
Stores matches locally to avoid re-fetching from Riot API.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

class CacheManager:
    """
    Simple JSON file-based cache for match data.
    Perfect for hackathon/testing - no database needed!
    """
    
    def __init__(self, cache_dir: str = "cache"):
        """Initialize cache manager with directory."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache files
        self.matches_file = self.cache_dir / "matches.json"
        self.profiles_file = self.cache_dir / "profiles.json"
        
        # Load existing caches
        self.matches_cache = self._load_cache(self.matches_file)
        self.profiles_cache = self._load_cache(self.profiles_file)
        
        print(f"📦 Cache initialized: {len(self.matches_cache)} matches, {len(self.profiles_cache)} profiles")
    
    def _load_cache(self, file_path: Path) -> Dict:
        """Load cache from JSON file."""
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Failed to load cache {file_path}: {e}")
                return {}
        return {}
    
    def _save_cache(self, data: Dict, file_path: Path):
        """Save cache to JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️  Failed to save cache {file_path}: {e}")
    
    def get_match(self, match_id: str, max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """
        Get cached match data if available and fresh.
        
        Args:
            match_id: Match ID
            max_age_hours: Maximum age in hours before re-fetching
            
        Returns:
            Match data or None if not cached/stale
        """
        if match_id not in self.matches_cache:
            return None
        
        cached = self.matches_cache[match_id]
        cached_time = datetime.fromisoformat(cached.get('cached_at', '2000-01-01'))
        
        if datetime.now() - cached_time > timedelta(hours=max_age_hours):
            # Stale cache
            return None
        
        return cached.get('data')
    
    def store_match(self, match_id: str, match_data: Dict[str, Any]):
        """Store match data in cache."""
        self.matches_cache[match_id] = {
            'data': match_data,
            'cached_at': datetime.now().isoformat()
        }
        self._save_cache(self.matches_cache, self.matches_file)
    
    def store_matches_batch(self, matches: Dict[str, Dict[str, Any]]):
        """Store multiple matches at once (more efficient)."""
        for match_id, match_data in matches.items():
            self.matches_cache[match_id] = {
                'data': match_data,
                'cached_at': datetime.now().isoformat()
            }
        self._save_cache(self.matches_cache, self.matches_file)
    
    def get_profile(self, puuid: str, max_age_hours: int = 1) -> Optional[Dict[str, Any]]:
        """Get cached profile data (profiles change frequently, shorter TTL)."""
        if puuid not in self.profiles_cache:
            return None
        
        cached = self.profiles_cache[puuid]
        cached_time = datetime.fromisoformat(cached.get('cached_at', '2000-01-01'))
        
        if datetime.now() - cached_time > timedelta(hours=max_age_hours):
            return None
        
        return cached.get('data')
    
    def store_profile(self, puuid: str, profile_data: Dict[str, Any]):
        """Store profile data in cache."""
        self.profiles_cache[puuid] = {
            'data': profile_data,
            'cached_at': datetime.now().isoformat()
        }
        self._save_cache(self.profiles_cache, self.profiles_file)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = datetime.now()
        
        # Count fresh matches (< 24h old)
        fresh_matches = sum(
            1 for cached in self.matches_cache.values()
            if now - datetime.fromisoformat(cached.get('cached_at', '2000-01-01')) < timedelta(hours=24)
        )
        
        return {
            'total_matches': len(self.matches_cache),
            'fresh_matches': fresh_matches,
            'total_profiles': len(self.profiles_cache),
            'cache_size_mb': sum(
                os.path.getsize(f) for f in [self.matches_file, self.profiles_file]
                if f.exists()
            ) / (1024 * 1024)
        }
    
    def clear_stale_data(self, max_age_days: int = 7):
        """Remove data older than X days to keep cache size reasonable."""
        now = datetime.now()
        cutoff = now - timedelta(days=max_age_days)
        
        # Clear old matches
        old_count = len(self.matches_cache)
        self.matches_cache = {
            k: v for k, v in self.matches_cache.items()
            if datetime.fromisoformat(v.get('cached_at', '2000-01-01')) > cutoff
        }
        removed = old_count - len(self.matches_cache)
        
        if removed > 0:
            print(f"🧹 Removed {removed} stale matches (older than {max_age_days} days)")
            self._save_cache(self.matches_cache, self.matches_file)

# Global cache instance
cache_manager = CacheManager(cache_dir=os.path.join(os.path.dirname(__file__), '..', 'cache'))
