from __future__ import annotations

from decimal import Decimal, InvalidOperation

import pytest

from arelle import XbrlConst
from arelle.ModelValue import DateTime, IsoDuration, QName, Time, gDay, gMonth, gMonthDay, gYear, gYearMonth
from arelle.oim._tc.metadata.constraint_value_parser import parse_constraint_value

_XSD_NS = XbrlConst.xsd


def _xsd(local: str) -> QName:
    return QName("xs", _XSD_NS, local)


class TestDecimalTypes:
    @pytest.mark.parametrize(
        "local_name",
        [
            "decimal",
            "integer",
            "int",
            "long",
            "short",
            "byte",
            "float",
            "double",
            "unsignedInt",
            "unsignedLong",
            "unsignedShort",
            "unsignedByte",
            "positiveInteger",
            "nonNegativeInteger",
            "negativeInteger",
            "nonPositiveInteger",
        ],
    )
    def test_valid_decimal_value(self, local_name: str) -> None:
        result = parse_constraint_value(_xsd(local_name), "42")
        assert result == Decimal("42")

    def test_decimal_with_fractional(self) -> None:
        result = parse_constraint_value(_xsd("decimal"), "3.14")
        assert result == Decimal("3.14")

    def test_negative_decimal(self) -> None:
        result = parse_constraint_value(_xsd("decimal"), "-100")
        assert result == Decimal("-100")

    def test_invalid_decimal_raises(self) -> None:
        with pytest.raises(InvalidOperation):
            parse_constraint_value(_xsd("decimal"), "notANumber")


class TestDateTimeTypes:
    def test_date(self) -> None:
        result = parse_constraint_value(_xsd("date"), "2024-01-15")
        assert isinstance(result, DateTime)

    def test_dateTime(self) -> None:
        result = parse_constraint_value(_xsd("dateTime"), "2024-01-15T10:30:00")
        assert isinstance(result, DateTime)

    def test_time(self) -> None:
        result = parse_constraint_value(_xsd("time"), "10:30:00")
        assert isinstance(result, Time)

    def test_invalid_date_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_constraint_value(_xsd("date"), "not-a-date")


class TestDuration:
    def test_duration(self) -> None:
        result = parse_constraint_value(_xsd("duration"), "P1Y2M3D")
        assert isinstance(result, IsoDuration)

    def test_invalid_duration_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_constraint_value(_xsd("duration"), "notDuration")


class TestGregorianTypes:
    def test_gYear(self) -> None:
        result = parse_constraint_value(_xsd("gYear"), "2024")
        assert isinstance(result, gYear)

    def test_gYearMonth(self) -> None:
        result = parse_constraint_value(_xsd("gYearMonth"), "2024-06")
        assert isinstance(result, gYearMonth)

    def test_gMonth(self) -> None:
        result = parse_constraint_value(_xsd("gMonth"), "--06")
        assert isinstance(result, gMonth)

    def test_gMonthDay(self) -> None:
        result = parse_constraint_value(_xsd("gMonthDay"), "--06-15")
        assert isinstance(result, gMonthDay)

    def test_gDay(self) -> None:
        result = parse_constraint_value(_xsd("gDay"), "---15")
        assert isinstance(result, gDay)

    def test_invalid_gYear_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_constraint_value(_xsd("gYear"), "notAYear")


class TestUnsupportedType:
    def test_unsupported_type_raises(self) -> None:
        with pytest.raises(ValueError, match="unsupported type"):
            parse_constraint_value(_xsd("string"), "hello")

    def test_unknown_qname_raises(self) -> None:
        with pytest.raises(ValueError, match="unsupported type"):
            parse_constraint_value(_xsd("bogus"), "hello")
