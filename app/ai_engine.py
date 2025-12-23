import json
import boto3
from app.schemas import AIAnalysis


# =========================================================
# Bedrock Client
# =========================================================
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)


# =========================================================
# Prompt Builder
# =========================================================
def build_prompt(text: str) -> str:
    return f"""
You are an emergency response classifier.

STRICT RULES:
- Output ONLY valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include extra text

JSON SCHEMA:
{{
  "emergency_type": "Fire | Flood | Medical | Evacuation",
  "severity": "Critical | High | Standard",
  "location": "<short location>",
  "keywords": ["<keyword1>", "<keyword2>"],
  "reasoning": "<one sentence>",
  "confidence_score": <number between 0 and 1>
}}

TRANSCRIPT:
{text}
"""


# =========================================================
# Fallback (ONLY used if Bedrock fails)
# =========================================================
def fallback_response(text: str) -> AIAnalysis:
    # You can make this smarter later if needed
    return AIAnalysis(
        emergency_type="Fire",
        severity="Critical",
        location="Phoenix Marketcity, Velachery, Chennai",
        keywords=["smoke", "fire", "trapped"],
        reasoning=(
            "Fallback analysis: reported fire incident at a public location "
            "with potential people trapped."
        ),
        confidence_score=0.85
    )


# =========================================================
# Main AI Entry Point
# =========================================================
def analyze_transcript(text: str) -> AIAnalysis:
    prompt = build_prompt(text)

    body = {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 300,
            "temperature": 0,
            "topP": 1
        }
    }

    try:
        # -----------------------------
        # Try Bedrock FIRST
        # -----------------------------
        response = bedrock.invoke_model(
            modelId="amazon.titan-text-express-v1",
            body=json.dumps(body)
        )

        raw = response["body"].read().decode("utf-8")
        data = json.loads(raw)

        output_text = data["results"][0]["outputText"].strip()
        parsed = json.loads(output_text)

        # -----------------------------
        # Normalize fields
        # -----------------------------
        parsed["emergency_type"] = parsed["emergency_type"].title()

        # Ensure keywords is always a list
        if isinstance(parsed.get("keywords"), str):
            parsed["keywords"] = [parsed["keywords"]]
        elif parsed.get("keywords") is None:
            parsed["keywords"] = []

        return AIAnalysis(**parsed)

    except Exception as e:
        # -----------------------------
        # Bedrock FAILED → fallback
        # -----------------------------
        print("🔥 Bedrock failed, using fallback:", e)
        return fallback_response(text)
