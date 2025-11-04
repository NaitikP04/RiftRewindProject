"""
Check which Claude models are available in your AWS Bedrock account.
"""
import boto3
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

# Load environment variables from backend/.env
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
    
    print("🔍 Checking available Claude models in your AWS Bedrock account...\n")
    
    # List foundation models
    response = bedrock_client.list_foundation_models(
        byProvider='Anthropic'
    )
    
    print("✅ Available Anthropic Claude Models:\n")
    for model in response['modelSummaries']:
        model_id = model['modelId']
        model_name = model['modelName']
        status = model.get('modelLifecycle', {}).get('status', 'ACTIVE')
        
        # Check if it's Claude Sonnet
        if 'sonnet' in model_id.lower() or 'sonnet' in model_name.lower():
            print(f"  🟢 {model_name}")
            print(f"     ID: {model_id}")
            print(f"     Status: {status}")
            print()
    
    print("\n" + "="*60)
    print("Recommended model IDs for use:")
    print("="*60)
    print("Claude 3.5 Sonnet (v2): anthropic.claude-3-5-sonnet-20241022-v2:0")
    print("Claude 3.5 Sonnet (v1): anthropic.claude-3-5-sonnet-20240620-v1:0")
    print("Claude 3 Sonnet:        anthropic.claude-3-sonnet-20240229-v1:0")
    print()
    
except Exception as e:
    print(f"❌ Error checking models: {e}")
    print("\nMake sure your AWS credentials have bedrock:ListFoundationModels permission")
