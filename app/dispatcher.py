from app.schemas import IncidentResponse, AIAnalysis
from app.resources import get_best_available_unit

def create_incident_report(analysis: AIAnalysis) -> IncidentResponse:
    # 1. Matches the AI's detected type to the best local unit [cite: 12]
    suggested = get_best_available_unit(analysis.emergency_type)
    
    # 2. Returns the final report with the random incident_id [cite: 5]
    return IncidentResponse(
        analysis=analysis,
        suggested_unit=suggested
    )