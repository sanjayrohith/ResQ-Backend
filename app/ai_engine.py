import boto3
import json
import re # Added Regex to clean AI output
from app.schemas import AIAnalysis

bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

def analyze_transcript(text: str) -> AIAnalysis:
    # 1. Improved Prompt to force stricter JSON
    prompt = f"""
    Human: You are a tactical dispatcher. Analyze: "{text}"
    Return ONLY a raw JSON object (no markdown, no text) with these keys:
    - emergency_type (String)
    - severity (String: Critical, High, Medium, Low, Normal)
    - location (String)
    - keywords (Array of Strings) - Example: ["fire", "smoke"]
    - reasoning (String)
    - confidence_score (Float 0.0-1.0)
    
    Assistant: {{""" 
    # ^ We pre-fill the "{" to force Claude to start JSON immediately

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "messages": [{"role": "user", "content": prompt}]
    })

    try:
        response = bedrock.invoke_model(body=body, modelId="anthropic.claude-3-5-sonnet-20240620-v1:0")
        response_body = json.loads(response.get('body').read())
        ai_text = response_body['content'][0]['text']

        # 2. Safety: Clean the output (Find the JSON block)
        # This fixes the crash if Claude adds text like "Here is the JSON:"
        json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
        if json_match:
            clean_json = json_match.group(0)
            data = json.loads(clean_json)
        else:
            # Fallback if we pre-filled the curly brace
            data = json.loads("{" + ai_text)

        return AIAnalysis(**data)

    except Exception as e:
        print(f"❌ Backend AI Error: {str(e)}")
        
        # --- THE FIX ---
        # Wrap the fallback data in the AIAnalysis object so dispatcher.py can read it
        return AIAnalysis(
            location="Signal Processing Error", 
            emergency_type="Unclassified",
            severity="Normal",
            keywords=["system_failure"], 
            reasoning="AI Parsing failed or Credentials missing. Manual review required.",
            confidence_score=0.0
        )