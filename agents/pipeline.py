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
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        cleaned = "\n".join(inner).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    if start == -1:
        raise ValueError(f"No JSON object found in output:\n{raw[:300]}")

    for end in range(len(cleaned), start, -1):
        if cleaned[end - 1] == "}":
            try:
                return json.loads(cleaned[start:end])
            except json.JSONDecodeError:
                continue

    raise ValueError(f"Could not parse JSON from model output:\n{raw[:500]}")


async def agent1_classify(scenario: str) -> dict:
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
    policy_text = "\n\n".join(
        f"[{p['source']}]\n{p['excerpt']}" for p in policies["retrieved_policies"]
    )

    system = """You are a clinical decision support reasoning agent for healthcare payment integrity.
You reason step-by-step over the case classification and retrieved policy evidence to produce
a structured recommendation. You do NOT make final decisions — you surface evidence and recommend
appropriate actions. Humans remain accountable for final determinations.

CONFIDENCE SCORING GUIDELINES — use this scale precisely:
- 0.95-0.99: All policy criteria clearly satisfied, complete evidence, no conflicts, strong clinical/policy alignment.
- 0.85-0.94: Minor uncertainty only, recommendation is strongly supported by available evidence.
- 0.70-0.84: Some evidence gaps or moderate ambiguity exist, but a reasonable recommendation can still be made.
- Below 0.70: Significant uncertainty, conflicting evidence, or major unresolved questions.

RECOMMENDATION GUIDANCE:
- If all policy requirements are clearly satisfied, evidence is complete, and there are no fraud or fairness
  concerns, recommend "Approve" with confidence 0.90 or above.
- If there is a clear, well-documented fraud pattern with strong statistical support and no mitigating context,
  recommend "Escalate for Fraud Investigation" with confidence reflecting the strength of the pattern (can be 0.85+).
- Only use "Escalate for Clinical Review" or "Flag for Manual Review" when there are genuine, material evidence
  gaps, fairness concerns, or ambiguity — not as a default safe choice.
- Be willing to recommend "Approve" when the case genuinely supports it. Do not default to caution when the
  evidence is actually sufficient.

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

Reason through this case step by step and produce your structured recommendation. Use the confidence
scale and recommendation guidance precisely — do not default to a moderate confidence or an escalation
out of general caution if the evidence genuinely supports a clear decision."""

    raw = await _call(system, [{"role": "user", "content": user}], max_tokens=1500)
    return _parse_json(raw)


async def agent4_governance(scenario: str, classification: dict, reasoning: dict) -> dict:
    system = """You are an AI governance and ethics review agent for a healthcare payment integrity system.
Your responsibility is to determine whether human review is required before any action is taken,
based on the case classification and the reasoning agent's output.

DECISION RULE — read carefully:
Set "human_review_required": false ONLY IF ALL of the following are true:
1. The recommendation is fully supported by the retrieved policy evidence.
2. Supporting evidence is complete, with no material gaps.
3. No conflicting clinical or claims information exists.
4. No fraud indicators remain unresolved or unexplained.
5. No fairness, equity, geographic, or population vulnerability concerns are present.
6. The reasoning is fully explainable and traceable to specific policy citations.
7. Confidence is 0.90 or greater.

If even ONE of these conditions fails, set "human_review_required": true and explain which
condition(s) failed in human_review_reason.

If human_review_required is false, explain in human_review_reason why the recommendation can
safely proceed without additional review — be specific about which criteria were satisfied.

Evaluate five governance dimensions independently. Use "Pass" when the dimension is clearly fine,
"Warning" when there is a minor or moderate concern, and "Fail" only when there is a material
problem with that dimension. Do not default every check to Warning — most cases should have a mix
of Pass and Warning, with Fail reserved for genuine deficiencies.

Also assign an overall_risk level:
- "Low": routine case, strong policy support, no red flags (e.g., a clean prior auth or routine approval)
- "Medium": some ambiguity, evidence gaps, or equity considerations requiring review
- "High": clear fraud signal, significant evidence gaps, or serious fairness/access concerns

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
  "overall_risk": "Low | Medium | High",
  "human_review_required": true,
  "human_review_reason": "string",
  "governance_summary": "2-3 sentence overall governance assessment"
}

Status must be exactly one of: Pass, Warning, Fail
human_review_required must be exactly true or false (no quotes, no strings)."""

    user = f"""ORIGINAL SCENARIO:
{scenario}

CLASSIFICATION:
{json.dumps(classification, indent=2)}

REASONING AGENT OUTPUT:
{json.dumps(reasoning, indent=2)}

Apply the decision rule precisely. If all seven conditions are genuinely satisfied, set
human_review_required to false — do not default to true out of general caution."""

    raw = await _call(system, [{"role": "user", "content": user}], max_tokens=1500)
    return _parse_json(raw)


async def run_pipeline(scenario: str) -> dict:
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
        "overall_risk": governance.get("overall_risk", "Medium"),
        "human_review_required": governance.get("human_review_required", True),
        "human_review_reason": governance.get("human_review_reason", ""),
    }