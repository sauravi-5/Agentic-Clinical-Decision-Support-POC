# Agentic Clinical Decision Support with Ethical Guardrails
### Cotiviti Intern Assessment — POC Demo

> **Beyond Accuracy: Ethical Chain Reasoning for Agentic Clinical Decision Support in Healthcare Payment Integrity**

---

## Overview

A multi-agent AI system that combines clinical reasoning, RAG-based policy retrieval, explainable decision support, and AI governance for healthcare payment integrity. Built as a proof-of-concept for the Cotiviti GenAI Intern assessment.

---

## Architecture

```
User Scenario
      │
      ▼
Agent 1 — Clinical & Claim Classification
      │    Identifies case type, signals, and risk indicators
      ▼
Agent 2 — Policy Retrieval (RAG)
      │    FAISS vector search over healthcare policy corpus
      ▼
Agent 3 — Decision Support & Reasoning
      │    Chain-of-thought inference → structured recommendation
      ▼
Agent 4 — Governance & Ethics Review
      │    Fairness, evidence, explainability, oversight checks
      ▼
Structured Recommendation + Human Review Determination
```

Each agent receives the full accumulated context from all previous agents — true sequential agentic chaining.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 + FastAPI |
| AI Reasoning | Anthropic Claude (claude-sonnet-4-6) |
| Policy Retrieval | FAISS + sentence-transformers (all-MiniLM-L6-v2) |
| Frontend | Vanilla HTML/CSS/JS (served by FastAPI) |
| Hosting | Render.com |

---

## Demo Scenarios

| Scenario | Governance Challenge |
|---|---|
| Rural Imaging Outlier | Fairness, geographic bias |
| Experimental Oncology Treatment | Evidence gaps, patient access, equity |
| Repeated Upcoding Pattern | Clear fraud signal, minimal ethics concerns |

---

## Local Setup

```bash
# 1. Clone
git clone <your-repo-url>
cd cotiviti-poc

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API key
export ANTHROPIC_API_KEY=your_key_here

# 4. Run
python main.py
# Visit http://localhost:8000
```

---

## Deploy to Render

1. Push repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service → Connect repo
3. Render auto-detects `render.yaml`
4. Add `ANTHROPIC_API_KEY` as an environment variable in Render dashboard
5. Deploy — live URL in ~2 minutes

---

## Key Capabilities Demonstrated

- **Multi-agent orchestration** — sequential stateful pipeline
- **Retrieval-Augmented Generation** — FAISS vector search over policy corpus
- **Chain-of-thought reasoning** — structured step-by-step clinical inference
- **Explainable AI** — every recommendation includes traceable rationale
- **AI Governance** — 5-dimension ethics and oversight review
- **Human-in-the-loop design** — system recommends, humans decide

---

## Citation

Built with Claude Sonnet (Anthropic), FastAPI, sentence-transformers, FAISS.  
Policy excerpts sourced from: CMS Rural Health Policy, AMA CPT 2024, NCCN NSCLC Guidelines v3.2024.
