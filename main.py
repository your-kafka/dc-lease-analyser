"""
DC Lease Extractor — main entry point.
Usage:
    python main.py lease.pdf
    python main.py lease.docx --json out.json --txt out.txt
"""
import os
import sys
import argparse
import time

sys.path.insert(0, os.path.dirname(__file__))

from loaders.loader import load_document
from prompts.extraction_prompt import build_extraction_prompt
from extraction.claude_client import call_groq
from extraction.risk_advisor import get_risk_solutions
from output.report_formatter import format_report
from output.json_saver import save_json


def clean_text(text):
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text


def run(file_path: str, output_json: str = None, output_txt: str = None):
    start_time = time.time()

    # -------- 1. LOAD -------- #
    print(f"[1/4] Loading  →  {file_path}")
    try:
        text, file_type = load_document(file_path)
        text = clean_text(text)
        print(f"       {file_type.upper()} | {len(text.split()):,} words")
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return

    # -------- 2. EXTRACT -------- #
    print("[2/4] Extracting  →  Groq API")
    try:
        prompt = build_extraction_prompt(text)
        extracted = call_groq(prompt)
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        return

    if not extracted:
        print("⚠️ Warning: No data extracted")

    # -------- 3. RISK SOLUTIONS -------- #
    print("[3/4] Generating risk solutions  →  Groq API")
    risk_solutions = []
    try:
        risk_flags = extracted.get("analysis", {}).get("risk_flags", [])
        if risk_flags:
            risk_solutions = get_risk_solutions(risk_flags)
            print(f"       {len(risk_solutions)} risk(s) analyzed")
        else:
            print("       ⚠️ No risk flags found to analyze")
    except Exception as e:
        print(f"⚠️ Could not generate risk solutions: {e}")

    # -------- 4. FORMAT -------- #
    try:
        report = format_report(extracted, file_path, file_type, "Groq API", risk_solutions)
    except Exception as e:
        print(f"❌ Error formatting report: {e}")
        return

    # -------- 5. SAVE OUTPUTS -------- #
    print("[4/4] Saving outputs")

    if output_json:
        try:
            extracted["risk_solutions"] = risk_solutions
            save_json(extracted, file_path, file_type, "Groq API", output_json)
            print(f"       JSON  →  {output_json}")
        except Exception as e:
            print(f"⚠️ Failed to save JSON: {e}")

    if output_txt:
        try:
            with open(output_txt, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"       TXT   →  {output_txt}")
        except Exception as e:
            print(f"⚠️ Failed to save TXT: {e}")

    # -------- FINAL OUTPUT -------- #
    elapsed = time.time() - start_time
    print(f"\n⏱ Completed in {elapsed:.2f}s\n")
    print(report)
    return extracted


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract key details from a DC lease agreement."
    )
    parser.add_argument("file", help="Path to PDF / DOCX / TXT file")
    parser.add_argument("--json", dest="output_json", help="Save JSON to this path")
    parser.add_argument("--txt",  dest="output_txt",  help="Save report to this path")
    args = parser.parse_args()

    run(args.file, args.output_json, args.output_txt)