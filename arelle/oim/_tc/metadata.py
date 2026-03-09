"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from arelle.oim._tc.const import (
    TC_COLUMN_ORDER,
    TC_CONSTRAINTS,
    TC_KEYS,
    TC_NAMESPACES_SET,
    TC_PARAMETERS,
    TC_TABLE_CONSTRAINTS,
)


@dataclass(frozen=True)
class TCValueConstraint:
    type: str
    optional: bool = False
    nillable: bool = False
    enumeration_values: tuple[str, ...] | None = None
    patterns: tuple[str, ...] | None = None
    time_zone: bool | None = None
    period_type: str | None = None
    duration_type: str | None = None
    length: int | None = None
    min_length: int | None = None
    max_length: int | None = None
    min_inclusive: str | None = None
    max_inclusive: str | None = None
    min_exclusive: str | None = None
    max_exclusive: str | None = None
    total_digits: int | None = None
    fraction_digits: int | None = None


@dataclass(frozen=True)
class TCUniqueKey:
    name: str
    fields: tuple[str, ...]
    severity: str = "error"
    shared: bool = False


@dataclass(frozen=True)
class TCReferenceKey:
    name: str
    fields: tuple[str, ...]
    referenced_key_name: str
    negate: bool = False
    severity: str = "error"


@dataclass(frozen=True)
class TCKeys:
    unique: tuple[TCUniqueKey, ...] | None = None
    reference: tuple[TCReferenceKey, ...] | None = None
    sort_key: str | None = None


@dataclass(frozen=True)
class TCTableConstraints:
    min_tables: int | None = None
    max_tables: int | None = None
    min_table_rows: int | None = None
    max_table_rows: int | None = None


@dataclass(frozen=True)
class TCTemplateConstraints:
    constraints: dict[str, TCValueConstraint] = field(default_factory=dict)
    parameters: dict[str, TCValueConstraint] = field(default_factory=dict)
    keys: TCKeys | None = None
    column_order: tuple[str, ...] | None = None
    table_constraints: TCTableConstraints | None = None


@dataclass(frozen=True)
class TCMetadata:
    template_constraints: dict[str, TCTemplateConstraints] = field(default_factory=dict)


def _to_str_tuple(val: Any) -> tuple[str, ...] | None:
    if isinstance(val, list):
        return tuple(val)
    return None


def _parse_value_constraint(obj: dict[str, Any]) -> TCValueConstraint:
    return TCValueConstraint(
        type=obj.get("type", ""),
        optional=obj.get("optional", False),
        nillable=obj.get("nillable", False),
        enumeration_values=_to_str_tuple(obj.get("enumerationValues")),
        patterns=_to_str_tuple(obj.get("patterns")),
        time_zone=obj.get("timeZone"),
        period_type=obj.get("periodType"),
        duration_type=obj.get("durationType"),
        length=obj.get("length"),
        min_length=obj.get("minLength"),
        max_length=obj.get("maxLength"),
        min_inclusive=obj.get("minInclusive"),
        max_inclusive=obj.get("maxInclusive"),
        min_exclusive=obj.get("minExclusive"),
        max_exclusive=obj.get("maxExclusive"),
        total_digits=obj.get("totalDigits"),
        fraction_digits=obj.get("fractionDigits"),
    )


def _parse_unique_key(obj: dict[str, Any]) -> TCUniqueKey:
    return TCUniqueKey(
        name=obj.get("name", ""),
        fields=tuple(obj.get("fields", ())),
        severity=obj.get("severity", "error"),
        shared=obj.get("shared", False),
    )


def _parse_reference_key(obj: dict[str, Any]) -> TCReferenceKey:
    return TCReferenceKey(
        name=obj.get("name", ""),
        fields=tuple(obj.get("fields", ())),
        referenced_key_name=obj.get("referencedKeyName", ""),
        negate=obj.get("negate", False),
        severity=obj.get("severity", "error"),
    )


def _parse_keys(obj: dict[str, Any]) -> TCKeys:
    unique = None
    unique_list = obj.get("unique")
    if isinstance(unique_list, list):
        unique = tuple(_parse_unique_key(k) for k in unique_list if isinstance(k, dict))

    reference = None
    reference_list = obj.get("reference")
    if isinstance(reference_list, list):
        reference = tuple(_parse_reference_key(k) for k in reference_list if isinstance(k, dict))

    return TCKeys(
        unique=unique,
        reference=reference,
        sort_key=obj.get("sortKey"),
    )


def _parse_table_constraints(obj: dict[str, Any]) -> TCTableConstraints:
    return TCTableConstraints(
        min_tables=obj.get("minTables"),
        max_tables=obj.get("maxTables"),
        min_table_rows=obj.get("minTableRows"),
        max_table_rows=obj.get("maxTableRows"),
    )


def parse_tc_metadata(
    oim_object: dict[str, Any],
    namespaces: dict[str, str],
) -> TCMetadata | None:
    """Parse TC metadata from an xBRL-CSV metadata object.

    Returns None if no TC namespace is declared in the document.
    Does NOT validate — just parses whatever TC data is present.
    """
    # Check if TC namespace is present
    has_tc = any(uri in TC_NAMESPACES_SET for uri in namespaces.values())
    if not has_tc:
        return None

    template_constraints: dict[str, TCTemplateConstraints] = {}
    table_templates = oim_object.get("tableTemplates", {})

    for template_id, template_obj in table_templates.items():
        if not isinstance(template_obj, dict):
            continue

        # Parse column constraints
        column_constraints: dict[str, TCValueConstraint] = {}
        columns = template_obj.get("columns", {})
        if isinstance(columns, dict):
            for col_name, col_obj in columns.items():
                if not isinstance(col_obj, dict):
                    continue
                constraint_obj = col_obj.get(TC_CONSTRAINTS)
                if isinstance(constraint_obj, dict):
                    column_constraints[col_name] = _parse_value_constraint(constraint_obj)

        # Parse parameter definitions
        param_constraints: dict[str, TCValueConstraint] = {}
        params_obj = template_obj.get(TC_PARAMETERS)
        if isinstance(params_obj, dict):
            for param_name, param_obj in params_obj.items():
                if isinstance(param_obj, dict):
                    param_constraints[param_name] = _parse_value_constraint(param_obj)

        # Parse keys
        keys: TCKeys | None = None
        keys_obj = template_obj.get(TC_KEYS)
        if isinstance(keys_obj, dict):
            keys = _parse_keys(keys_obj)

        # Parse column order
        column_order: tuple[str, ...] | None = None
        column_order_obj = template_obj.get(TC_COLUMN_ORDER)
        if isinstance(column_order_obj, list):
            column_order = tuple(column_order_obj)

        # Parse table constraints
        table_constraints: TCTableConstraints | None = None
        table_constraints_obj = template_obj.get(TC_TABLE_CONSTRAINTS)
        if isinstance(table_constraints_obj, dict):
            table_constraints = _parse_table_constraints(table_constraints_obj)

        # Only create entry if template has at least one TC property
        if column_constraints or param_constraints or keys or column_order is not None or table_constraints:
            template_constraints[template_id] = TCTemplateConstraints(
                constraints=column_constraints,
                parameters=param_constraints,
                keys=keys,
                column_order=column_order,
                table_constraints=table_constraints,
            )

    return TCMetadata(template_constraints=template_constraints)
