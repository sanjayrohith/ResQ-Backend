from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    TranscriptInput,
    FrontendResponse
)
from app.ai_engine import analyze_transcript
from app.orchestrator import orchestrate_decision

app = FastAPI(title="ResQ-Connect AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze", response_model=FrontendResponse)
async def process_call(input_data: TranscriptInput):
    analysis = analyze_transcript(input_data.text)
    incident = orchestrate_decision(analysis)

    return FrontendResponse(
        incident_id=incident.incident_id,
        emergency_type=incident.analysis.emergency_type,
        severity=incident.analysis.severity,
        location=incident.analysis.location,
        reasoning=incident.analysis.reasoning,
        confidence_score=incident.analysis.confidence_score,
        suggested_unit=incident.suggested_unit
    )
