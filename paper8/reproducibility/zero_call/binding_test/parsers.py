"""Prospectively frozen deterministic parsers for Binding Test choices.

The parser never assigns an ordinal value to unavailable, refusal, or invalid
responses. Strict-format validity and semantic validity are retained
separately so a permissive semantic parse cannot erase contract failures.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
import re
from typing import Any, Mapping


class ChoiceCategory(str, Enum):
    LOW = "L"
    HIGH = "H"
    UNAVAILABLE = "U"


@dataclass(frozen=True)
class ParseResult:
    category: ChoiceCategory
    strict_valid: bool
    semantic_valid: bool
    reason: str
    raw_text: str | None

    @property
    def available(self) -> bool:
        return self.category in (ChoiceCategory.LOW, ChoiceCategory.HIGH)


_FENCED_JSON = re.compile(
    r"\A```(?:json)?\s*(\{.*\})\s*```\Z",
    flags=re.IGNORECASE | re.DOTALL,
)
_DISPLAY_CHOICE = re.compile(r"\APLAN:(A|B)\Z")


def _exact_choice_object(value: Any) -> ChoiceCategory | None:
    if not isinstance(value, dict) or set(value) != {"choice"}:
        return None
    choice = value.get("choice")
    if not isinstance(choice, str):
        return None
    normalized = choice.strip().upper()
    if normalized == "L":
        return ChoiceCategory.LOW
    if normalized == "H":
        return ChoiceCategory.HIGH
    return None


def _strict_choice_json(text: str) -> ChoiceCategory | None:
    """Return a choice only for a one-pair JSON object with an exact value.

    ``dict`` decoding silently overwrites duplicate keys, which would let a
    malformed transport payload enter the strict ledger.  Decoding into an
    ordered pair list keeps that failure observable.
    """

    try:
        pairs = json.loads(text, object_pairs_hook=lambda value: value)
    except (json.JSONDecodeError, TypeError):
        return None
    if pairs == [("choice", "L")]:
        return ChoiceCategory.LOW
    if pairs == [("choice", "H")]:
        return ChoiceCategory.HIGH
    return None


def _explicit_refusal(text: str) -> bool:
    upper = text.strip().upper()
    if upper in {"REFUSAL", "REFUSE", "UNAVAILABLE"}:
        return True
    try:
        value = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return False
    return isinstance(value, dict) and set(value) == {"status"} and str(
        value.get("status", "")
    ).strip().lower() in {"refusal", "unavailable"}


def parse_choice(raw_text: str | None, *, transport_error: bool = False) -> ParseResult:
    """Parse a choice under the frozen strict-then-semantic policy.

    Strict-valid output is exactly one JSON object with the single key
    ``choice`` and value ``L`` or ``H``. The semantic parser additionally
    accepts an exact single token or an otherwise empty fenced JSON block.
    All other responses remain in the non-ordinal unavailable category.
    """

    if transport_error:
        return ParseResult(
            ChoiceCategory.UNAVAILABLE,
            strict_valid=False,
            semantic_valid=False,
            reason="transport_error",
            raw_text=raw_text,
        )
    if raw_text is None:
        return ParseResult(
            ChoiceCategory.UNAVAILABLE,
            strict_valid=False,
            semantic_valid=False,
            reason="missing_response",
            raw_text=None,
        )

    text = raw_text.strip()
    if not text:
        return ParseResult(
            ChoiceCategory.UNAVAILABLE,
            strict_valid=False,
            semantic_valid=False,
            reason="empty_response",
            raw_text=raw_text,
        )
    if _explicit_refusal(text):
        return ParseResult(
            ChoiceCategory.UNAVAILABLE,
            strict_valid=False,
            semantic_valid=False,
            reason="explicit_refusal",
            raw_text=raw_text,
        )

    strict_choice = _strict_choice_json(text)
    if strict_choice is not None:
        return ParseResult(
            strict_choice,
            strict_valid=True,
            semantic_valid=True,
            reason="strict_json",
            raw_text=raw_text,
        )

    token = text.upper()
    if token in {"L", "H"}:
        return ParseResult(
            ChoiceCategory(token),
            strict_valid=False,
            semantic_valid=True,
            reason="exact_token",
            raw_text=raw_text,
        )

    fenced = _FENCED_JSON.fullmatch(text)
    if fenced:
        fenced_choice = _strict_choice_json(fenced.group(1))
        if fenced_choice is not None:
            return ParseResult(
                fenced_choice,
                strict_valid=False,
                semantic_valid=True,
                reason="fenced_json",
                raw_text=raw_text,
            )

    return ParseResult(
        ChoiceCategory.UNAVAILABLE,
        strict_valid=False,
        semantic_valid=False,
        reason="invalid_or_ambiguous",
        raw_text=raw_text,
    )


def parse_display_choice(
    raw_text: str | None,
    *,
    displayed_label_to_canonical: Mapping[str, str],
    transport_error: bool = False,
) -> ParseResult:
    """Parse the item bank's counterbalanced ``PLAN:A``/``PLAN:B`` surface.

    This is deliberately strict-only: after trimming ASCII whitespace, no
    prose, synonym, or inferred-intent recovery is attempted.  Canonical
    recoding uses the frozen presentation variant and is retained internally;
    it is never echoed to the model-visible event stream.
    """

    normalized_mapping = {
        label: str(value).strip().upper()
        for label, value in displayed_label_to_canonical.items()
    }
    normalized_mapping = {
        label: ({"LOW": "L", "HIGH": "H"}.get(value, value))
        for label, value in normalized_mapping.items()
    }
    if set(normalized_mapping) != {"A", "B"} or set(normalized_mapping.values()) != {
        "L",
        "H",
    }:
        raise ValueError("display mapping must bijectively map A/B to low/high")
    if transport_error:
        return ParseResult(
            ChoiceCategory.UNAVAILABLE,
            strict_valid=False,
            semantic_valid=False,
            reason="transport_error",
            raw_text=raw_text,
        )
    if raw_text is None:
        return ParseResult(
            ChoiceCategory.UNAVAILABLE,
            strict_valid=False,
            semantic_valid=False,
            reason="missing_response",
            raw_text=None,
        )

    raw_match = _DISPLAY_CHOICE.fullmatch(raw_text)
    text = raw_text.strip(" \t\r\n\f\v")
    match = _DISPLAY_CHOICE.fullmatch(text)
    if match is None:
        return ParseResult(
            ChoiceCategory.UNAVAILABLE,
            strict_valid=False,
            semantic_valid=False,
            reason="invalid_display_choice",
            raw_text=raw_text,
        )
    category = ChoiceCategory(normalized_mapping[match.group(1)])
    return ParseResult(
        category,
        strict_valid=raw_match is not None,
        semantic_valid=True,
        reason=(
            "strict_display_choice_recode"
            if raw_match is not None
            else "ascii_trimmed_display_choice_recode"
        ),
        raw_text=raw_text,
    )
