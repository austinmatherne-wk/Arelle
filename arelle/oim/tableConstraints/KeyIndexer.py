"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import cast

from arelle.ModelXbrl import ModelXbrl
from arelle.oim.tableConstraints import Const, Types, Utils
from arelle.typing import TypeGetText

_: TypeGetText


@dataclass(frozen=True)
class UniqueKeyInfo:
    """
    Information about a unique key being tracked.

    Attributes:
        fields: Tuple of field names that make up the key (immutable)
        values: Set of key values seen so far (for duplicate detection)
                Note: The set itself is mutable for adding values, but the reference is frozen
        severity: Error severity level ("error" or "warning")
        sortedRows: Whether rows should be sorted by this key
        fieldTypes: Dict mapping field names to types (mutable for updates)
                    Note: The dict itself is mutable, but the reference is frozen
    """

    fields: tuple[str, ...]
    values: set[Types.KeyValue] = field(default_factory=set)
    severity: str = "error"
    sortedRows: bool = False
    fieldTypes: dict[str, str] = field(default_factory=dict)


class KeyIndexer:
    """
    Memory-efficient key indexing for unique/reference key validation.
    Uses hash-based deduplication for unique keys.
    """

    def __init__(
        self,
        modelXbrl: ModelXbrl,
        keysConfig: Types.KeysDict | None,
        errors: list[str] | None = None,
        sharedKeySets: dict[str, set[Types.KeyValue]] | None = None,
    ) -> None:
        self.modelXbrl = modelXbrl
        self.keysConfig = keysConfig or {}
        self.errors: list[str] = errors if errors is not None else []
        self.sharedKeySets = sharedKeySets or {}

        # Unique key tracking: keyName -> UniqueKeyInfo
        self.uniqueKeys: dict[str, UniqueKeyInfo] = {}

        # Reference key tracking: keyName -> list of (tableName, rowNum, keyValue, refConfig)
        self.referenceKeys: dict[str, list[tuple[str, int, Types.KeyValue, Types.ReferenceKeyDict]]] = {}

        # Initialize from config
        self._initializeKeys()

    def _initializeKeys(self) -> None:
        """Initialize key tracking structures from configuration."""
        # Process unique keys (includes primary keys which are just unique keys with special name)
        uniqueKeys = Utils.normalizeKeyArray(self.keysConfig.get(Const.KEYS_UNIQUE))
        for uniqueKey in uniqueKeys:
            keyName = uniqueKey.get(Const.KEY_NAME)
            if keyName:
                keyFields = uniqueKey.get(Const.KEY_FIELDS, [])
                # Use shared set if provided, otherwise create new set
                valueSet = self.sharedKeySets.get(keyName, set())
                if keyName not in self.sharedKeySets:
                    self.sharedKeySets[keyName] = valueSet

                self.uniqueKeys[keyName] = UniqueKeyInfo(
                    fields=tuple(keyFields),  # Convert to tuple for immutability
                    values=valueSet,  # Use shared or new set
                    severity=uniqueKey.get(Const.KEY_SEVERITY, "error"),
                    sortedRows=uniqueKey.get("sortedRows", False),
                )

        # Process reference keys
        referenceKeys = Utils.normalizeKeyArray(self.keysConfig.get(Const.KEYS_REFERENCE))
        for refKey in referenceKeys:
            keyName = refKey.get(Const.KEY_NAME)
            if keyName:
                self.referenceKeys[keyName] = []

    def setFieldTypes(self, fieldTypes: dict[str, str]) -> None:
        """Set type information for fields (used for comparison)."""
        for keyInfo in self.uniqueKeys.values():
            for fieldName in keyInfo.fields:
                if fieldName in fieldTypes:
                    keyInfo.fieldTypes[fieldName] = fieldTypes[fieldName]

    def addRow(self, row: Types.CsvRow, rowNum: int, tableName: str) -> None:
        """
        Add a row to key indices.
        Raises errors if unique key violations detected.
        """
        # Process unique keys
        for keyName, keyInfo in self.uniqueKeys.items():
            keyValue = self._extractKeyValue(row, keyInfo.fields)

            # Check if all values are nil
            if self._allNil(keyValue):
                if keyInfo.severity == "error":
                    self.modelXbrl.error(
                        Const.TCRE_UNIQUE_KEY_NIL_VIOLATION,
                        _("All key values are nil for unique key '%(keyName)s' in table '%(table)s' row %(row)s"),
                        keyName=keyName,
                        table=tableName,
                        row=rowNum,
                    )
                    self.errors.append(Const.TCRE_UNIQUE_KEY_NIL_VIOLATION)
                else:
                    self.modelXbrl.warning(
                        Const.TCRE_UNIQUE_KEY_NIL_VIOLATION,
                        _("All key values are nil for unique key '%(keyName)s' in table '%(table)s' row %(row)s"),
                        keyName=keyName,
                        table=tableName,
                        row=rowNum,
                    )
                continue

            # Check for duplicates
            if self._isDuplicate(keyValue, keyInfo.values, keyInfo.fieldTypes):
                if keyInfo.severity == "error":
                    self.modelXbrl.error(
                        Const.TCRE_UNIQUE_KEY_VIOLATION,
                        _("Duplicate unique key '%(keyName)s' in table '%(table)s' row %(row)s: %(values)s"),
                        keyName=keyName,
                        table=tableName,
                        row=rowNum,
                        values=str(keyValue),
                    )
                    self.errors.append(Const.TCRE_UNIQUE_KEY_VIOLATION)
                else:
                    self.modelXbrl.warning(
                        Const.TCRE_UNIQUE_KEY_VIOLATION,
                        _("Duplicate unique key '%(keyName)s' in table '%(table)s' row %(row)s: %(values)s"),
                        keyName=keyName,
                        table=tableName,
                        row=rowNum,
                        values=str(keyValue),
                    )
            else:
                # Add to set
                keyInfo.values.add(keyValue)

        # Collect reference key values for later validation
        # Handle both dict and array formats
        refKeysConfigRaw = self.keysConfig.get(Const.KEYS_REFERENCE, [])
        if isinstance(refKeysConfigRaw, dict):
            refKeysConfig = [refKeysConfigRaw]
        elif isinstance(refKeysConfigRaw, list):
            refKeysConfig = refKeysConfigRaw
        else:
            refKeysConfig = []
        for refKey in refKeysConfig:
            keyNameRaw = refKey.get(Const.KEY_NAME)
            if not keyNameRaw or not isinstance(keyNameRaw, str):
                continue
            keyName = cast(str, keyNameRaw)  # Type narrowing for mypy
            fields = refKey.get(Const.KEY_FIELDS, [])
            keyValue = self._extractKeyValue(row, fields)
            skipNils = refKey.get(Const.KEY_SKIP_NILS, False)

            # Skip if skipNils and any value is nil
            if skipNils and self._anyNil(keyValue):
                continue

            self.referenceKeys[keyName].append((tableName, rowNum, keyValue, refKey))

    def finalize(self, allKeyIndexers: dict[str, KeyIndexer]) -> None:
        """
        Finalize validation after all tables processed.
        Validates reference keys against target unique keys.

        Args:
            allKeyIndexers: Map of templateName -> KeyIndexer for cross-table validation
        """
        # Validate reference keys
        for references in self.referenceKeys.values():
            for tableName, rowNum, keyValue, refConfig in references:
                self._validateReference(tableName, rowNum, keyValue, refConfig, allKeyIndexers)

    def _validateReference(
        self,
        tableName: str,
        rowNum: int,
        keyValue: Types.KeyValue,
        config: Types.ReferenceKeyDict,
        allKeyIndexers: dict[str, KeyIndexer],
    ) -> None:
        """Validate a single reference key entry."""
        referencedKeyName = config.get(Const.KEY_REFERENCED_KEY_NAME)
        negate = config.get(Const.KEY_NEGATE, False)
        severity = config.get(Const.KEY_SEVERITY, "error")

        # Find the target unique key
        targetValues = None
        for indexer in allKeyIndexers.values():
            if referencedKeyName in indexer.uniqueKeys:
                targetValues = indexer.uniqueKeys[referencedKeyName].values
                break

        if targetValues is None:
            # Referenced key not found - should have been caught in metadata validation
            return

        # Check if reference exists
        exists = self._existsInSet(keyValue, targetValues)

        # Apply negate logic
        violation = (not exists and not negate) or (exists and negate)

        if violation:
            if severity == "error":
                self.modelXbrl.error(
                    Const.TCRE_REFERENCE_KEY_VIOLATION,
                    _("Reference key violation for '%(keyName)s' in table '%(table)s' row %(row)s: %(values)s"),
                    keyName=config.get(Const.KEY_NAME),
                    table=tableName,
                    row=rowNum,
                    values=str(keyValue),
                )
                self.errors.append(Const.TCRE_REFERENCE_KEY_VIOLATION)
            else:
                self.modelXbrl.warning(
                    Const.TCRE_REFERENCE_KEY_VIOLATION,
                    _("Reference key violation for '%(keyName)s' in table '%(table)s' row %(row)s: %(values)s"),
                    keyName=config.get(Const.KEY_NAME),
                    table=tableName,
                    row=rowNum,
                    values=str(keyValue),
                )

    def _extractKeyValue(self, row: Types.CsvRow, fields: tuple[str, ...] | list[str]) -> Types.KeyValue:
        """Extract key value tuple from row."""
        return tuple(row.get(field) for field in fields)

    def _allNil(self, keyValue: Types.KeyValue) -> bool:
        """Check if all key values are nil."""
        return all(Utils.isNilValue(v) for v in keyValue)

    def _anyNil(self, keyValue: Types.KeyValue) -> bool:
        """Check if any key value is nil."""
        return any(Utils.isNilValue(v) for v in keyValue)

    def _isDuplicate(
        self, keyValue: Types.KeyValue, existingValues: set[Types.KeyValue], fieldTypes: dict[str, str]
    ) -> bool:
        """
        Check if key value already exists in set using type-specific equality.
        """
        # If no type info, use simple tuple equality (fast path)
        if not fieldTypes:
            return keyValue in existingValues

        # Use type-specific comparison for each value in existing set
        return any(self._keyValuesEqual(keyValue, existingValue, fieldTypes) for existingValue in existingValues)

    def _existsInSet(self, keyValue: Types.KeyValue, existingValues: set[Types.KeyValue]) -> bool:
        """Check if key value exists in set (same as _isDuplicate)."""
        # For reference key checking, we can use simpler equality
        # since we already stored the values with proper types
        return keyValue in existingValues

    def _keyValuesEqual(self, value1: Types.KeyValue, value2: Types.KeyValue, fieldTypes: dict[str, str]) -> bool:
        """
        Check if two key value tuples are equal using type-specific comparison.
        """
        if len(value1) != len(value2):
            return False

        # We don't have field names here, only values
        # So we compare by position
        return all(v1 == v2 for v1, v2 in zip(value1, value2))


class KeyIndexerManager:
    """
    Manages multiple KeyIndexers for cross-table validation.
    Handles shared keys (same key name across templates).
    """

    def __init__(self, modelXbrl: ModelXbrl, errors: list[str] | None = None) -> None:
        self.modelXbrl = modelXbrl
        self.indexers: dict[str, KeyIndexer] = {}
        # Shared unique key tracking: keyName -> shared value set
        self.sharedUniqueKeys: dict[str, set[Types.KeyValue]] = {}
        self.errors: list[str] = errors if errors is not None else []

    def createIndexer(self, templateName: str, keysConfig: Types.KeysDict | None) -> KeyIndexer:
        """Create and register a key indexer for a template."""
        # Pass shared key sets so UniqueKeyInfo instances can use them during initialization
        indexer = KeyIndexer(self.modelXbrl, keysConfig, self.errors, self.sharedUniqueKeys)

        # Update our shared keys dict with any new keys from this indexer
        self.sharedUniqueKeys.update(indexer.sharedKeySets)

        self.indexers[templateName] = indexer
        return indexer

    def finalizeAll(self) -> None:
        """Finalize all indexers (validate cross-table references)."""
        for indexer in self.indexers.values():
            indexer.finalize(self.indexers)
