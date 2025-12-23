import json
import boto3
import re
from app.schemas import AIAnalysis

# =========================================================
# Bedrock Client
# =========================================================
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

# =========================================================
# Prompt Builder (THE FIX)
# =========================================================
def build_prompt(text: str) -> str:
    # We give it an example so it knows EXACTLY what to do.
    return f"""User: You are a strict API Backend. You convert emergency transcripts into raw JSON.
    
    RULES:
    1. Output ONLY valid JSON.
    2. Do NOT add explanations or conversational text.
    3. Do NOT use Markdown formatting (no ```json blocks).
    
    EXAMPLE INPUT:
    "Help, there is a big fire at the central station!"
    
    EXAMPLE JSON OUTPUT:
    {{
      "emergency_type": "Fire",
      "severity": "Critical",
      "location": "Central Station",
      "keywords": ["fire", "central station"],
      "reasoning": "User explicitly stated a big fire at a public hub.",
      "confidence_score": 0.98
    }}

    REAL INPUT:
    "{text}"
    
    REAL JSON OUTPUT:"""

# =========================================================
# Fallback
# =========================================================
def fallback_response(text: str, error_msg: str = "") -> AIAnalysis:
    return AIAnalysis(
        emergency_type="Unclassified",
        severity="Normal",
        location="Signal Processing Error",
        keywords=["error"],
        reasoning=f"AI Error: {error_msg}",
        confidence_score=0.0
    )

# =========================================================
# Main AI Entry Point
# =========================================================
def analyze_transcript(text: str) -> AIAnalysis:
    prompt = build_prompt(text)

    body = {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 512,
            "temperature": 0, # Strict mode
            "topP": 1,
            "stopSequences": ["User:"]
        }
    }

    try:
        response = bedrock.invoke_model(
            modelId="amazon.titan-text-express-v1",
            body=json.dumps(body)
        )

        raw = response["body"].read().decode("utf-8")
        data = json.loads(raw)
        output_text = data["results"][0]["outputText"].strip()
        
        print(f"🤖 Raw AI Output: {output_text}") 

        # 1. Regex Extraction (Find the JSON block)
        # This grabs everything between the first { and the last }
        json_match = re.search(r'\{.*\}', output_text, re.DOTALL)
        
        if json_match:
            clean_json = json_match.group(0)
        else:
            # Fallback: If AI forgot the braces, try to wrap it
            clean_json = "{" + output_text if not output_text.startswith("{") else output_text
        
        parsed = json.loads(clean_json)

        # 2. Normalization (Handle weird AI formatting)
        # If it wrapped it in a list or "rows", unwrap it
        if "rows" in parsed and isinstance(parsed["rows"], list):
            parsed = parsed["rows"][0]
        elif isinstance(parsed, list):
            parsed = parsed[0]

        # 3. Clean Keys (Convert "Emergency Type" -> "emergency_type")
        normalized = {}
        for key, value in parsed.items():
            new_key = key.lower().replace(" ", "_")
            normalized[new_key] = value

        # 4. Final Data Polish
        normalized["emergency_type"] = normalized.get("emergency_type", "Unclassified").title()
        
        if "keywords" in normalized and isinstance(normalized["keywords"], str):
             normalized["keywords"] = [k.strip() for k in normalized["keywords"].split(',')]
        
        if "confidence_score" in normalized:
            normalized["confidence_score"] = float(normalized["confidence_score"])

        return AIAnalysis(**normalized)

    except Exception as e:
        print(f"🔥 Bedrock Error: {str(e)}")
        # If it fails, return the Safe Fallback so the Frontend doesn't crash
        return fallback_response(text, str(e))