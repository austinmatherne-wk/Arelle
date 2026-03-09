from __future__ import annotations

import pytest

from arelle.oim._tc.metadata import (
    TCMetadata,
    TCUniqueKey,
    TCValueConstraint,
    parse_tc_metadata,
)

TC_NS = "https://xbrl.org/WGWD/YYYY-MM-DD/tc"


class TestParseTcMetadataNamespaceDetection:
    def test_returns_none_when_no_tc_namespace(self) -> None:
        result = parse_tc_metadata(
            {"tableTemplates": {}},
            {"xbrl": "https://xbrl.org/2021"},
        )
        assert result is None

    def test_returns_none_when_namespaces_empty(self) -> None:
        result = parse_tc_metadata({"tableTemplates": {}}, {})
        assert result is None

    def test_returns_metadata_when_tc_namespace_present(self) -> None:
        result = parse_tc_metadata(
            {"tableTemplates": {}},
            {"tc": TC_NS},
        )
        assert result is not None
        assert isinstance(result, TCMetadata)
        assert result.template_constraints == {}

    def test_detects_final_tc_namespace(self) -> None:
        result = parse_tc_metadata(
            {"tableTemplates": {}},
            {"tc": "https://xbrl.org/2025/tc"},
        )
        assert result is not None


class TestParseTcMetadataColumnConstraints:
    def test_parses_column_constraint(self) -> None:
        result = parse_tc_metadata(
            {"tableTemplates": {"t1": {"columns": {"col_a": {"tc:constraints": {"type": "xs:integer"}}}}}},
            {"tc": TC_NS},
        )
        assert result is not None
        tc = result.template_constraints["t1"]
        assert "col_a" in tc.constraints
        assert tc.constraints["col_a"].type == "xs:integer"

    def test_parses_all_value_constraint_properties(self) -> None:
        result = parse_tc_metadata(
            {
                "tableTemplates": {
                    "t1": {
                        "columns": {
                            "col_a": {
                                "tc:constraints": {
                                    "type": "xs:string",
                                    "optional": True,
                                    "nillable": True,
                                    "enumerationValues": ["a", "b"],
                                    "patterns": ["^[A-Z]+$"],
                                    "timeZone": False,
                                    "periodType": "month",
                                    "durationType": "yearMonth",
                                    "length": 10,
                                    "minLength": 1,
                                    "maxLength": 100,
                                    "minInclusive": "0",
                                    "maxInclusive": "999",
                                    "minExclusive": "-1",
                                    "maxExclusive": "1000",
                                    "totalDigits": 5,
                                    "fractionDigits": 2,
                                }
                            }
                        }
                    }
                }
            },
            {"tc": TC_NS},
        )
        assert result is not None
        vc = result.template_constraints["t1"].constraints["col_a"]
        assert vc.type == "xs:string"
        assert vc.optional is True
        assert vc.nillable is True
        assert vc.enumeration_values == ("a", "b")
        assert vc.patterns == ("^[A-Z]+$",)
        assert vc.time_zone is False
        assert vc.period_type == "month"
        assert vc.duration_type == "yearMonth"
        assert vc.length == 10
        assert vc.min_length == 1
        assert vc.max_length == 100
        assert vc.min_inclusive == "0"
        assert vc.max_inclusive == "999"
        assert vc.min_exclusive == "-1"
        assert vc.max_exclusive == "1000"
        assert vc.total_digits == 5
        assert vc.fraction_digits == 2

    def test_defaults_for_missing_optional_properties(self) -> None:
        result = parse_tc_metadata(
            {"tableTemplates": {"t1": {"columns": {"col_a": {"tc:constraints": {"type": "xs:date"}}}}}},
            {"tc": TC_NS},
        )
        assert result is not None
        vc = result.template_constraints["t1"].constraints["col_a"]
        assert vc.optional is False
        assert vc.nillable is False
        assert vc.enumeration_values is None
        assert vc.patterns is None
        assert vc.time_zone is None
        assert vc.period_type is None
        assert vc.length is None
        assert vc.total_digits is None

    def test_multiple_columns(self) -> None:
        result = parse_tc_metadata(
            {
                "tableTemplates": {
                    "t1": {
                        "columns": {
                            "col_a": {"tc:constraints": {"type": "xs:integer"}},
                            "col_b": {"tc:constraints": {"type": "xs:string"}},
                            "col_c": {},
                        }
                    }
                }
            },
            {"tc": TC_NS},
        )
        assert result is not None
        tc = result.template_constraints["t1"]
        assert len(tc.constraints) == 2
        assert "col_a" in tc.constraints
        assert "col_b" in tc.constraints
        assert "col_c" not in tc.constraints

    def test_skips_non_dict_constraint(self) -> None:
        result = parse_tc_metadata(
            {"tableTemplates": {"t1": {"columns": {"col_a": {"tc:constraints": "not a dict"}}}}},
            {"tc": TC_NS},
        )
        assert result is not None
        assert "t1" not in result.template_constraints


class TestParseTcMetadataParameters:
    def test_parses_parameters(self) -> None:
        result = parse_tc_metadata(
            {
                "tableTemplates": {
                    "t1": {
                        "columns": {},
                        "tc:parameters": {
                            "calendar_month": {
                                "type": "period",
                                "periodType": "month",
                                "timeZone": False,
                            }
                        },
                    }
                }
            },
            {"tc": TC_NS},
        )
        assert result is not None
        tc = result.template_constraints["t1"]
        assert "calendar_month" in tc.parameters
        p = tc.parameters["calendar_month"]
        assert p.type == "period"
        assert p.period_type == "month"
        assert p.time_zone is False

    def test_skips_non_dict_parameter(self) -> None:
        result = parse_tc_metadata(
            {
                "tableTemplates": {
                    "t1": {
                        "columns": {},
                        "tc:parameters": {
                            "good": {"type": "xs:string"},
                            "bad": "not a dict",
                        },
                    }
                }
            },
            {"tc": TC_NS},
        )
        assert result is not None
        tc = result.template_constraints["t1"]
        assert "good" in tc.parameters
        assert "bad" not in tc.parameters


class TestParseTcMetadataKeys:
    def test_parses_unique_keys(self) -> None:
        result = parse_tc_metadata(
            {
                "tableTemplates": {
                    "t1": {
                        "columns": {},
                        "tc:keys": {
                            "unique": [
                                {
                                    "name": "pk",
                                    "fields": ["id"],
                                    "severity": "error",
                                    "shared": True,
                                }
                            ]
                        },
                    }
                }
            },
            {"tc": TC_NS},
        )
        assert result is not None
        keys = result.template_constraints["t1"].keys
        assert keys is not None
        assert keys.unique is not None
        assert len(keys.unique) == 1
        uk = keys.unique[0]
        assert uk.name == "pk"
        assert uk.fields == ("id",)
        assert uk.severity == "error"
        assert uk.shared is True

    def test_parses_reference_keys(self) -> None:
        result = parse_tc_metadata(
            {
                "tableTemplates": {
                    "t1": {
                        "columns": {},
                        "tc:keys": {
                            "reference": [
                                {
                                    "name": "fk",
                                    "fields": ["country_code"],
                                    "referencedKeyName": "countriesUK",
                                    "negate": True,
                                    "severity": "warning",
                                }
                            ]
                        },
                    }
                }
            },
            {"tc": TC_NS},
        )
        assert result is not None
        keys = result.template_constraints["t1"].keys
        assert keys is not None
        assert keys.reference is not None
        rk = keys.reference[0]
        assert rk.name == "fk"
        assert rk.fields == ("country_code",)
        assert rk.referenced_key_name == "countriesUK"
        assert rk.negate is True
        assert rk.severity == "warning"

    def test_parses_sort_key(self) -> None:
        result = parse_tc_metadata(
            {
                "tableTemplates": {
                    "t1": {
                        "columns": {},
                        "tc:keys": {
                            "unique": [{"name": "pk", "fields": ["id"]}],
                            "sortKey": "pk",
                        },
                    }
                }
            },
            {"tc": TC_NS},
        )
        assert result is not None
        keys = result.template_constraints["t1"].keys
        assert keys is not None
        assert keys.sort_key == "pk"

    def test_unique_key_defaults(self) -> None:
        result = parse_tc_metadata(
            {
                "tableTemplates": {
                    "t1": {
                        "columns": {},
                        "tc:keys": {"unique": [{"name": "pk", "fields": ["id"]}]},
                    }
                }
            },
            {"tc": TC_NS},
        )
        assert result is not None
        uk = result.template_constraints["t1"].keys.unique[0]  # type: ignore[union-attr]
        assert uk.severity == "error"
        assert uk.shared is False

    def test_reference_key_defaults(self) -> None:
        result = parse_tc_metadata(
            {
                "tableTemplates": {
                    "t1": {
                        "columns": {},
                        "tc:keys": {
                            "reference": [
                                {
                                    "name": "fk",
                                    "fields": ["col"],
                                    "referencedKeyName": "pk",
                                }
                            ]
                        },
                    }
                }
            },
            {"tc": TC_NS},
        )
        assert result is not None
        rk = result.template_constraints["t1"].keys.reference[0]  # type: ignore[union-attr]
        assert rk.negate is False
        assert rk.severity == "error"

    def test_skips_non_dict_key_entries(self) -> None:
        result = parse_tc_metadata(
            {
                "tableTemplates": {
                    "t1": {
                        "columns": {},
                        "tc:keys": {
                            "unique": [
                                {"name": "pk", "fields": ["id"]},
                                "not a dict",
                            ]
                        },
                    }
                }
            },
            {"tc": TC_NS},
        )
        assert result is not None
        keys = result.template_constraints["t1"].keys
        assert keys is not None
        assert keys.unique is not None
        assert len(keys.unique) == 1


class TestParseTcMetadataColumnOrder:
    def test_parses_column_order(self) -> None:
        result = parse_tc_metadata(
            {
                "tableTemplates": {
                    "t1": {
                        "columns": {},
                        "tc:columnOrder": ["col_a", "col_b", "col_c"],
                    }
                }
            },
            {"tc": TC_NS},
        )
        assert result is not None
        tc = result.template_constraints["t1"]
        assert tc.column_order == ("col_a", "col_b", "col_c")

    def test_skips_non_list_column_order(self) -> None:
        result = parse_tc_metadata(
            {
                "tableTemplates": {
                    "t1": {
                        "columns": {},
                        "tc:columnOrder": "not a list",
                    }
                }
            },
            {"tc": TC_NS},
        )
        assert result is not None
        assert "t1" not in result.template_constraints


class TestParseTcMetadataTableConstraints:
    def test_parses_table_constraints(self) -> None:
        result = parse_tc_metadata(
            {
                "tableTemplates": {
                    "t1": {
                        "columns": {},
                        "tc:tableConstraints": {
                            "minTables": 1,
                            "maxTables": 5,
                            "minTableRows": 10,
                            "maxTableRows": 100,
                        },
                    }
                }
            },
            {"tc": TC_NS},
        )
        assert result is not None
        tc_obj = result.template_constraints["t1"].table_constraints
        assert tc_obj is not None
        assert tc_obj.min_tables == 1
        assert tc_obj.max_tables == 5
        assert tc_obj.min_table_rows == 10
        assert tc_obj.max_table_rows == 100

    def test_partial_table_constraints(self) -> None:
        result = parse_tc_metadata(
            {
                "tableTemplates": {
                    "t1": {
                        "columns": {},
                        "tc:tableConstraints": {"minTables": 1},
                    }
                }
            },
            {"tc": TC_NS},
        )
        assert result is not None
        tc_obj = result.template_constraints["t1"].table_constraints
        assert tc_obj is not None
        assert tc_obj.min_tables == 1
        assert tc_obj.max_tables is None
        assert tc_obj.min_table_rows is None
        assert tc_obj.max_table_rows is None


class TestParseTcMetadataMultipleTemplates:
    def test_parses_multiple_templates(self) -> None:
        result = parse_tc_metadata(
            {
                "tableTemplates": {
                    "customers": {
                        "columns": {"id": {"tc:constraints": {"type": "xs:integer"}}},
                    },
                    "orders": {
                        "columns": {"order_id": {"tc:constraints": {"type": "xs:integer"}}},
                        "tc:keys": {"unique": [{"name": "pk", "fields": ["order_id"]}]},
                    },
                    "no_tc": {
                        "columns": {"plain_col": {}},
                    },
                }
            },
            {"tc": TC_NS},
        )
        assert result is not None
        assert "customers" in result.template_constraints
        assert "orders" in result.template_constraints
        assert "no_tc" not in result.template_constraints

    def test_skips_template_with_no_tc_properties(self) -> None:
        result = parse_tc_metadata(
            {
                "tableTemplates": {
                    "t1": {
                        "columns": {"col_a": {"dimensions": {"concept": "foo"}}},
                    }
                }
            },
            {"tc": TC_NS},
        )
        assert result is not None
        assert result.template_constraints == {}

    def test_skips_non_dict_template(self) -> None:
        result = parse_tc_metadata(
            {
                "tableTemplates": {
                    "bad": "not a dict",
                    "good": {"columns": {"col": {"tc:constraints": {"type": "xs:string"}}}},
                }
            },
            {"tc": TC_NS},
        )
        assert result is not None
        assert "bad" not in result.template_constraints
        assert "good" in result.template_constraints


class TestParseTcMetadataNoTableTemplates:
    def test_missing_table_templates_key(self) -> None:
        result = parse_tc_metadata({}, {"tc": TC_NS})
        assert result is not None
        assert result.template_constraints == {}


class TestFrozenDataclasses:
    def test_value_constraint_is_frozen(self) -> None:
        vc = TCValueConstraint(type="xs:string")
        with pytest.raises(AttributeError):
            vc.type = "xs:integer"  # type: ignore[misc]

    def test_unique_key_is_frozen(self) -> None:
        uk = TCUniqueKey(name="pk", fields=("id",))
        with pytest.raises(AttributeError):
            uk.name = "other"  # type: ignore[misc]

    def test_metadata_is_frozen(self) -> None:
        md = TCMetadata()
        with pytest.raises(AttributeError):
            md.template_constraints = {}  # type: ignore[misc]
