"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from collections.abc import Generator, Iterable, Mapping

import regex

from arelle.ModelValue import QName
from arelle.oim._tc.const import TCME_ILLEGAL_CONSTRAINT, TCME_UNKNOWN_TYPE
from arelle.oim._tc.metadata.common import TCMetadataValidationError
from arelle.oim._tc.metadata.model import TCValueConstraint
from arelle.oim._tc.metadata.types import TCFacet, applicable_facets, resolve_effective_lexical_type
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
    yield from _validate_length_facets(constraint, effective_lexical_type)


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


def _validate_length_facets(
    constraint: TCValueConstraint,
    effective_lexical_type: QName,
) -> Generator[TCMetadataValidationError, None, None]:
    if TCFacet.LENGTH not in applicable_facets(effective_lexical_type):
        for facet_name, facet_value in (
            ("length", constraint.length),
            ("minLength", constraint.min_length),
            ("maxLength", constraint.max_length),
        ):
            if facet_value is not None:
                yield TCMetadataIllegalConstraintError(
                    _("{} is not applicable to type '{}'").format(facet_name, constraint.type),
                    facet_name,
                    related_paths=(("type",),),
                )
        return

    length = constraint.length
    min_length = constraint.min_length
    max_length = constraint.max_length
    if min_length is not None and length is not None and min_length > length:
        yield TCMetadataIllegalConstraintError(
            _("minLength ({}) must be less than or equal to length ({})").format(min_length, length),
            "minLength",
            related_paths=(("length",),),
        )
    if length is not None and max_length is not None and length > max_length:
        yield TCMetadataIllegalConstraintError(
            _("length ({}) must be less than or equal to maxLength ({})").format(length, max_length),
            "length",
            related_paths=(("maxLength",),),
        )
    if min_length is not None and max_length is not None and min_length > max_length:
        yield TCMetadataIllegalConstraintError(
            _("minLength ({}) must be less than or equal to maxLength ({})").format(min_length, max_length),
            "minLength",
            related_paths=(("maxLength",),),
        )
