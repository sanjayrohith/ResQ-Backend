from app.schemas import IncidentResponse, AIAnalysis
from app.resources import get_available_units_by_capability
from app.telegram_notifier import send_telegram_alert


def orchestrate_decision(analysis: AIAnalysis) -> IncidentResponse:
    """
    Orchestrates the final decision:
    - Maps emergency type to capability
    - Finds best available unit
    - Sends Telegram alert to volunteer
    - Returns response to frontend
    """

    # 1️⃣ Map emergency type → required capability
    if analysis.emergency_type == "Flood":
        capability = "RESCUE_BOAT"
    elif analysis.emergency_type == "Fire":
        capability = "FIRE_ENGINE"
    else:
        capability = "AMBULANCE"

    # 2️⃣ Fetch available units for that capability
    units = get_available_units_by_capability(capability)

    if not units:
        suggested = "No suitable units available"
    else:
        best = min(units, key=lambda x: x["eta_minutes"])
        suggested = f"{best['unit_id']} ({best['eta_minutes']} mins ETA)"

    # 3️⃣ Build incident response
    incident = IncidentResponse(
        analysis=analysis,
        suggested_unit=suggested
    )

    # 4️⃣ Send Telegram alert (SAFE: never breaks backend)
    try:
        send_telegram_alert(incident)
    except Exception as e:
        print("⚠️ Telegram alert failed:", e)

    # 5️⃣ Return response to frontend
    return incident
