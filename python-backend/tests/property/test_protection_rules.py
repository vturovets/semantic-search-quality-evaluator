"""Property 17: Protection Rule Enforcement

For any recommendation of type reduce-retire-obsolete where isProtected is true
and the reason does not contain "governance-approved", the protection rules
should convert it to type no-update with actionability protected-override.

**Validates: Requirements 8.4**
"""

from __future__ import annotations

# Feature: python-analysis-backend, Property 17: Protection Rule Enforcement

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from engine.protection_rules import (
    PROTECTED_CLASSES,
    is_protected,
    enforce_protection_rules,
)

# ─── Strategies ──────────────────────────────────────────────────────────────

_protected_class = st.sampled_from(PROTECTED_CLASSES)

_reason_without_governance = st.text(min_size=1, max_size=100).filter(
    lambda s: "governance-approved" not in s.lower()
)

_reason_with_governance = st.text(min_size=0, max_size=50).map(
    lambda s: f"{s} governance-approved {s}"
)

_enabled_rules = st.lists(
    st.fixed_dictionaries({
        "protectedClass": _protected_class,
        "description": st.just("test rule"),
        "enabled": st.just(True),
    }),
    min_size=1,
    max_size=5,
)


def _retirement_rec(reason_st=_reason_without_governance, is_protected_val=True):
    return st.fixed_dictionaries({
        "type": st.just("reduce-retire-obsolete"),
        "isProtected": st.just(is_protected_val),
        "protectedClasses": st.lists(_protected_class, min_size=0, max_size=2),
        "reason": reason_st,
        "actionability": st.sampled_from([
            "action-ready", "monitor", "insufficient-evidence",
        ]),
        "recommendationId": st.text(min_size=1, max_size=10),
        "runId": st.just("test-run"),
        "affectedGoldenSet": st.just("accuracy"),
        "impactedIntentId": st.text(min_size=1, max_size=10),
    })


# ─── Property Tests ─────────────────────────────────────────────────────────


@given(
    rec=_retirement_rec(reason_st=_reason_without_governance, is_protected_val=True),
    rules=_enabled_rules,
)
@settings(max_examples=100)
def test_protected_retirement_without_governance_becomes_no_update(rec, rules):
    """Protected reduce-retire-obsolete without governance-approved -> no-update + protected-override."""
    result = enforce_protection_rules([rec], rules)

    assert len(result) == 1
    assert result[0]["type"] == "no-update"
    assert result[0]["actionability"] == "protected-override"
    assert result[0]["reason"].startswith("[Protected case — retirement blocked]")


@given(
    rec=_retirement_rec(reason_st=_reason_with_governance, is_protected_val=True),
    rules=_enabled_rules,
)
@settings(max_examples=100)
def test_protected_retirement_with_governance_stays(rec, rules):
    """Protected reduce-retire-obsolete with governance-approved stays as-is."""
    result = enforce_protection_rules([rec], rules)

    assert len(result) == 1
    assert result[0]["type"] == "reduce-retire-obsolete"


@given(
    rec=_retirement_rec(reason_st=_reason_without_governance, is_protected_val=False),
)
@settings(max_examples=100)
def test_non_protected_retirement_stays(rec):
    """Non-protected reduce-retire-obsolete stays as-is (no protectedClasses match)."""
    # Use empty rules so no classes are enabled
    result = enforce_protection_rules([rec], [])

    assert len(result) == 1
    assert result[0]["type"] == "reduce-retire-obsolete"


@given(
    non_retire_type=st.sampled_from([
        "add-new-intent", "add-examples-for-intent", "no-update",
        "add-paraphrase-variants", "create-paraphrase-group",
    ]),
    rules=_enabled_rules,
)
@settings(max_examples=100)
def test_non_retirement_types_unaffected(non_retire_type, rules):
    """Non reduce-retire-obsolete types are never modified by protection rules."""
    rec = {
        "type": non_retire_type,
        "isProtected": True,
        "protectedClasses": ["policy-blocked"],
        "reason": "some reason",
        "actionability": "action-ready",
    }

    result = enforce_protection_rules([rec], rules)

    assert len(result) == 1
    assert result[0]["type"] == non_retire_type


@given(
    record_classes=st.lists(_protected_class, min_size=1, max_size=3),
)
@settings(max_examples=100)
def test_is_protected_with_matching_enabled_rules(record_classes):
    """isProtected returns True when record has protectedClasses matching enabled rules."""
    rules = [
        {"protectedClass": record_classes[0], "description": "test", "enabled": True},
    ]
    record = {"protectedClasses": record_classes}

    assert is_protected(record, rules) is True


@given(
    record_class=_protected_class,
    rule_class=_protected_class,
)
@settings(max_examples=100)
def test_is_protected_false_when_no_match(record_class, rule_class):
    """isProtected returns False when no enabled rule matches."""
    assume(record_class != rule_class)
    rules = [
        {"protectedClass": rule_class, "description": "test", "enabled": True},
    ]
    record = {"protectedClasses": [record_class]}

    # Only false if the single class doesn't match
    result = is_protected(record, rules)
    assert result is False


@given(record_class=_protected_class)
@settings(max_examples=100)
def test_is_protected_false_when_rules_disabled(record_class):
    """isProtected returns False when all rules are disabled."""
    rules = [
        {"protectedClass": record_class, "description": "test", "enabled": False},
    ]
    record = {"protectedClasses": [record_class]}

    assert is_protected(record, rules) is False
