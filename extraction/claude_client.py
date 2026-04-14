import json
import re
import os
from dotenv import load_dotenv
from groq import Groq
from config import GROQ_MODEL_ID, MAX_TOKENS


def call_groq(prompt: str) -> dict:
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL_ID,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        raw = response.choices[0].message.content.strip()

        # ❌ Empty response check
        if not raw:
            return {
                "status": "empty_response",
                "raw_output": raw
            }

        # ✅ Clean markdown fences
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()

        # ✅ Try parsing JSON
        parsed = None
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group())
                except Exception:
                    pass

        # ❌ If still failed
        if parsed is None:
            return {
                "status": "invalid_json",
                "raw_output": raw
            }

        # ✅ SUCCESS
        return parsed

    except Exception as e:
        return {
            "status": "unexpected_error",
            "error": str(e)
        }