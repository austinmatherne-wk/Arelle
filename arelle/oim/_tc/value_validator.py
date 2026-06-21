"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from arelle.ModelValue import parseDateTimeString, validateDateComponents, validateDateTimeComponents
from arelle.oim._tc.metadata.model import TCValueConstraint
from arelle.oim._tc.metadata.types import resolve_effective_lexical_type
from arelle.XmlValidate import lexicalPatterns, validateValueString

_LEXICAL_DATE_TYPES = frozenset({"date", "dateTime"})


def _is_valid_date_lexical(baseXsdType: str, value: str) -> bool:
    lexicalPattern = lexicalPatterns.get(baseXsdType)
    if lexicalPattern is None or lexicalPattern.match(value) is None:
        return False
    components = parseDateTimeString(value)
    if components is None:
        return False
    try:
        if components.hasTime:
            assert components.hour is not None
            assert components.minute is not None
            assert components.second is not None
            assert components.microsecond is not None
            validateDateTimeComponents(
                components.year,
                components.month,
                components.day,
                components.hour,
                components.minute,
                components.second,
                components.microsecond,
            )
        else:
            validateDateComponents(
                components.year,
                components.month,
                components.day,
            )
        return True
    except (ValueError, TypeError):
        return False


class ValueConstraintValidator:
    def __init__(self, constraint: TCValueConstraint, namespaces: Mapping[str, str]) -> None:
        self._constraint = constraint
        self._namespaces = namespaces
        self._effective_lexical_type = resolve_effective_lexical_type(constraint.type, namespaces)

    def validate(self, value: str) -> bool:
        return self._is_base_xsd_type_valid(value)

    def _is_base_xsd_type_valid(self, value: str) -> bool:
        if self._effective_lexical_type is None:
            return False
        baseXsdType = self._effective_lexical_type.localName
        if baseXsdType in _LEXICAL_DATE_TYPES:
            return _is_valid_date_lexical(baseXsdType, value)
        result = validateValueString(
            baseXsdType,
            value,
            nsmap=cast(Mapping[str | None, str], self._namespaces),
        )
        return result.isXValid
