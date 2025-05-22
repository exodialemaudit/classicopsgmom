from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.debate_service import process_debate

app = FastAPI(title="Classico Foot LLM Backend")

class DebateRequest(BaseModel):
    initial_question: str
    mode: str = "standard"
    max_turns: int = 4

@app.post("/debate")
async def debate_endpoint(request: DebateRequest):
    try:
        transcript = process_debate(request.initial_question, mode=request.mode, max_turns=request.max_turns)
        return {"transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)