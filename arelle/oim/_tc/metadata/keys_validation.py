"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from collections.abc import Generator, Mapping

from arelle.oim._tc.const import (
    TC_KEYS_PROPERTY_NAME,
    TCME_DUPLICATE_KEY_NAME,
    TCME_ILLEGAL_KEY_FIELD,
    TCME_MISSING_KEY_PROPERTY,
    TCME_UNKNOWN_SEVERITY,
)
from arelle.oim._tc.metadata.common import TCMetadataValidationError
from arelle.oim._tc.metadata.model import TCKeys, TCMetadata, TCTemplateConstraints
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
