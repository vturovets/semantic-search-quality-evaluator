"""Property 1: Parse-Serialize Round Trip

For any valid set of records and for any supported format (CSV, JSON, Markdown),
serializing the records to that format and then parsing the result back should
produce a set of records equivalent to the original.

**Validates: Requirements 3.1, 3.3, 3.4, 3.10, 3.11**
"""

from __future__ import annotations

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from engine.parser import parse_csv, parse_json, parse_markdown_table
from engine.serializer import serialize_to_csv, serialize_to_json, serialize_to_markdown


# ─── Hypothesis Strategies ───────────────────────────────────────────────────

# Generate safe strings that survive the coerce_value round-trip.
# Avoid: pipes (Markdown cell separator), newlines, null chars, BOM,
# leading/trailing whitespace, and values that coerce_value would transform
# (numbers like "00", booleans like "true", null-like "null"/"undefined",
# JSON arrays like "[...]").
_safe_char = st.sampled_from(
    "abcdefghijklmnopqrstuvwxyz _-."
)
_safe_str = st.text(alphabet=_safe_char, min_size=1, max_size=30).filter(
    lambda s: (
        s.strip() == s
        and s.strip() != ""
        and s.strip().lower() not in ("null", "undefined", "true", "false")
        and not s.strip().startswith("[")
    )
)

# Header names: simple alphanumeric, no special chars
_header_name = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz"),
    min_size=1,
    max_size=10,
)


@st.composite
def _record_set(draw):
    """Generate a list of records with consistent headers and safe string values."""
    n_headers = draw(st.integers(min_value=1, max_value=5))
    headers = draw(
        st.lists(_header_name, min_size=n_headers, max_size=n_headers, unique=True)
    )
    n_records = draw(st.integers(min_value=1, max_value=5))
    records = []
    for _ in range(n_records):
        rec = {}
        for h in headers:
            rec[h] = draw(_safe_str)
        records.append(rec)
    return records


# ─── Property Tests ─────────────────────────────────────────────────────────
# Feature: python-analysis-backend, Property 1: Parse-Serialize Round Trip


@given(records=_record_set())
@settings(max_examples=100)
def test_csv_roundtrip(records):
    """Serializing records to CSV and parsing back produces equivalent records."""
    csv_text = serialize_to_csv(records)
    result = parse_csv(csv_text, "reference-catalog")

    assert len(result.records) == len(records)
    for orig, parsed in zip(records, result.records):
        for key in orig:
            assert key in parsed, f"Missing key {key} in parsed record"
            assert str(parsed[key]) == str(orig[key]), (
                f"Value mismatch for key {key}: {parsed[key]!r} != {orig[key]!r}"
            )


@given(records=_record_set())
@settings(max_examples=100)
def test_json_roundtrip(records):
    """Serializing records to JSON and parsing back produces equivalent records."""
    json_text = serialize_to_json(records)
    result = parse_json(json_text, "reference-catalog")

    assert len(result.records) == len(records)
    for orig, parsed in zip(records, result.records):
        for key in orig:
            assert key in parsed, f"Missing key {key} in parsed record"
            assert parsed[key] == orig[key], (
                f"Value mismatch for key {key}: {parsed[key]!r} != {orig[key]!r}"
            )


@given(records=_record_set())
@settings(max_examples=100)
def test_markdown_roundtrip(records):
    """Serializing records to Markdown and parsing back produces equivalent records."""
    md_text = serialize_to_markdown(records)
    result = parse_markdown_table(md_text, "reference-catalog")

    assert len(result.records) == len(records)
    for orig, parsed in zip(records, result.records):
        for key in orig:
            assert key in parsed, f"Missing key {key} in parsed record"
            assert str(parsed[key]) == str(orig[key]), (
                f"Value mismatch for key {key}: {parsed[key]!r} != {orig[key]!r}"
            )
