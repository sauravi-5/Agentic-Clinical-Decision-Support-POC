POLICY_DOCUMENTS = [
    {
        "id": "imaging_policy_1",
        "source": "Medical Imaging Utilization Policy — Section 3.1",
        "text": (
            "Advanced imaging (MRI, CT, PET) requires documented clinical necessity. "
            "Volume outliers exceeding 2x regional peer benchmarks trigger utilization review. "
            "Geographic access limitations may be considered as mitigating factors in frontier "
            "and rural Health Professional Shortage Areas (HPSAs) as designated by HRSA."
        ),
    },
    {
        "id": "imaging_policy_2",
        "source": "CMS Rural Health Policy — Section 7",
        "text": (
            "Providers serving communities classified as Rural or Frontier under RUCA codes "
            "5–10 are recognized to face higher per-capita service burdens due to specialist "
            "shortages. Utilization patterns for such providers should be benchmarked against "
            "rural-adjusted peer groups rather than statewide or national averages."
        ),
    },
    {
        "id": "prior_auth_1",
        "source": "Prior Authorization Guideline — Oncology Section 4.2",
        "text": (
            "Immunotherapy agents including PD-1/PD-L1 inhibitors (e.g., pembrolizumab, nivolumab) "
            "require documented PD-L1 expression testing results and evidence of disease progression "
            "on at least one prior line of systemic therapy for second-line or later authorization. "
            "Phase III randomized controlled trial evidence is the preferred evidence standard; "
            "Phase II or real-world evidence may be considered when Phase III data is unavailable "
            "for the specific indication."
        ),
    },
    {
        "id": "prior_auth_2",
        "source": "NCCN Clinical Practice Guideline — NSCLC v3.2024",
        "text": (
            "For metastatic NSCLC with PD-L1 TPS ≥50%, pembrolizumab monotherapy is a Category 1 "
            "preferred recommendation for first-line therapy. For PD-L1 TPS 1–49%, pembrolizumab "
            "combination therapy is preferred. Second-line immunotherapy following prior platinum-based "
            "chemotherapy is supported for patients with adequate performance status (ECOG 0–2)."
        ),
    },
    {
        "id": "coding_policy_1",
        "source": "E/M Coding Guidelines — AMA CPT 2024",
        "text": (
            "CPT 99215 (Office/Outpatient Visit, High Complexity) requires medical decision making "
            "of high complexity OR total time of 55 minutes or more on the date of encounter. "
            "High complexity MDM requires at least two of: multiple chronic conditions with severe "
            "exacerbation; drug therapy requiring intensive monitoring; or diagnosis/treatment "
            "significantly limited by social determinants of health."
        ),
    },
    {
        "id": "coding_policy_2",
        "source": "Payment Integrity Policy — Upcoding Detection Section 2.4",
        "text": (
            "Statistical outlier analysis for E/M code distribution compares provider-level "
            "utilization of high-complexity codes (99214–99215) against specialty- and geography-adjusted "
            "peer benchmarks. Providers exceeding the 95th percentile for 99215 frequency without "
            "corresponding documentation of high-complexity encounters are subject to pre-payment "
            "review and potential recoupment under the False Claims Act framework."
        ),
    },
    {
        "id": "governance_1",
        "source": "AI Governance Framework for Healthcare — Section 5",
        "text": (
            "Automated clinical decision support systems must maintain human oversight for all "
            "decisions affecting patient access to care. Final determinations on prior authorization, "
            "claim denial, or provider investigation must involve a qualified clinical reviewer "
            "when algorithmic confidence is below 90% or when equity concerns are flagged. "
            "All AI-assisted recommendations must be explainable and auditable."
        ),
    },
]
