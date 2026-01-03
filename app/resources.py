import json
import os

def get_available_units_by_capability(capability: str):
    try:
        # Use absolute path relative to this file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "data", "units.json")
        
        with open(file_path, "r") as f:
            units = json.load(f)

        return [
            u for u in units
            if u["status"] == "AVAILABLE"
            and u["vehicle_type"] == capability
        ]

    except Exception:
        return []
