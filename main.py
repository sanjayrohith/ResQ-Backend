import os
import json
import boto3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# 1. Allow React (Frontend) to talk to Python (Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon, allow all. In prod, specify localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Setup AWS Bedrock Client
# Ensure you have run 'aws configure' in your terminal!
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1' # Or your specific region
)

# 3. Define the Data Models (Must match your Frontend Interface!)
class TranscriptionInput(BaseModel):
    transcript: str

class VictimCounts(BaseModel):
    adults: str = "0"
    children: str = "0"
    elderly: str = "0"

class IncidentResponse(BaseModel):
    location: str
    emergencyType: str
    severity: str
    adults: str
    children: str
    elderly: str
    flags: List[str]

# 4. The AI Analysis Endpoint
@app.post("/analyze", response_model=IncidentResponse)
async def analyze_transcript(input_data: TranscriptionInput):
    prompt = f"""
    You are an AI assistant for Emergency Dispatch (911/108). 
    Analyze the following real-time call transcript and extract structured data.
    
    TRANSCRIPT:
    "{input_data.transcript}"
    
    RULES:
    1. Extract the 'location' (street, landmark, city). If unknown, return empty string.
    2. Determine 'emergencyType' (options: flood-rescue, medical, fire, accident). Default: flood-rescue.
    3. Determine 'severity' (critical, high, medium, low). If 'unconscious', 'bleeding', 'trapped', set to 'critical'.
    4. Count victims (adults, children, elderly). Return as strings.
    5. Detect 'flags' (e.g., ["Elderly", "Mobility Issue", "Pregnant"]).
    
    OUTPUT FORMAT:
    Return ONLY a valid JSON object. No markdown, no pre-text.
    Example:
    {{
        "location": "Perumal Temple, Velachery",
        "emergencyType": "flood-rescue",
        "severity": "critical",
        "adults": "2",
        "children": "0",
        "elderly": "1",
        "flags": ["Elderly", "Mobility Issue"]
    }}
    """

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })

    try:
        # Call Claude 3.5 Sonnet
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0", # Check your available models
            body=body
        )
        
        response_body = json.loads(response.get('body').read())
        result_text = response_body['content'][0]['text']
        
        # Parse the AI's JSON text into a Python Dict
        # Sometimes AI adds extra text, so we try to find the JSON start/end
        start_idx = result_text.find('{')
        end_idx = result_text.rfind('}') + 1
        clean_json = result_text[start_idx:end_idx]
        
        data = json.loads(clean_json)
        
        # Flatten the structure to match your specific frontend need if necessary
        return IncidentResponse(
            location=data.get("location", ""),
            emergencyType=data.get("emergencyType", "flood-rescue"),
            severity=data.get("severity", "low"),
            adults=data.get("adults", "0"),
            children=data.get("children", "0"),
            elderly=data.get("elderly", "0"),
            flags=data.get("flags", [])
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        # Return a safe fallback if AI fails
        return IncidentResponse(
            location="", emergencyType="flood-rescue", severity="low",
            adults="0", children="0", elderly="0", flags=[]
        )

# Run with: uvicorn main:app --reload