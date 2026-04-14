import json
from extraction.schema import SCHEMA
from config import MAX_DOC_CHARS


def build_extraction_prompt(document_text: str) -> str:
    if len(document_text) > MAX_DOC_CHARS:
        document_text = document_text[:MAX_DOC_CHARS] + "\n\n[... truncated ...]"

    return f"""You are a legal AI specializing in data centre lease agreements.
Your job is to extract structured information from the lease document below.

=== STRICT OUTPUT RULES ===
- Return ONLY a single valid JSON object. No explanation. No markdown. No backticks.
- Every field must be filled. If not found in the document, write "Not specified".
- "risk_flags" MUST be a JSON array of strings — find at least 3-5 risks from the document.
- "summary" MUST be a paragraph of 3-5 sentences describing the key terms of the lease.
- Do NOT return empty arrays [] or empty strings "" for risk_flags or summary.

=== RISK FLAGS GUIDANCE ===
Look for risks such as:
- High early exit penalties
- Aggressive auto-renewal clauses
- Low SLA credits vs high downtime impact
- Liability caps that may be insufficient
- Unilateral change of control rights
- Escalation clauses (rent increases)
- Short maintenance notice windows
- Audit limitations
- One-sided indemnification
- Data privacy obligations

=== SUMMARY GUIDANCE ===
Write a 3-5 sentence paragraph covering:
- Who are the parties and what is the lease for
- Key financial terms (rent, deposit, escalation)
- Term and renewal details
- Most important risk or obligation for the Lessee

=== SCHEMA TO FOLLOW ===
{json.dumps(SCHEMA, indent=2)}

=== DOCUMENT ===
{document_text}

=== REMINDER ===
You MUST populate "risk_flags" as a non-empty array and "summary" as a non-empty string.
Return ONLY the JSON object. No other text whatsoever."""