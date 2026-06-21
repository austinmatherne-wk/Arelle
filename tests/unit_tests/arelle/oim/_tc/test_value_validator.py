from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

import pytest

from arelle import XbrlConst
from arelle.ModelValue import QName
from arelle.oim._tc.metadata import types as tc_types
from arelle.oim._tc.metadata.model import TCValueConstraint
from arelle.oim._tc.value_validator import ValueConstraintValidator

_NAMESPACES = MappingProxyType({"xs": XbrlConst.xsd})
_UNIT_NAMESPACES = MappingProxyType(
    {
        **_NAMESPACES,
        "iso4217": "http://www.xbrl.org/2003/iso4217",
        "scheme": "http://example.com/scheme",
    }
)


def _validator(constraint_type: QName | str, namespaces: Mapping[str, str] = _NAMESPACES) -> ValueConstraintValidator:
    return ValueConstraintValidator(TCValueConstraint(str(constraint_type)), namespaces)


class TestValidateUnknownType:
    def test_unknown_type_validation(self) -> None:
        assert _validator("unknown:type").validate("anything") is False


class TestValidateString:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("hello", True),
            ("", True),
        ],
    )
    def test_string_validation(self, value: str, expected: bool) -> None:
        assert _validator(tc_types.STRING).validate(value) is expected


class TestValidateDecimal:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("1", True),
            ("2.5", True),
            ("abc", False),
        ],
    )
    def test_decimal_validation(self, value: str, expected: bool) -> None:
        assert _validator(tc_types.DECIMAL).validate(value) is expected


class TestValidateInteger:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("1", True),
            ("1.5", False),
        ],
    )
    def test_integer_validation(self, value: str, expected: bool) -> None:
        assert _validator(tc_types.INTEGER).validate(value) is expected


class TestValidateDate:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("2020-01-01", True),
            ("2024-02-29", True),
            ("2024-02-29Z", True),
            ("2024-01-01+14:00", True),
            ("2024-01-01-14:00", True),
            ("-2024-01-01", True),
            ("12024-01-01", True),
            ("-12024-01-01", True),
            ("not-a-date", False),
            ("0000-01-01", False),
            ("2024-02-30", False),
            ("2024-13-01", False),
            ("2023-02-29", False),
        ],
    )
    def test_date_validation(self, value: str, expected: bool) -> None:
        assert _validator(tc_types.DATE).validate(value) is expected


class TestValidateDateTime:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("2024-01-01T00:00:00", True),
            ("2024-01-01T00:00:00Z", True),
            ("2024-01-01T24:00:00", True),
            ("-2024-01-01T00:00:00", True),
            ("12024-01-01T00:00:00", True),
            ("-12024-01-01T00:00:00", True),
            ("-12024-01-01T00:00:00Z", True),
            ("12024-01-01T12:30:00+05:45", True),
            ("not-a-datetime", False),
            ("0000-01-01T00:00:00", False),
            ("-2024-01-01T24:00:01", False),
            ("2024-13-01T00:00:00", False),
            ("2024-02-30T00:00:00", False),
        ],
    )
    def test_datetime_validation(self, value: str, expected: bool) -> None:
        assert _validator(tc_types.DATE_TIME).validate(value) is expected


class TestValidateGMonthDay:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("--01-01", True),
            ("--07-04", True),
            ("01-01", False),
        ],
    )
    def test_g_month_day_validation(self, value: str, expected: bool) -> None:
        assert _validator(tc_types.G_MONTH_DAY).validate(value) is expected


class TestValidateBoolean:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("true", True),
            ("false", True),
            ("1", True),
            ("0", True),
            ("yes", False),
        ],
    )
    def test_boolean_validation(self, value: str, expected: bool) -> None:
        assert _validator(tc_types.BOOLEAN).validate(value) is expected


class TestValidateQName:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("xs:string", True),
            ("not a qname!", False),
        ],
    )
    def test_qname_validation(self, value: str, expected: bool) -> None:
        assert _validator(tc_types.QNAME).validate(value) is expected


class TestValidateConcept:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("xs:string", True),
            ("localName", False),
            ("bad:not a qname!", False),
            ("", False),
        ],
    )
    def test_concept_validation(self, value: str, expected: bool) -> None:
        assert _validator(tc_types.CORE_CONCEPT).validate(value) is expected


class TestValidateLanguage:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("en", True),
            ("en-us", True),
            ("en-x-twain", True),
            ("he-il-u-ca-hebrew-tz-jeruslm", True),
            ("zh-hans", True),
            ("x-private", True),
            ("i-klingon", True),
            ("abcdefgh", True),
            ("en-US", False),
            ("EN", False),
            ("EN-US", False),
            ("he-IL-u-ca-hebrew-tz-jeruslm", False),
            ("zh-Hant", False),
            (" hello", False),
            ("hello ", False),
            ("", False),
        ],
    )
    def test_language_validation(self, value: str, expected: bool) -> None:
        assert _validator(tc_types.CORE_LANGUAGE).validate(value) is expected


class TestValidateEntity:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("xs:entity", True),
            ("xs:entity with space", False),
            ("unprefixed", False),
            ("unknown:entity", False),
            ("", False),
        ],
    )
    def test_entity_validation(self, value: str, expected: bool) -> None:
        assert _validator(tc_types.CORE_ENTITY).validate(value) is expected


class TestValidateUnit:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("iso4217:USD", True),
            ("iso4217:EUR*iso4217:USD", True),
            ("iso4217:USD/scheme:m", True),
            ("(iso4217:EUR*iso4217:USD)/scheme:m", True),
            ("iso4217:USD/(scheme:m*scheme:s)", True),
            ("(iso4217:EUR*iso4217:USD)/(scheme:m*scheme:s)", True),
            ("iso4217:USD*iso4217:USD", True),
            ("", False),
            ("localOnly", False),
            ("undef:foo", False),
            ("scheme:m*iso4217:USD", False),
            ("iso4217:USD/(scheme:s*iso4217:m)", False),
            ("*iso4217:USD", False),
            ("iso4217:USD*", False),
            ("iso4217:USD/scheme:m/scheme:s", False),
            ("iso4217:USD / scheme:m", False),
            ("iso4217:EUR*iso4217:USD/scheme:m", False),
            ("iso4217:USD/scheme:m*scheme:s", False),
            ("/scheme:m", False),
            ("(iso4217:USD)/scheme:m", False),
            ("iso4217:USD ", False),
        ],
    )
    def test_unit_validation(self, value: str, expected: bool) -> None:
        assert _validator(tc_types.CORE_UNIT, _UNIT_NAMESPACES).validate(value) is expected
