"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from collections.abc import Generator, Iterable, Mapping

import regex

from arelle.oim._tc.const import TCME_ILLEGAL_CONSTRAINT, TCME_UNKNOWN_TYPE
from arelle.oim._tc.metadata.common import TCMetadataValidationError
from arelle.oim._tc.metadata.model import TCValueConstraint
from arelle.oim._tc.metadata.types import resolve_effective_lexical_type
from arelle.typing import TypeGetText
from arelle.XmlValidate import XsdPattern

_: TypeGetText


class TCMetadataIllegalConstraintError(TCMetadataValidationError):
    def __init__(
        self,
        message: str,
        *path: str,
        related_paths: Iterable[Iterable[str]] = (),
    ) -> None:
        super().__init__(message, *path, code=TCME_ILLEGAL_CONSTRAINT, related_paths=related_paths)


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
    yield from _validate_patterns(constraint)


def _validate_patterns(constraint: TCValueConstraint) -> Generator[TCMetadataValidationError, None, None]:
    if constraint.patterns is None:
        return
    invalid_patterns = [pattern for pattern in sorted(constraint.patterns) if not _is_valid_xsd_pattern(pattern)]
    if invalid_patterns:
        yield TCMetadataIllegalConstraintError(
            _("Patterns {} are not valid XSD regular expressions").format(invalid_patterns),
            "patterns",
        )


def _is_valid_xsd_pattern(pattern: str) -> bool:
    try:
        XsdPattern.compile(pattern)
    except regex.error:
        return False
    return True
