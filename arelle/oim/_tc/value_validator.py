"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from arelle.ModelValue import QName
from arelle.oim._tc.metadata.model import TCValueConstraint
from arelle.oim._tc.metadata.types import CORE_CONCEPT, CORE_ENTITY, QNAME, resolve_effective_lexical_type
from arelle.oim.const import SQNAME_PATTERN
from arelle.XmlValidate import validateValueString


class ValueConstraintValidator:
    def __init__(self, constraint: TCValueConstraint, namespaces: Mapping[str, str]) -> None:
        self._constraint = constraint
        self._namespaces = namespaces
        self._effective_lexical_type = resolve_effective_lexical_type(constraint.type, namespaces)

    def validate(self, value: str) -> bool:
        if self._effective_lexical_type is None:
            return False
        if self._constraint.type == CORE_CONCEPT:
            return self._is_valid_concept_value(value)
        if self._constraint.type == CORE_ENTITY:
            return self._is_valid_entity_value(value)
        return self._is_base_xsd_type_valid(self._effective_lexical_type, value)

    def _is_valid_concept_value(self, value: str) -> bool:
        if ":" not in value:
            # Concept value QName must have a namespace prefix
            return False
        return self._is_base_xsd_type_valid(QNAME, value)

    def _is_valid_entity_value(self, value: str) -> bool:
        if not SQNAME_PATTERN.fullmatch(value):
            return False
        prefix = value.split(":", 1)[0]
        return prefix in self._namespaces

    def _is_base_xsd_type_valid(self, base_xsd_type: QName, value: str) -> bool:
        result = validateValueString(
            base_xsd_type.localName,
            value,
            nsmap=cast(Mapping[str | None, str], self._namespaces),
        )
        return result.isXValid
