"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

import regex

from arelle.ModelXbrl import ModelXbrl
from arelle.oim.tableConstraints import Const, Types, Utils
from arelle.oim.tableConstraints.XmlSchemaHelper import isValidForFacet, isXmlSchemaBuiltInType, validateXmlSchemaValue
from arelle.typing import TypeGetText

_: TypeGetText


class MetadataValidator:
    """
    Validates Table Constraints metadata structure (tcme errors).
    """

    def __init__(self, modelXbrl: ModelXbrl, metadata: Types.Metadata) -> None:
        self.modelXbrl = modelXbrl
        self.metadata = metadata
        self.errors: list[tuple[str, str]] = []

    def validate(self) -> bool:
        """
        Validate all TC metadata.
        Returns True if errors found.
        """
        # Validate namespace binding
        self.validateNamespaces()

        # Validate table templates
        tableTemplates = self.metadata.tableTemplates

        # Validate referenced key names exist FIRST (before detailed template validation)
        # This catches missing key references early
        self.validateReferencedKeyNames(tableTemplates)

        # Continue with detailed template validation
        for templateName, template in tableTemplates.items():
            self.validateTemplate(templateName, template)

        # Validate cross-template consistency
        self.validateCrossTemplateConsistency(tableTemplates)

        return len(self.errors) > 0

    def validateNamespaces(self) -> None:
        """Validate tc namespace binding."""
        namespaces = self.metadata.namespaces
        if Const.TC_PREFIX in namespaces:
            # Check if namespace matches any known TC namespace pattern
            tcNs = namespaces[Const.TC_PREFIX]
            # Accept exact matches or date-based patterns like CR-YYYY-MM-DD, PWD-YYYY-MM-DD, etc.
            isValid = (
                tcNs in Const.TC_NAMESPACE_PATTERNS
                or regex.match(r"https://xbrl\.org/(?:CR|PWD|REC|PR)-\d{4}-\d{2}-\d{2}/tc$", tcNs)
                or regex.match(r"https://xbrl\.org/\d{4}/tc$", tcNs)
            )
            if not isValid:
                self.error(
                    Const.TCME_INVALID_NAMESPACE_PREFIX,
                    f"Namespace prefix '{Const.TC_PREFIX}' bound to '{tcNs}', must be a valid TC namespace",
                )

    def validateTemplate(self, templateName: str, template: Types.TableTemplateDict) -> None:
        """Validate a single table template."""
        # Validate columns with constraints
        columns = template.get("columns", {})
        for colName, column in columns.items():
            if Const.TC_CONSTRAINTS in column:
                # Check if this is a comment column
                if column.get("comment") is True:
                    self.error(
                        Const.TCME_INVALID_COMMENT_COLUMN_CONSTRAINT,
                        f"Column '{colName}' is a comment column and cannot have tc:constraints",
                    )
                    continue
                self.validateConstraints(f"column:{colName}", column[Const.TC_CONSTRAINTS], isParameter=False)

        # Validate parameters
        parameters = template.get(Const.TC_PARAMETERS, {})
        for paramName, paramConstraints in parameters.items():
            self.validateConstraints(f"parameter:{paramName}", paramConstraints, isParameter=True)

        # Validate keys
        keys = template.get(Const.TC_KEYS)
        if keys is not None:
            self.validateKeys(templateName, template, keys)

        # Validate table constraints
        tableConstraints = template.get(Const.TC_TABLE_CONSTRAINTS)
        if tableConstraints:
            self.validateTableConstraints(templateName, tableConstraints)

        # Validate column order
        columnOrder = template.get(Const.TC_COLUMN_ORDER)
        if columnOrder:
            self.validateColumnOrder(templateName, template, columnOrder)

    def validateConstraints(self, context: str, constraints: Types.ConstraintDict, isParameter: bool) -> None:
        """Validate a constraint object."""
        # Get namespaces once for this method
        namespaces = self.metadata.namespaces

        # Check for unknown properties
        for prop in constraints:
            if prop not in Const.VALID_CONSTRAINT_PROPERTIES:
                self.error(
                    Const.TCME_INVALID_JSON_STRUCTURE, f"Unknown property '{prop}' in constraint object at {context}"
                )
                return

        # Type is required
        typeStr = constraints.get(Const.CONSTRAINT_TYPE)
        if not typeStr:
            self.error(Const.TCME_INVALID_JSON_STRUCTURE, f"Missing required 'type' property in {context}")
            return

        # Validate type constraint
        if not self.isValidType(typeStr):
            self.error(Const.TCME_INVALID_TYPE_CONSTRAINT, f"Invalid type '{typeStr}' in {context}")

        # Validate allowedValues
        allowedValues = constraints.get(Const.CONSTRAINT_ALLOWED_VALUES)
        if allowedValues:
            if not isinstance(allowedValues, list) or len(allowedValues) == 0:
                self.error(Const.TCME_INVALID_JSON_STRUCTURE, f"allowedValues must be non-empty array in {context}")
            else:
                # Convert all values to strings for validation
                # (CSV values are always strings, so we validate the string representation)
                allowedValuesStr = [str(v) for v in allowedValues]

                # Check uniqueness of string representations
                if len(allowedValuesStr) != len(set(allowedValuesStr)):
                    self.error(Const.TCME_INVALID_JSON_STRUCTURE, f"allowedValues must be unique in {context}")
                else:
                    # Each value must conform to the type
                    from ..XmlSchemaHelper import isCoreDimension, validateXmlSchemaValue

                    for val in allowedValuesStr:
                        # Check type validity
                        isValid, errorMsg = validateXmlSchemaValue(val, typeStr, namespaces)
                        if not isValid and not isCoreDimension(typeStr):
                            # Core dimensions don't have specific value validation in metadata
                            self.error(
                                Const.TCME_ILLEGAL_ALLOWED_VALUE,
                                f"allowedValue '{val}' does not conform to type '{typeStr}' in {context}",
                            )
                            break  # Report first violation only

        # Validate allowedPatterns
        allowedPatterns = constraints.get(Const.CONSTRAINT_ALLOWED_PATTERNS)
        if allowedPatterns:
            if not isinstance(allowedPatterns, list) or len(allowedPatterns) == 0:
                self.error(Const.TCME_INVALID_JSON_STRUCTURE, f"allowedPatterns must be non-empty array in {context}")
            elif len(allowedPatterns) != len(set(allowedPatterns)):
                self.error(Const.TCME_INVALID_JSON_STRUCTURE, f"allowedPatterns must be unique in {context}")

        # Validate timezone constraint
        timeZone = constraints.get(Const.CONSTRAINT_TIMEZONE)
        if timeZone is not None and typeStr != "period" and typeStr not in Const.OPTIONALLY_TIMEZONED_TYPES:
            self.error(Const.TCME_UNKNOWN_TIMEZONE, f"timeZone not applicable to type '{typeStr}' in {context}")

        # Validate periodType
        periodType = constraints.get(Const.CONSTRAINT_PERIOD_TYPE)
        if periodType:
            if typeStr != "period":
                self.error(Const.TCME_ILLEGAL_PERIOD_TYPE, f"periodType requires type 'period' in {context}")
            elif periodType not in Const.PERIOD_TYPES:
                self.error(Const.TCME_UNKNOWN_PERIOD_TYPE, f"Unknown periodType '{periodType}' in {context}")

        # Validate durationType
        durationType = constraints.get(Const.CONSTRAINT_DURATION_TYPE)
        if durationType:
            if typeStr != "xs:duration":
                self.error(Const.TCME_ILLEGAL_DURATION_TYPE, f"durationType requires type 'xs:duration' in {context}")
            elif durationType not in Const.DURATION_TYPES:
                self.error(Const.TCME_UNKNOWN_DURATION_TYPE, f"Unknown durationType '{durationType}' in {context}")

        # Validate facets
        self.validateFacets(context, constraints, typeStr)

    def validateFacets(self, context: str, constraints: Types.ConstraintDict, typeStr: str) -> None:
        """Validate XML Schema facets."""
        # Get namespaces once for this method
        namespaces = self.metadata.namespaces

        facets = [
            (Const.CONSTRAINT_LENGTH, "invalidLengthType"),
            (Const.CONSTRAINT_MIN_LENGTH, "invalidLengthType"),
            (Const.CONSTRAINT_MAX_LENGTH, "invalidLengthType"),
            (Const.CONSTRAINT_MIN_INCLUSIVE, "invalidBoundaryType"),
            (Const.CONSTRAINT_MAX_INCLUSIVE, "invalidBoundaryType"),
            (Const.CONSTRAINT_MIN_EXCLUSIVE, "invalidBoundaryType"),
            (Const.CONSTRAINT_MAX_EXCLUSIVE, "invalidBoundaryType"),
            (Const.CONSTRAINT_TOTAL_DIGITS, "invalidDigitsType"),
            (Const.CONSTRAINT_FRACTION_DIGITS, "invalidDigitsType"),
        ]

        for facetName, errorSuffix in facets:
            if facetName in constraints:
                value = constraints[facetName]

                # Validate length facets are non-negative integers
                isLengthFacet = facetName in (
                    Const.CONSTRAINT_LENGTH,
                    Const.CONSTRAINT_MIN_LENGTH,
                    Const.CONSTRAINT_MAX_LENGTH,
                )
                if isLengthFacet and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
                    self.error(
                        Const.TCME_INVALID_JSON_STRUCTURE,
                        f"'{facetName}' must be a non-negative integer in {context}",
                    )
                    continue

                # Validate digits facets are positive integers
                isDigitFacet = facetName in (Const.CONSTRAINT_TOTAL_DIGITS, Const.CONSTRAINT_FRACTION_DIGITS)
                if isDigitFacet and (isinstance(value, bool) or not isinstance(value, int) or value < 1):
                    self.error(
                        Const.TCME_INVALID_JSON_STRUCTURE, f"'{facetName}' must be a positive integer in {context}"
                    )
                    continue

                # Validate boundary facet values are valid for the type
                if facetName in [
                    Const.CONSTRAINT_MIN_INCLUSIVE,
                    Const.CONSTRAINT_MAX_INCLUSIVE,
                    Const.CONSTRAINT_MIN_EXCLUSIVE,
                    Const.CONSTRAINT_MAX_EXCLUSIVE,
                ]:
                    if not isinstance(value, str):
                        self.error(Const.TCRE_INVALID_BOUNDARY_VALUE, f"'{facetName}' must be a string in {context}")
                        continue
                    # For 'decimals' type, validate as xs:integer (per spec section on decimals)
                    validationType = "xs:integer" if typeStr == Const.TYPE_DECIMALS else typeStr
                    # Only validate if it's an XML Schema type
                    if validationType.startswith("xs:"):
                        isValid, errorMsg = validateXmlSchemaValue(value, validationType, namespaces)
                        if not isValid:
                            self.error(
                                Const.TCRE_INVALID_BOUNDARY_VALUE,
                                f"'{facetName}' value '{value}' is not valid for type '{typeStr}' in {context}: {errorMsg}",
                            )
                            continue

                # Then check applicability to type
                if not isValidForFacet(facetName, typeStr, namespaces):
                    self.error(
                        f"tcme:{errorSuffix}", f"Facet '{facetName}' not applicable to type '{typeStr}' in {context}"
                    )

    def validateKeys(self, templateName: str, template: Types.TableTemplateDict, keys: Types.KeysDict) -> None:
        """Validate keys object."""
        # Check for unknown properties in keys object
        validKeysProperties = {Const.KEYS_UNIQUE, Const.KEYS_REFERENCE, "sortKey"}
        for prop in keys:
            if prop not in validKeysProperties:
                self.error(
                    Const.TCME_INVALID_JSON_STRUCTURE,
                    f"Unknown property '{prop}' in keys object of template '{templateName}'",
                )
                return

        # Handle unique keys - can be a single object or array
        uniqueKeysRaw = keys.get(Const.KEYS_UNIQUE, [])
        # Check if explicitly provided as empty array (structural error)
        if Const.KEYS_UNIQUE in keys and isinstance(uniqueKeysRaw, list) and len(uniqueKeysRaw) == 0:
            self.error(
                Const.TCME_INVALID_JSON_STRUCTURE, f"'unique' array must not be empty in template '{templateName}'"
            )
            return

        uniqueKeys = Utils.normalizeKeyArray(uniqueKeysRaw)

        # Handle reference keys - can be a single object or array
        referenceKeysRaw = keys.get(Const.KEYS_REFERENCE, [])
        # Check if explicitly provided as empty array (structural error)
        if Const.KEYS_REFERENCE in keys and isinstance(referenceKeysRaw, list) and len(referenceKeysRaw) == 0:
            self.error(
                Const.TCME_INVALID_JSON_STRUCTURE, f"'reference' array must not be empty in template '{templateName}'"
            )
            return

        referenceKeys = Utils.normalizeKeyArray(referenceKeysRaw)

        if not uniqueKeys and not referenceKeys:
            self.error(
                Const.TCME_MISSING_KEY_PROPERTY,
                f"Keys must have at least 'unique' or 'reference' in template '{templateName}'",
            )

        # Get available fields (constrained columns and parameters)
        # Per spec: "Each entry in the fields list MUST correspond to a constrained column or a defined parameter"
        columns = template.get("columns", {})
        parameters = template.get(Const.TC_PARAMETERS, {})
        constrainedColumns = {colName for colName, col in columns.items() if Const.TC_CONSTRAINTS in col}
        availableFields = constrainedColumns | set(parameters.keys())

        # Track key names for duplicates
        keyNames = set()

        # Validate unique keys
        validUniqueKeyProperties = {Const.KEY_NAME, Const.KEY_FIELDS, Const.KEY_SEVERITY, "sortedRows"}
        for uniqueKey in uniqueKeys:
            # Check for unknown properties in unique key
            for prop in uniqueKey:
                if prop not in validUniqueKeyProperties:
                    self.error(Const.TCME_INVALID_JSON_STRUCTURE, f"Unknown property '{prop}' in unique key")
                    return

            name = uniqueKey.get(Const.KEY_NAME)
            if name in keyNames:
                self.error(Const.TCME_DUPLICATE_KEY_NAME, f"Duplicate key name '{name}' in template '{templateName}'")
            keyNames.add(name)

            fields = uniqueKey.get(Const.KEY_FIELDS, [])
            if not fields:
                self.error(Const.TCME_INVALID_JSON_STRUCTURE, f"Unique key '{name}' must have non-empty fields")
            elif len(fields) != len(set(fields)):
                self.error(Const.TCME_INVALID_JSON_STRUCTURE, f"Unique key '{name}' fields must be unique")
            else:
                # Validate fields exist
                for field in fields:
                    if field not in availableFields:
                        self.error(
                            Const.TCME_ILLEGAL_UNIQUE_KEY_FIELD,
                            f"Unique key '{name}' field '{field}' not found in columns or parameters",
                        )

            severity = uniqueKey.get(Const.KEY_SEVERITY, "error")
            if severity not in Const.KEY_SEVERITY_VALUES:
                self.error(Const.TCME_INVALID_KEY_SEVERITY, f"Invalid severity '{severity}' for key '{name}'")

        # Validate reference keys
        validReferenceKeyProperties = {
            Const.KEY_NAME,
            Const.KEY_FIELDS,
            Const.KEY_SEVERITY,
            Const.KEY_REFERENCED_KEY_NAME,
            Const.KEY_NEGATE,
            Const.KEY_SKIP_NILS,
        }
        for refKey in referenceKeys:
            # Check for unknown properties in reference key
            for prop in refKey:
                if prop not in validReferenceKeyProperties:
                    self.error(Const.TCME_INVALID_JSON_STRUCTURE, f"Unknown property '{prop}' in reference key")
                    return

            name = refKey.get(Const.KEY_NAME)
            if name in keyNames:
                self.error(Const.TCME_DUPLICATE_KEY_NAME, f"Duplicate key name '{name}' in template '{templateName}'")
            keyNames.add(name)

            fields = refKey.get(Const.KEY_FIELDS, [])
            if not fields:
                self.error(Const.TCME_INVALID_JSON_STRUCTURE, f"Reference key '{name}' must have non-empty fields")
            elif len(fields) != len(set(fields)):
                self.error(Const.TCME_INVALID_JSON_STRUCTURE, f"Reference key '{name}' fields must be unique")
            else:
                # Validate fields exist
                for field in fields:
                    if field not in availableFields:
                        self.error(
                            Const.TCME_ILLEGAL_REFERENCE_KEY_FIELD,
                            f"Reference key '{name}' field '{field}' not found in columns or parameters",
                        )

            severity = refKey.get(Const.KEY_SEVERITY, "error")
            if severity not in Const.KEY_SEVERITY_VALUES:
                self.error(Const.TCME_INVALID_KEY_SEVERITY, f"Invalid severity '{severity}' for key '{name}'")

    def validateTableConstraints(self, templateName: str, tableConstraints: Types.TableConstraintsDict) -> None:
        """Validate table constraints object."""
        # Check for unknown properties
        validProperties = {Const.TC_MIN_TABLES, Const.TC_MAX_TABLES, Const.TC_MIN_TABLE_ROWS, Const.TC_MAX_TABLE_ROWS}
        for prop in tableConstraints:
            if prop not in validProperties:
                self.error(Const.TCME_INVALID_JSON_STRUCTURE, f"Unknown property '{prop}' in tableConstraints")
                return

        for prop in [Const.TC_MIN_TABLES, Const.TC_MAX_TABLES, Const.TC_MIN_TABLE_ROWS, Const.TC_MAX_TABLE_ROWS]:
            if prop in tableConstraints:
                value = tableConstraints[prop]
                # Check for boolean first (bool is subclass of int in Python)
                if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 1 or value != int(value):
                    self.error(Const.TCME_INVALID_JSON_STRUCTURE, f"Property '{prop}' must be positive integer")

    def validateColumnOrder(self, templateName: str, template: Types.TableTemplateDict, columnOrder: list[str]) -> None:
        """Validate column order."""
        columns = set(template.get("columns", {}).keys())
        orderSet = set(columnOrder)

        if columns != orderSet:
            self.error(
                Const.TCME_INCONSISTENT_COLUMN_ORDER_DEFINITION,
                f"Column order must include all columns exactly once in template '{templateName}'",
            )
        elif len(columnOrder) != len(orderSet):
            self.error(
                Const.TCME_INCONSISTENT_COLUMN_ORDER_DEFINITION,
                f"Column order contains duplicates in template '{templateName}'",
            )

    def validateCrossTemplateConsistency(self, tableTemplates: dict[str, Types.TableTemplateDict]) -> None:
        """Validate shared keys across templates."""
        # Group keys by name
        keysByName: dict[str, list[tuple[str, Types.UniqueKeyDict]]] = {}

        for templateName, template in tableTemplates.items():
            keys = template.get(Const.TC_KEYS, {})
            uniqueKeys = Utils.normalizeKeyArray(keys.get(Const.KEYS_UNIQUE))
            for uniqueKey in uniqueKeys:
                keyName = uniqueKey.get(Const.KEY_NAME)
                if keyName:
                    if keyName not in keysByName:
                        keysByName[keyName] = []
                    keysByName[keyName].append((templateName, uniqueKey))

        # Check shared keys for consistency
        for keyName, instances in keysByName.items():
            if len(instances) > 1:
                # This is a shared key - validate consistency
                first = instances[0][1]
                for _templateName, key in instances[1:]:
                    # Check severity
                    if key.get(Const.KEY_SEVERITY, "error") != first.get(Const.KEY_SEVERITY, "error"):
                        self.error(
                            Const.TCME_INCONSISTENT_SHARED_KEY_SEVERITY,
                            f"Inconsistent severity for shared key '{keyName}'",
                        )

                    # Check field count
                    if len(key.get(Const.KEY_FIELDS, [])) != len(first.get(Const.KEY_FIELDS, [])):
                        self.error(
                            Const.TCME_INCONSISTENT_SHARED_KEY_FIELDS,
                            f"Inconsistent field count for shared key '{keyName}'",
                        )

    def validateReferencedKeyNames(self, tableTemplates: dict[str, Types.TableTemplateDict]) -> None:
        """Validate that all referencedKeyName values exist as unique keys."""
        # Collect all unique keys with their field counts
        uniqueKeyInfo = {}  # keyName -> {fieldCount, ...}
        for template in tableTemplates.values():
            keys = template.get(Const.TC_KEYS)
            if not keys:
                continue

            uniqueKeys = Utils.normalizeKeyArray(keys.get(Const.KEYS_UNIQUE))

            for uniqueKey in uniqueKeys:
                keyName = uniqueKey.get(Const.KEY_NAME)
                if keyName:
                    fieldCount = len(uniqueKey.get(Const.KEY_FIELDS, []))
                    uniqueKeyInfo[keyName] = fieldCount

        # Now check all reference keys
        for template in tableTemplates.values():
            keys = template.get(Const.TC_KEYS)
            if not keys:
                continue

            referenceKeys = Utils.normalizeKeyArray(keys.get(Const.KEYS_REFERENCE))

            for refKey in referenceKeys:
                referencedKeyName = refKey.get(Const.KEY_REFERENCED_KEY_NAME)
                refKeyName = refKey.get(Const.KEY_NAME)
                if referencedKeyName:
                    if referencedKeyName not in uniqueKeyInfo:
                        self.error(
                            Const.TCME_INVALID_KEY_IDENTIFIER,
                            f"Referenced key name '{referencedKeyName}' not found in any template",
                        )
                    else:
                        # Validate field count matches
                        refFieldCount = len(refKey.get(Const.KEY_FIELDS, []))
                        uniqueFieldCount = uniqueKeyInfo[referencedKeyName]
                        if refFieldCount != uniqueFieldCount:
                            self.error(
                                Const.TCME_INVALID_REFERENCE_KEY,
                                f"Reference key '{refKeyName}' has {refFieldCount} fields but referenced key '{referencedKeyName}' has {uniqueFieldCount} fields",
                            )

    def isValidType(self, typeStr: str) -> bool:
        """Check if a type constraint is valid."""
        namespaces = self.metadata.namespaces
        if isXmlSchemaBuiltInType(typeStr, namespaces):
            return True
        if typeStr in Const.XBRL_CSV_CORE_DIMENSIONS:
            return True
        return typeStr == Const.TYPE_DECIMALS

    def error(self, code: str, message: str) -> None:
        """Log a metadata error."""
        self.errors.append((code, message))
        self.modelXbrl.error(code, message)
