"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

# Row data types
# CSV row is a dict mapping column name to string value (or None for nil)
CsvRow = dict[str, str | None]

# Key value is a tuple of field values extracted from a row
KeyValue = tuple[str | None, ...]

# JSON metadata structure types (using dict[str, Any] for flexibility with dynamic JSON)
# These are more semantic aliases rather than strict types

# Constraint definition with type, optional/nillable, and facets
ConstraintDict = dict[str, Any]

# Column definition in a table template
ColumnDict = dict[str, Any]

# Parameter definition
ParameterDict = dict[str, Any]

# Unique key definition
UniqueKeyDict = dict[str, Any]

# Reference key definition
ReferenceKeyDict = dict[str, Any]

# Keys configuration (unique, reference, sortKey)
KeysDict = dict[str, Any]

# Table-level constraints (minTables, maxTables, minTableRows, maxTableRows)
TableConstraintsDict = dict[str, Any]

# Table template definition
TableTemplateDict = dict[str, Any]

# Table configuration in xBRL-CSV metadata
TableConfigDict = dict[str, Any]

# Document info section
DocumentInfoDict = dict[str, Any]

# Complete xBRL-CSV metadata structure with Table Constraints
MetadataDict = dict[str, Any]


@dataclass(frozen=True)
class Metadata:
    """
    Immutable wrapper around xBRL-CSV metadata dictionary providing convenient accessors.

    This frozen dataclass encapsulates metadata access patterns and provides a cleaner API
    than passing around both metadata dict and namespaces separately.

    The dataclass is frozen to ensure metadata immutability after loading, preventing
    accidental modifications during validation.

    Example usage:
        metadata = Metadata(rawMetadataDict)
        namespaces = metadata.namespaces
        tables = metadata.tables
    """

    _data: MetadataDict

    @property
    def namespaces(self) -> dict[str, str]:
        """Get namespace prefix mappings from documentInfo."""
        return cast(dict[str, str], self._data.get("documentInfo", {}).get("namespaces", {}))

    @property
    def documentInfo(self) -> DocumentInfoDict:
        """Get documentInfo section."""
        return cast(DocumentInfoDict, self._data.get("documentInfo", {}))

    @property
    def tableTemplates(self) -> dict[str, TableTemplateDict]:
        """Get table templates dictionary."""
        return cast(dict[str, TableTemplateDict], self._data.get("tableTemplates", {}))

    @property
    def tables(self) -> dict[str, TableConfigDict]:
        """Get tables dictionary."""
        return cast(dict[str, TableConfigDict], self._data.get("tables", {}))
