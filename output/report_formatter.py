from datetime import datetime
from pathlib import Path

SECTION_TITLES = {
    "parties":           "CONTRACTING PARTIES",
    "agreement_details": "AGREEMENT DETAILS",
    "financial_terms":   "FINANCIAL TERMS",
    "infrastructure":    "INFRASTRUCTURE & SPACE",
    "sla":               "SLA & UPTIME",
    "liability":         "LIABILITY & LEGAL",
    "termination":       "TERMINATION",
    "compliance":        "SECURITY & COMPLIANCE",
    "analysis":          "RISK ANALYSIS"
}


def _val(v) -> str:
    if v is None:
        return "—  (not found)"
    return str(v)


def _wrap(text: str, width: int, indent: int = 4) -> list:
    """Word-wrap a long string into lines of max `width` chars with `indent` spaces."""
    words = text.split()
    lines = []
    current = " " * indent
    for word in words:
        if len(current) + len(word) + 1 > width:
            lines.append(current)
            current = " " * indent + word
        else:
            current = current + " " + word if current.strip() else " " * indent + word
    if current.strip():
        lines.append(current)
    return lines


def format_report(extracted: dict, file_path: str, file_type: str, method: str,
                  risk_solutions: list = None) -> str:
    W = 72
    lines = [
        "=" * W,
        "  DATA CENTRE LEASE — EXTRACTED KEY DETAILS".center(W),
        "=" * W,
        f"  File    : {Path(file_path).name}",
        f"  Type    : {file_type.upper()}",
        f"  Method  : {method}",
        f"  Run at  : {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * W,
        "",
    ]

    is_structured = any(k in extracted for k in SECTION_TITLES)

    if is_structured:
        for key, title in SECTION_TITLES.items():
            section = extracted.get(key)
            if not section:
                continue

            lines.append(f"  {'─' * (W - 4)}")
            lines.append(f"  {title}")
            lines.append(f"  {'─' * (W - 4)}")

            if key == "analysis":
                # Summary
                summary = section.get("summary", "")
                if summary:
                    lines.append(f"  {'Summary'.ljust(30)}")
                    for wrap_line in _wrap(summary, W - 4, indent=4):
                        lines.append(wrap_line)
                    lines.append("")

                # Risk flags (plain list — solutions shown separately below)
                risk_flags = section.get("risk_flags", [])
                if risk_flags:
                    lines.append(f"  {'Risk Flags'.ljust(30)}")
                    for item in risk_flags:
                        lines.append(f"    ⚠️  {item}")
                lines.append("")

            else:
                for field, value in section.items():
                    label = field.replace("_", " ").title().ljust(30)
                    lines.append(f"  {label}  {_val(value)}")
                lines.append("")

    else:
        lines.append(f"  {'─' * (W - 4)}")
        lines.append("  EXTRACTED FIELDS")
        lines.append(f"  {'─' * (W - 4)}")
        for field, value in extracted.items():
            label = field.replace("_", " ").title().ljust(30)
            if isinstance(value, list):
                lines.append(f"  {label}")
                for item in value:
                    lines.append(f"    ⚠️  {item}")
            else:
                lines.append(f"  {label}  {_val(value)}")
        lines.append("")

    # ── RISK SOLUTIONS SECTION ──────────────────────────────────────────────
    if risk_solutions:
        lines.append("=" * W)
        lines.append("  RISK MITIGATION RECOMMENDATIONS".center(W))
        lines.append("=" * W)
        lines.append("")

        for i, item in enumerate(risk_solutions, 1):
            risk     = item.get("risk", "Unknown risk")
            solution = item.get("solution", "No solution available.")

            lines.append(f"  {'─' * (W - 4)}")
            lines.append(f"  RISK {i}")
            lines.append(f"  {'─' * (W - 4)}")

            lines.append(f"  ⚠️  Risk:")
            for wrap_line in _wrap(risk, W - 4, indent=6):
                lines.append(wrap_line)
            lines.append("")

            lines.append(f"  ✅  Recommendation:")
            for wrap_line in _wrap(solution, W - 4, indent=6):
                lines.append(wrap_line)
            lines.append("")

    lines += ["=" * W]
    return "\n".join(lines)