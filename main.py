# -*- coding: utf-8 -*-
import os
import sys
from fastapi.responses import JSONResponse

# Force UTF-8 output encoding (fixes Unicode emoji errors on macOS/Windows)
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.pipeline import run_pipeline
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


@app.get("/scenarios")
async def get_scenarios():
    return {"scenarios": SCENARIOS}


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    if not request.scenario.strip():
        raise HTTPException(status_code=400, detail="Scenario cannot be empty.")
    try:
        result = await run_pipeline(request.scenario)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.head("/")
async def health():
    return JSONResponse(content={})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=False)