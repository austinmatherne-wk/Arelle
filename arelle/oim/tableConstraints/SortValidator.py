"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from typing import Any

from arelle.ModelXbrl import ModelXbrl
from arelle.oim.tableConstraints import Const, Types, Utils
from arelle.oim.tableConstraints.XmlSchemaHelper import compareValues
from arelle.typing import TypeGetText

_: TypeGetText


class SortValidator:
    """
    Validates row sorting with constant memory.
    Only stores last seen row for comparison.
    """

    def __init__(
        self,
        modelXbrl: ModelXbrl,
        keyName: str | None,
        keyFields: list[str],
        fieldTypes: dict[str, str],
        namespaces: dict[str, str],
        errors: list[str] | None = None,
    ) -> None:
        self.modelXbrl = modelXbrl
        self.keyName = keyName
        self.keyFields = keyFields
        self.fieldTypes = fieldTypes
        self.namespaces = namespaces
        self.lastRow: Types.CsvRow | None = None
        self.lastRowNum = 0
        self.lastTableName: str | None = None
        self.enabled = keyName is not None and len(keyFields) > 0
        self.errors: list[str] = errors if errors is not None else []

    def checkRow(self, currentRow: Types.CsvRow, rowNum: int, tableName: str) -> None:
        """
        Check if current row is sorted correctly relative to last row.
        Raises error if sort order is violated.
        """
        if not self.enabled:
            return

        if self.lastRow is None:
            # First row - just store it
            self.lastRow = currentRow
            self.lastRowNum = rowNum
            self.lastTableName = tableName
            return

        # Compare current row with last row
        comparison = self._compareRows(self.lastRow, currentRow)

        if comparison > 0:
            # lastRow > currentRow - wrong order!
            self.modelXbrl.error(
                Const.TCRE_KEY_SORT_VIOLATION,
                _(
                    "Sort order violation for key '%(keyName)s': "
                    "row %(currentRow)s in table '%(currentTable)s' "
                    "comes before row %(lastRow)s in table '%(lastTable)s'"
                ),
                keyName=self.keyName,
                currentRow=rowNum,
                currentTable=tableName,
                lastRow=self.lastRowNum,
                lastTable=self.lastTableName,
            )
            self.errors.append(Const.TCRE_KEY_SORT_VIOLATION)  # Track error for summary

        # Store current row for next comparison
        self.lastRow = currentRow
        self.lastRowNum = rowNum
        self.lastTableName = tableName

    def _compareRows(self, row1: Types.CsvRow, row2: Types.CsvRow) -> int:
        """
        Compare two rows based on key fields.

        Per spec: ALL fields must be checked for comparability, even if earlier
        fields determine the sort order.

        Returns:
            -1 if row1 < row2
             0 if row1 == row2
             1 if row1 > row2
        """
        result = 0  # Track comparison result

        for field in self.keyFields:
            value1 = row1.get(field)
            value2 = row2.get(field)

            # Get type for this field
            typeStr = self.fieldTypes.get(field, "xs:string")

            # Handle nil values (nil < any non-nil)
            if self._isNil(value1) and self._isNil(value2):
                continue  # Both nil, check next field
            elif self._isNil(value1):
                if result == 0:
                    result = -1  # nil < non-nil
                continue
            elif self._isNil(value2):
                if result == 0:
                    result = 1  # non-nil > nil
                continue

            # Compare using type-specific comparison
            # MUST check ALL fields for comparability per spec
            # At this point, both values are non-nil (checked above)
            try:
                comparison = compareValues(str(value1), str(value2), typeStr, self.namespaces)
            except ValueError as e:
                # Incomparable values (e.g., mixed duration types or period types)
                errorCode = str(e)
                self.modelXbrl.error(
                    errorCode,
                    _(
                        "Cannot compare values for key '%(keyName)s' field '%(field)s': "
                        "%(value1)s and %(value2)s are incomparable"
                    ),
                    keyName=self.keyName,
                    field=field,
                    value1=value1,
                    value2=value2,
                )
                self.errors.append(errorCode)  # Track error for summary
                # Continue checking other fields for comparability
                continue

            # Only update result if we haven't determined order yet
            if result == 0 and comparison != 0:
                result = comparison
            # Continue to check remaining fields for comparability

        return result

    def _isNil(self, value: Any) -> bool:
        """Check if a value represents nil."""
        return Utils.isNilValue(value)


class SortValidatorManager:
    """
    Manages sort validators for multiple tables.
    Handles cross-table sorting for shared keys.
    """

    def __init__(self, modelXbrl: ModelXbrl, errors: list[str] | None = None) -> None:
        self.modelXbrl = modelXbrl
        self.validators: dict[str, SortValidator] = {}
        self.errors: list[str] = errors if errors is not None else []

    def createValidator(
        self,
        templateName: str,
        keyName: str | None,
        keyFields: list[str],
        fieldTypes: dict[str, str],
        namespaces: dict[str, str],
    ) -> SortValidator:
        """Get or create a sort validator for a template."""
        # Reuse existing validator for this template to maintain state across tables
        if templateName in self.validators:
            return self.validators[templateName]

        validator = SortValidator(
            self.modelXbrl,
            keyName,
            keyFields,
            fieldTypes,
            namespaces,  # Pass shared namespaces
            self.errors,  # Pass shared errors list
        )
        self.validators[templateName] = validator
        return validator

    def getValidator(self, templateName: str) -> SortValidator | None:
        """Get validator for a template."""
        return self.validators.get(templateName)
