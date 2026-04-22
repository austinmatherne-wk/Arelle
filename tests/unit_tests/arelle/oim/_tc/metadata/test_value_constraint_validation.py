from __future__ import annotations

import pytest

from arelle import XbrlConst
from arelle.oim._tc.const import TCME_ILLEGAL_CONSTRAINT, TCME_UNKNOWN_TYPE
from arelle.oim._tc.metadata.common import TCMetadataValidationError
from arelle.oim._tc.metadata.model import TCValueConstraint
from arelle.oim._tc.metadata.value_constraint_validation import (
    validate_value_constraint,
)

_NAMESPACES: dict[str, str] = {"xs": XbrlConst.xsd}


def _errors(constraint: TCValueConstraint) -> list[TCMetadataValidationError]:
    return list(validate_value_constraint(constraint, _NAMESPACES))


class TestValidateValueConstraint:
    def test_unknown_type_yields_unknown_type_code(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:otherType"))
        assert len(errors) == 1
        assert errors[0].code == TCME_UNKNOWN_TYPE

    def test_unknown_type_json_pointer_is_type(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:otherType"))
        assert errors[0].json_pointers == ["/type"]

    def test_valid_type_no_error(self) -> None:
        assert _errors(TCValueConstraint(type="xs:string")) == []

    def test_patterns_single_valid_no_error(self) -> None:
        assert _errors(TCValueConstraint(type="xs:string", patterns=frozenset({r"[a-z]+"}))) == []

    def test_patterns_multiple_valid_no_error(self) -> None:
        assert _errors(TCValueConstraint(type="xs:string", patterns=frozenset({r"[a-z]+", r"\d{3}-\d{4}"}))) == []

    def test_patterns_invalid_error(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:string", patterns=frozenset({"["})))
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_CONSTRAINT
        assert errors[0].json_pointers == ["/patterns"]

    def test_patterns_mixed_reports_only_invalid(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:string", patterns=frozenset({r"[a-z]+", "(", r"\d+"})))
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_CONSTRAINT
        assert "(" in str(errors[0])
        assert "[a-z]+" not in str(errors[0])

    def test_patterns_xsd_name_char_escapes_no_error(self) -> None:
        assert _errors(TCValueConstraint(type="xs:string", patterns=frozenset({r"\i\c*"}))) == []

    def test_patterns_unicode_category_no_error(self) -> None:
        assert _errors(TCValueConstraint(type="xs:string", patterns=frozenset({r"\p{L}+"}))) == []

    def test_patterns_unknown_type_short_circuits(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:bogus", patterns=frozenset({"["})))
        assert len(errors) == 1
        assert errors[0].code == TCME_UNKNOWN_TYPE

    @pytest.mark.parametrize(
        "xs_type",
        [
            "xs:string",
            "xs:normalizedString",
            "xs:token",
            "xs:language",
            "xs:Name",
            "xs:NCName",
            "xs:anyURI",
            "xs:hexBinary",
            "xs:base64Binary",
            "xs:QName",
        ],
    )
    def test_length_on_applicable_types_no_error(self, xs_type: str) -> None:
        assert _errors(TCValueConstraint(type=xs_type, length=5)) == []

    @pytest.mark.parametrize(
        "xs_type",
        [
            "xs:integer",
            "xs:int",
            "xs:decimal",
            "xs:float",
            "xs:double",
            "xs:boolean",
            "xs:date",
            "xs:dateTime",
            "xs:time",
            "xs:duration",
        ],
    )
    def test_length_on_non_applicable_types_error(self, xs_type: str) -> None:
        errors = _errors(TCValueConstraint(type=xs_type, length=5))
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_CONSTRAINT
        assert errors[0].json_pointers == ["/length", "/type"]

    def test_min_length_on_non_applicable_type_error(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:integer", min_length=1))
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_CONSTRAINT
        assert errors[0].json_pointers == ["/minLength", "/type"]

    def test_max_length_on_non_applicable_type_error(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:decimal", max_length=10))
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_CONSTRAINT
        assert errors[0].json_pointers == ["/maxLength", "/type"]

    def test_all_length_facets_on_non_applicable_type_yields_three_errors(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:integer", length=5, min_length=1, max_length=10))
        assert len(errors) == 3
        assert all(e.code == TCME_ILLEGAL_CONSTRAINT for e in errors)
        assert {e.json_pointers[0] for e in errors} == {"/length", "/minLength", "/maxLength"}

    def test_min_length_greater_than_length_error(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:string", length=3, min_length=5))
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_CONSTRAINT
        assert errors[0].json_pointers == ["/minLength", "/length"]

    def test_length_greater_than_max_length_error(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:string", length=10, max_length=5))
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_CONSTRAINT
        assert errors[0].json_pointers == ["/length", "/maxLength"]

    def test_min_length_greater_than_max_length_error(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:string", min_length=10, max_length=5))
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_CONSTRAINT
        assert errors[0].json_pointers == ["/minLength", "/maxLength"]

    def test_min_length_equal_length_no_error(self) -> None:
        assert _errors(TCValueConstraint(type="xs:string", length=5, min_length=5)) == []

    def test_length_equal_max_length_no_error(self) -> None:
        assert _errors(TCValueConstraint(type="xs:string", length=5, max_length=5)) == []

    def test_min_length_equal_max_length_no_error(self) -> None:
        assert _errors(TCValueConstraint(type="xs:string", min_length=5, max_length=5)) == []

    def test_valid_length_range_no_error(self) -> None:
        assert _errors(TCValueConstraint(type="xs:string", length=5, min_length=3, max_length=10)) == []

    def test_min_and_max_length_without_length_no_error(self) -> None:
        assert _errors(TCValueConstraint(type="xs:string", min_length=2, max_length=10)) == []

    def test_multiple_cross_facet_violations_all_reported(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:string", length=5, min_length=10, max_length=3))
        assert len(errors) == 3
        assert all(e.code == TCME_ILLEGAL_CONSTRAINT for e in errors)

    def test_length_unknown_type_short_circuits(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:bogus", length=5))
        assert len(errors) == 1
        assert errors[0].code == TCME_UNKNOWN_TYPE
