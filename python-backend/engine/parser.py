"""Parser module — port of lib/quality-evaluation/parser.ts.

CSV, JSON, and Markdown table parsing with validation.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from engine.schemas import validate_import_record


# ─── Parse Result ───────────────────────────────────────────────────────────


@dataclass
class ParseResult:
    records: list[dict[str, Any]] = field(default_factory=list)
    issues: list[dict[str, Any]] = field(default_factory=list)


# ─── CSV Parsing ────────────────────────────────────────────────────────────


def parse_csv_line(line: str) -> list[str]:
    """Parse a single CSV line respecting quoted fields.

    Handles commas inside quotes and escaped quotes ("").
    """
    fields: list[str] = []
    current = ""
    in_quotes = False
    i = 0

    while i < len(line):
        ch = line[i]

        if in_quotes:
            if ch == '"':
                # Check for escaped quote ""
                if i + 1 < len(line) and line[i + 1] == '"':
                    current += '"'
                    i += 2
                    continue
                # End of quoted field
                in_quotes = False
                i += 1
                continue
            current += ch
            i += 1
        else:
            if ch == '"':
                in_quotes = True
                i += 1
                continue
            if ch == ',':
                fields.append(current)
                current = ""
                i += 1
                continue
            current += ch
            i += 1

    fields.append(current)
    return fields


def split_csv_lines(content: str) -> list[str]:
    """Split CSV content into logical lines, handling newlines inside quoted fields."""
    lines: list[str] = []
    current = ""
    in_quotes = False
    i = 0

    while i < len(content):
        ch = content[i]

        if ch == '"':
            # Check for escaped quote
            if in_quotes and i + 1 < len(content) and content[i + 1] == '"':
                current += '""'
                i += 2
                continue
            in_quotes = not in_quotes
            current += ch
            i += 1
            continue

        if not in_quotes and (
            ch == '\n' or (ch == '\r' and i + 1 < len(content) and content[i + 1] == '\n')
        ):
            lines.append(current)
            current = ""
            if ch == '\r':
                i += 2
            else:
                i += 1
            continue

        if not in_quotes and ch == '\r':
            # Bare \r
            lines.append(current)
            current = ""
            i += 1
            continue

        current += ch
        i += 1

    if len(current) > 0:
        lines.append(current)

    return lines


def coerce_value(value: str) -> Any:
    """Attempt to coerce a string value to the appropriate Python type.

    Handles numbers, booleans, JSON arrays, null/undefined → None.
    """
    trimmed = value.strip()

    if trimmed == "" or trimmed.lower() == "null" or trimmed.lower() == "undefined":
        return None

    # Boolean
    if trimmed.lower() == "true":
        return True
    if trimmed.lower() == "false":
        return False

    # Number
    if re.match(r'^-?\d+(\.\d+)?$', trimmed):
        num = float(trimmed)
        # Return int if it's a whole number
        if '.' not in trimmed:
            return int(trimmed)
        return num

    # JSON array (e.g. ["a","b"])
    if trimmed.startswith('[') and trimmed.endswith(']'):
        try:
            return json.loads(trimmed)
        except (json.JSONDecodeError, ValueError):
            pass  # Not valid JSON array, return as string

    return trimmed


def check_encoding(content: str, issues: list[dict[str, Any]]) -> None:
    """Check for encoding issues in content.
    BOM is silently stripped by the parsers — no warning needed since Excel
    and many Windows tools add it by default.
    """
    # Check for null bytes
    if '\0' in content:
        issues.append({
            "severity": "error",
            "message": "File contains null bytes — possible encoding issue",
        })


def get_id_field(dataset_type: str) -> str | list[str] | None:
    """Get the ID field name(s) for a given dataset type (used for duplicate detection).

    Returns a single field name, or a list of field names for composite keys.
    """
    if dataset_type == "real-input":
        return "recordId"
    elif dataset_type == "accuracy-golden-set":
        return "testCaseId"
    elif dataset_type == "consistency-golden-set":
        return ["sourceTestCaseId", "variantId"]
    elif dataset_type == "status-mapping":
        return "statusCode"
    elif dataset_type == "reference-catalog":
        return None
    else:
        return None


def check_duplicate_ids(
    records: list[dict[str, Any]],
    dataset_type: str,
    issues: list[dict[str, Any]],
) -> None:
    """Check for duplicate IDs and add issues.

    Supports single-field and composite (multi-field) keys.
    """
    id_field = get_id_field(dataset_type)
    if id_field is None:
        return

    fields = id_field if isinstance(id_field, list) else [id_field]
    label = "+".join(fields)

    seen: dict[str, int] = {}
    for i, record in enumerate(records):
        parts = [record.get(f) for f in fields]
        # Only check if all key parts are non-empty strings
        if all(isinstance(p, str) and len(p.strip()) > 0 for p in parts):
            composite_key = "::".join(parts)
            prev = seen.get(composite_key)
            if prev is not None:
                if len(fields) == 1:
                    display = f'{fields[0]} "{parts[0]}"'
                else:
                    display = ", ".join(f'{f}="{p}"' for f, p in zip(fields, parts))
                issues.append({
                    "row": i + 1,
                    "field": label,
                    "severity": "warning",
                    "message": f"Duplicate {label} {display} (first seen at row {prev})",
                })
            else:
                seen[composite_key] = i + 1


def parse_production_csv(
    lines: list[str],
    issues: list[dict[str, Any]],
) -> ParseResult:
    """Parse a single-column production CSV (header: "query") into RealInputRecords.

    Maps query → sanitizedText, auto-generates recordId and observedAt.
    """
    records: list[dict[str, Any]] = []
    row_index = 0

    for i in range(1, len(lines)):
        fields = parse_csv_line(lines[i])
        raw_query = fields[0] if len(fields) > 0 else ""

        # Normalize embedded newlines to a single space, collapse multiple spaces, then trim
        query_value = re.sub(r'\r\n|\n', ' ', raw_query)
        query_value = re.sub(r' {2,}', ' ', query_value)
        query_value = query_value.strip()

        # Skip empty or whitespace-only rows with a warning
        if query_value == "":
            issues.append({
                "row": i + 1,  # 1-based row number (header is row 1, data starts at row 2)
                "severity": "warning",
                "message": f"Skipped empty or whitespace-only query at row {i + 1}",
            })
            continue

        row_index += 1

        # Detect PII placeholders ({ADDRESS} or {NAME}) — {LOCATION} is NOT PII
        pii_detected = bool(re.search(r'\{(ADDRESS|NAME)\}', query_value))

        record: dict[str, Any] = {
            "recordId": f"prod-{row_index}",
            "observedAt": datetime.now(timezone.utc).isoformat(),
            "sanitizedText": query_value,
        }
        if pii_detected:
            record["protectedClassHint"] = "pii-related"

        validation = validate_import_record(record, "real-input")
        if not validation.valid:
            for err in validation.errors:
                issues.append({"row": i, "severity": "error", "message": err})

        records.append(record)

    return ParseResult(records=records, issues=issues)


def parse_csv(content: str, dataset_type: str) -> ParseResult:
    """Parse CSV text into typed records with validation."""
    issues: list[dict[str, Any]] = []

    check_encoding(content, issues)

    # Strip BOM if present
    cleaned = content[1:] if len(content) > 0 and ord(content[0]) == 0xFEFF else content

    lines = split_csv_lines(cleaned)

    if len(lines) == 0:
        issues.append({"severity": "error", "message": "CSV file is empty"})
        return ParseResult(records=[], issues=issues)

    header_line = lines[0]
    headers = [h.strip() for h in parse_csv_line(header_line)]

    if len(headers) == 0 or (len(headers) == 1 and headers[0] == ""):
        issues.append({"severity": "error", "message": "CSV file has no headers"})
        return ParseResult(records=[], issues=issues)

    # Production CSV detection: single-column "query" header for real-input datasets
    if len(headers) == 1 and headers[0] == "query" and dataset_type == "real-input":
        return parse_production_csv(lines, issues)
    if len(headers) == 1 and headers[0] != "query" and dataset_type == "real-input":
        issues.append({
            "severity": "error",
            "message": f'Single-column CSV has header "{headers[0]}" but expected "query" for real-input dataset type',
        })
        return ParseResult(records=[], issues=issues)

    records: list[dict[str, Any]] = []

    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "":
            continue  # skip blank lines

        values = parse_csv_line(line)

        if len(values) != len(headers):
            issues.append({
                "row": i,
                "severity": "warning",
                "message": f"Row {i} has {len(values)} fields but expected {len(headers)}",
            })

        record: dict[str, Any] = {}
        for j in range(len(headers)):
            raw = values[j] if j < len(values) else ""
            val = coerce_value(raw)
            if val is not None:
                record[headers[j]] = val

        # Validate record
        validation = validate_import_record(record, dataset_type)
        if not validation.valid:
            for err in validation.errors:
                issues.append({
                    "row": i,
                    "severity": "error",
                    "message": err,
                })

        records.append(record)

    check_duplicate_ids(records, dataset_type, issues)

    return ParseResult(records=records, issues=issues)


# ─── JSON Parsing ───────────────────────────────────────────────────────────


def parse_json(content: str, dataset_type: str) -> ParseResult:
    """Parse JSON text into typed records with validation."""
    issues: list[dict[str, Any]] = []

    check_encoding(content, issues)

    # Strip BOM if present
    cleaned = content[1:] if len(content) > 0 and ord(content[0]) == 0xFEFF else content

    try:
        parsed = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError) as e:
        issues.append({
            "severity": "error",
            "message": f"Invalid JSON: {e}",
        })
        return ParseResult(records=[], issues=issues)

    # Accept either an array or an object with a data/records array
    raw_records: list[Any]
    if isinstance(parsed, list):
        raw_records = parsed
    elif isinstance(parsed, dict):
        if isinstance(parsed.get("data"), list):
            raw_records = parsed["data"]
        elif isinstance(parsed.get("records"), list):
            raw_records = parsed["records"]
        else:
            issues.append({
                "severity": "error",
                "message": 'JSON must be an array or an object with a "data" or "records" array',
            })
            return ParseResult(records=[], issues=issues)
    else:
        issues.append({
            "severity": "error",
            "message": 'JSON must be an array or an object with a "data" or "records" array',
        })
        return ParseResult(records=[], issues=issues)

    records: list[dict[str, Any]] = []

    for i, item in enumerate(raw_records):
        if item is None or not isinstance(item, dict):
            issues.append({
                "row": i + 1,
                "severity": "error",
                "message": f"Record at index {i} is not an object",
            })
            continue

        record: dict[str, Any] = item

        validation = validate_import_record(record, dataset_type)
        if not validation.valid:
            for err in validation.errors:
                issues.append({
                    "row": i + 1,
                    "severity": "error",
                    "message": err,
                })

        records.append(record)

    check_duplicate_ids(records, dataset_type, issues)

    return ParseResult(records=records, issues=issues)


# ─── Golden Set Header Mapping & Helpers ────────────────────────────────────

ACCURACY_HEADER_MAP: dict[str, str] = {
    "Test Case#": "testCaseId",
    "Business requirement": "businessRequirement",
    "Scenario": "scenario",
    "Free-text input": "freeTextInput",
    "Expected options, status": "_combinedOptionsStatus",
}

CONSISTENCY_HEADER_MAP: dict[str, str] = {
    "Source Test Case#": "sourceTestCaseId",
    "Variant Type": "variantId",
    "Business requirement": "businessRequirement",
    "Scenario": "scenario",
    "Free-text input": "freeTextInput",
    "Expected options/status": "_combinedOptionsStatus",
}


def split_options_status(value: str) -> dict[str, Any]:
    """Split a combined options/status string into expectedOptions and expectedStatus.

    Examples:
      "Facilities: Free Wi-Fi; Status: MAPPED_AND_APPLIED"
        → {"expectedOptions": ["Facilities: Free Wi-Fi"], "expectedStatus": "MAPPED_AND_APPLIED"}
      ""
        → {"expectedOptions": []}
    """
    trimmed = value.strip()
    if trimmed == "":
        return {"expectedOptions": []}

    segments = trimmed.split("; ")

    # Find the segment starting with 'Status:' (case-insensitive)
    status_idx = -1
    for idx, s in enumerate(segments):
        if s.strip().lower().startswith("status:"):
            status_idx = idx
            break

    if status_idx == -1:
        # No Status: segment — entire value is a single-element expectedOptions array
        return {"expectedOptions": [trimmed]}

    option_segments = [s.strip() for s in segments[:status_idx] if s.strip()]
    status_value = re.sub(r'^status:\s*', '', segments[status_idx].strip(), flags=re.IGNORECASE).strip()

    result: dict[str, Any] = {"expectedOptions": option_segments}
    if status_value:
        result["expectedStatus"] = status_value

    return result


def apply_golden_set_transform(
    record: dict[str, Any],
    dataset_type: str,
) -> dict[str, Any]:
    """Post-process a parsed record for golden set dataset types.

    Remaps human-readable header keys to camelCase field names,
    splits the combined options/status column, and injects defaults
    for canonicalIntent and goldenSetVersion.
    """
    header_map = (
        ACCURACY_HEADER_MAP if dataset_type == "accuracy-golden-set" else CONSISTENCY_HEADER_MAP
    )

    # Remap keys using the header map
    transformed: dict[str, Any] = {}
    for key, value in record.items():
        mapped_key = header_map.get(key, key)
        transformed[mapped_key] = value

    # Split _combinedOptionsStatus into expectedOptions and expectedStatus
    if isinstance(transformed.get("_combinedOptionsStatus"), str):
        split_result = split_options_status(transformed["_combinedOptionsStatus"])
        del transformed["_combinedOptionsStatus"]
        transformed["expectedOptions"] = split_result["expectedOptions"]
        if "expectedStatus" in split_result:
            transformed["expectedStatus"] = split_result["expectedStatus"]
    else:
        transformed.pop("_combinedOptionsStatus", None)

    # Set canonicalIntent to the scenario field value if not already present
    if "canonicalIntent" not in transformed and isinstance(transformed.get("scenario"), str):
        transformed["canonicalIntent"] = transformed["scenario"]

    # Set goldenSetVersion to '1.0' if not already present
    if "goldenSetVersion" not in transformed:
        transformed["goldenSetVersion"] = "1.0"

    return transformed


# ─── Markdown Table Parsing ─────────────────────────────────────────────────


def _parse_markdown_row(line: str) -> list[str]:
    """Parse a Markdown table row into cell values."""
    trimmed = line.strip()
    stripped = trimmed[1:] if trimmed.startswith("|") else trimmed
    without_trailing = stripped[:-1] if stripped.endswith("|") else stripped
    return [cell.strip() for cell in without_trailing.split("|")]


def _is_separator_row(line: str) -> bool:
    """Check if a line is a Markdown table separator (e.g. |---|---|)."""
    trimmed = line.strip()
    return bool(re.match(r'^\|?[\s:]*-{2,}[\s:]*(\|[\s:]*-{2,}[\s:]*)*\|?$', trimmed))


def parse_markdown_table(content: str, dataset_type: str) -> ParseResult:
    """Parse Markdown table text into typed records with validation."""
    issues: list[dict[str, Any]] = []

    check_encoding(content, issues)

    # Strip BOM if present
    cleaned = content[1:] if len(content) > 0 and ord(content[0]) == 0xFEFF else content

    lines = [l for l in re.split(r'\r?\n', cleaned) if l.strip()]

    # Find the header row (first line containing |)
    header_idx = -1
    for i, line in enumerate(lines):
        if "|" in line and not _is_separator_row(line):
            header_idx = i
            break

    if header_idx == -1:
        issues.append({"severity": "error", "message": "No Markdown table header found"})
        return ParseResult(records=[], issues=issues)

    headers = _parse_markdown_row(lines[header_idx])

    if len(headers) == 0 or (len(headers) == 1 and headers[0] == ""):
        issues.append({"severity": "error", "message": "Markdown table has no headers"})
        return ParseResult(records=[], issues=issues)

    records: list[dict[str, Any]] = []

    # Process data rows (skip header and separator)
    for i in range(header_idx + 1, len(lines)):
        line = lines[i]
        if _is_separator_row(line):
            continue
        if "|" not in line:
            continue

        values = _parse_markdown_row(line)
        row_num = i + 1

        if len(values) != len(headers):
            issues.append({
                "row": row_num,
                "severity": "warning",
                "message": f"Row {row_num} has {len(values)} cells but expected {len(headers)}",
            })

        record: dict[str, Any] = {}
        for j in range(len(headers)):
            raw = values[j] if j < len(values) else ""
            val = coerce_value(raw)
            if val is not None:
                record[headers[j]] = val

        # Apply golden set transform if applicable
        if dataset_type in ("accuracy-golden-set", "consistency-golden-set"):
            record = apply_golden_set_transform(record, dataset_type)

        validation = validate_import_record(record, dataset_type)
        if not validation.valid:
            for err in validation.errors:
                issues.append({
                    "row": row_num,
                    "severity": "error",
                    "message": err,
                })

        records.append(record)

    check_duplicate_ids(records, dataset_type, issues)

    return ParseResult(records=records, issues=issues)
