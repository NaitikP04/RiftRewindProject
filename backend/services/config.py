"""
Configuration and environment validation.
Fails fast with clear error messages if required env vars are missing.
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration with validation."""
    
    # Riot API
    RIOT_API_KEY: str
    
    # AWS Bedrock
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    
    # Rate Limits
    RIOT_RATE_LIMIT_PER_SECOND: int = 20
    RIOT_RATE_LIMIT_PER_2MIN: int = 100
    
    # Cache Settings
    ENABLE_CACHE: bool = True
    CACHE_MATCH_TTL_HOURS: int = 24
    CACHE_PROFILE_TTL_HOURS: int = 1
    
    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        """
        Validate that all required environment variables are set.
        
        Returns:
            (is_valid, error_message)
        """
        required_vars = {
            'RIOT_API_KEY': 'Riot API Key',
            'AWS_ACCESS_KEY_ID': 'AWS Access Key ID',
            'AWS_SECRET_ACCESS_KEY': 'AWS Secret Access Key',
            'AWS_REGION': 'AWS Region'
        }
        
        missing = []
        for var, name in required_vars.items():
            value = os.getenv(var)
            if not value or value.startswith('your_'):
                missing.append(f"  - {var} ({name})")
            else:
                setattr(cls, var, value)
        
        if missing:
            error = (
                "❌ Missing required environment variables:\n" +
                "\n".join(missing) +
                "\n\n📋 To fix:\n"
                "  1. Copy backend/.env.example to backend/.env\n"
                "  2. Fill in your actual API keys\n"
                "  3. Restart the server"
            )
            return False, error
        
        # Set validated values
        cls.RIOT_API_KEY = os.getenv('RIOT_API_KEY', '')
        cls.AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
        cls.AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
        cls.AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
        
        # Optional settings
        cls.ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'true').lower() == 'true'
        
        return True, None
    
    @classmethod
    def get_summary(cls) -> str:
        """Get configuration summary for startup logs."""
        return f"""
🔧 Configuration:
   Riot API: {'✓ Configured' if cls.RIOT_API_KEY else '✗ Missing'}
   AWS Bedrock: {'✓ Configured' if cls.AWS_ACCESS_KEY_ID else '✗ Missing'}
   Region: {cls.AWS_REGION}
   Cache: {'Enabled' if cls.ENABLE_CACHE else 'Disabled'}
   Rate Limits: {cls.RIOT_RATE_LIMIT_PER_SECOND}/s, {cls.RIOT_RATE_LIMIT_PER_2MIN}/2min
"""

# Validate on module import
config = Config()
is_valid, error_message = config.validate()

if not is_valid:
    print("\n" + "="*60)
    print(error_message)
    print("="*60 + "\n")
    # Don't exit - let FastAPI startup handle it gracefully
