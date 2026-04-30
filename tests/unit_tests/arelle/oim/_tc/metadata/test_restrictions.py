from __future__ import annotations

import pytest

from arelle import XbrlConst
from arelle.ModelValue import QName
from arelle.oim._tc.metadata.model import TCValueConstraint
from arelle.oim._tc.metadata.restrictions import (
    _DURATION_RESTRICTIONS,
    _NUMERIC_RESTRICTIONS,
    _ORDERED_RESTRICTIONS,
    _PATTERN_AND_ENUM_RESTRICTIONS,
    _PERIOD_RESTRICTIONS,
    _STRING_RESTRICTIONS,
    _TIME_ZONED_RESTRICTIONS,
    TCRestriction,
    applicable_restrictions,
)

_XSD_NS = XbrlConst.xsd
_EXAMPLE_NS = "http://example.com/ns"


def _xsd(local: str) -> QName:
    return QName("xs", _XSD_NS, local)


class TestApplicableRestrictionsSchemaTypes:
    @pytest.mark.parametrize(
        "local_name",
        [
            "anyURI",
            "base64Binary",
            "hexBinary",
            "language",
            "Name",
            "NCName",
            "normalizedString",
            "string",
            "token",
        ],
    )
    def test_string_like_types(self, local_name: str) -> None:
        assert applicable_restrictions(f"xs:{local_name}", _xsd(local_name)) == _STRING_RESTRICTIONS

    def test_qname_only_supports_pattern_and_enumeration(self) -> None:
        assert applicable_restrictions("xs:QName", _xsd("QName")) == _PATTERN_AND_ENUM_RESTRICTIONS

    @pytest.mark.parametrize(
        "local_name",
        [
            "byte",
            "decimal",
            "int",
            "integer",
            "long",
            "negativeInteger",
            "nonNegativeInteger",
            "nonPositiveInteger",
            "positiveInteger",
            "short",
            "unsignedByte",
            "unsignedInt",
            "unsignedLong",
            "unsignedShort",
        ],
    )
    def test_numeric_types(self, local_name: str) -> None:
        assert applicable_restrictions(f"xs:{local_name}", _xsd(local_name)) == _NUMERIC_RESTRICTIONS

    @pytest.mark.parametrize(
        "local_name",
        [
            "date",
            "dateTime",
            "gDay",
            "gMonth",
            "gMonthDay",
            "gYear",
            "gYearMonth",
            "time",
        ],
    )
    def test_time_zoned_types(self, local_name: str) -> None:
        assert applicable_restrictions(f"xs:{local_name}", _xsd(local_name)) == _TIME_ZONED_RESTRICTIONS

    @pytest.mark.parametrize(
        "local_name",
        [
            "double",
            "float",
        ],
    )
    def test_ordered_non_numeric_types(self, local_name: str) -> None:
        assert applicable_restrictions(f"xs:{local_name}", _xsd(local_name)) == _ORDERED_RESTRICTIONS

    def test_duration_type(self) -> None:
        assert applicable_restrictions("xs:duration", _xsd("duration")) == _DURATION_RESTRICTIONS

    def test_boolean_only_supports_pattern(self) -> None:
        assert applicable_restrictions("xs:boolean", _xsd("boolean")) == frozenset({TCRestriction.PATTERNS})

    def test_any_simple_type_has_no_restrictions(self) -> None:
        assert applicable_restrictions("xs:anySimpleType", _xsd("anySimpleType")) == frozenset()

    def test_unknown_qname_returns_empty(self) -> None:
        assert applicable_restrictions("ex:custom", QName("ex", _EXAMPLE_NS, "custom")) == frozenset()

    def test_xsd_qname_not_in_table_returns_empty(self) -> None:
        assert applicable_restrictions("xs:bogusType", _xsd("bogusType")) == frozenset()


class TestApplicableRestrictionsCoreTypes:
    def test_concept(self) -> None:
        assert applicable_restrictions("concept", _xsd("QName")) == _PATTERN_AND_ENUM_RESTRICTIONS

    def test_entity(self) -> None:
        assert applicable_restrictions("entity", _xsd("token")) == _STRING_RESTRICTIONS

    def test_period(self) -> None:
        assert applicable_restrictions("period", _xsd("string")) == _PERIOD_RESTRICTIONS

    def test_unit(self) -> None:
        assert applicable_restrictions("unit", _xsd("string")) == _STRING_RESTRICTIONS

    def test_language(self) -> None:
        assert applicable_restrictions("language", _xsd("language")) == _STRING_RESTRICTIONS

    def test_decimals(self) -> None:
        assert applicable_restrictions("decimals", _xsd("integer")) == _NUMERIC_RESTRICTIONS


class TestTCRestrictionAttrName:
    @pytest.mark.parametrize("restriction", list(TCRestriction))
    def test_attr_name_matches_value_constraint_field(self, restriction: TCRestriction) -> None:
        assert hasattr(TCValueConstraint, restriction.attr_name)

    @pytest.mark.parametrize(
        "restriction,expected",
        [
            (TCRestriction.TIME_ZONE, "time_zone"),
            (TCRestriction.PERIOD_TYPE, "period_type"),
            (TCRestriction.DURATION_TYPE, "duration_type"),
            (TCRestriction.ENUMERATION_VALUES, "enumeration_values"),
            (TCRestriction.PATTERNS, "patterns"),
            (TCRestriction.LENGTH, "length"),
            (TCRestriction.MIN_LENGTH, "min_length"),
            (TCRestriction.MAX_LENGTH, "max_length"),
            (TCRestriction.MIN_INCLUSIVE, "min_inclusive"),
            (TCRestriction.MAX_INCLUSIVE, "max_inclusive"),
            (TCRestriction.MIN_EXCLUSIVE, "min_exclusive"),
            (TCRestriction.MAX_EXCLUSIVE, "max_exclusive"),
            (TCRestriction.TOTAL_DIGITS, "total_digits"),
            (TCRestriction.FRACTION_DIGITS, "fraction_digits"),
        ],
    )
    def test_attr_name_derivation(self, restriction: TCRestriction, expected: str) -> None:
        assert restriction.attr_name == expected
