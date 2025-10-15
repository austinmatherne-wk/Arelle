"""
See COPYRIGHT.md for copyright information.

Report Validator - validates xBRL-CSV report data against Table Constraints.
"""

from __future__ import annotations

import contextlib
import csv
import os
from typing import Any

from arelle.FileSource import FileSource
from arelle.ModelXbrl import ModelXbrl
from arelle.oim.tableConstraints import Const, Types
from arelle.oim.tableConstraints.KeyIndexer import KeyIndexerManager
from arelle.oim.tableConstraints.Metadata import Metadata
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

    def __init__(
        self,
        modelXbrl: ModelXbrl,
        metadata: Metadata,
        fileSource: FileSource | None = None
    ) -> None:
        self.modelXbrl = modelXbrl
        self.cntlr = modelXbrl.modelManager.cntlr
        self.metadata = metadata
        self.fileSource = fileSource  # For reading files from archives
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.valueValidator = ValueValidator(modelXbrl)
        self.keyIndexerManager = KeyIndexerManager(modelXbrl, self.errors)
        self.sortValidatorManager = SortValidatorManager(modelXbrl, self.errors)

    def validate(self) -> bool:
        try:
            templateTableCounts: dict[str, list[tuple[str, int]]] = {}

            for tableName, tableConfig in self.metadata.tables.items():
                templateName = tableConfig.get("template", tableName)
                template = self.metadata.tableTemplates.get(templateName, {})

                self.updateProgress(f"Validating table: {tableName}")
                rowCount = self.validateTableStream(tableName, tableConfig, template)

                if templateName not in templateTableCounts:
                    templateTableCounts[templateName] = []
                templateTableCounts[templateName].append((tableName, rowCount))

            self.updateProgress("Validating table/row counts...")
            for templateName, tableTemplateData in self.metadata.tableTemplates.items():
                tableConstraints = tableTemplateData.get(Const.TC_TABLE_CONSTRAINTS, {})
                if tableConstraints:
                    tablesInfo = templateTableCounts.get(templateName, [])
                    self.validateTableConstraints(templateName, tablesInfo, tableConstraints)

            self.updateProgress("Finalizing key validation...")
            self.keyIndexerManager.finalizeAll()

            self.reportSummary()

            return len(self.errors) > 0

        except (OSError, RuntimeError, ValueError, KeyError, TypeError, csv.Error) as e:
            self.modelXbrl.error("tc:validationFailed", f"Table Constraints validation failed: {str(e)}")
            return True

    def validateCsvColumnOrder(
        self,
        tableName: str,
        csvColumns: list[str],
        expectedOrder: list[str],
        columnDefs: dict[str, Any],
    ) -> None:
        """
        Validate that CSV columns appear in the order specified by columnOrder constraint.
        """
        templateColumns = [col for col in csvColumns if col in columnDefs]

        expectedColumnsInCsv = [col for col in expectedOrder if col in templateColumns]

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
        """
        assert self.metadata is not None, "Metadata must be loaded before validating tables"

        csvUrl = tableConfig.get("url")
        if not csvUrl:
            return 0

        csvPath = self.resolveCsvPath(csvUrl)
        if self.fileSource is not None:
            pass
        elif not os.path.exists(csvPath):
            self.modelXbrl.warning("tc:missingCsv", f"CSV file not found: {csvPath}")
            return 0

        templateName = tableConfig.get("template")
        if templateName is None or not isinstance(templateName, str):
            templateName = tableName  # Fallback to table name

        columns = template.get("columns", {})
        parameters = template.get(Const.TC_PARAMETERS, {})
        tableParams = tableConfig.get("parameters", {})

        fieldTypes = {}
        for colName, colDef in columns.items():
            if Const.TC_CONSTRAINTS in colDef:
                typeStr = colDef[Const.TC_CONSTRAINTS].get(Const.CONSTRAINT_TYPE)
                if typeStr:
                    fieldTypes[colName] = typeStr

        for paramName, paramDef in parameters.items():
            typeStr = paramDef.get("type")
            if typeStr:
                fieldTypes[paramName] = typeStr

        keys = template.get(Const.TC_KEYS, {})
        keyIndexer = self.keyIndexerManager.createIndexer(templateName, keys)
        keyIndexer.setFieldTypes(fieldTypes)

        sortKeyName = None
        sortKeyFields = []
        sortKeyRef = keys.get("sortKey")
        if sortKeyRef:
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

        for paramName, paramConstraint in parameters.items():
            paramValue = tableParams.get(paramName)
            context = f"table:{tableName}, parameter:{paramName}"
            violations = self.valueValidator.validateValue(
                paramValue, paramConstraint, context, self.metadata.namespaces, isParameter=True
            )
            for violation in violations:
                self.logViolation(violation)

        def _openCsv() -> Any:
            if self.fileSource is not None:
                return self.fileSource.file(csvPath, encoding="utf-8")[0]
            return open(csvPath, encoding="utf-8")

        rowNum = 0
        with _openCsv() as csvFile:
            reader = csv.DictReader(csvFile)

            columnOrder = template.get(Const.TC_COLUMN_ORDER)
            if columnOrder and reader.fieldnames is not None:
                self.validateCsvColumnOrder(tableName, list(reader.fieldnames), columnOrder, columns)

            for row in reader:
                rowNum += 1

                for colName, colDef in columns.items():
                    if Const.TC_CONSTRAINTS in colDef:
                        cellValue = row.get(colName)
                        context = f"table:{tableName}, column:{colName}, row:{rowNum}"

                        violations = self.valueValidator.validateValue(
                            cellValue, colDef[Const.TC_CONSTRAINTS], context, self.metadata.namespaces
                        )

                        for violation in violations:
                            self.logViolation(violation)

                rowWithParams = dict(row)
                rowWithParams.update(tableParams)

                with contextlib.suppress(KeyError, ValueError, TypeError):
                    keyIndexer.addRow(rowWithParams, rowNum, tableName)

                with contextlib.suppress(KeyError, ValueError, TypeError):
                    sortValidator.checkRow(rowWithParams, rowNum, tableName)

        self.validateTableRowCount(tableName, template, rowNum)

        return rowNum

    def validateTableConstraints(
        self, templateName: str, tablesInfo: list[tuple[str, int]], tableConstraints: dict[str, int]
    ) -> None:
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
        if self.metadata.path is None:
            # If no metadata path provided, return as-is
            return csvUrl
        metadataDir = os.path.dirname(self.metadata.path)
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
