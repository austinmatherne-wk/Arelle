from __future__ import annotations

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

    def test_valid_type_with_permitted_restriction_no_error(self) -> None:
        assert _errors(TCValueConstraint(type="xs:string", length=10)) == []

    def test_valid_type_with_all_permitted_restrictions_no_error(self) -> None:
        assert (
            _errors(
                TCValueConstraint(
                    type="xs:decimal",
                    total_digits=10,
                    fraction_digits=2,
                    min_inclusive="0",
                    max_inclusive="100",
                    patterns=frozenset({"\\d+"}),
                    enumeration_values=frozenset({"1", "2"}),
                )
            )
            == []
        )

    def test_disallowed_restriction_yields_illegal_constraint_code(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:string", total_digits=5))
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_CONSTRAINT

    def test_multiple_disallowed_restrictions(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:string", total_digits=5, fraction_digits=2))
        assert len(errors) == 1
        pointers = errors[0].json_pointers
        assert "/type" in pointers
        assert "/fractionDigits" in pointers
        assert "/totalDigits" in pointers

    def test_boolean_disallows_length(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:boolean", length=1))
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_CONSTRAINT

    def test_boolean_permits_patterns(self) -> None:
        assert _errors(TCValueConstraint(type="xs:boolean", patterns=frozenset({"true|false"}))) == []

    def test_date_disallows_length_and_digits(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:date", length=10, total_digits=5))
        assert len(errors) == 1
        pointers = errors[0].json_pointers
        assert "/length" in pointers
        assert "/totalDigits" in pointers

    def test_date_permits_bounds(self) -> None:
        assert _errors(TCValueConstraint(type="xs:date", min_inclusive="2020-01-01")) == []

    def test_any_simple_type_disallows_all_restrictions(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:anySimpleType", length=1))
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_CONSTRAINT

    def test_time_zone_permitted_on_period(self) -> None:
        assert _errors(TCValueConstraint(type="period", time_zone=True)) == []

    def test_time_zone_permitted_on_date_time(self) -> None:
        assert _errors(TCValueConstraint(type="xs:dateTime", time_zone=True)) == []

    def test_time_zone_disallowed_on_string(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:string", time_zone=True))
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_CONSTRAINT

    def test_period_type_permitted_on_period(self) -> None:
        assert _errors(TCValueConstraint(type="period", period_type="instant")) == []

    def test_period_type_disallowed_on_string(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:string", period_type="instant"))
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_CONSTRAINT

    def test_duration_type_permitted_on_duration(self) -> None:
        assert _errors(TCValueConstraint(type="xs:duration", duration_type="P1Y")) == []

    def test_duration_type_disallowed_on_string(self) -> None:
        errors = _errors(TCValueConstraint(type="xs:string", duration_type="P1Y"))
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_CONSTRAINT

    def test_duration_type_disallowed_on_period(self) -> None:
        errors = _errors(TCValueConstraint(type="period", duration_type="P1Y"))
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_CONSTRAINT

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
