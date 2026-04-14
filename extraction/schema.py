SCHEMA = {
    "parties": {
        "lessor": "",
        "lessee": ""
    },

    "agreement_details": {
        "agreement_date": "",       # YYYY-MM-DD
        "effective_date": "",       # YYYY-MM-DD
        "expiry_date": "",          # YYYY-MM-DD
        "term_years": "",
        "auto_renewal": "",
        "governing_law": ""
    },

    "financial_terms": {
        "monthly_rent": "",
        "security_deposit": "",
        "payment_due_days": "",
        "late_payment_penalty": "",
        "price_escalation": "",
        "power_rate": "",
        "cross_connect_fee": "",
        "remote_hands_rate": ""
    },

    "infrastructure": {
        "facility_address": "",
        "cabinets_count": "",
        "cage_sqft": "",
        "power_kw": "",
        "cooling_type": "",
        "connectivity": ""   # comma-separated list preferred
    },

    "sla": {
        "uptime_sla": "",
        "network_sla": "",
        "sla_remedy": "",
        "sla_exclusions": "",
        "maintenance_window": "",
        "mttr_hours": ""
    },

    "liability": {
        "liability_cap": "",
        "consequential_damages_excluded": "",  # yes/no
        "indemnification": "",
        "insurance_required": ""
    },

    "termination": {
        "notice_period": "",
        "termination_for_cause": "",
        "termination_convenience": "",
        "early_exit_penalty": "",
        "change_of_control": ""
    },

    "compliance": {
        "certifications": "",     # comma-separated
        "physical_security": "",
        "audit_rights": "",
        "data_privacy": ""
    },

    "analysis": {
        "risk_flags": [],         # list of strings
        "summary": ""             # short paragraph
    }
}