"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from arelle.oim._tc.metadata.model import TCValueConstraint
from arelle.oim._tc.metadata.types import resolve_effective_lexical_type
from arelle.XmlValidate import validateValueString


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
        result = validateValueString(
            self._effective_lexical_type.localName,
            value,
            nsmap=cast(Mapping[str | None, str], self._namespaces),
        )
        return result.isXValid
