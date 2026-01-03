import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
VOLUNTEER_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_alert(incident):
    message = f"""
🚨 *NEW EMERGENCY ALERT*

🔥 Type: {incident.analysis.emergency_type}
⚠️ Severity: {incident.analysis.severity}
📍 Location: {incident.analysis.location}

🧠 Reasoning:
{incident.analysis.reasoning}

🚑 Suggested Unit:
{incident.suggested_unit}

— ResQ Dispatch System
"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": VOLUNTEER_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print("Telegram notification failed:", e)
