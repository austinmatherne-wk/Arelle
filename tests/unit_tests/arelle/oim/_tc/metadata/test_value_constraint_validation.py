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
