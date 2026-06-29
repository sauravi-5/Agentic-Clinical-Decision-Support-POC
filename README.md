# Agentic Clinical Decision Support with Ethical Guardrails

**Cotiviti GenAI Intern Assessment — Sauravi Lalge**  
Topic 2: Clinical Decision Making and Pattern Recognition in Health Care

Live Demo: https://agentic-clinical-decision-support.onrender.com

---

## What This Is

A multi-agent AI system for healthcare payment integrity that chains four specialized AI agents — clinical classification, RAG-based policy retrieval, chain-of-thought reasoning, and a governance review layer — to produce explainable, auditable decision support recommendations.

The core thesis: payment integrity isn't just about identifying incorrect claims. It requires simultaneously balancing clinical appropriateness, payer policy compliance, provider equity, and patient access to care. A single rule engine or a single LLM call can't navigate all of those dimensions at once. This pipeline can.

---

## Architecture

```
User Scenario
      │
      ▼
Agent 1 — Clinical & Claim Classification
      │    Case type, risk signals, geographic context, population vulnerability
      ▼
Agent 2 — Policy Retrieval (RAG)
      │    FAISS vector search over 7 healthcare policy documents
      ▼
Agent 3 — Decision Support & Reasoning
      │    3-step chain-of-thought → recommendation + confidence + evidence gaps
      ▼
Agent 4 — Governance & Ethics Review
           Fairness · Evidence · Explainability · Confidence · Human Oversight
      │
      ▼
Structured Recommendation + Human Review Determination
```

Each agent receives the full accumulated context from all prior agents — true stateful sequential chaining, not four isolated prompts.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 + FastAPI |
| AI Reasoning | Anthropic Claude (claude-sonnet-4-6) via AsyncAnthropic |
| Vector Search | FAISS + sentence-transformers (all-MiniLM-L6-v2) |
| Frontend | Vanilla HTML/CSS/JS served by FastAPI static middleware |
| Deployment | Render.com (auto-deploy from GitHub) |

---

## Policy Corpus (Agent 2 RAG)

7 real healthcare policy documents embedded and indexed at startup:

- CMS Rural Health Policy — Section 7 (RUCA codes, rural benchmarking)
- Medical Imaging Utilization Policy — Section 3.1 (volume outlier thresholds)
- NCCN NSCLC Clinical Practice Guidelines v3.2024
- Prior Authorization Guidelines — Oncology Section 4.2
- AMA CPT 2024 E/M Coding Guidelines
- Payment Integrity Policy — Upcoding Detection Section 2.4
- AI Governance Framework — Section 5 (human oversight requirements)

---

## Demo Scenarios

Three pre-loaded scenarios designed to produce meaningfully different pipeline behaviors:

| Scenario | What It Tests |
|---|---|
| Rural Imaging Outlier | Fairness — are rural providers being unfairly benchmarked? |
| Experimental Oncology Treatment | Evidence gaps + patient access when no alternative exists |
| Repeated Upcoding Pattern | Clean fraud signal — all governance checks pass |

---

## Key Design Decisions

**Why sequential chaining?** Context accumulates across agents. Agent 3 reasons over a scenario that has already been classified and enriched with policy evidence — producing qualitatively better output than four isolated calls.

**Why a dedicated governance agent?** Ethics embedded in Agent 3 produces blended output. An independent Agent 4 produces a clean, auditable governance record that is separable from the clinical recommendation — mirroring how regulated AI systems actually work.

**Why FAISS over simulated retrieval?** Hardcoded policy injection demonstrates the concept but not the technology. Real vector similarity search with sentence-transformer embeddings demonstrates the actual capability.

**Why decision support, not decision making?** LLMs hallucinate. CMS requires denial rationale. The False Claims Act creates liability for automated adverse actions. Human-in-the-loop isn't a limitation — it's the correct architecture for AI operating in regulated healthcare contexts.

---

## Local Setup

```bash
git clone https://github.com/sauravi-5/Agentic-Clinical-Decision-Support-POC.git
cd Agentic-Clinical-Decision-Support-POC

pip install -r requirements.txt

export ANTHROPIC_API_KEY=your_key_here
python main.py

# Visit http://localhost:8000
```

---

## Project Structure

```
main.py               FastAPI app, routes, static serving
scenarios.py          3 pre-loaded demo scenarios
agents/
    pipeline.py       4-agent orchestrator
    rag.py            FAISS index, embedding, retrieval
data/
    policies.py       7 healthcare policy document chunks
static/
    index.html        Frontend UI
    style.css         Styling
    app.js            Pipeline animation + result rendering
requirements.txt
render.yaml           Render.com deployment config
```

---

## Sources

American Medical Association. (2024). *CPT 2024 Professional Edition.*

Centers for Medicare & Medicaid Services. (2024). *CMS Interoperability and Prior Authorization Final Rule (CMS-4201-F).*

Johnson, J., Douze, M., & Jégou, H. (2021). Billion-scale similarity search with GPUs. *IEEE Transactions on Big Data, 7*(3), 535–547.

Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *NeurIPS 33*, 9459–9474.

National Comprehensive Cancer Network. (2024). *NCCN Guidelines: NSCLC v3.2024.*

Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. *EMNLP 2019.*

Wei, J., et al. (2022). Chain-of-thought prompting elicits reasoning in large language models. *NeurIPS 35*, 24824–24837.
