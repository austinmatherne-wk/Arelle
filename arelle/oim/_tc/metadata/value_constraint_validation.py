"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from collections.abc import Generator, Mapping
from dataclasses import dataclass
from decimal import InvalidOperation

import regex

from arelle.ModelValue import QName
from arelle.oim._tc.const import (
    TCME_ILLEGAL_CONSTRAINT,
    TCME_UNKNOWN_DURATION_TYPE,
    TCME_UNKNOWN_PERIOD_TYPE,
    TCME_UNKNOWN_TYPE,
)
from arelle.oim._tc.metadata.common import TCMetadataValidationError
from arelle.oim._tc.metadata.constraint_value_parser import ParsedValue, parse_constraint_value
from arelle.oim._tc.metadata.model import TCValueConstraint
from arelle.oim._tc.metadata.restrictions import TCRestriction, applicable_restrictions
from arelle.oim._tc.metadata.types import resolve_effective_lexical_type
from arelle.typing import TypeGetText
from arelle.XmlValidate import XsdPattern

_: TypeGetText

_VALID_DURATION_TYPES = frozenset(
    {
        "yearMonth",
        "dayTime",
    }
)

_VALID_PERIOD_TYPES = frozenset(
    {
        "year",
        "half",
        "quarter",
        "week",
        "month",
        "day",
        "instant",
    }
)


class TCMetadataIllegalConstraintError(TCMetadataValidationError):
    def __init__(self, message: str, *paths: str) -> None:
        primary, *related = paths
        super().__init__(
            message,
            primary,
            code=TCME_ILLEGAL_CONSTRAINT,
            related_paths=[(r,) for r in related],
        )


def validate_value_constraint(
    constraint: TCValueConstraint,
    namespaces: Mapping[str, str],
) -> Generator[TCMetadataValidationError, None, None]:
    """Yields TCMetadataValidationError with relative path segments.

    The caller is responsible for prepending the full path prefix via prepend_path().
    """
    effective_lexical_type = resolve_effective_lexical_type(constraint.type, namespaces)
    if effective_lexical_type is None:
        yield TCMetadataValidationError(
            _("Unknown type: '{}'").format(constraint.type),
            "type",
            code=TCME_UNKNOWN_TYPE,
        )
        return
    yield from _validate_restrictions_applicability(constraint, effective_lexical_type)
    yield from _validate_patterns_restriction(constraint)
    yield from _validate_length_restrictions(constraint)
    yield from _validate_bounds_restrictions(constraint, effective_lexical_type)
    yield from _validate_digit_restrictions(constraint)
    yield from _validate_period_type_restriction(constraint)
    yield from _validate_duration_type_restriction(constraint)


def _validate_restrictions_applicability(
    constraint: TCValueConstraint,
    effective_lexical_type: QName,
) -> Generator[TCMetadataValidationError, None, None]:
    applied_restrictions = {
        restriction for restriction in TCRestriction if getattr(constraint, restriction.attr_name, None) is not None
    }
    permitted_restrictions = applicable_restrictions(constraint.type, effective_lexical_type)
    if disallowed_restrictions := sorted(applied_restrictions - permitted_restrictions):
        yield TCMetadataIllegalConstraintError(
            _("Constraint of type '{}' must not define restrictions '{}'").format(
                constraint.type,
                ", ".join(disallowed_restrictions),
            ),
            "type",
            *disallowed_restrictions,
        )


def _validate_period_type_restriction(
    constraint: TCValueConstraint,
) -> Generator[TCMetadataValidationError, None, None]:
    if constraint.period_type is not None and constraint.period_type not in _VALID_PERIOD_TYPES:
        yield TCMetadataValidationError(
            _("Unknown period type: '{}'").format(constraint.period_type),
            TCRestriction.PERIOD_TYPE,
            code=TCME_UNKNOWN_PERIOD_TYPE,
        )


def _validate_duration_type_restriction(
    constraint: TCValueConstraint,
) -> Generator[TCMetadataValidationError, None, None]:
    if constraint.duration_type is not None and constraint.duration_type not in _VALID_DURATION_TYPES:
        yield TCMetadataValidationError(
            _("Unknown duration type: '{}'").format(constraint.duration_type),
            TCRestriction.DURATION_TYPE,
            code=TCME_UNKNOWN_DURATION_TYPE,
        )


def _validate_patterns_restriction(constraint: TCValueConstraint) -> Generator[TCMetadataValidationError, None, None]:
    if constraint.patterns is None:
        return
    invalid_patterns = sorted(pattern for pattern in constraint.patterns if not _is_valid_pattern(pattern))
    if invalid_patterns:
        yield TCMetadataIllegalConstraintError(
            _("Patterns {} are not valid XSD regular expressions").format(invalid_patterns), TCRestriction.PATTERNS
        )


def _is_valid_pattern(pattern: str) -> bool:
    try:
        XsdPattern.compile(pattern)
    except regex.error:
        return False
    return True


def _validate_length_restrictions(constraint: TCValueConstraint) -> Generator[TCMetadataValidationError, None, None]:
    if constraint.length is not None:
        conflictingProperties = []
        if constraint.min_length is not None:
            conflictingProperties.append(TCRestriction.MIN_LENGTH)
        if constraint.max_length is not None:
            conflictingProperties.append(TCRestriction.MAX_LENGTH)
        if conflictingProperties:
            yield TCMetadataIllegalConstraintError(
                _("length must not be specified together with {}").format(" or ".join(conflictingProperties)),
                TCRestriction.LENGTH,
                *conflictingProperties,
            )

    min_length = constraint.min_length
    max_length = constraint.max_length
    if min_length is not None and max_length is not None and min_length > max_length:
        yield TCMetadataIllegalConstraintError(
            _("minLength ({}) must be less than or equal to maxLength ({})").format(min_length, max_length),
            TCRestriction.MIN_LENGTH,
            TCRestriction.MAX_LENGTH,
        )


def _validate_digit_restrictions(constraint: TCValueConstraint) -> Generator[TCMetadataValidationError, None, None]:
    total_digits = constraint.total_digits
    if total_digits is not None and total_digits < 1:
        yield TCMetadataIllegalConstraintError(
            _("totalDigits must be a positive integer, got {}").format(total_digits),
            TCRestriction.TOTAL_DIGITS,
        )

    fraction_digits = constraint.fraction_digits
    if total_digits is not None and fraction_digits is not None and fraction_digits > total_digits:
        yield TCMetadataIllegalConstraintError(
            _("fractionDigits ({}) must be less than or equal to totalDigits ({})").format(
                fraction_digits, total_digits
            ),
            TCRestriction.FRACTION_DIGITS,
            TCRestriction.TOTAL_DIGITS,
        )


def _validate_bounds_restrictions(
    constraint: TCValueConstraint,
    effective_lexical_type: QName,
) -> Generator[TCMetadataValidationError, None, None]:
    min_inclusive = constraint.min_inclusive
    min_exclusive = constraint.min_exclusive
    if min_inclusive is not None and min_exclusive is not None:
        yield TCMetadataIllegalConstraintError(
            _("minInclusive and minExclusive must not be specified together"),
            TCRestriction.MIN_INCLUSIVE,
            TCRestriction.MIN_EXCLUSIVE,
        )

    max_inclusive = constraint.max_inclusive
    max_exclusive = constraint.max_exclusive
    if max_inclusive is not None and max_exclusive is not None:
        yield TCMetadataIllegalConstraintError(
            _("maxInclusive and maxExclusive must not be specified together"),
            TCRestriction.MAX_INCLUSIVE,
            TCRestriction.MAX_EXCLUSIVE,
        )

    min_inc = _try_parse_bound(TCRestriction.MIN_INCLUSIVE, min_inclusive, effective_lexical_type)
    min_exc = _try_parse_bound(TCRestriction.MIN_EXCLUSIVE, min_exclusive, effective_lexical_type)
    max_inc = _try_parse_bound(TCRestriction.MAX_INCLUSIVE, max_inclusive, effective_lexical_type)
    max_exc = _try_parse_bound(TCRestriction.MAX_EXCLUSIVE, max_exclusive, effective_lexical_type)

    yield from _check_bounds_ordering(min_inc, max_inc, exclusive=False)
    yield from _check_bounds_ordering(min_inc, max_exc, exclusive=True)
    yield from _check_bounds_ordering(min_exc, max_inc, exclusive=True)
    yield from _check_bounds_ordering(min_exc, max_exc, exclusive=False)


@dataclass(frozen=True, slots=True)
class _Bound:
    restriction: TCRestriction
    raw: str
    parsed: ParsedValue


def _try_parse_bound(restriction: TCRestriction, raw: str | None, effective_lexical_type: QName) -> _Bound | None:
    if raw is None:
        return None
    try:
        parsed = parse_constraint_value(effective_lexical_type, raw)
    except (InvalidOperation, TypeError, ValueError):
        return None
    return _Bound(restriction, raw, parsed)


def _check_bounds_ordering(
    lower: _Bound | None,
    upper: _Bound | None,
    exclusive: bool,
) -> Generator[TCMetadataValidationError, None, None]:
    if lower is None or upper is None:
        return
    violates = lower.parsed >= upper.parsed if exclusive else lower.parsed > upper.parsed  # type: ignore[operator]
    if violates:
        relation = "<" if exclusive else "<="
        yield TCMetadataIllegalConstraintError(
            _("{} ({}) must be {} {} ({})").format(
                lower.restriction,
                lower.raw,
                relation,
                upper.restriction,
                upper.raw,
            ),
            lower.restriction,
            upper.restriction,
        )
