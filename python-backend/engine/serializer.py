"""Serializer module — port of serialization functions from lib/quality-evaluation/parser.ts.

CSV, JSON, and Markdown table serialization.
"""

from __future__ import annotations

import json
from typing import Any


def escape_csv_field(value: Any) -> str:
    """Escape a value for CSV output."""
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        s = json.dumps(value)
    else:
        s = str(value)
    if ',' in s or '"' in s or '\n' in s or '\r' in s:
        return '"' + s.replace('"', '""') + '"'
    return s


def serialize_to_csv(records: list[dict[str, Any]]) -> str:
    """Serialize records to CSV format."""
    if len(records) == 0:
        return ""

    # Collect all unique keys across all records for headers
    header_set: dict[str, None] = {}
    for rec in records:
        for key in rec:
            header_set[key] = None
    headers = list(header_set.keys())

    lines: list[str] = [",".join(headers)]
    for rec in records:
        row = [escape_csv_field(rec.get(h)) for h in headers]
        lines.append(",".join(row))

    return "\n".join(lines)


def serialize_to_json(records: list[dict[str, Any]]) -> str:
    """Serialize records to JSON format."""
    return json.dumps(records, indent=2)


def escape_md_cell(value: Any) -> str:
    """Escape a value for Markdown table cell."""
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        s = json.dumps(value)
    else:
        s = str(value)
    return s.replace("|", "\\|").replace("\n", " ")


def serialize_to_markdown(records: list[dict[str, Any]]) -> str:
    """Serialize records to Markdown table format."""
    if len(records) == 0:
        return ""

    header_set: dict[str, None] = {}
    for rec in records:
        for key in rec:
            header_set[key] = None
    headers = list(header_set.keys())

    lines: list[str] = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")

    for rec in records:
        row = [escape_md_cell(rec.get(h)) for h in headers]
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def serialize_records(records: list[dict[str, Any]], fmt: str) -> str:
    """Serialize typed records back to CSV, JSON, or Markdown table format."""
    if fmt == "csv":
        return serialize_to_csv(records)
    elif fmt == "json":
        return serialize_to_json(records)
    elif fmt == "markdown":
        return serialize_to_markdown(records)
    else:
        raise ValueError(f"Unsupported export format: {fmt}")
