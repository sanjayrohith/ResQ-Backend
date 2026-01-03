import json
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from app.schemas import AIAnalysis  

load_dotenv()

MOCK_MODE = False


api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-2.5-flash"

def analyze_transcript(text: str) -> AIAnalysis:
    
    if MOCK_MODE:
        print(f"⚠️ SIMULATION MODE: Gemini skipped for input: '{text}'")
        time.sleep(1.5)
        return AIAnalysis(
            emergency_type="Fire",
            severity="Critical",
            location="Phoenix Marketcity, Velachery, Chennai",
            keywords=["smoke", "fire", "trapped"],
            reasoning="Simulation",
            confidence_score=0.98
        )

    
    prompt = f"""
    Analyze this emergency call transcript. 
    Extract the emergency type, severity (Critical/High/Medium/Low), location, relevant keywords, 
    reasoning for the severity, and a confidence score (0.0 to 1.0).
    
    Transcript: "{text}"
    """

    try:
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AIAnalysis 
            )
        )

        
        if not response.parsed:
             raise ValueError("Empty response from Gemini")

        print(f"🤖 Analyzed: {response.parsed.emergency_type} at {response.parsed.location}")
        
        return response.parsed

    except Exception as e:
        print(f"🔥 Gemini Error: {str(e)}")
        
        return AIAnalysis(
            emergency_type="Unclassified",
            severity="Normal",
            location="Unknown",
            keywords=["error"],
            reasoning=f"System Error: {str(e)}",
            confidence_score=0.0
        )