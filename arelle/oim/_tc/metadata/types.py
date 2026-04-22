"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from types import MappingProxyType

from arelle import XbrlConst
from arelle.ModelValue import QName

_REQUIRED_XS_PREFIX = "xs"


def _xs_qname(name: str) -> QName:
    return QName(_REQUIRED_XS_PREFIX, XbrlConst.xsd, name)


class TCFacet(Enum):
    ENUMERATION = "enumeration"
    PATTERN = "pattern"
    LENGTH = "length"
    MIN_LENGTH = "minLength"
    MAX_LENGTH = "maxLength"
    MIN_INCLUSIVE = "minInclusive"
    MAX_INCLUSIVE = "maxInclusive"
    MIN_EXCLUSIVE = "minExclusive"
    MAX_EXCLUSIVE = "maxExclusive"
    TOTAL_DIGITS = "totalDigits"
    FRACTION_DIGITS = "fractionDigits"


_PATTERN_AND_ENUM_FACETS = frozenset(
    {
        TCFacet.PATTERN,
        TCFacet.ENUMERATION,
    }
)
_LENGTH_FACETS = frozenset(
    {
        TCFacet.LENGTH,
        TCFacet.MIN_LENGTH,
        TCFacet.MAX_LENGTH,
    }
)
_BOUNDS_FACETS = frozenset(
    {
        TCFacet.MIN_INCLUSIVE,
        TCFacet.MAX_INCLUSIVE,
        TCFacet.MIN_EXCLUSIVE,
        TCFacet.MAX_EXCLUSIVE,
    }
)
_DIGIT_FACETS = frozenset(
    {
        TCFacet.TOTAL_DIGITS,
        TCFacet.FRACTION_DIGITS,
    }
)

_STRING_FACETS = _LENGTH_FACETS | _PATTERN_AND_ENUM_FACETS
_ORDERED_FACETS = _BOUNDS_FACETS | _PATTERN_AND_ENUM_FACETS
_NUMERIC_FACETS = _ORDERED_FACETS | _DIGIT_FACETS


_ANY_SIMPLE_TYPE = _xs_qname("anySimpleType")
_ANY_URI = _xs_qname("anyURI")
_BASE64_BINARY = _xs_qname("base64Binary")
_BOOLEAN = _xs_qname("boolean")
_BYTE = _xs_qname("byte")
_DATE = _xs_qname("date")
_DATE_TIME = _xs_qname("dateTime")
_DECIMAL = _xs_qname("decimal")
_DOUBLE = _xs_qname("double")
_DURATION = _xs_qname("duration")
_FLOAT = _xs_qname("float")
_G_DAY = _xs_qname("gDay")
_G_MONTH = _xs_qname("gMonth")
_G_MONTH_DAY = _xs_qname("gMonthDay")
_G_YEAR = _xs_qname("gYear")
_G_YEAR_MONTH = _xs_qname("gYearMonth")
_HEX_BINARY = _xs_qname("hexBinary")
_INT = _xs_qname("int")
_INTEGER = _xs_qname("integer")
_LANGUAGE = _xs_qname("language")
_LONG = _xs_qname("long")
_NAME = _xs_qname("Name")
_NC_NAME = _xs_qname("NCName")
_NEGATIVE_INTEGER = _xs_qname("negativeInteger")
_NON_NEGATIVE_INTEGER = _xs_qname("nonNegativeInteger")
_NON_POSITIVE_INTEGER = _xs_qname("nonPositiveInteger")
_NORMALIZED_STRING = _xs_qname("normalizedString")
_POSITIVE_INTEGER = _xs_qname("positiveInteger")
_QNAME = _xs_qname("QName")
_SHORT = _xs_qname("short")
_STRING = _xs_qname("string")
_TIME = _xs_qname("time")
_TOKEN = _xs_qname("token")
_UNSIGNED_BYTE = _xs_qname("unsignedByte")
_UNSIGNED_INT = _xs_qname("unsignedInt")
_UNSIGNED_LONG = _xs_qname("unsignedLong")
_UNSIGNED_SHORT = _xs_qname("unsignedShort")

_TYPE_FACETS: Mapping[QName, frozenset[TCFacet]] = MappingProxyType(
    {
        _ANY_SIMPLE_TYPE: frozenset(),
        _ANY_URI: _STRING_FACETS,
        _BASE64_BINARY: _STRING_FACETS,
        _BOOLEAN: frozenset({TCFacet.PATTERN}),
        _BYTE: _NUMERIC_FACETS,
        _DATE: _ORDERED_FACETS,
        _DATE_TIME: _ORDERED_FACETS,
        _DECIMAL: _NUMERIC_FACETS,
        _DOUBLE: _ORDERED_FACETS,
        _DURATION: _ORDERED_FACETS,
        _FLOAT: _ORDERED_FACETS,
        _G_DAY: _ORDERED_FACETS,
        _G_MONTH: _ORDERED_FACETS,
        _G_MONTH_DAY: _ORDERED_FACETS,
        _G_YEAR: _ORDERED_FACETS,
        _G_YEAR_MONTH: _ORDERED_FACETS,
        _HEX_BINARY: _STRING_FACETS,
        _INT: _NUMERIC_FACETS,
        _INTEGER: _NUMERIC_FACETS,
        _LANGUAGE: _STRING_FACETS,
        _LONG: _NUMERIC_FACETS,
        _NAME: _STRING_FACETS,
        _NC_NAME: _STRING_FACETS,
        _NEGATIVE_INTEGER: _NUMERIC_FACETS,
        _NON_NEGATIVE_INTEGER: _NUMERIC_FACETS,
        _NON_POSITIVE_INTEGER: _NUMERIC_FACETS,
        _NORMALIZED_STRING: _STRING_FACETS,
        _POSITIVE_INTEGER: _NUMERIC_FACETS,
        _QNAME: _STRING_FACETS,
        _SHORT: _NUMERIC_FACETS,
        _STRING: _STRING_FACETS,
        _TIME: _ORDERED_FACETS,
        _TOKEN: _STRING_FACETS,
        _UNSIGNED_BYTE: _NUMERIC_FACETS,
        _UNSIGNED_INT: _NUMERIC_FACETS,
        _UNSIGNED_LONG: _NUMERIC_FACETS,
        _UNSIGNED_SHORT: _NUMERIC_FACETS,
    }
)

_CORE_EFFECTIVE_LEXICAL_TYPES: Mapping[str, QName] = MappingProxyType(
    {
        "concept": _QNAME,
        "entity": _TOKEN,
        "period": _STRING,
        "unit": _STRING,
        "language": _LANGUAGE,
        "decimals": _INTEGER,
    }
)


OPTIONALLY_TIME_ZONED_TYPES = frozenset(
    {
        _DATE,
        _DATE_TIME,
        _G_DAY,
        _G_MONTH_DAY,
        _G_YEAR_MONTH,
        _TIME,
    }
)

PROHIBITED_KEY_TYPES = frozenset(
    {
        _DOUBLE,
        _FLOAT,
        _HEX_BINARY,
        _BASE64_BINARY,
    }
)

PERIOD_CONSTRAINT_TYPE = "period"


def resolve_effective_lexical_type(constraint_type: str, namespaces: Mapping[str, str]) -> QName | None:
    if core_effective_type := _CORE_EFFECTIVE_LEXICAL_TYPES.get(constraint_type):
        return core_effective_type
    prefix, _, local_name = constraint_type.partition(":")
    namespace_uri = namespaces.get(prefix)
    if namespace_uri is None:
        return None
    effective_type = QName(prefix, namespace_uri, local_name)
    return effective_type if effective_type in _TYPE_FACETS else None


def applicable_facets(effective_type: QName) -> frozenset[TCFacet]:
    return _TYPE_FACETS.get(effective_type, frozenset())
