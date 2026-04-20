from __future__ import annotations

import dataclasses

import pytest

from arelle import XbrlConst
from arelle.oim._tc.const import (
    TCME_DUPLICATE_KEY_NAME,
    TCME_ILLEGAL_KEY_FIELD,
    TCME_MISSING_KEY_PROPERTY,
    TCME_UNKNOWN_KEY,
    TCME_UNKNOWN_SEVERITY,
)
from arelle.oim._tc.metadata.common import TCMetadataValidationError
from arelle.oim._tc.metadata.keys_validation import validate_keys
from arelle.oim._tc.metadata.model import (
    TCKeys,
    TCMetadata,
    TCReferenceKey,
    TCTemplateConstraints,
    TCUniqueKey,
    TCValueConstraint,
)

_T = "t"
_T1 = "t1"
_T2 = "t2"


_CONSTRAINT_C = TCTemplateConstraints(constraints={"c": TCValueConstraint(type="xs:string")})
_CONSTRAINT_ID = TCTemplateConstraints(constraints={"id": TCValueConstraint(type="xs:string")})

_NAMESPACES = {"xs": XbrlConst.xsd}


def _errors(keys: TCKeys, tc: TCTemplateConstraints | None = None) -> list[TCMetadataValidationError]:
    tc_obj = dataclasses.replace(tc if tc is not None else _CONSTRAINT_C, keys=keys)
    return list(validate_keys(TCMetadata(template_constraints={_T: tc_obj}), _NAMESPACES))


def _cross_errors(
    t1_keys: TCKeys,
    t2_keys: TCKeys,
    t1_tc: TCTemplateConstraints | None = None,
    t2_tc: TCTemplateConstraints | None = None,
) -> list[TCMetadataValidationError]:
    t1 = dataclasses.replace(t1_tc if t1_tc is not None else _CONSTRAINT_ID, keys=t1_keys)
    t2 = dataclasses.replace(t2_tc if t2_tc is not None else _CONSTRAINT_ID, keys=t2_keys)
    return list(validate_keys(TCMetadata(template_constraints={_T1: t1, _T2: t2}), _NAMESPACES))


_UNIQUE_KEY = TCUniqueKey(name="k", fields=("c",))
_REFERENCE_KEY = TCReferenceKey(name="r", fields=("c",), referenced_key_name="k")


class TestMissingKeyProperty:
    def test_empty_keys(self) -> None:
        errors = _errors(TCKeys())
        assert len(errors) == 1
        assert errors[0].code == TCME_MISSING_KEY_PROPERTY
        assert errors[0].json_pointers == [f"/tableTemplates/{_T}/tc:keys"]

    def test_unique_only(self) -> None:
        assert _errors(TCKeys(unique=(_UNIQUE_KEY,))) == []

    def test_reference_only(self) -> None:
        t1 = dataclasses.replace(_CONSTRAINT_C, keys=TCKeys(unique=(_UNIQUE_KEY,)))
        t2 = dataclasses.replace(_CONSTRAINT_C, keys=TCKeys(reference=(_REFERENCE_KEY,)))
        errors = list(validate_keys(TCMetadata(template_constraints={_T1: t1, _T2: t2}), _NAMESPACES))
        assert errors == []

    def test_both_present(self) -> None:
        assert _errors(TCKeys(unique=(_UNIQUE_KEY,), reference=(_REFERENCE_KEY,))) == []


class TestDuplicateKeyName:
    def test_unique_duplicate(self) -> None:
        tc = TCTemplateConstraints(
            constraints={
                "a": TCValueConstraint(type="xs:string"),
                "b": TCValueConstraint(type="xs:string"),
            }
        )
        keys = TCKeys(unique=(TCUniqueKey(name="k", fields=("a",)), TCUniqueKey(name="k", fields=("b",))))
        errors = _errors(keys, tc)
        assert len(errors) == 1
        assert errors[0].code == TCME_DUPLICATE_KEY_NAME
        assert errors[0].json_pointers == [
            f"/tableTemplates/{_T}/tc:keys/unique/0/name",
            f"/tableTemplates/{_T}/tc:keys/unique/1/name",
        ]

    def test_reference_duplicate(self) -> None:
        tc = TCTemplateConstraints(
            constraints={
                "c": TCValueConstraint(type="xs:string"),
                "a": TCValueConstraint(type="xs:string"),
                "b": TCValueConstraint(type="xs:string"),
            }
        )
        keys = TCKeys(
            unique=(_UNIQUE_KEY,),
            reference=(
                TCReferenceKey(name="r", fields=("a",), referenced_key_name="k"),
                TCReferenceKey(name="r", fields=("b",), referenced_key_name="k"),
            ),
        )
        errors = _errors(keys, tc)
        assert len(errors) == 1
        assert errors[0].code == TCME_DUPLICATE_KEY_NAME
        assert errors[0].json_pointers == [
            f"/tableTemplates/{_T}/tc:keys/reference/0/name",
            f"/tableTemplates/{_T}/tc:keys/reference/1/name",
        ]

    def test_unique_and_reference_same_name(self) -> None:
        tc = TCTemplateConstraints(
            constraints={
                "a": TCValueConstraint(type="xs:string"),
                "b": TCValueConstraint(type="xs:string"),
            }
        )
        keys = TCKeys(
            unique=(TCUniqueKey(name="k", fields=("a",)),),
            reference=(TCReferenceKey(name="k", fields=("b",), referenced_key_name="k"),),
        )
        errors = _errors(keys, tc)
        assert len(errors) == 1
        assert errors[0].code == TCME_DUPLICATE_KEY_NAME
        assert errors[0].json_pointers == [
            f"/tableTemplates/{_T}/tc:keys/unique/0/name",
            f"/tableTemplates/{_T}/tc:keys/reference/0/name",
        ]

    def test_no_error_distinct_names(self) -> None:
        assert _errors(TCKeys(unique=(_UNIQUE_KEY,), reference=(_REFERENCE_KEY,))) == []


class TestIllegalKeyField:
    @pytest.mark.parametrize("prohibited_type", ["xs:double", "xs:float", "xs:hexBinary", "xs:base64Binary"])
    def test_prohibited_type_in_unique_key_column(self, prohibited_type: str) -> None:
        tc = TCTemplateConstraints(constraints={"c": TCValueConstraint(type=prohibited_type)})
        keys = TCKeys(unique=(TCUniqueKey(name="k", fields=("c",)),))
        errors = _errors(keys, tc)
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_KEY_FIELD
        assert errors[0].json_pointers == [f"/tableTemplates/{_T}/tc:keys/unique/0/fields/0"]

    @pytest.mark.parametrize("prohibited_type", ["xs:double", "xs:float", "xs:hexBinary", "xs:base64Binary"])
    def test_prohibited_type_in_unique_key_parameter(self, prohibited_type: str) -> None:
        tc = TCTemplateConstraints(parameters={"p": TCValueConstraint(type=prohibited_type)})
        keys = TCKeys(unique=(TCUniqueKey(name="k", fields=("p",)),))
        errors = _errors(keys, tc)
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_KEY_FIELD
        assert errors[0].json_pointers == [f"/tableTemplates/{_T}/tc:keys/unique/0/fields/0"]

    @pytest.mark.parametrize("prohibited_type", ["xs:double", "xs:float", "xs:hexBinary", "xs:base64Binary"])
    def test_prohibited_type_in_reference_key(self, prohibited_type: str) -> None:
        tc = TCTemplateConstraints(
            constraints={"safe": TCValueConstraint(type="xs:string"), "c": TCValueConstraint(type=prohibited_type)}
        )
        keys = TCKeys(
            unique=(TCUniqueKey(name="k", fields=("safe",)),),
            reference=(TCReferenceKey(name="r", fields=("c",), referenced_key_name="k"),),
        )
        errors = _errors(keys, tc)
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_KEY_FIELD
        assert errors[0].json_pointers == [f"/tableTemplates/{_T}/tc:keys/reference/0/fields/0"]

    def test_allowed_type(self) -> None:
        tc = TCTemplateConstraints(constraints={"c": TCValueConstraint(type="xs:string")})
        keys = TCKeys(unique=(TCUniqueKey(name="k", fields=("c",)),))
        assert _errors(keys, tc) == []

    def test_field_not_in_constraints_or_parameters_unique_key(self) -> None:
        tc = TCTemplateConstraints()
        keys = TCKeys(unique=(TCUniqueKey(name="k", fields=("unknown",)),))
        errors = _errors(keys, tc)
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_KEY_FIELD
        assert errors[0].json_pointers == [f"/tableTemplates/{_T}/tc:keys/unique/0/fields/0"]

    def test_field_not_in_constraints_or_parameters_reference_key(self) -> None:
        tc = TCTemplateConstraints(constraints={"c": TCValueConstraint(type="xs:string")})
        keys = TCKeys(
            unique=(TCUniqueKey(name="k", fields=("c",)),),
            reference=(TCReferenceKey(name="r", fields=("unknown",), referenced_key_name="k"),),
        )
        errors = _errors(keys, tc)
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_KEY_FIELD
        assert errors[0].json_pointers == [f"/tableTemplates/{_T}/tc:keys/reference/0/fields/0"]

    def test_field_name_with_trailing_space_not_matched(self) -> None:
        tc = TCTemplateConstraints(constraints={"c": TCValueConstraint(type="xs:string")})
        keys = TCKeys(unique=(TCUniqueKey(name="k", fields=("c ",)),))
        errors = _errors(keys, tc)
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_KEY_FIELD

    def test_duration_field_without_duration_type_unique_key(self) -> None:
        tc = TCTemplateConstraints(constraints={"c": TCValueConstraint(type="xs:duration")})
        keys = TCKeys(unique=(TCUniqueKey(name="k", fields=("c",)),))
        errors = _errors(keys, tc)
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_KEY_FIELD
        assert errors[0].json_pointers == [f"/tableTemplates/{_T}/tc:keys/unique/0/fields/0"]

    def test_duration_field_with_duration_type_is_valid(self) -> None:
        tc = TCTemplateConstraints(constraints={"c": TCValueConstraint(type="xs:duration", duration_type="yearMonth")})
        keys = TCKeys(unique=(TCUniqueKey(name="k", fields=("c",)),))
        assert _errors(keys, tc) == []

    def test_duration_field_without_duration_type_reference_key(self) -> None:
        tc = TCTemplateConstraints(
            constraints={
                "safe": TCValueConstraint(type="xs:string"),
                "dur": TCValueConstraint(type="xs:duration"),
            }
        )
        keys = TCKeys(
            unique=(TCUniqueKey(name="k", fields=("safe",)),),
            reference=(TCReferenceKey(name="r", fields=("dur",), referenced_key_name="k"),),
        )
        errors = _errors(keys, tc)
        assert len(errors) == 1
        assert errors[0].code == TCME_ILLEGAL_KEY_FIELD
        assert errors[0].json_pointers == [f"/tableTemplates/{_T}/tc:keys/reference/0/fields/0"]


class TestCrossTemplateDuplicateKeyName:
    def test_both_non_shared(self) -> None:
        key = TCUniqueKey(name="customer", fields=("id",))
        errors = _cross_errors(TCKeys(unique=(key,)), TCKeys(unique=(key,)))
        assert len(errors) == 1
        assert errors[0].code == TCME_DUPLICATE_KEY_NAME
        assert errors[0].json_pointers == [
            f"/tableTemplates/{_T1}/tc:keys/unique/0/name",
            f"/tableTemplates/{_T2}/tc:keys/unique/0/name",
        ]

    def test_first_shared_second_non_shared(self) -> None:
        k1 = TCUniqueKey(name="customer", fields=("id",), shared=True)
        k2 = TCUniqueKey(name="customer", fields=("id",))
        errors = _cross_errors(TCKeys(unique=(k1,)), TCKeys(unique=(k2,)))
        assert len(errors) == 1
        assert errors[0].code == TCME_DUPLICATE_KEY_NAME
        assert errors[0].json_pointers == [
            f"/tableTemplates/{_T2}/tc:keys/unique/0/name",
            f"/tableTemplates/{_T1}/tc:keys/unique/0/name",
        ]

    def test_non_shared_before_shared(self) -> None:
        k1 = TCUniqueKey(name="customer", fields=("id",))
        k2 = TCUniqueKey(name="customer", fields=("id",), shared=True)
        errors = _cross_errors(TCKeys(unique=(k1,)), TCKeys(unique=(k2,)))
        assert len(errors) == 1
        assert errors[0].code == TCME_DUPLICATE_KEY_NAME
        assert errors[0].json_pointers == [
            f"/tableTemplates/{_T1}/tc:keys/unique/0/name",
            f"/tableTemplates/{_T2}/tc:keys/unique/0/name",
        ]

    def test_both_shared(self) -> None:
        key = TCUniqueKey(name="customer", fields=("id",), shared=True)
        assert _cross_errors(TCKeys(unique=(key,)), TCKeys(unique=(key,))) == []

    def test_distinct_names(self) -> None:
        k1 = TCUniqueKey(name="key1", fields=("id",))
        k2 = TCUniqueKey(name="key2", fields=("id",))
        assert _cross_errors(TCKeys(unique=(k1,)), TCKeys(unique=(k2,))) == []


class TestUnknownSeverity:
    @pytest.mark.parametrize("valid_severity", ["error", "warning"])
    def test_valid_severity_unique_key(self, valid_severity: str) -> None:
        keys = TCKeys(unique=(TCUniqueKey(name="k", fields=("c",), severity=valid_severity),))
        assert _errors(keys) == []

    @pytest.mark.parametrize("valid_severity", ["error", "warning"])
    def test_valid_severity_reference_key(self, valid_severity: str) -> None:
        keys = TCKeys(
            unique=(_UNIQUE_KEY,),
            reference=(TCReferenceKey(name="r", fields=("c",), referenced_key_name="k", severity=valid_severity),),
        )
        assert _errors(keys) == []

    def test_invalid_severity_unique_key(self) -> None:
        keys = TCKeys(unique=(TCUniqueKey(name="k", fields=("c",), severity="info"),))
        errors = _errors(keys)
        assert len(errors) == 1
        assert errors[0].code == TCME_UNKNOWN_SEVERITY
        assert errors[0].json_pointers == [f"/tableTemplates/{_T}/tc:keys/unique/0/severity"]

    def test_invalid_severity_reference_key(self) -> None:
        keys = TCKeys(
            unique=(_UNIQUE_KEY,),
            reference=(TCReferenceKey(name="r", fields=("c",), referenced_key_name="k", severity="critical"),),
        )
        errors = _errors(keys)
        assert len(errors) == 1
        assert errors[0].code == TCME_UNKNOWN_SEVERITY
        assert errors[0].json_pointers == [f"/tableTemplates/{_T}/tc:keys/reference/0/severity"]


class TestUnknownKey:
    def test_sort_key_refers_to_existing_unique_key(self) -> None:
        keys = TCKeys(unique=(_UNIQUE_KEY,), sort_key="k")
        assert _errors(keys) == []

    def test_sort_key_not_a_unique_key(self) -> None:
        keys = TCKeys(unique=(_UNIQUE_KEY,), sort_key="nonexistent")
        errors = _errors(keys)
        assert len(errors) == 1
        assert errors[0].code == TCME_UNKNOWN_KEY
        assert errors[0].json_pointers == [f"/tableTemplates/{_T}/tc:keys/sortKey"]

    def test_referenced_key_name_exists(self) -> None:
        keys = TCKeys(unique=(_UNIQUE_KEY,), reference=(_REFERENCE_KEY,))
        assert _errors(keys) == []

    def test_referenced_key_name_not_found(self) -> None:
        keys = TCKeys(reference=(TCReferenceKey(name="r", fields=("c",), referenced_key_name="nonexistent"),))
        errors = _errors(keys)
        assert len(errors) == 1
        assert errors[0].code == TCME_UNKNOWN_KEY
        assert errors[0].json_pointers == [f"/tableTemplates/{_T}/tc:keys/reference/0/referencedKeyName"]

    def test_referenced_key_name_in_different_template(self) -> None:
        t1_keys = TCKeys(unique=(_UNIQUE_KEY,))
        t2_keys = TCKeys(reference=(_REFERENCE_KEY,))
        t1 = dataclasses.replace(_CONSTRAINT_ID, constraints={"c": TCValueConstraint(type="xs:string")}, keys=t1_keys)
        t2 = dataclasses.replace(_CONSTRAINT_ID, constraints={"c": TCValueConstraint(type="xs:string")}, keys=t2_keys)
        errors = list(validate_keys(TCMetadata(template_constraints={_T1: t1, _T2: t2}), _NAMESPACES))
        assert errors == []
