from __future__ import annotations

import pytest

from arelle import XbrlConst
from arelle.ModelValue import QName
from arelle.oim._tc.metadata.types import (
    _CORE_EFFECTIVE_LEXICAL_TYPES,
    _NUMERIC_FACETS,
    _ORDERED_FACETS,
    _STRING_FACETS,
    TCFacet,
    applicable_facets,
    resolve_effective_lexical_type,
)

_XSD_NS = XbrlConst.xsd
_EXAMPLE_NS = "http://example.com/ns"
_XS_NAMESPACES = {"xs": _XSD_NS}


def _xsd(local: str) -> QName:
    return QName("xs", _XSD_NS, local)


class TestResolveEffectiveLexicalTypeCoreTypes:
    @pytest.mark.parametrize(
        "core_type,expected_local",
        [
            ("concept", "QName"),
            ("entity", "token"),
            ("period", "string"),
            ("unit", "string"),
            ("language", "language"),
            ("decimals", "integer"),
        ],
    )
    def test_core_type_resolves_to_xsd_qname(self, core_type: str, expected_local: str) -> None:
        result = resolve_effective_lexical_type(core_type, {})
        assert result == _xsd(expected_local)

    def test_core_type_ignores_namespaces(self) -> None:
        # Core types resolve without needing any namespace binding.
        assert resolve_effective_lexical_type("concept", {}) == resolve_effective_lexical_type(
            "concept", _XS_NAMESPACES
        )

    def test_core_types_match_core_effective_types_mapping(self) -> None:
        for core_type, expected_qname in _CORE_EFFECTIVE_LEXICAL_TYPES.items():
            assert resolve_effective_lexical_type(core_type, {}) == expected_qname


class TestResolveEffectiveLexicalTypeXsdTypes:
    def test_xs_string_with_bound_prefix(self) -> None:
        result = resolve_effective_lexical_type("xs:string", _XS_NAMESPACES)
        assert result == _xsd("string")

    def test_xs_decimal_with_bound_prefix(self) -> None:
        assert resolve_effective_lexical_type("xs:decimal", _XS_NAMESPACES) == _xsd("decimal")

    def test_xs_duration_with_bound_prefix(self) -> None:
        assert resolve_effective_lexical_type("xs:duration", _XS_NAMESPACES) == _xsd("duration")

    def test_xs_date_with_bound_prefix(self) -> None:
        assert resolve_effective_lexical_type("xs:date", _XS_NAMESPACES) == _xsd("date")

    def test_xs_integer_with_bound_prefix(self) -> None:
        assert resolve_effective_lexical_type("xs:integer", _XS_NAMESPACES) == _xsd("integer")

    def test_xs_type_with_unbound_prefix_returns_none(self) -> None:
        assert resolve_effective_lexical_type("xs:string", {}) is None

    def test_xs_type_bound_to_non_xsd_namespace_returns_none(self) -> None:
        # "xs:string" resolves to a QName in _EXAMPLE_NS, which is not in ALLOWED_SCHEMA_TYPES.
        assert resolve_effective_lexical_type("xs:string", {"xs": _EXAMPLE_NS}) is None

    def test_xs_type_not_in_allowed_schema_types_returns_none(self) -> None:
        assert resolve_effective_lexical_type("xs:bogusType", _XS_NAMESPACES) is None


class TestResolveEffectiveLexicalTypeCustomNamespace:
    def test_custom_ns_type_with_bound_prefix_returns_none(self) -> None:
        # Only xs: types (bound to XSD namespace) and core types are allowed.
        assert resolve_effective_lexical_type("ex:myType", {"ex": _EXAMPLE_NS}) is None

    def test_custom_ns_type_with_unbound_prefix_returns_none(self) -> None:
        assert resolve_effective_lexical_type("ex:myType", {}) is None


class TestResolveEffectiveLexicalTypeUnknown:
    def test_unprefixed_non_core_type_returns_none(self) -> None:
        assert resolve_effective_lexical_type("unknown", _XS_NAMESPACES) is None

    def test_empty_string_returns_none(self) -> None:
        assert resolve_effective_lexical_type("", _XS_NAMESPACES) is None

    def test_whitespace_padded_xs_type_returns_none(self) -> None:
        # " xs:string" has a leading space so " xs" won't match any namespace binding.
        assert resolve_effective_lexical_type(" xs:string", _XS_NAMESPACES) is None


class TestApplicableFacets:
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
            "QName",
            "string",
            "token",
        ],
    )
    def test_string_like_types(self, local_name: str) -> None:
        assert applicable_facets(_xsd(local_name)) == _STRING_FACETS

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
        assert applicable_facets(_xsd(local_name)) == _NUMERIC_FACETS

    @pytest.mark.parametrize(
        "local_name",
        [
            "date",
            "dateTime",
            "double",
            "duration",
            "float",
            "gDay",
            "gMonth",
            "gMonthDay",
            "gYear",
            "gYearMonth",
            "time",
        ],
    )
    def test_ordered_non_numeric_types(self, local_name: str) -> None:
        assert applicable_facets(_xsd(local_name)) == _ORDERED_FACETS

    def test_boolean_only_supports_pattern(self) -> None:
        assert applicable_facets(_xsd("boolean")) == frozenset({TCFacet.PATTERN})

    def test_any_simple_type_has_no_facets(self) -> None:
        assert applicable_facets(_xsd("anySimpleType")) == frozenset()

    def test_unknown_qname_returns_empty(self) -> None:
        assert applicable_facets(QName("ex", _EXAMPLE_NS, "custom")) == frozenset()

    def test_xsd_qname_not_in_table_returns_empty(self) -> None:
        assert applicable_facets(_xsd("bogusType")) == frozenset()
