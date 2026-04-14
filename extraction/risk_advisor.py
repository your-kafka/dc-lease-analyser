import os
from dotenv import load_dotenv
from groq import Groq
from config import GROQ_MODEL_ID


def get_risk_solutions(risk_flags: list) -> list:
    """
    Takes a list of risk flag strings and returns a list of dicts:
    [ { "risk": "...", "solution": "..." }, ... ]
    """
    if not risk_flags:
        return []

    load_dotenv()
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Format risks as a numbered list for the prompt
    risks_text = "\n".join(f"{i+1}. {risk}" for i, risk in enumerate(risk_flags))

    prompt = f"""You are a legal and commercial advisor specializing in data centre colocation contracts.

Below are key risks identified in a data centre lease agreement.
For each risk, provide a clear, practical, and actionable solution or mitigation strategy.

=== RISKS ===
{risks_text}

=== INSTRUCTIONS ===
- Respond ONLY in valid JSON format. No markdown. No backticks. No explanation outside JSON.
- Return a JSON array where each element has exactly two fields: "risk" and "solution".
- "risk" should be the original risk text (copy exactly).
- "solution" should be 2-4 sentences: specific, practical advice a Lessee's legal team can act on.
- Cover negotiation tactics, contract clause amendments, or protective measures.

=== EXAMPLE FORMAT ===
[
  {{
    "risk": "High early exit penalty of 3 months MRC",
    "solution": "Negotiate to reduce the early exit penalty to 1-2 months MRC. Request a sliding scale where the penalty decreases the longer the Lessee has been in the agreement. Ensure the clause distinguishes between termination due to Lessor's breach vs convenience."
  }}
]

Now generate solutions for all {len(risk_flags)} risks listed above.
Return ONLY the JSON array."""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL_ID,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        import json, re
        raw = response.choices[0].message.content.strip()

        # Clean markdown fences if any
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()

        parsed = None
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract array from response
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group())
                except Exception:
                    pass

        if parsed and isinstance(parsed, list):
            return parsed

        # Fallback: return risks without solutions
        return [{"risk": r, "solution": "Could not generate solution."} for r in risk_flags]

    except Exception as e:
        return [{"risk": r, "solution": f"Error: {str(e)}"} for r in risk_flags]