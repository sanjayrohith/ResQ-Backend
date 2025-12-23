# ResQ-Connect AI Backend

**Intelligent emergency response orchestration powered by AI**

Transform emergency call transcripts into actionable intelligence. Automatically analyze incidents, classify severity, and dispatch optimal response units in real-time.

---

## Overview

ResQ-Connect is a FastAPI-based backend that serves as the decision engine for emergency response systems. It leverages AWS Bedrock AI to extract structured data from natural language emergency calls and intelligently routes incidents to the nearest available response units.

**Core Capabilities**

- Natural language processing of emergency transcripts
- Real-time incident classification (Fire, Flood, Medical)
- Severity assessment with confidence scoring
- Intelligent resource allocation based on unit availability and ETA
- Automated Telegram notifications to registered volunteers
- Demo-ready mock mode for presentations

---


## System Architecture

The system follows a clean, layered architecture with clear separation of concerns:

```
Emergency Transcript
        ↓
┌──────────────────────────────────┐
│   API Layer (main.py)            │  ← FastAPI endpoint
│   POST /analyze                  │
└──────────────────────────────────┘
        ↓
┌──────────────────────────────────┐
│   AI Engine (ai_engine.py)       │  ← AWS Bedrock integration
│   • Prompt engineering           │
│   • Response parsing             │
│   • Mock mode support            │
└──────────────────────────────────┘
        ↓
┌──────────────────────────────────┐
│   Orchestrator (orchestrator.py) │  ← Decision logic
│   • Emergency type mapping       │
│   • Unit selection algorithm     │
└──────────────────────────────────┘
        ↓
┌──────────────────────────────────┐
│   Resources (resources.py)       │  ← Data access
│   • Unit availability filtering  │
│   • Capability matching          │
└──────────────────────────────────┘
        ↓
┌──────────────────────────────────┐
│ Telegram Notifier                │  ← Alert system
│ (telegram_notifier.py)           │
│   • Volunteer notifications      │
│   • Formatted alerts             │
└──────────────────────────────────┘
        ↓
    Incident Response + Volunteer Alert
```

**Component Breakdown**

| Component | Responsibility | Key Functions |
|-----------|---------------|---------------|
| `main.py` | HTTP interface | Request handling, CORS, response formatting |
| `ai_engine.py` | AI integration | Bedrock API calls, prompt engineering, JSON parsing |
| `orchestrator.py` | Business logic | Emergency classification, unit matching |
| `resources.py` | Data layer | Unit queries, availability checks |
| `schemas.py` | Data models | Pydantic validation, type safety |
| `telegram_notifier.py` | Alert system | Volunteer notifications via Telegram Bot API |

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- AWS CLI (only for production mode with real AI)
- pip or similar package manager

### Installation

```bash
# Navigate to project directory
cd resq-backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn boto3 pydantic requests
```

### Running Locally

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- Base URL: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/openapi.json`

---

## API Documentation

### Endpoint: `POST /analyze`

Processes emergency call transcripts and returns structured incident data with resource recommendations.

**Request**

```json
{
  "text": "There's thick black smoke coming from the second floor of Phoenix Marketcity!"
}
```

**Response**

```json
{
  "incident_id": "RESQ-A3F2",
  "emergency_type": "Fire",
  "severity": "Critical",
  "location": "Phoenix Marketcity, Velachery, Chennai",
  "reasoning": "Caller reported thick black smoke visible from the food court area. Potential structural hazard.",
  "confidence_score": 0.98,
  "suggested_unit": "Fire Engine FE12 (4 mins ETA)",
  "keywords": ["smoke", "fire", "second_floor", "trapped"]
}
```

**Response Schema**

| Field | Type | Description |
|-------|------|-------------|
| `incident_id` | string | Unique identifier (format: RESQ-XXXX) |
| `emergency_type` | string | Classification: Fire, Flood, Medical, etc. |
| `severity` | string | Critical, High, or Normal |
| `location` | string | Extracted location from transcript |
| `reasoning` | string | AI's analysis rationale |
| `confidence_score` | float | Model confidence (0.0 to 1.0) |
| `suggested_unit` | string | Optimal unit with ETA |
| `keywords` | array | Extracted key terms |

---

## Configuration

### Demo Mode

For presentations and development without AWS costs:

**File:** `app/ai_engine.py`

```python
MOCK_MODE = True  # Toggle to False for production
```

**Mock Mode Benefits:**
- Zero AWS costs
- Instant responses with realistic delay simulation
- Consistent demo behavior
- No API rate limits or failures

### Production Mode

**Step 1:** Configure AWS credentials

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-east-1
```

**Step 2:** Enable Bedrock access

Ensure your AWS account has access to Amazon Bedrock in `us-east-1` region with the `amazon.titan-text-express-v1` model.

**Step 3:** Disable mock mode

```python
# In app/ai_engine.py
MOCK_MODE = False
```

### Resource Configuration

Customize available emergency units in `data/units.json`:

```json
{
  "unit_id": "Fire Engine FE12",
  "vehicle_type": "FIRE_ENGINE",
  "distance_km": 2.3,
  "eta_minutes": 4,
  "status": "AVAILABLE"
}
```

**Supported Vehicle Types:**
- `FIRE_ENGINE` - Fire and rescue operations
- `AMBULANCE` - Medical emergencies
- `RESCUE_BOAT` - Flood and water rescue

**Status Values:**
- `AVAILABLE` - Ready for dispatch
- `BUSY` - Currently on assignment

### Telegram Notifications

The system automatically sends real-time alerts to registered volunteers via Telegram when incidents are dispatched.

**Configuration:** `app/telegram_notifier.py`

```python
BOT_TOKEN = "your-telegram-bot-token"
VOLUNTEER_CHAT_ID = "volunteer-chat-id"
```

**Setting Up Telegram Notifications:**

1. Create a Telegram bot via [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot)
4. Update `BOT_TOKEN` and `VOLUNTEER_CHAT_ID` in `telegram_notifier.py`

**Alert Format:**

```
🚨 NEW EMERGENCY ALERT

🔥 Type: Fire
⚠️ Severity: Critical
📍 Location: Phoenix Marketcity, Velachery, Chennai

🧠 Reasoning:
Caller reported thick black smoke visible from the food court area.

🚑 Suggested Unit:
Fire Engine FE12 (4 mins ETA)

— ResQ Dispatch System
```

**Features:**
- Non-blocking notifications (API never fails due to Telegram issues)
- Markdown formatting for better readability
- Includes all critical incident details
- Instant delivery to volunteers

---

## Testing

### cURL Example

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Two elderly people trapped on second floor with rising water"}'
```

### Interactive Testing

Navigate to `http://localhost:8000/docs` for Swagger UI with:
- Live API testing
- Request/response examples
- Schema documentation
- Try-it-now functionality

---

## Project Structure

```
resq-backend/
├── app/
│   ├── main.py              # FastAPI application and routes
│   ├── ai_engine.py         # AWS Bedrock integration and AI logic
│   ├── orchestrator.py      # Decision engine and unit matching
│   ├── resources.py         # Resource management and data access
│   ├── schemas.py           # Pydantic models and validation
│   └── telegram_notifier.py # Telegram bot integration for alerts
├── data/
│   └── units.json           # Emergency unit database
└── README.md
```

---

## Technical Decisions

**FastAPI Framework**
- Automatic OpenAPI documentation generation
- Built-in request/response validation via Pydantic
- Native async support for high concurrency
- Type hints for improved developer experience

**AWS Bedrock for AI**
- Serverless inference (no infrastructure management)
- Pay-per-use pricing model
- Enterprise-grade security and compliance
- Multiple model options (currently using Amazon Titan)

**Mock Mode Architecture**
- Enables reliable demos without external dependencies
- Simulates realistic response times
- Provides consistent test data
- Reduces development costs

---

## Production Deployment

**Pre-deployment Checklist**

```bash
# Generate requirements file
pip freeze > requirements.txt

# Security hardening
# - Restrict CORS origins in main.py
# - Add API authentication
# - Enable HTTPS/TLS

# Monitoring setup
# - Configure CloudWatch logs
# - Set up error alerting
# - Add performance metrics

# Configuration
# - Set MOCK_MODE = False
# - Use environment variables for secrets
# - Configure production database
```

**Recommended Enhancements**

- Replace `units.json` with PostgreSQL/DynamoDB
- Implement rate limiting (e.g., slowapi)
- Add request logging and tracing
- Set up CI/CD pipeline
- Configure auto-scaling
- Add health check endpoints
- Support multiple Telegram channels for different emergency types
- Implement volunteer acknowledgment system
- Add SMS fallback for critical alerts

---

## Development

**Code Style**
- Type hints throughout
- Pydantic for data validation
- Clear separation of concerns
- Minimal external dependencies

**Adding New Emergency Types**

1. Update `orchestrator.py` mapping logic
2. Add corresponding vehicle types to `units.json`
3. Update AI prompt in `ai_engine.py` if needed

**Extending AI Capabilities**

Modify the prompt template in `ai_engine.py`:

```python
def build_prompt(text: str) -> str:
    return f"""Your custom prompt here..."""
```

---

## License

MIT License - Free for personal and commercial use

---

## Acknowledgments

Built with AWS Bedrock, FastAPI, and a focus on saving lives through intelligent automation.

*Designed for emergency response systems that need speed, accuracy, and reliability.*
