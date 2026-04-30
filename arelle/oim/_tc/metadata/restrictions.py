"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from types import MappingProxyType

import regex

from arelle.ModelValue import QName
from arelle.oim._tc.metadata import types as tc_types


class TCRestriction(str, Enum):
    TIME_ZONE = "timeZone"
    PERIOD_TYPE = "periodType"
    DURATION_TYPE = "durationType"
    ENUMERATION_VALUES = "enumerationValues"
    PATTERNS = "patterns"
    LENGTH = "length"
    MIN_LENGTH = "minLength"
    MAX_LENGTH = "maxLength"
    MIN_INCLUSIVE = "minInclusive"
    MAX_INCLUSIVE = "maxInclusive"
    MIN_EXCLUSIVE = "minExclusive"
    MAX_EXCLUSIVE = "maxExclusive"
    TOTAL_DIGITS = "totalDigits"
    FRACTION_DIGITS = "fractionDigits"

    @property
    def attr_name(self) -> str:
        return regex.sub(r"([A-Z])", r"_\1", self.value).lower()


_PATTERN_AND_ENUM_RESTRICTIONS = frozenset(
    {
        TCRestriction.PATTERNS,
        TCRestriction.ENUMERATION_VALUES,
    }
)
_LENGTH_RESTRICTIONS = frozenset(
    {
        TCRestriction.LENGTH,
        TCRestriction.MIN_LENGTH,
        TCRestriction.MAX_LENGTH,
    }
)
_BOUNDS_RESTRICTIONS = frozenset(
    {
        TCRestriction.MIN_INCLUSIVE,
        TCRestriction.MAX_INCLUSIVE,
        TCRestriction.MIN_EXCLUSIVE,
        TCRestriction.MAX_EXCLUSIVE,
    }
)
_DIGIT_RESTRICTIONS = frozenset(
    {
        TCRestriction.TOTAL_DIGITS,
        TCRestriction.FRACTION_DIGITS,
    }
)

_ORDERED_RESTRICTIONS = _BOUNDS_RESTRICTIONS | _PATTERN_AND_ENUM_RESTRICTIONS
_STRING_RESTRICTIONS = _LENGTH_RESTRICTIONS | _PATTERN_AND_ENUM_RESTRICTIONS
_DURATION_RESTRICTIONS = _ORDERED_RESTRICTIONS | frozenset({TCRestriction.DURATION_TYPE})
_PERIOD_RESTRICTIONS = _STRING_RESTRICTIONS | frozenset({TCRestriction.TIME_ZONE, TCRestriction.PERIOD_TYPE})
_TIME_ZONED_RESTRICTIONS = _ORDERED_RESTRICTIONS | frozenset({TCRestriction.TIME_ZONE})
_NUMERIC_RESTRICTIONS = _ORDERED_RESTRICTIONS | _DIGIT_RESTRICTIONS

_CORE_TYPE_RESTRICTIONS: Mapping[str, frozenset[TCRestriction]] = MappingProxyType(
    {
        tc_types.CORE_CONCEPT: _PATTERN_AND_ENUM_RESTRICTIONS,
        tc_types.CORE_ENTITY: _STRING_RESTRICTIONS,
        tc_types.CORE_PERIOD: _PERIOD_RESTRICTIONS,
        tc_types.CORE_UNIT: _STRING_RESTRICTIONS,
        tc_types.CORE_LANGUAGE: _STRING_RESTRICTIONS,
        tc_types.CORE_DECIMALS: _NUMERIC_RESTRICTIONS,
    }
)

_SCHEMA_TYPE_RESTRICTIONS: Mapping[QName, frozenset[TCRestriction]] = MappingProxyType(
    {
        tc_types.ANY_SIMPLE_TYPE: frozenset(),
        tc_types.ANY_URI: _STRING_RESTRICTIONS,
        tc_types.BASE64_BINARY: _STRING_RESTRICTIONS,
        tc_types.BOOLEAN: frozenset({TCRestriction.PATTERNS}),
        tc_types.BYTE: _NUMERIC_RESTRICTIONS,
        tc_types.DATE: _TIME_ZONED_RESTRICTIONS,
        tc_types.DATE_TIME: _TIME_ZONED_RESTRICTIONS,
        tc_types.DECIMAL: _NUMERIC_RESTRICTIONS,
        tc_types.DOUBLE: _ORDERED_RESTRICTIONS,
        tc_types.DURATION: _DURATION_RESTRICTIONS,
        tc_types.FLOAT: _ORDERED_RESTRICTIONS,
        tc_types.G_DAY: _TIME_ZONED_RESTRICTIONS,
        tc_types.G_MONTH: _TIME_ZONED_RESTRICTIONS,
        tc_types.G_MONTH_DAY: _TIME_ZONED_RESTRICTIONS,
        tc_types.G_YEAR: _TIME_ZONED_RESTRICTIONS,
        tc_types.G_YEAR_MONTH: _TIME_ZONED_RESTRICTIONS,
        tc_types.HEX_BINARY: _STRING_RESTRICTIONS,
        tc_types.INT: _NUMERIC_RESTRICTIONS,
        tc_types.INTEGER: _NUMERIC_RESTRICTIONS,
        tc_types.LANGUAGE: _STRING_RESTRICTIONS,
        tc_types.LONG: _NUMERIC_RESTRICTIONS,
        tc_types.NAME: _STRING_RESTRICTIONS,
        tc_types.NC_NAME: _STRING_RESTRICTIONS,
        tc_types.NEGATIVE_INTEGER: _NUMERIC_RESTRICTIONS,
        tc_types.NON_NEGATIVE_INTEGER: _NUMERIC_RESTRICTIONS,
        tc_types.NON_POSITIVE_INTEGER: _NUMERIC_RESTRICTIONS,
        tc_types.NORMALIZED_STRING: _STRING_RESTRICTIONS,
        tc_types.POSITIVE_INTEGER: _NUMERIC_RESTRICTIONS,
        tc_types.QNAME: _PATTERN_AND_ENUM_RESTRICTIONS,
        tc_types.SHORT: _NUMERIC_RESTRICTIONS,
        tc_types.STRING: _STRING_RESTRICTIONS,
        tc_types.TIME: _TIME_ZONED_RESTRICTIONS,
        tc_types.TOKEN: _STRING_RESTRICTIONS,
        tc_types.UNSIGNED_BYTE: _NUMERIC_RESTRICTIONS,
        tc_types.UNSIGNED_INT: _NUMERIC_RESTRICTIONS,
        tc_types.UNSIGNED_LONG: _NUMERIC_RESTRICTIONS,
        tc_types.UNSIGNED_SHORT: _NUMERIC_RESTRICTIONS,
    }
)


def applicable_restrictions(constraint_type: str, effective_type: QName) -> frozenset[TCRestriction]:
    if core_restrictions := _CORE_TYPE_RESTRICTIONS.get(constraint_type, frozenset()):
        return core_restrictions
    return _SCHEMA_TYPE_RESTRICTIONS.get(effective_type, frozenset())
