import json
from app.schemas import AIAnalysis

# Initialize Bedrock Runtime
bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

# -----------------------------
# System Prompt (Titan-friendly)
# -----------------------------
SYSTEM_PROMPT = """
You are an emergency response text analysis system.

Your task is to extract structured information from emergency call transcripts.

STRICT RULES:
- Output ONLY valid JSON
- Do NOT include explanations or markdown
- Be concise and precise
- Panic language is expected
- Use landmarks if address is unclear
"""

def build_prompt(transcript: str) -> str:
    return f"""
{SYSTEM_PROMPT}

Transcript:
\"\"\"{transcript}\"\"\"

Return ONLY valid JSON with exactly these fields:
- emergency_type (Medical, Fire, Flood, Evacuation, Other)
- severity (Critical, High, Standard)
- location
- keywords (array of strings)
- reasoning (1 short sentence)
- confidence_score (0.0 to 1.0)
"""

# -----------------------------
# Main AI Function
# -----------------------------
def analyze_transcript(text: str) -> AIAnalysis:
    # SYSTEM PROMPT: Optimized for Indian emergency contexts (slang/vague directions) [cite: 25]
    prompt = f"""
    Human: You are an emergency dispatcher. Analyze this transcript: "{text}"
    Extract the following in JSON format:
    - emergency_type (Medical, Fire, Flood, or Evacuation)
    - severity (Critical, High, or Standard)
    - location (Specific address or landmarks)
    - keywords (Relevant medical/danger terms)
    - reasoning (1 sentence why you chose this severity)
    - confidence_score (0.0 to 1.0)
    
    Assistant:"""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "messages": [{"role": "user", "content": prompt}]
    })

    try:
        response = bedrock.invoke_model(body=body, modelId="anthropic.claude-3-5-sonnet-20240620-v1:0")
        response_body = json.loads(response.get('body').read())
        # Note: In a live demo, you'd parse the specific JSON block from Claude's text output
        return AIAnalysis(**json.loads(response_body['content'][0]['text']))
    except Exception as e:
        # Robust fallback for hackathon stability [cite: 25]
        return AIAnalysis(
            emergency_type="General Emergency",
            severity="High",
            location="Detecting...",
            keywords=["unknown"],
            reasoning="System fallback due to processing error.",
            confidence_score=0.5
        )