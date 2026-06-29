"""
Four-agent sequential pipeline.
Each agent receives the full context chain accumulated so far,
ensuring true stateful agentic chaining rather than isolated prompts.
"""

from __future__ import annotations
import os
import json
import anthropic
from agents.rag import retrieve

MODEL = "claude-sonnet-4-6"


def _get_client() -> anthropic.AsyncAnthropic:
    """Read and sanitize API key at call time, not import time."""
    raw_key = os.environ.get("ANTHROPIC_API_KEY", "")
    clean_key = "".join(c for c in raw_key if ord(c) < 128).strip()
    if not clean_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set or is empty.")
    return anthropic.AsyncAnthropic(api_key=clean_key)


async def _call(system: str, messages: list[dict], max_tokens: int = 1024) -> str:
    client = _get_client()
    response = await client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    )
    return response.content[0].text.strip()


def _parse_json(raw: str) -> dict:
    """
    Robustly parse JSON from model output.
    Handles markdown fences, truncation, and minor formatting issues.
    """
    # Strip markdown fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        cleaned = "\n".join(inner).strip()

    # Try direct parse first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Find outermost { ... } block
    start = cleaned.find("{")
    if start == -1:
        raise ValueError(f"No JSON object found in output:\n{raw[:300]}")

    # Walk backwards from end to find largest valid JSON object
    for end in range(len(cleaned), start, -1):
        if cleaned[end - 1] == "}":
            try:
                return json.loads(cleaned[start:end])
            except json.JSONDecodeError:
                continue

    raise ValueError(f"Could not parse JSON from model output:\n{raw[:500]}")


async def agent1_classify(scenario: str) -> dict:
    """Classify the case type and extract key clinical/billing signals."""
    system = """You are a clinical and claims classification agent for a healthcare payment integrity system.
Your role is to identify the case type and extract structured signals from the scenario.

Respond ONLY with a valid JSON object — no markdown, no explanation — in this exact shape:
{
  "case_type": "Prior Authorization | Fraud Investigation | Utilization Review | Coding Audit | Other",
  "clinical_domain": "string",
  "primary_signals": ["signal1", "signal2", "signal3"],
  "risk_indicators": ["indicator1", "indicator2"],
  "geographic_context": "Urban | Rural | Frontier | Unknown",
  "population_vulnerability": "High | Medium | Low",
  "summary": "One sentence case summary"
}"""

    user = f"Classify this scenario:\n\n{scenario}"
    raw = await _call(system, [{"role": "user", "content": user}], max_tokens=800)
    return _parse_json(raw)


async def agent2_retrieve_policy(scenario: str, classification: dict) -> dict:
    """RAG-based policy retrieval relevant to the classified case."""
    query = f"{classification.get('case_type', '')} {classification.get('clinical_domain', '')} {scenario[:300]}"
    retrieved = retrieve(query, top_k=3)

    return {
        "retrieved_policies": [
            {
                "source": r["source"],
                "excerpt": r["text"][:300] + "...",
                "relevance_score": round(r["score"], 3),
            }
            for r in retrieved
        ]
    }


async def agent3_reason(scenario: str, classification: dict, policies: dict) -> dict:
    """Chain-of-thought reasoning over classification + retrieved evidence."""
    policy_text = "\n\n".join(
        f"[{p['source']}]\n{p['excerpt']}" for p in policies["retrieved_policies"]
    )

    system = """You are a clinical decision support reasoning agent for healthcare payment integrity.
You reason step-by-step over the case classification and retrieved policy evidence to produce
a structured recommendation. You do NOT make final decisions — you surface evidence and recommend
appropriate actions. Humans remain accountable for final determinations.

Respond ONLY with valid JSON — no markdown — in this exact shape:
{
  "reasoning_steps": [
    {"step": 1, "label": "string", "finding": "string"},
    {"step": 2, "label": "string", "finding": "string"},
    {"step": 3, "label": "string", "finding": "string"}
  ],
  "recommendation": "Approve | Deny | Escalate for Clinical Review | Escalate for Fraud Investigation | Flag for Manual Review",
  "confidence": 0.75,
  "supporting_evidence": ["evidence point 1", "evidence point 2"],
  "gaps_in_evidence": ["gap 1", "gap 2"],
  "rationale": "2-3 sentence explanation of the recommendation"
}"""

    user = f"""SCENARIO:
{scenario}

CLASSIFICATION:
{json.dumps(classification, indent=2)}

RETRIEVED POLICY EVIDENCE:
{policy_text}

Reason through this case step by step and produce your structured recommendation."""

    raw = await _call(system, [{"role": "user", "content": user}], max_tokens=1500)
    return _parse_json(raw)


async def agent4_governance(scenario: str, classification: dict, reasoning: dict) -> dict:
    """Governance and ethics review across five dimensions."""
    system = """You are an AI governance and ethics review agent for a healthcare payment integrity system.
Evaluate the decision support output across five governance dimensions.

Respond ONLY with valid JSON — no markdown — in this exact shape:
{
  "governance_checks": {
    "fairness": {"status": "Pass", "finding": "string"},
    "evidence_sufficiency": {"status": "Warning", "finding": "string"},
    "explainability": {"status": "Pass", "finding": "string"},
    "confidence_threshold": {"status": "Pass", "finding": "string"},
    "human_oversight": {"status": "Warning", "finding": "string"}
  },
  "equity_concerns": ["concern1"],
  "human_review_required": true,
  "human_review_reason": "string",
  "governance_summary": "2-3 sentence overall governance assessment"
}

Status must be exactly one of: Pass, Warning, Fail
human_review_required must be exactly true or false (no quotes)."""

    user = f"""ORIGINAL SCENARIO:
{scenario}

CLASSIFICATION:
{json.dumps(classification, indent=2)}

REASONING AGENT OUTPUT:
{json.dumps(reasoning, indent=2)}

Perform a full governance and ethics review."""

    raw = await _call(system, [{"role": "user", "content": user}], max_tokens=1500)
    return _parse_json(raw)


async def run_pipeline(scenario: str) -> dict:
    """Orchestrates the full four-agent sequential pipeline."""
    print("Agent 1: Classifying...", flush=True)
    classification = await agent1_classify(scenario)
    print("Agent 1 done.", flush=True)

    print("Agent 2: Retrieving policies...", flush=True)
    policies = await agent2_retrieve_policy(scenario, classification)
    print("Agent 2 done.", flush=True)

    print("Agent 3: Reasoning...", flush=True)
    reasoning = await agent3_reason(scenario, classification, policies)
    print("Agent 3 done.", flush=True)

    print("Agent 4: Governance review...", flush=True)
    governance = await agent4_governance(scenario, classification, reasoning)
    print("Agent 4 done.", flush=True)

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
        "human_review_required": governance.get("human_review_required", True),
        "human_review_reason": governance.get("human_review_reason", ""),
    }