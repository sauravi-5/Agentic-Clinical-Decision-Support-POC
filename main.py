# -*- coding: utf-8 -*-
import os
import sys
import json

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.pipeline import (
    agent1_classify, agent2_retrieve_policy, agent3_reason, agent4_governance
)
from scenarios import SCENARIOS

app = FastAPI(title="Clinical Decision Support POC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


class AnalyzeRequest(BaseModel):
    scenario: str


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.head("/")
async def health():
    return JSONResponse(content={})


@app.get("/scenarios")
async def get_scenarios():
    return {"scenarios": SCENARIOS}


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.post("/analyze-stream")
async def analyze_stream(request: AnalyzeRequest):
    """Streams agent progress via Server-Sent Events so the UI can show real per-agent status."""
    scenario = request.scenario.strip()
    if not scenario:
        raise HTTPException(status_code=400, detail="Scenario cannot be empty.")

    async def event_generator():
        try:
            yield _sse("agent_start", {"agent": 1})
            classification = await agent1_classify(scenario)
            yield _sse("agent_done", {"agent": 1, "data": classification})

            yield _sse("agent_start", {"agent": 2})
            policies = await agent2_retrieve_policy(scenario, classification)
            yield _sse("agent_done", {"agent": 2, "data": policies})

            yield _sse("agent_start", {"agent": 3})
            reasoning = await agent3_reason(scenario, classification, policies)
            yield _sse("agent_done", {"agent": 3, "data": reasoning})

            yield _sse("agent_start", {"agent": 4})
            governance = await agent4_governance(scenario, classification, reasoning)
            yield _sse("agent_done", {"agent": 4, "data": governance})

            result = {
                "scenario": scenario,
                "agents": {
                    "classification": classification,
                    "policy_retrieval": policies,
                    "reasoning": reasoning,
                    "governance": governance,
                },
                "final_recommendation": reasoning.get("recommendation", "Escalate for Manual Review"),
                "confidence": reasoning.get("confidence", 0.0),
                "overall_risk": governance.get("overall_risk", "Medium"),
                "human_review_required": governance.get("human_review_required", True),
                "human_review_reason": governance.get("human_review_reason", ""),
            }
            yield _sse("complete", result)

        except Exception as e:
            yield _sse("error", {"message": str(e)})

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """Non-streaming fallback endpoint."""
    scenario = request.scenario.strip()
    if not scenario:
        raise HTTPException(status_code=400, detail="Scenario cannot be empty.")
    try:
        classification = await agent1_classify(scenario)
        policies = await agent2_retrieve_policy(scenario, classification)
        reasoning = await agent3_reason(scenario, classification, policies)
        governance = await agent4_governance(scenario, classification, reasoning)
        return {
            "scenario": scenario,
            "agents": {
                "classification": classification,
                "policy_retrieval": policies,
                "reasoning": reasoning,
                "governance": governance,
            },
            "final_recommendation": reasoning.get("recommendation", "Escalate for Manual Review"),
            "confidence": reasoning.get("confidence", 0.0),
            "overall_risk": governance.get("overall_risk", "Medium"),
            "human_review_required": governance.get("human_review_required", True),
            "human_review_reason": governance.get("human_review_reason", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=False)