"""
See COPYRIGHT.md for copyright information.

Linter Validator - validates Table Constraints metadata consistency with taxonomy.

This validator performs non-normative linting checks that require a loaded taxonomy.
Unlike metadata and report validation, linting checks are recommendations, not requirements.

Note: The TC spec does not define standardized error codes for linting.
This implementation uses tcl:* warning codes (Table Constraints Linter).
"""

from __future__ import annotations

from typing import cast

from arelle.ModelDtsObject import ModelConcept
from arelle.ModelValue import QName
from arelle.ModelXbrl import ModelXbrl
from arelle.typing import TypeGetText

from .. import Const, Types
from ..XmlSchemaHelper import validateXmlSchemaValue

_: TypeGetText


class LinterValidator:
    """
    Validates Table Constraints metadata for consistency with XBRL taxonomy.

    This is a non-normative linting validator that checks:
    1. Type consistency between constraints and taxonomy types
    2. AllowedValues validity against taxonomy types

    Note: These are recommendations, not requirements per the TC spec.
    The TC spec does not define standardized error codes for linting.
    Uses tcl:* warning codes (Table Constraints Linter):
    - tcl:inconsistentType
    - tcl:invalidAllowedValue
    """

    def __init__(self, modelXbrl: ModelXbrl, metadata: Types.Metadata) -> None:
        self.modelXbrl = modelXbrl
        self.metadata = metadata
        self.warnings: list[tuple[str, str]] = []

    def validate(self) -> bool:
        for templateName, template in self.metadata.tableTemplates.items():
            self.validateTemplate(templateName, template)

        return len(self.warnings) > 0

    def validateTemplate(self, templateName: str, template: Types.TableTemplateDict) -> None:
        columns = template.get("columns", {})

        for colName, column in columns.items():
            if Const.TC_CONSTRAINTS not in column:
                continue

            constraints = column[Const.TC_CONSTRAINTS]

            taxonomyType = self.getTaxonomyTypeForColumn(colName, column)
            if taxonomyType is None:
                continue

            self.validateTypeConsistency(
                f"template:{templateName}, column:{colName}",
                constraints,
                taxonomyType
            )

            self.validateAllowedValues(
                f"template:{templateName}, column:{colName}",
                constraints,
                taxonomyType
            )

    def getTaxonomyTypeForColumn(
        self,
        colName: str,
        column: Types.ColumnDict
    ) -> ModelConcept | None:
        """
        Try to determine the taxonomy type for a column.

        Returns the concept type, or None if it cannot be determined.
        This handles the simple case of a fixed concept in dimensions.
        """
        dimensions = column.get("dimensions")
        if not dimensions or not isinstance(dimensions, dict):
            return None

        conceptValue = dimensions.get("concept")
        if conceptValue and isinstance(conceptValue, str):
            # Parse as QName
            conceptQName = self.parseQName(conceptValue)
            if conceptQName and conceptQName in self.modelXbrl.qnameConcepts:
                return self.modelXbrl.qnameConcepts[conceptQName]

        for dimName in dimensions:
            if dimName == "concept":
                continue

            dimQName = self.parseQName(dimName)
            if dimQName and dimQName in self.modelXbrl.qnameConcepts:
                dimConcept = self.modelXbrl.qnameConcepts[dimQName]
                if hasattr(dimConcept, 'isExplicitDimension') and dimConcept.isExplicitDimension:
                    continue
                if hasattr(dimConcept, 'typedDomainElement'):
                    typedDomain = dimConcept.typedDomainElement
                    if typedDomain is not None and isinstance(typedDomain, ModelConcept):
                        return cast(ModelConcept, typedDomain)

        return None

    def parseQName(self, value: str) -> QName | None:
        if ":" not in value:
            return None

        prefix, localName = value.split(":", 1)
        namespace = self.metadata.namespaces.get(prefix)
        if not namespace:
            return None

        return QName(prefix, namespace, localName)

    def validateTypeConsistency(
        self,
        context: str,
        constraints: Types.ConstraintDict,
        taxonomyType: ModelConcept
    ) -> None:
        constraintType = constraints.get(Const.CONSTRAINT_TYPE)
        if not constraintType:
            return

        if taxonomyType.type is None:
            return

        taxonomyTypeQName = taxonomyType.type.qname

        constraintTypeQName = self.parseQName(constraintType) if ":" in constraintType else None

        if constraintTypeQName and constraintTypeQName != taxonomyTypeQName:
            isDerived = self.isDerivedFrom(constraintTypeQName, taxonomyTypeQName)
            if not isDerived:
                self.warning(
                    "tcl:inconsistentType",
                    f"Constraint type '{constraintType}' may not be consistent with "
                    f"taxonomy type '{taxonomyTypeQName}' at {context}"
                )

    def isDerivedFrom(self, derivedQName: QName, baseQName: QName) -> bool:
        if derivedQName not in self.modelXbrl.qnameConcepts:
            return False

        derivedConcept = self.modelXbrl.qnameConcepts[derivedQName]
        if not hasattr(derivedConcept, 'type') or derivedConcept.type is None:
            return False

        return bool(derivedConcept.type.isDerivedFrom(baseQName))

    def validateAllowedValues(
        self,
        context: str,
        constraints: Types.ConstraintDict,
        taxonomyType: ModelConcept
    ) -> None:
        allowedValues = constraints.get(Const.CONSTRAINT_ALLOWED_VALUES)
        if not allowedValues:
            return

        if taxonomyType.type is None:
            return

        taxonomyTypeQName = taxonomyType.type.qname

        for value in allowedValues:
            valueStr = str(value)
            isValid, errorMsg = validateXmlSchemaValue(
                valueStr,
                str(taxonomyTypeQName),
                self.metadata.namespaces
            )
            if not isValid:
                self.warning(
                    "tcl:invalidAllowedValue",
                    f"Allowed value '{valueStr}' may not be valid for taxonomy type "
                    f"'{taxonomyTypeQName}' at {context}: {errorMsg}"
                )

    def warning(self, code: str, message: str) -> None:
        self.warnings.append((code, message))
        self.modelXbrl.warning(code, message)
