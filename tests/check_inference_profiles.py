"""
Check available inference profiles for Claude Sonnet 4.
"""
import boto3
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
env_path = backend_path / '.env'
load_dotenv(env_path)

try:
    bedrock_client = boto3.client(
        service_name='bedrock',
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    )
    
    print("🔍 Checking inference profiles...\n")
    
    # List inference profiles
    try:
        response = bedrock_client.list_inference_profiles()
        
        if 'inferenceProfileSummaries' in response and response['inferenceProfileSummaries']:
            print("✅ Available Inference Profiles:\n")
            for profile in response['inferenceProfileSummaries']:
                print(f"  Profile: {profile.get('inferenceProfileName', 'N/A')}")
                print(f"  ARN: {profile.get('inferenceProfileArn', 'N/A')}")
                print(f"  ID: {profile.get('inferenceProfileId', 'N/A')}")
                print()
        else:
            print("❌ No inference profiles found.")
            print("\n📝 To use Claude Sonnet 4, you need to:")
            print("   1. Go to AWS Bedrock Console")
            print("   2. Navigate to 'Inference Profiles'")
            print("   3. Create a profile with Claude Sonnet 4")
            print("   4. Use the profile ARN instead of model ID")
    except Exception as e:
        if 'AccessDeniedException' in str(e):
            print("⚠️  Cannot list inference profiles (permission denied)")
            print("   But you can still try using the model directly")
        else:
            raise
            
    print("\n" + "="*60)
    print("💡 RECOMMENDATION:")
    print("="*60)
    print("For now, use Claude 3.5 Sonnet v2 (no profile needed):")
    print("Model ID: anthropic.claude-3-5-sonnet-20241022-v2:0")
    print("\nThis model works great and doesn't require inference profiles!")
    print()
    
except Exception as e:
    print(f"❌ Error: {e}")
