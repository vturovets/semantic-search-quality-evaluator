"""Property 2: Value Coercion Consistency

For any string representation of a number, boolean, JSON array, or null/undefined
value, the parser's coercion function should produce the correct Python type, and
re-stringifying then coercing again should yield the same value.

**Validates: Requirements 3.9**
"""

from __future__ import annotations

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from engine.parser import coerce_value


# ─── Hypothesis Strategies ───────────────────────────────────────────────────

# Integer strings
_int_str = st.integers(min_value=-999999, max_value=999999).map(str)

# Float strings (with decimal point)
_float_str = st.tuples(
    st.integers(min_value=-9999, max_value=9999),
    st.integers(min_value=0, max_value=9999),
).map(lambda t: f"{t[0]}.{t[1]}")

# Boolean strings
_bool_str = st.sampled_from(["true", "false", "True", "False", "TRUE", "FALSE"])

# Null/undefined strings
_null_str = st.sampled_from(["", "null", "NULL", "Null", "undefined", "UNDEFINED", "Undefined"])

# JSON array strings
_json_array_str = st.lists(
    st.text(
        alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789"),
        min_size=1,
        max_size=10,
    ),
    min_size=0,
    max_size=5,
).map(lambda items: "[" + ",".join(f'"{item}"' for item in items) + "]")

# Plain strings that won't be coerced to other types
_plain_str = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz "),
    min_size=1,
    max_size=20,
).filter(lambda s: s.strip() not in ("", "null", "undefined", "true", "false"))


# ─── Property Tests ─────────────────────────────────────────────────────────
# Feature: python-analysis-backend, Property 2: Value Coercion Consistency


@given(s=_int_str)
@settings(max_examples=100)
def test_integer_coercion(s):
    """Integer strings are coerced to int and re-coercion is idempotent."""
    result = coerce_value(s)
    assert isinstance(result, int)
    assert result == int(s)
    # Re-stringify and coerce again
    result2 = coerce_value(str(result))
    assert result2 == result


@given(s=_float_str)
@settings(max_examples=100)
def test_float_coercion(s):
    """Float strings are coerced to float and re-coercion is idempotent."""
    result = coerce_value(s)
    assert isinstance(result, float)
    assert result == float(s)
    # Re-stringify and coerce again
    result2 = coerce_value(str(result))
    # Float re-stringification may differ in format, but value should match
    assert isinstance(result2, (int, float))
    assert float(result2) == result


@given(s=_bool_str)
@settings(max_examples=100)
def test_boolean_coercion(s):
    """Boolean strings are coerced to bool and re-coercion is idempotent."""
    result = coerce_value(s)
    assert isinstance(result, bool)
    expected = s.strip().lower() == "true"
    assert result == expected
    # Re-stringify and coerce again
    result2 = coerce_value(str(result))
    assert result2 == result


@given(s=_null_str)
@settings(max_examples=100)
def test_null_coercion(s):
    """Empty/null/undefined strings are coerced to None."""
    result = coerce_value(s)
    assert result is None


@given(s=_json_array_str)
@settings(max_examples=100)
def test_json_array_coercion(s):
    """JSON array strings are coerced to list."""
    result = coerce_value(s)
    assert isinstance(result, list)


@given(s=_plain_str)
@settings(max_examples=100)
def test_plain_string_passthrough(s):
    """Plain strings that don't match any coercion pattern are returned as-is (trimmed)."""
    result = coerce_value(s)
    assert isinstance(result, str)
    assert result == s.strip()
