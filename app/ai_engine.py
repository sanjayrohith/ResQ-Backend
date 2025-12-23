import json
from app.schemas import AIAnalysis

# NOTE: AWS Bedrock imports are commented out for Mock Mode
# import boto3
# import re

def analyze_transcript(text: str) -> AIAnalysis:
    print(f"⚠️ MOCK MODE: Received transcript: {text}")
    
    # --- SIMULATION LOGIC ---
    # Instead of calling AWS, we return a hardcoded 'Perfect' response.
    # This proves your Frontend Auto-fill works.
    
    mock_response = AIAnalysis(
        emergency_type="Fire",
        severity="Critical",
        location="Phoenix Marketcity, Velachery, Chennai",
        keywords=["smoke", "fire", "second_floor", "trapped"],
        reasoning="Caller reported thick black smoke visible from the food court area. Potential structural hazard.",
        confidence_score=0.98
    )
    
    return mock_response

    # --- BELOW IS THE REAL CODE (Keep this for later) ---
    """
    bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
    
    prompt = f"..."
    
    try:
        # AWS Call Logic...
    except Exception as e:
        # Fallback Logic...
    """