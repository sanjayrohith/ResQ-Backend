from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import TranscriptInput, IncidentResponse
from app.ai_engine import analyze_transcript
from app.orchestrator import orchestrate_decision

app = FastAPI(title="ResQ-Connect AI Backend")

# Enable CORS for your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze", response_model=IncidentResponse)
async def process_call(input_data: TranscriptInput):
    analysis = analyze_transcript(input_data.text)
    return orchestrate_decision(analysis)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)