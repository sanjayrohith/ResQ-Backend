# ResQ Backend

FastAPI service that analyzes emergency call transcripts with Amazon Bedrock (Claude 3.5 Sonnet) and returns structured incident summaries for a React frontend.

## Prerequisites

- Python 3.10+
- AWS CLI configured with access to Bedrock (`aws configure`)
- Optional: virtual environment tooling such as `venv`

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install fastapi uvicorn boto3 pydantic python-dotenv
```

3. Ensure your AWS credentials allow Bedrock runtime access in the chosen region (default `us-east-1`).

## Running the API

```bash
uvicorn main:app --reload
```

The server exposes a single POST endpoint at `/analyze`.

## Example Request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Caller reports two elderly people trapped on the second floor with rising water."
  }'
```

Successful responses follow this shape:

```json
{
  "location": "",
  "emergencyType": "flood-rescue",
  "severity": "critical",
  "adults": "0",
  "children": "0",
  "elderly": "2",
  "flags": ["Elderly"]
}
```

## Deployment Notes

- Lock dependencies in `requirements.txt` before production deployment.
- Restrict `allow_origins` in CORS middleware to trusted frontend origins outside hackathon usage.
- Add structured logging and monitoring for request tracing in production.
