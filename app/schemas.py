import uuid
from pydantic import BaseModel, Field
from typing import List, Optional

class TranscriptInput(BaseModel):
    text: str

class AIAnalysis(BaseModel):
    emergency_type: str
    severity: str
    location: str
    keywords: List[str]
    reasoning: str
    confidence_score: float

class IncidentResponse(BaseModel):
    
    incident_id: str = Field(default_factory=lambda: f"RESQ-{uuid.uuid4().hex[:4].upper()}")
    analysis: AIAnalysis
    suggested_unit: Optional[str] = None
    status: str = "Pending Confirmation"