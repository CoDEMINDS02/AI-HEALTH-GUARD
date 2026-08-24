import re

from app.schemas.reports import LabFinding, ReportFindings

LAB_LINE_RE = re.compile(
    r"^\s*(?P<name>[A-Za-z][A-Za-z0-9 ()/%\-\.,]{0,48}?)\s*[:=]\s*"
    r"(?P<value>[+-]?\d+(?:\.\d+)?)\s*"
    r"(?P<unit>[a-zA-Zµ%°/\^\*\d\.\-]+)?"
    r"(?P<rest>.*)$"
)

RANGE_RE = re.compile(
    r"(?P<lo>[+-]?\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(?P<hi>[+-]?\d+(?:\.\d+)?)"
)

NOTE_PREFIXES = ("impression", "comment", "remark", "interpretation", "note")


def parse_reference_range(rest: str) -> str | None:
    lowered = rest.lower()
    if "ref" not in lowered and "(" not in rest and "[" not in rest:
        return None
    match = RANGE_RE.search(rest)
    if not match:
        return None
    return f"{match.group('lo')}-{match.group('hi')}"


def compute_flag(value: float | None, reference: str | None) -> str:
    if value is None or not reference:
        return "unknown"
    lo, hi = reference.split("-")
    try:
        low, high = float(lo), float(hi)
    except ValueError:
        return "unknown"
    if high < low:
        low, high = high, low
    if value < low:
        return "low"
    if value > high:
        return "high"
    return "normal"


def normalize_report(text: str) -> ReportFindings:
    findings: list[LabFinding] = []
    notes: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        lowered = stripped.lower()
        if any(lowered.startswith(prefix) for prefix in NOTE_PREFIXES):
            notes.append(stripped[:500])
            continue

        match = LAB_LINE_RE.match(line)
        if not match:
            continue

        name = match.group("name").strip().rstrip(":").strip()
        value_str = match.group("value")
        unit = (match.group("unit") or "").strip() or None
        rest = match.group("rest") or ""

        if unit and unit.lower() in {"ref", "reference", "range", "rr"}:
            unit = None

        reference = parse_reference_range(rest)
        numeric_value = float(value_str)
        findings.append(
            LabFinding(
                name=name[:120],
                value=value_str,
                numeric_value=numeric_value,
                unit=(unit[:24] if unit else None),
                reference_range=reference,
                flag=compute_flag(numeric_value, reference),
            )
        )

    flagged_count = sum(1 for f in findings if f.flag in ("high", "low", "abnormal"))
    summary = (
        f"Extracted {len(findings)} structured value(s); {flagged_count} appear outside their "
        f"typical range. Values are reproduced as written; nothing was inferred."
        if findings
        else "No structured laboratory-style values were recognized in the extracted text."
    )

    return ReportFindings(findings=findings, notes=notes, summary=summary, extraction_status="parsed")
