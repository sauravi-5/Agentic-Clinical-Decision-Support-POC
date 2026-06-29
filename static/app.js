/* ── Scenario Loading ──────────────────────────────────────── */
async function loadScenarios() {
  try {
    const res = await fetch("/scenarios");
    const { scenarios } = await res.json();
    const container = document.getElementById("scenarioButtons");
    scenarios.forEach(s => {
      const btn = document.createElement("button");
      btn.className = "scenario-btn";
      btn.textContent = s.title;
      btn.title = s.description;
      btn.onclick = () => {
        document.querySelectorAll(".scenario-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById("scenarioText").value = s.text;
      };
      container.appendChild(btn);
    });
  } catch (e) {
    console.error("Failed to load scenarios", e);
  }
}

/* ── Pipeline Node State ───────────────────────────────────── */
function setNode(id, state) {
  const node = document.getElementById(`node${id}`);
  const status = node.querySelector(".node-status");
  node.className = `pipeline-node ${state}`;
  status.className = `node-status ${state}`;
  const labels = { idle: "Waiting", active: "Running…", done: "Complete" };
  status.textContent = labels[state] || state;
}

function resetNodes() {
  [1, 2, 3, 4].forEach(i => setNode(i, "idle"));
}

/* ── Confidence Ring ───────────────────────────────────────── */
function setConfidence(value) {
  const pct = Math.round(value * 100);
  const circumference = 213.6;
  const offset = circumference - (pct / 100) * circumference;
  document.getElementById("confidenceRing").style.strokeDashoffset = offset;
  document.getElementById("confidenceLabel").textContent = `${pct}%`;
}

/* ── Render Helpers ────────────────────────────────────────── */
function kv(key, val) {
  return `<div class="kv-row"><span class="kv-key">${key}</span><span class="kv-val">${val}</span></div>`;
}

function tags(arr, cls = "tag-purple") {
  return (arr || []).map(t => `<span class="tag ${cls}">${t}</span>`).join(" ");
}

function renderClassification(data) {
  const el = document.getElementById("classificationBody");
  el.innerHTML = `
    ${kv("Case Type", `<strong>${data.case_type}</strong>`)}
    ${kv("Clinical Domain", data.clinical_domain)}
    ${kv("Geographic Context", data.geographic_context)}
    ${kv("Population Vulnerability", data.population_vulnerability)}
    <div class="kv-row">
      <span class="kv-key">Primary Signals</span>
      <span class="kv-val">${tags(data.primary_signals)}</span>
    </div>
    <div class="kv-row">
      <span class="kv-key">Risk Indicators</span>
      <span class="kv-val">${tags(data.risk_indicators, "tag-gray")}</span>
    </div>
    ${kv("Summary", `<em>${data.summary}</em>`)}
  `;
}

function renderPolicies(data) {
  const el = document.getElementById("policyBody");
  el.innerHTML = data.retrieved_policies.map(p => `
    <div class="policy-item">
      <div class="policy-source">📄 ${p.source}</div>
      <div class="policy-excerpt">${p.excerpt}</div>
      <div class="policy-score">Relevance: ${Math.round(p.relevance_score * 100)}%</div>
    </div>
  `).join("");
}

function renderReasoning(data) {
  const el = document.getElementById("reasoningBody");
  const steps = (data.reasoning_steps || []).map(s => `
    <div class="step-item">
      <div class="step-num">${s.step}</div>
      <div class="step-content">
        <div class="step-label">${s.label}</div>
        <div class="step-finding">${s.finding}</div>
      </div>
    </div>
  `).join("");

  const evidence = (data.supporting_evidence || []).map(e => `<li>${e}</li>`).join("");
  const gaps = (data.gaps_in_evidence || []).map(g => `<li>${g}</li>`).join("");

  el.innerHTML = `
    <div class="section-label">CHAIN OF REASONING</div>
    <div class="reasoning-steps">${steps}</div>
    <div class="section-label">SUPPORTING EVIDENCE</div>
    <ul class="evidence-list">${evidence}</ul>
    <div class="section-label">EVIDENCE GAPS</div>
    <ul class="gap-list">${gaps}</ul>
    <div class="section-label">RATIONALE</div>
    <p style="font-size:0.87rem;line-height:1.6;color:var(--text)">${data.rationale}</p>
  `;
}

function renderGovernance(data) {
  const el = document.getElementById("governanceBody");
  const checkNames = {
    fairness: "Fairness",
    evidence_sufficiency: "Evidence Sufficiency",
    explainability: "Explainability",
    confidence_threshold: "Confidence Threshold",
    human_oversight: "Human Oversight",
  };

  const checks = Object.entries(data.governance_checks || {}).map(([key, val]) => `
    <div class="gov-check ${val.status}">
      <div class="gov-check-name">${checkNames[key] || key}</div>
      <div class="gov-check-status">${val.status === "Pass" ? "✓ Pass" : val.status === "Warning" ? "⚠ Warning" : "✗ Fail"}</div>
      <div class="gov-check-finding">${val.finding}</div>
    </div>
  `).join("");

  const equityConcerns = (data.equity_concerns || []).map(c =>
    `<span class="tag tag-gray">${c}</span>`
  ).join(" ");

  const reviewClass = data.human_review_required ? "required" : "not-required";
  const reviewIcon  = data.human_review_required ? "👤" : "✅";
  const reviewTitle = data.human_review_required ? "Human Review Required" : "No Human Review Required";

  el.innerHTML = `
    <div class="section-label">GOVERNANCE CHECKS</div>
    <div class="gov-grid">${checks}</div>
    ${equityConcerns ? `
      <div class="section-label">EQUITY CONCERNS</div>
      <div style="margin-bottom:14px">${equityConcerns}</div>
    ` : ""}
    <div class="section-label">OVERSIGHT DETERMINATION</div>
    <div class="human-review-box ${reviewClass}">
      <span class="review-icon">${reviewIcon}</span>
      <div>
        <div class="review-title">${reviewTitle}</div>
        <div class="review-reason">${data.human_review_reason || data.governance_summary || ""}</div>
      </div>
    </div>
  `;
}

function renderBanner(result) {
  document.getElementById("recValue").textContent = result.final_recommendation;
  document.getElementById("recSub").textContent = result.human_review_required
    ? `⚠ Human review required — ${result.human_review_reason}`
    : "✓ Sufficient confidence for automated processing";
  setConfidence(result.confidence);
}

/* ── Main Analyze Flow ─────────────────────────────────────── */
async function analyze() {
  const scenario = document.getElementById("scenarioText").value.trim();
  if (!scenario) return alert("Please enter or select a scenario.");

  // UI reset
  const btn = document.getElementById("analyzeBtn");
  document.getElementById("btnText").textContent = "Running Pipeline…";
  document.getElementById("btnSpinner").classList.remove("hidden");
  btn.disabled = true;

  document.getElementById("pipelineSection").classList.remove("hidden");
  document.getElementById("results").classList.add("hidden");
  resetNodes();

  // Only mark Agent 1 as active immediately — rest wait for real data
  setNode(1, "active");

  try {
    const res = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Pipeline failed");
    }

    const result = await res.json();

    // Step through nodes sequentially with short visual delays
    // so the pipeline animation feels earned rather than fake
    const stepDelay = ms => new Promise(r => setTimeout(r, ms));

    setNode(1, "done"); setNode(2, "active");
    await stepDelay(400);
    setNode(2, "done"); setNode(3, "active");
    await stepDelay(400);
    setNode(3, "done"); setNode(4, "active");
    await stepDelay(400);
    setNode(4, "done");

    // Render results
    renderBanner(result);
    renderClassification(result.agents.classification);
    renderPolicies(result.agents.policy_retrieval);
    renderReasoning(result.agents.reasoning);
    renderGovernance(result.agents.governance);

    document.getElementById("results").classList.remove("hidden");
    document.getElementById("results").scrollIntoView({ behavior: "smooth", block: "start" });

  } catch (err) {
    alert(`Error: ${err.message}`);
    resetNodes();
  } finally {
    document.getElementById("btnText").textContent = "Run Agent Pipeline";
    document.getElementById("btnSpinner").classList.add("hidden");
    btn.disabled = false;
  }
}

/* ── Init ──────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", loadScenarios);