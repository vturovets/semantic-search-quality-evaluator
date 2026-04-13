"""Priority Rules — port of lib/quality-evaluation/priority-rules.ts.

Deterministic priority scoring for recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


# ─── PriorityInput ──────────────────────────────────────────────────────────


@dataclass
class PriorityInput:
    """Input factors for deterministic priority scoring.

    Each field maps to a weighted component in the scoring algorithm.
    """

    observed_share_percent: float
    """Observed real-input share as a percentage (e.g. 3.0 means 3%)."""

    actionability: Literal[
        "action-ready", "monitor", "insufficient-evidence", "protected-override"
    ]
    """Statistical actionability classification for the intent."""

    is_protected: bool
    """Whether the intent/record is protected."""

    representation_delta: float
    """Representation delta between real-input share and golden-set share."""

    affects_governance: bool
    """Whether the recommendation affects governance coverage."""

    affects_accuracy: bool
    """Whether the recommendation affects accuracy coverage."""

    affects_consistency: bool
    """Whether the recommendation affects consistency coverage."""


# ─── Actionability score lookup ─────────────────────────────────────────────

ACTIONABILITY_SCORES: dict[str, int] = {
    "action-ready": 25,
    "monitor": 10,
    "insufficient-evidence": 0,
    "protected-override": 20,
}


# ─── computePriority ────────────────────────────────────────────────────────


def compute_priority(
    input_: PriorityInput,
) -> Literal["critical", "high", "medium", "low"]:
    """Compute a deterministic 4-level priority from weighted scoring factors.

    Scoring breakdown (max 100 points):
    - Frequency/share weight:   0-30 pts  (observedSharePercent * 10, capped at 30)
    - Actionability weight:     0-25 pts  (lookup by classification)
    - Protected-case boost:     0-20 pts  (flat 20 when isProtected)
    - Gap size weight:          0-15 pts  (|representationDelta| * 5, capped at 15)
    - Coverage type weight:     0-10 pts  (governance > accuracy > consistency)

    Thresholds: >= 70 -> critical, >= 45 -> high, >= 25 -> medium, else low.
    """
    score = 0.0

    # Frequency/share weight (0-30 points)
    score += min(30, input_.observed_share_percent * 10)

    # Actionability weight (0-25 points)
    score += ACTIONABILITY_SCORES.get(input_.actionability, 0)

    # Protected-case boost (0-20 points)
    if input_.is_protected:
        score += 20

    # Gap size weight (0-15 points)
    score += min(15, abs(input_.representation_delta) * 5)

    # Coverage type weight (0-10 points)
    if input_.affects_governance:
        score += 10
    elif input_.affects_accuracy:
        score += 7
    elif input_.affects_consistency:
        score += 5

    # Thresholds
    if score >= 70:
        return "critical"
    if score >= 45:
        return "high"
    if score >= 25:
        return "medium"
    return "low"
