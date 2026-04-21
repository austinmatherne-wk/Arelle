"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from collections.abc import Generator, Mapping

from arelle.oim._tc.const import (
    TC_KEYS_PROPERTY_NAME,
    TCME_DUPLICATE_KEY_NAME,
    TCME_ILLEGAL_KEY_FIELD,
    TCME_INCONSISTENT_REFERENCE_KEY_FIELDS,
    TCME_INCONSISTENT_SHARED_KEY_FIELDS,
    TCME_INCONSISTENT_SHARED_KEY_SEVERITY,
    TCME_MISSING_KEY_PROPERTY,
    TCME_UNKNOWN_KEY,
    TCME_UNKNOWN_SEVERITY,
)
from arelle.oim._tc.metadata.common import TCMetadataValidationError
from arelle.oim._tc.metadata.model import TCKeys, TCMetadata, TCTemplateConstraints, TCUniqueKey
from arelle.oim._tc.metadata.types import (
    OPTIONALLY_TIME_ZONED_TYPES,
    PERIOD_CONSTRAINT_TYPE,
    PROHIBITED_KEY_TYPES,
    resolve_effective_lexical_type,
)
from arelle.oim.csv.metadata.common import TABLE_TEMPLATES_KEY
from arelle.typing import TypeGetText
from arelle.XbrlConst import qnXsdDuration

_: TypeGetText

_VALID_SEVERITIES = frozenset(
    {
        "error",
        "warning",
    }
)


def validate_keys(
    tc_metadata: TCMetadata,
    namespaces: Mapping[str, str],
) -> Generator[TCMetadataValidationError, None, None]:
    """Validates all tc:keys structures across the metadata.

    Yields TCMetadataValidationError with full path segments.
    """
    for template_id, tc in tc_metadata.template_constraints.items():
        if tc.keys is not None:
            keys_path = (TABLE_TEMPLATES_KEY, template_id, TC_KEYS_PROPERTY_NAME)
            for error in _validate_template_keys(tc.keys, tc, namespaces):
                error.prepend_path(*keys_path)
                yield error
    yield from _validate_cross_template_unique_keys(tc_metadata)
    yield from _validate_referenced_key_names(tc_metadata)
    yield from _validate_reference_key_field_consistency(tc_metadata)
    yield from _validate_shared_key_consistency(tc_metadata)


def _validate_template_keys(
    keys: TCKeys,
    tc: TCTemplateConstraints,
    namespaces: Mapping[str, str],
) -> Generator[TCMetadataValidationError, None, None]:
    """Yields TCMetadataValidationError with relative path segments."""
    if keys.unique is None and keys.reference is None:
        yield TCMetadataValidationError(
            _("At least one of 'unique' and 'reference' must be specified"),
            code=TCME_MISSING_KEY_PROPERTY,
        )
        return

    name_occurrences: dict[str, list[tuple[str, int]]] = {}
    if keys.unique is not None:
        for key_i, key in enumerate(keys.unique):
            name_occurrences.setdefault(key.name, []).append(("unique", key_i))
            if key.severity not in _VALID_SEVERITIES:
                yield TCMetadataValidationError(
                    _("Unknown severity '{}' for unique key '{}'").format(key.severity, key.name),
                    "unique",
                    str(key_i),
                    "severity",
                    code=TCME_UNKNOWN_SEVERITY,
                )
            yield from _validate_key_fields(key.fields, tc, namespaces, "unique", key_i)

    if keys.reference is not None:
        for ref_i, ref_key in enumerate(keys.reference):
            name_occurrences.setdefault(ref_key.name, []).append(("reference", ref_i))
            if ref_key.severity not in _VALID_SEVERITIES:
                yield TCMetadataValidationError(
                    _("Unknown severity '{}' for reference key '{}'").format(ref_key.severity, ref_key.name),
                    "reference",
                    str(ref_i),
                    "severity",
                    code=TCME_UNKNOWN_SEVERITY,
                )
            yield from _validate_key_fields(ref_key.fields, tc, namespaces, "reference", ref_i)

    for name, name_occ in name_occurrences.items():
        if len(name_occ) < 2:
            continue
        first_section, first_index = name_occ[0]
        yield TCMetadataValidationError(
            _("Duplicate key name '{}'").format(name),
            first_section,
            str(first_index),
            "name",
            code=TCME_DUPLICATE_KEY_NAME,
            related_paths=tuple((section, str(index), "name") for section, index in name_occ[1:]),
        )

    if keys.sort_key is not None:
        unique_key_names = {key.name for key in (keys.unique or ())}
        if keys.sort_key not in unique_key_names:
            yield TCMetadataValidationError(
                _("Sort key '{}' does not refer to a unique key in this template").format(keys.sort_key),
                "sortKey",
                code=TCME_UNKNOWN_KEY,
            )


def _validate_key_fields(
    fields: tuple[str, ...],
    tc: TCTemplateConstraints,
    namespaces: Mapping[str, str],
    key_kind: str,
    key_i: int,
) -> Generator[TCMetadataValidationError, None, None]:
    """Validates fields in a single key, yielding errors with relative path segments."""
    for field_j, field in enumerate(fields):
        constraint = tc.constraints.get(field) or tc.parameters.get(field)
        if constraint is None:
            yield TCMetadataValidationError(
                _("Key field '{}' does not correspond to a constrained column or defined parameter").format(field),
                key_kind,
                str(key_i),
                "fields",
                str(field_j),
                code=TCME_ILLEGAL_KEY_FIELD,
            )
            continue
        effective_type = resolve_effective_lexical_type(constraint.type, namespaces)
        if effective_type is None:
            continue
        duration_type = effective_type == qnXsdDuration
        time_zone_type = effective_type in OPTIONALLY_TIME_ZONED_TYPES or constraint.type == PERIOD_CONSTRAINT_TYPE
        if effective_type in PROHIBITED_KEY_TYPES:
            yield TCMetadataValidationError(
                _("Key field '{}' uses prohibited type '{}'").format(field, constraint.type),
                key_kind,
                str(key_i),
                "fields",
                str(field_j),
                code=TCME_ILLEGAL_KEY_FIELD,
            )
        elif duration_type and constraint.duration_type is None:
            yield TCMetadataValidationError(
                _("Key field '{}' has type xs:duration but no durationType is specified").format(field),
                key_kind,
                str(key_i),
                "fields",
                str(field_j),
                code=TCME_ILLEGAL_KEY_FIELD,
            )
        elif time_zone_type and constraint.time_zone is None:
            yield TCMetadataValidationError(
                _("Key field '{}' has a time-zone-applicable type but no timeZone is specified").format(field),
                key_kind,
                str(key_i),
                "fields",
                str(field_j),
                code=TCME_ILLEGAL_KEY_FIELD,
            )


def _validate_cross_template_unique_keys(tc_metadata: TCMetadata) -> Generator[TCMetadataValidationError, None, None]:
    """Validates that unique key names are not duplicated across templates without shared=true."""
    occurrences: dict[str, list[tuple[str, int, bool]]] = {}
    for template_id, tc in tc_metadata.template_constraints.items():
        if tc.keys is None or tc.keys.unique is None:
            continue
        for key_i, key in enumerate(tc.keys.unique):
            occurrences.setdefault(key.name, []).append((template_id, key_i, key.shared))

    for key_name, key_occurrences in occurrences.items():
        templates = set()
        shared_keys = []
        non_shared_keys = []
        for tid, key_i, shared in key_occurrences:
            templates.add(tid)
            if shared:
                shared_keys.append((tid, key_i))
            else:
                non_shared_keys.append((tid, key_i))
        if len(templates) < 2 or len(non_shared_keys) == 0:
            continue
        first_template_id, first_key_i = non_shared_keys[0]
        yield TCMetadataValidationError(
            _("Duplicate key name '{}' across templates").format(key_name),
            TABLE_TEMPLATES_KEY,
            first_template_id,
            TC_KEYS_PROPERTY_NAME,
            "unique",
            str(first_key_i),
            "name",
            code=TCME_DUPLICATE_KEY_NAME,
            related_paths=tuple(
                (TABLE_TEMPLATES_KEY, tid, TC_KEYS_PROPERTY_NAME, "unique", str(key_i), "name")
                for tid, key_i in (*non_shared_keys[1:], *shared_keys)
            ),
        )


def _validate_referenced_key_names(tc_metadata: TCMetadata) -> Generator[TCMetadataValidationError, None, None]:
    """Validates that referencedKeyName in each reference key names an existing unique key."""
    all_unique_key_names = {
        key.name
        for tc in tc_metadata.template_constraints.values()
        if tc.keys is not None and tc.keys.unique is not None
        for key in tc.keys.unique
    }
    for template_id, tc in tc_metadata.template_constraints.items():
        if tc.keys is None or tc.keys.reference is None:
            continue
        for ref_i, ref_key in enumerate(tc.keys.reference):
            if ref_key.referenced_key_name not in all_unique_key_names:
                yield TCMetadataValidationError(
                    _("Referenced key '{}' does not exist as a unique key in any template").format(
                        ref_key.referenced_key_name
                    ),
                    TABLE_TEMPLATES_KEY,
                    template_id,
                    TC_KEYS_PROPERTY_NAME,
                    "reference",
                    str(ref_i),
                    "referencedKeyName",
                    code=TCME_UNKNOWN_KEY,
                )


def _validate_reference_key_field_consistency(
    tc_metadata: TCMetadata,
) -> Generator[TCMetadataValidationError, None, None]:
    """Validates that reference key fields are consistent with the referenced unique key's fields."""
    unique_key_registry: dict[str, tuple[str, int, TCUniqueKey]] = {}
    for template_id, tc in tc_metadata.template_constraints.items():
        if tc.keys is not None and tc.keys.unique is not None:
            for key_i, key in enumerate(tc.keys.unique):
                unique_key_registry.setdefault(key.name, (template_id, key_i, key))

    for template_id, tc in tc_metadata.template_constraints.items():
        if tc.keys is None or tc.keys.reference is None:
            continue
        for ref_i, ref_key in enumerate(tc.keys.reference):
            if ref_key.referenced_key_name not in unique_key_registry:
                continue
            unique_template_id, unique_key_i, unique_key = unique_key_registry[ref_key.referenced_key_name]
            unique_tc = tc_metadata.template_constraints[unique_template_id]
            ref_path = (TABLE_TEMPLATES_KEY, template_id, TC_KEYS_PROPERTY_NAME, "reference", str(ref_i))
            unique_path = (TABLE_TEMPLATES_KEY, unique_template_id, TC_KEYS_PROPERTY_NAME, "unique", str(unique_key_i))

            if len(ref_key.fields) != len(unique_key.fields):
                yield TCMetadataValidationError(
                    _("Reference key '{}' has {} fields but referenced key '{}' has {} fields").format(
                        ref_key.name,
                        len(ref_key.fields),
                        ref_key.referenced_key_name,
                        len(unique_key.fields),
                    ),
                    *ref_path,
                    "fields",
                    code=TCME_INCONSISTENT_REFERENCE_KEY_FIELDS,
                    related_paths=((*unique_path, "fields"),),
                )
                continue

            zipped_fields = zip(ref_key.fields, unique_key.fields, strict=True)
            for field_j, (ref_field, uniq_field) in enumerate(zipped_fields):
                ref_constraint = tc.constraints.get(ref_field) or tc.parameters.get(ref_field)
                uniq_constraint = unique_tc.constraints.get(uniq_field) or unique_tc.parameters.get(uniq_field)
                if ref_constraint is None or uniq_constraint is None:
                    continue
                if (
                    ref_constraint.type != uniq_constraint.type
                    or ref_constraint.time_zone != uniq_constraint.time_zone
                    or ref_constraint.duration_type != uniq_constraint.duration_type
                ):
                    yield TCMetadataValidationError(
                        _("Reference key '{}' has fields inconsistent with referenced key '{}'").format(
                            ref_key.name, ref_key.referenced_key_name
                        ),
                        *ref_path,
                        "fields",
                        str(field_j),
                        code=TCME_INCONSISTENT_REFERENCE_KEY_FIELDS,
                        related_paths=((*unique_path, "fields", str(field_j)),),
                    )
                    break


def _validate_shared_key_consistency(tc_metadata: TCMetadata) -> Generator[TCMetadataValidationError, None, None]:
    """Validates that shared unique keys with the same name have consistent fields and severity."""
    shared_key_occurrences: dict[str, list[tuple[str, int, TCUniqueKey]]] = {}
    for template_id, tc in tc_metadata.template_constraints.items():
        if tc.keys is not None and tc.keys.unique is not None:
            for key_i, key in enumerate(tc.keys.unique):
                if key.shared:
                    shared_key_occurrences.setdefault(key.name, []).append((template_id, key_i, key))

    for key_name, occurrences in shared_key_occurrences.items():
        if len(occurrences) < 2:
            continue
        first_template_id, first_key_i, first_key = occurrences[0]
        first_tc = tc_metadata.template_constraints[first_template_id]
        first_path = (TABLE_TEMPLATES_KEY, first_template_id, TC_KEYS_PROPERTY_NAME, "unique", str(first_key_i))

        fields_diverging = []
        for tid, ki, key in occurrences[1:]:
            if len(key.fields) != len(first_key.fields):
                fields_diverging.append((TABLE_TEMPLATES_KEY, tid, TC_KEYS_PROPERTY_NAME, "unique", str(ki), "fields"))
                continue
            this_tc = tc_metadata.template_constraints[tid]
            for this_field, first_field in zip(key.fields, first_key.fields, strict=True):
                this_constraint = this_tc.constraints.get(this_field) or this_tc.parameters.get(this_field)
                first_constraint = first_tc.constraints.get(first_field) or first_tc.parameters.get(first_field)
                if this_constraint is None or first_constraint is None:
                    continue
                if (
                    this_constraint.type != first_constraint.type
                    or this_constraint.time_zone != first_constraint.time_zone
                    or this_constraint.duration_type != first_constraint.duration_type
                ):
                    fields_diverging.append(
                        (TABLE_TEMPLATES_KEY, tid, TC_KEYS_PROPERTY_NAME, "unique", str(ki), "fields")
                    )
                    break
        if fields_diverging:
            yield TCMetadataValidationError(
                _("Shared key '{}' has inconsistent fields across templates").format(key_name),
                *first_path,
                "fields",
                code=TCME_INCONSISTENT_SHARED_KEY_FIELDS,
                related_paths=tuple(fields_diverging),
            )

        severity_diverging = [
            (TABLE_TEMPLATES_KEY, tid, TC_KEYS_PROPERTY_NAME, "unique", str(ki), "severity")
            for tid, ki, key in occurrences[1:]
            if key.severity != first_key.severity
        ]
        if severity_diverging:
            yield TCMetadataValidationError(
                _("Shared key '{}' has inconsistent severity across templates").format(key_name),
                *first_path,
                "severity",
                code=TCME_INCONSISTENT_SHARED_KEY_SEVERITY,
                related_paths=tuple(severity_diverging),
            )
