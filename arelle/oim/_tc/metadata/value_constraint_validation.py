"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from collections.abc import Generator, Mapping

import regex

from arelle.ModelValue import QName
from arelle.oim._tc.const import TCME_ILLEGAL_CONSTRAINT, TCME_UNKNOWN_TYPE
from arelle.oim._tc.metadata.common import TCMetadataValidationError
from arelle.oim._tc.metadata.model import TCValueConstraint
from arelle.oim._tc.metadata.restrictions import TCRestriction, applicable_restrictions
from arelle.oim._tc.metadata.types import resolve_effective_lexical_type
from arelle.typing import TypeGetText
from arelle.XmlValidate import XsdPattern

_: TypeGetText


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
