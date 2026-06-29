SCENARIOS = [
    {
        "id": "rural_imaging",
        "title": "Rural Imaging Outlier",
        "description": "Highlights fairness and contextual interpretation",
        "text": (
            "A rural Montana provider has submitted imaging claims at 3.2x the regional average "
            "over the past 6 months. The provider serves a frontier community with no specialist "
            "within 150 miles. Claims include repeated MRI and CT for chronic conditions including "
            "COPD, diabetes, and cardiovascular disease. No billing irregularities detected in "
            "code usage, but volume triggers an automated fraud flag."
        ),
    },
    {
        "id": "oncology_auth",
        "title": "Experimental Oncology Treatment",
        "description": "Highlights evidence limitations and patient access",
        "text": (
            "A prior authorization request has been submitted for pembrolizumab (Keytruda) in a "
            "67-year-old Stage IV non-small cell lung cancer patient with PD-L1 expression of 60%. "
            "The patient has exhausted two prior lines of therapy. No FDA-approved generic "
            "alternative exists. Payer policy requires Phase III trial evidence; available data "
            "includes one Phase II trial and two retrospective cohort studies."
        ),
    },
    {
        "id": "upcoding_pattern",
        "title": "Repeated Upcoding Pattern",
        "description": "Highlights strong fraud indicators with minimal governance concerns",
        "text": (
            "A suburban outpatient clinic has submitted 14 claims over 30 days using CPT 99215 "
            "(high-complexity office visit) for patients whose documented encounter notes reflect "
            "routine follow-ups for hypertension and medication refills. Peer comparison shows "
            "the clinic uses 99215 at 4.7x the rate of similar practices in the same ZIP code. "
            "Documentation does not support the complexity level billed."
        ),
    },
]
