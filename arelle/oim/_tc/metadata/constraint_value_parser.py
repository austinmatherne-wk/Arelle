"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import cast

import regex

from arelle.ModelValue import (
    DATE,
    DATETIME,
    DateTime,
    IsoDuration,
    QName,
    Time,
    dateTime,
    gDay,
    gMonth,
    gMonthDay,
    gYear,
    gYearMonth,
    isoDuration,
    time,
)
from arelle.oim._tc.metadata import types as tc_types
from arelle.XmlValidate import lexicalPatterns

ParsedValue = Decimal | DateTime | Time | IsoDuration | gYearMonth | gYear | gMonthDay | gMonth | gDay


def _match_lexical(local_name: str, value: str) -> regex.Match[str]:
    match = lexicalPatterns[local_name].match(value)
    if match is None:
        raise ValueError(f"invalid lexical form for xs:{local_name}")
    return match


_DECIMAL_PARSER_TYPES = frozenset(
    {
        tc_types.BYTE,
        tc_types.DECIMAL,
        tc_types.DOUBLE,
        tc_types.FLOAT,
        tc_types.INT,
        tc_types.INTEGER,
        tc_types.LONG,
        tc_types.NEGATIVE_INTEGER,
        tc_types.NON_NEGATIVE_INTEGER,
        tc_types.NON_POSITIVE_INTEGER,
        tc_types.POSITIVE_INTEGER,
        tc_types.SHORT,
        tc_types.UNSIGNED_BYTE,
        tc_types.UNSIGNED_INT,
        tc_types.UNSIGNED_LONG,
        tc_types.UNSIGNED_SHORT,
    }
)

_TYPE_PARSERS: Mapping[QName, Callable[[str], ParsedValue]] = MappingProxyType(
    {
        **{decimal_type: Decimal for decimal_type in _DECIMAL_PARSER_TYPES},
        tc_types.DATE_TIME: lambda v: cast(DateTime, dateTime(v, type=DATETIME, castException=ValueError)),
        tc_types.DATE: lambda v: cast(DateTime, dateTime(v, type=DATE, castException=ValueError)),
        tc_types.TIME: lambda v: cast(Time, time(v, castException=ValueError)),
        tc_types.DURATION: isoDuration,
        tc_types.G_YEAR_MONTH: lambda v: gYearMonth(*_match_lexical("gYearMonth", v).group(1, 2)),
        tc_types.G_YEAR: lambda v: gYear(_match_lexical("gYear", v).group(1)),
        tc_types.G_MONTH_DAY: lambda v: gMonthDay(*_match_lexical("gMonthDay", v).group(1, 2)),
        tc_types.G_MONTH: lambda v: gMonth(_match_lexical("gMonth", v).group(1)),
        tc_types.G_DAY: lambda v: gDay(_match_lexical("gDay", v).group(1)),
    }
)


def parse_constraint_value(effective_lexical_type: QName, value: str) -> ParsedValue:
    """Parse a constraint value string into a comparable Python object for the given XSD type.

    Raises ``ValueError`` (or :class:`decimal.InvalidOperation` for numeric types) if
    the value is not a valid lexical form for the type, or if parsing is not supported
    for the type.
    """
    if parser := _TYPE_PARSERS.get(effective_lexical_type):
        return parser(value)
    raise ValueError(f"unsupported type: {effective_lexical_type}")
