import json

def get_best_available_unit(emergency_type: str):
    try:
        with open("data/units.json", "r") as f:
            units = json.load(f)
        
        # Filter for AVAILABLE units [cite: 29]
        available = [u for u in units if u["status"] == "AVAILABLE"]
        
        if not available:
            return "No units available. Please standby."

        # OPTIMIZATION: Pick the unit with the lowest ETA [cite: 12]
        best_match = min(available, key=lambda x: x["eta_minutes"])
        return f"{best_match['unit_id']} ({best_match['eta_minutes']} mins ETA)"
    
    except Exception:
        return "Manual selection required."