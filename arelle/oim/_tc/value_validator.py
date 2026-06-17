"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

import regex

from arelle.ModelValue import (
    DATE,
    DATETIME,
    DateTime,
    XsdDate,
    XsdDateTime,
    dateTime,
    parseDateTimeString,
    validateDateComponents,
    validateDateTimeComponents,
)
from arelle.oim._tc.metadata.model import TCValueConstraint
from arelle.oim._tc.metadata.types import (
    CORE_ENTITY,
    CORE_LANGUAGE,
    CORE_PERIOD,
    CORE_UNIT,
    QNAME,
    resolve_effective_lexical_type,
)
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

# Period validation patterns.
# Year: no year zero, no plus sign, at least 4 digits.
_YEAR_RE = r"-?[1-9][0-9]{3,}"
_DATE_RE = rf"(?:{_YEAR_RE})-[0-9]{{2}}-[0-9]{{2}}"
_TIME_RE = r"(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
_DATETIME_RE = rf"(?:{_DATE_RE})T(?:{_TIME_RE})Z?"
_SUFFIX_RE = r"@(?:start|end)"

_PERIOD_EXPLICIT_DURATION = regex.compile(rf"{_DATETIME_RE}/{_DATETIME_RE}$")
_PERIOD_DATETIME_INSTANT = regex.compile(rf"{_DATETIME_RE}$")
_PERIOD_DATE_RANGE = regex.compile(rf"{_DATE_RE}\.\.{_DATE_RE}$")
_PERIOD_SINGLE_DATE = regex.compile(rf"{_DATE_RE}(?:{_SUFFIX_RE})?$")
_PERIOD_YEAR_MONTH = regex.compile(rf"{_YEAR_RE}-[0-9]{{2}}(?:{_SUFFIX_RE})?$")
_PERIOD_QUARTER = regex.compile(rf"{_YEAR_RE}Q[1-4](?:{_SUFFIX_RE})?$")
_PERIOD_HALF = regex.compile(rf"{_YEAR_RE}H[12](?:{_SUFFIX_RE})?$")
_PERIOD_WEEK = regex.compile(rf"{_YEAR_RE}W[0-9]{{2}}(?:{_SUFFIX_RE})?$")
_PERIOD_YEAR = regex.compile(rf"{_YEAR_RE}(?:{_SUFFIX_RE})?$")

_DAY_OF_WEEK_TABLE = (0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4)


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
        if self._constraint.type == CORE_PERIOD:
            return self._is_valid_period(value)
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

    def _is_valid_period(self, value: str) -> bool:
        if _PERIOD_EXPLICIT_DURATION.fullmatch(value):
            start, end = value.split("/")
            start_datetime = _parse_datetime_or_none(start)
            end_datetime = _parse_datetime_or_none(end)
            if start_datetime is None or end_datetime is None:
                return False
            return start_datetime < end_datetime
        if _PERIOD_DATETIME_INSTANT.fullmatch(value):
            return _parse_datetime_or_none(value) is not None
        if _PERIOD_DATE_RANGE.fullmatch(value):
            start, end = value.split("..")
            start_date = _parse_date_or_none(start)
            end_date = _parse_date_or_none(end)
            if start_date is None or end_date is None:
                return False
            return start_date <= end_date
        if _PERIOD_SINGLE_DATE.fullmatch(value):
            return _parse_date_or_none(value.split("@")[0]) is not None
        if _PERIOD_YEAR_MONTH.fullmatch(value):
            return _is_valid_year_month(value.split("@")[0])
        if _PERIOD_QUARTER.fullmatch(value):
            return True
        if _PERIOD_HALF.fullmatch(value):
            return True
        if _PERIOD_WEEK.fullmatch(value):
            return _is_valid_week(value.split("@")[0])
        if _PERIOD_YEAR.fullmatch(value):
            return True
        return False


def _parse_date_or_none(value: str) -> DateTime | XsdDate | None:
    try:
        return dateTime(value, type=DATE)
    except ValueError:
        return None


def _parse_datetime_or_none(value: str) -> DateTime | XsdDateTime | None:
    try:
        return dateTime(value, type=DATETIME)
    except ValueError:
        return None


def _is_valid_year_month(year_month_str: str) -> bool:
    parts = year_month_str.rsplit("-", 1)
    month = int(parts[1])
    return 1 <= month <= 12


def _is_valid_week(week_str: str) -> bool:
    yearStr, weekStr = week_str.split("W")
    year, week = int(yearStr), int(weekStr)
    if week < 1 or week > 53:
        return False
    if week == 53:
        return _year_has_53_weeks(year)
    return True


def _year_has_53_weeks(year: int) -> bool:
    return _day_of_week(year, 1, 1) == 4 or _day_of_week(year, 12, 31) == 4


def _day_of_week(year: int, month: int, day: int) -> int:
    """0=Sunday, 1=Monday, ..., 4=Thursday, ..., 6=Saturday.
    Tomohiko Sakamoto's algorithm for proleptic Gregorian calendar."""
    y = year
    if month < 3:
        y -= 1
    return (y + y // 4 - y // 100 + y // 400 + _DAY_OF_WEEK_TABLE[month - 1] + day) % 7
