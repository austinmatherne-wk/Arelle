"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from typing import Any

# Re-export Metadata and MetadataDict from Metadata module for backward compatibility
from arelle.oim.tableConstraints.Metadata import Metadata, MetadataDict

CsvRow = dict[str, str | None]

KeyValue = tuple[str | None, ...]

ConstraintDict = dict[str, Any]

ColumnDict = dict[str, Any]

ParameterDict = dict[str, Any]

UniqueKeyDict = dict[str, Any]

ReferenceKeyDict = dict[str, Any]

KeysDict = dict[str, Any]

TableConstraintsDict = dict[str, Any]

TableTemplateDict = dict[str, Any]

TableConfigDict = dict[str, Any]

DocumentInfoDict = dict[str, Any]
