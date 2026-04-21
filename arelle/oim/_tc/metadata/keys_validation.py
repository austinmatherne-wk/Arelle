"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from collections.abc import Generator, Mapping

from arelle.oim._tc.const import (
    TC_KEYS_PROPERTY_NAME,
    TCME_DUPLICATE_KEY_NAME,
    TCME_MISSING_KEY_PROPERTY,
)
from arelle.oim._tc.metadata.common import TCMetadataValidationError
from arelle.oim._tc.metadata.model import TCKeys, TCMetadata, TCTemplateConstraints
from arelle.oim.csv.metadata.common import TABLE_TEMPLATES_KEY
from arelle.typing import TypeGetText

_: TypeGetText


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

    if keys.reference is not None:
        for ref_i, ref_key in enumerate(keys.reference):
            name_occurrences.setdefault(ref_key.name, []).append(("reference", ref_i))

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
