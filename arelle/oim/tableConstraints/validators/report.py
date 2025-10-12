"""
See COPYRIGHT.md for copyright information.

Report Validator - validates xBRL-CSV report data against Table Constraints.
"""

from __future__ import annotations

import contextlib
import csv
import json
import os
from typing import Any

from arelle.FileSource import FileSource
from arelle.ModelXbrl import ModelXbrl
from arelle.oim.tableConstraints import Const, Types
from arelle.oim.tableConstraints.KeyIndexer import KeyIndexerManager
from arelle.oim.tableConstraints.SortValidator import SortValidatorManager
from arelle.oim.tableConstraints.ValueValidator import ConstraintViolation, ValueValidator
from arelle.typing import TypeGetText
from arelle.UrlUtil import isHttpUrl

_: TypeGetText


class ReportValidator:
    """
    Validates xBRL-CSV report data against Table Constraints.
    Processes CSV files without loading into memory.
    """

    def __init__(self, modelXbrl: ModelXbrl, metadataPath: str, fileSource: FileSource | None = None) -> None:
        self.modelXbrl = modelXbrl
        self.cntlr = modelXbrl.modelManager.cntlr
        self.metadataPath = metadataPath
        self.fileSource = fileSource  # For reading files from archives
        self.metadata: Types.Metadata | None = None
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.valueValidator = ValueValidator(modelXbrl)
        self.keyIndexerManager = KeyIndexerManager(modelXbrl, self.errors)
        self.sortValidatorManager = SortValidatorManager(modelXbrl, self.errors)

    def validate(self) -> bool:
        """
        Main validation entry point for report data.

        Returns:
            True if errors found.
        """
        try:
            # Step 1: Load metadata
            self.updateProgress("Loading metadata...")
            self.metadata = self.loadMetadata()

            # Step 2: Stream validate each table
            # Track table counts and row counts per template for validation
            templateTableCounts: dict[str, list[tuple[str, int]]] = {}  # templateName -> list of (tableName, rowCount)

            for tableName, tableConfig in self.metadata.tables.items():
                templateName = tableConfig.get("template", tableName)  # Default to table name if not specified
                template = self.metadata.tableTemplates.get(templateName, {})

                self.updateProgress(f"Validating table: {tableName}")
                rowCount = self.validateTableStream(tableName, tableConfig, template)

                # Track table and row count for this template
                if templateName not in templateTableCounts:
                    templateTableCounts[templateName] = []
                templateTableCounts[templateName].append((tableName, rowCount))

            # Step 3: Validate table/row counts per template
            self.updateProgress("Validating table/row counts...")
            for templateName, tableTemplateData in self.metadata.tableTemplates.items():
                tableConstraints = tableTemplateData.get(Const.TC_TABLE_CONSTRAINTS, {})
                if tableConstraints:
                    tablesInfo = templateTableCounts.get(templateName, [])
                    self.validateTableConstraints(templateName, tablesInfo, tableConstraints)

            # Step 4: Finalize key validation (cross-table)
            self.updateProgress("Finalizing key validation...")
            self.keyIndexerManager.finalizeAll()

            # Step 5: Report summary
            self.reportSummary()

            return len(self.errors) > 0

        except (OSError, RuntimeError, ValueError, KeyError, TypeError, csv.Error) as e:
            self.modelXbrl.error("tc:validationFailed", f"Table Constraints validation failed: {str(e)}")
            return True

    def loadMetadata(self) -> Types.Metadata:
        """Load and parse JSON metadata, handling extends."""
        try:
            # Use FileSource if available (for archive files), otherwise plain open
            if self.fileSource is not None:
                fileStream = self.fileSource.file(self.metadataPath, encoding="utf-8")[0]
                metadata: Types.MetadataDict = json.load(fileStream)
                fileStream.close()
            else:
                with open(self.metadataPath, encoding="utf-8") as f:
                    metadata = json.load(f)

            # Handle extends - merge extended files
            extends = metadata.get("documentInfo", {}).get("extends", [])
            if extends:
                basedir = os.path.dirname(self.metadataPath)
                for extendedFile in extends:
                    extendedPath = os.path.normpath(os.path.join(basedir, extendedFile))
                    # Check if file exists (for archives, FileSource handles this)
                    fileExists = self.fileSource is not None or os.path.exists(extendedPath)
                    if fileExists:
                        if self.fileSource is not None:
                            fileStream = self.fileSource.file(extendedPath, encoding="utf-8")[0]
                            extendedData = json.load(fileStream)
                            fileStream.close()
                        else:
                            with open(extendedPath, encoding="utf-8") as f:
                                extendedData = json.load(f)
                        # Merge extended data into metadata (simple shallow merge)
                        # Extended tableTemplates are merged
                        if "tableTemplates" in extendedData:
                            if "tableTemplates" not in metadata:
                                metadata["tableTemplates"] = {}
                            metadata["tableTemplates"].update(extendedData["tableTemplates"])
                        # Extended namespaces are merged
                        if "documentInfo" in extendedData and "namespaces" in extendedData["documentInfo"]:
                            if "documentInfo" not in metadata:
                                metadata["documentInfo"] = {}
                            if "namespaces" not in metadata["documentInfo"]:
                                metadata["documentInfo"]["namespaces"] = {}
                            metadata["documentInfo"]["namespaces"].update(extendedData["documentInfo"]["namespaces"])

            return Types.Metadata(metadata)
        except (OSError, json.JSONDecodeError, KeyError) as e:
            raise RuntimeError(f"Failed to load metadata: {str(e)}") from e

    def validateCsvColumnOrder(
        self,
        tableName: str,
        csvColumns: list[str],
        expectedOrder: list[str],
        columnDefs: dict[str, Any],
    ) -> None:
        """
        Validate that CSV columns appear in the order specified by columnOrder constraint.

        Args:
            tableName: Name of the table being validated
            csvColumns: List of column names from CSV header (in order they appear)
            expectedOrder: Expected column order from tc:columnOrder
            columnDefs: Column definitions from template
        """
        # Filter CSV columns to only include those defined in template
        # (columns not in template are ignored for order checking)
        templateColumns = [col for col in csvColumns if col in columnDefs]

        # Filter expected order to only include columns present in CSV
        # (columns in columnOrder but not in CSV are allowed to be absent)
        expectedColumnsInCsv = [col for col in expectedOrder if col in templateColumns]

        # Check if order matches
        if templateColumns != expectedColumnsInCsv:
            self.modelXbrl.error(
                Const.TCRE_INVALID_COLUMN_ORDER,
                f"Columns in CSV do not match columnOrder constraint for table '{tableName}'. "
                f"Expected: {expectedColumnsInCsv}, Found: {templateColumns}",
            )
            self.errors.append(Const.TCRE_INVALID_COLUMN_ORDER)

    def validateTableStream(
        self,
        tableName: str,
        tableConfig: Types.TableConfigDict,
        template: Types.TableTemplateDict,
    ) -> int:
        """
        Stream process one CSV table.

        Returns:
            Number of rows in the table (0 if CSV not found)
        """
        assert self.metadata is not None, "Metadata must be loaded before validating tables"

        # Resolve CSV URL
        csvUrl = tableConfig.get("url")
        if not csvUrl:
            return 0

        csvPath = self.resolveCsvPath(csvUrl)
        # Check if file exists
        if self.fileSource is not None:
            # For archives, FileSource will handle existence check when opening
            pass
        elif not os.path.exists(csvPath):
            self.modelXbrl.warning("tc:missingCsv", f"CSV file not found: {csvPath}")
            return 0

        # Get template name for key tracking
        templateName = tableConfig.get("template")
        if templateName is None or not isinstance(templateName, str):
            templateName = tableName  # Fallback to table name

        # Get column constraints
        columns = template.get("columns", {})
        parameters = template.get(Const.TC_PARAMETERS, {})
        tableParams = tableConfig.get("parameters", {})

        # Build field types map for key validation
        fieldTypes = {}
        for colName, colDef in columns.items():
            if Const.TC_CONSTRAINTS in colDef:
                typeStr = colDef[Const.TC_CONSTRAINTS].get(Const.CONSTRAINT_TYPE)
                if typeStr:
                    fieldTypes[colName] = typeStr

        # Add parameter types to field types map
        for paramName, paramDef in parameters.items():
            typeStr = paramDef.get("type")
            if typeStr:
                fieldTypes[paramName] = typeStr

        # Get or create key indexer for this template
        keys = template.get(Const.TC_KEYS, {})
        keyIndexer = self.keyIndexerManager.createIndexer(templateName, keys)
        keyIndexer.setFieldTypes(fieldTypes)

        # Get or create sort validator
        sortKeyName = None
        sortKeyFields = []
        # Check if sortKey is specified at keys level
        sortKeyRef = keys.get("sortKey")
        if sortKeyRef:
            # Find the unique key with this name
            uniqueKeysRaw = keys.get(Const.KEYS_UNIQUE, [])
            if isinstance(uniqueKeysRaw, dict):
                uniqueKeys = [uniqueKeysRaw]
            elif isinstance(uniqueKeysRaw, list):
                uniqueKeys = uniqueKeysRaw
            else:
                uniqueKeys = []
            for uniqueKey in uniqueKeys:
                if uniqueKey.get(Const.KEY_NAME) == sortKeyRef:
                    sortKeyName = sortKeyRef
                    sortKeyFields = uniqueKey.get(Const.KEY_FIELDS, [])
                    break

        sortValidator = self.sortValidatorManager.createValidator(
            templateName, sortKeyName, sortKeyFields, fieldTypes, self.metadata.namespaces
        )

        # Validate parameters first
        for paramName, paramConstraint in parameters.items():
            paramValue = tableParams.get(paramName)
            context = f"table:{tableName}, parameter:{paramName}"
            violations = self.valueValidator.validateValue(
                paramValue, paramConstraint, context, self.metadata.namespaces, isParameter=True
            )
            for violation in violations:
                self.logViolation(violation)

        def _openCsv() -> Any:
            # Use FileSource if available (for archive files), otherwise plain open
            if self.fileSource is not None:
                return self.fileSource.file(csvPath, encoding="utf-8")[0]
            return open(csvPath, encoding="utf-8")

        rowNum = 0
        # Stream CSV file
        with _openCsv() as csvFile:
            reader = csv.DictReader(csvFile)

            # Validate column order if specified
            columnOrder = template.get(Const.TC_COLUMN_ORDER)
            if columnOrder and reader.fieldnames is not None:
                self.validateCsvColumnOrder(tableName, list(reader.fieldnames), columnOrder, columns)

            for row in reader:
                rowNum += 1

                # Validate each column value
                for colName, colDef in columns.items():
                    if Const.TC_CONSTRAINTS in colDef:
                        cellValue = row.get(colName)
                        context = f"table:{tableName}, column:{colName}, row:{rowNum}"

                        violations = self.valueValidator.validateValue(
                            cellValue, colDef[Const.TC_CONSTRAINTS], context, self.metadata.namespaces
                        )

                        for violation in violations:
                            self.logViolation(violation)

                # Merge parameters into row for key and sort validation
                # Parameters are table-level values that can be used in keys
                rowWithParams = dict(row)
                rowWithParams.update(tableParams)

                # Add row to key indexer (errors already logged inside)
                with contextlib.suppress(KeyError, ValueError, TypeError):
                    keyIndexer.addRow(rowWithParams, rowNum, tableName)

                # Validate sort order (errors already logged inside)
                with contextlib.suppress(KeyError, ValueError, TypeError):
                    sortValidator.checkRow(rowWithParams, rowNum, tableName)

        # Validate table row counts (per-table validation)
        self.validateTableRowCount(tableName, template, rowNum)

        # Return row count for template-level validation
        return rowNum

    def validateTableConstraints(
        self, templateName: str, tablesInfo: list[tuple[str, int]], tableConstraints: dict[str, int]
    ) -> None:
        """
        Validate template-level table constraints (minTables, maxTables).

        Args:
            templateName: Name of the template
            tablesInfo: List of (tableName, rowCount) tuples for tables using this template
            tableConstraints: Dictionary of table constraints from tc:tableConstraints
        """
        tableCount = len(tablesInfo)

        # Validate minTables
        minTables = tableConstraints.get(Const.TC_MIN_TABLES)
        if minTables is not None and tableCount < minTables:
            self.modelXbrl.error(
                Const.TCRE_MIN_TABLES_VIOLATION,
                f"Template '{templateName}' requires at least {minTables} table(s), but only {tableCount} found",
            )
            self.errors.append(Const.TCRE_MIN_TABLES_VIOLATION)

        # Validate maxTables
        maxTables = tableConstraints.get(Const.TC_MAX_TABLES)
        if maxTables is not None and tableCount > maxTables:
            self.modelXbrl.error(
                Const.TCRE_MAX_TABLES_VIOLATION,
                f"Template '{templateName}' allows at most {maxTables} table(s), but {tableCount} found",
            )
            self.errors.append(Const.TCRE_MAX_TABLES_VIOLATION)

    def validateTableRowCount(self, tableName: str, template: Types.TableTemplateDict, rowCount: int) -> None:
        """Validate table row count constraints."""
        tableConstraints = template.get(Const.TC_TABLE_CONSTRAINTS, {})

        minRows = tableConstraints.get(Const.TC_MIN_TABLE_ROWS)
        if minRows and rowCount < minRows:
            self.modelXbrl.error(
                Const.TCRE_MIN_TABLE_ROWS_VIOLATION, f"Table '{tableName}' has {rowCount} rows, minimum is {minRows}"
            )
            self.errors.append(Const.TCRE_MIN_TABLE_ROWS_VIOLATION)

        maxRows = tableConstraints.get(Const.TC_MAX_TABLE_ROWS)
        if maxRows and rowCount > maxRows:
            self.modelXbrl.error(
                Const.TCRE_MAX_TABLE_ROWS_VIOLATION, f"Table '{tableName}' has {rowCount} rows, maximum is {maxRows}"
            )
            self.errors.append(Const.TCRE_MAX_TABLE_ROWS_VIOLATION)

    def resolveCsvPath(self, csvUrl: str) -> str:
        """Resolve CSV URL to file path."""
        if isHttpUrl(csvUrl):
            # Would need to fetch from web - for now assume local
            return csvUrl

        # Resolve relative to metadata file
        metadataDir = os.path.dirname(self.metadataPath)
        return os.path.normpath(os.path.join(metadataDir, csvUrl))

    def logViolation(self, violation: ConstraintViolation) -> None:
        """Log a constraint violation."""
        severity = "error"  # Could be extended to support warnings

        if severity == "error":
            self.modelXbrl.error(violation.errorCode, violation.message)
            self.errors.append(violation.errorCode)
        else:
            self.modelXbrl.warning(violation.errorCode, violation.message)
            self.warnings.append(violation.errorCode)

    def updateProgress(self, message: str) -> None:
        """Update progress in GUI or CLI."""
        if hasattr(self.cntlr, "showStatus"):
            self.cntlr.showStatus(message)

    def reportSummary(self) -> None:
        """Report validation summary."""
        msg = f"Table Constraints validation complete: {len(self.errors)} errors, {len(self.warnings)} warnings"
        if hasattr(self.cntlr, "addToLog"):
            self.cntlr.addToLog(msg)
        self.updateProgress(msg)
