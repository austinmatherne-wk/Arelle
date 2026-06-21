"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

import regex

from arelle.ModelValue import parseDateTimeString, validateDateComponents, validateDateTimeComponents
from arelle.oim._tc.metadata.model import TCValueConstraint
from arelle.oim._tc.metadata.types import CORE_ENTITY, CORE_LANGUAGE, CORE_UNIT, QNAME, resolve_effective_lexical_type
from arelle.oim.const import PREFIXED_QNAME_PATTERN, SQNAME_PATTERN, UNIT_PATTERN, UNIT_QNAME_SUBSTITUTION_CHAR
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


# TC prohibits uppercase characters in core language.
_TC_CORE_LANGUAGE_PATTERN = regex.compile(r"[a-z]{1,8}(-[a-z0-9]{1,8})*$")

_PREFIX_SEPARATOR_CHAR = ":"


class ValueConstraintValidator:
    def __init__(self, constraint: TCValueConstraint, namespaces: Mapping[str, str]) -> None:
        self._constraint = constraint
        self._namespaces = namespaces
        self._effective_lexical_type = resolve_effective_lexical_type(constraint.type, namespaces)

    def validate(self, value: str) -> bool:
        if not self._is_base_xsd_type_valid(value):
            return False
        if self._effective_lexical_type == QNAME:
            # Local only QNames are prohibited.
            return self._has_valid_namespace_prefix(value)
        if self._constraint.type == CORE_ENTITY:
            return self._is_valid_sqname(value)
        if self._constraint.type == CORE_LANGUAGE:
            return self._is_valid_core_language(value)
        if self._constraint.type == CORE_UNIT:
            return self._is_valid_unit(value)
        return True

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

    def _has_valid_namespace_prefix(self, value: str) -> bool:
        prefix, sep, _local_name = value.partition(_PREFIX_SEPARATOR_CHAR)
        return sep == _PREFIX_SEPARATOR_CHAR and prefix in self._namespaces

    def _is_valid_sqname(self, value: str) -> bool:
        if SQNAME_PATTERN.fullmatch(value) is None:
            return False
        if _PREFIX_SEPARATOR_CHAR in value:
            return self._has_valid_namespace_prefix(value)
        return True

    def _is_valid_core_language(self, value: str) -> bool:
        return _TC_CORE_LANGUAGE_PATTERN.fullmatch(value) is not None

    def _is_valid_unit(self, value: str) -> bool:
        qnames = PREFIXED_QNAME_PATTERN.findall(value)
        if not qnames:
            return False
        substituted = PREFIXED_QNAME_PATTERN.sub(UNIT_QNAME_SUBSTITUTION_CHAR, value)
        if UNIT_PATTERN.fullmatch(substituted) is None:
            return False
        for qname in qnames:
            prefix = qname.partition(_PREFIX_SEPARATOR_CHAR)[0]
            if prefix not in self._namespaces:
                return False
        numerator, _, denominator = value.partition("/")
        return self._is_sorted_product(numerator) and self._is_sorted_product(denominator)

    def _is_sorted_product(self, product: str) -> bool:
        if not product:
            return True
        if product.startswith("(") and product.endswith(")"):
            product = product[1:-1]
        qnames = product.split("*")
        return qnames == sorted(qnames)
