"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

import contextlib
from decimal import Decimal
from typing import Any

import isodate
import regex

from arelle.ModelValue import QName
from arelle.ModelXbrl import ModelXbrl
from arelle.oim.tableConstraints import Const, Types, Utils
from arelle.oim.tableConstraints.XmlSchemaHelper import (
    hasTimezone,
    isDurationDayTime,
    isDurationYearMonth,
    isOptionallyTimezoned,
    isXmlSchemaBuiltInType,
    validateXmlSchemaValue,
    valuesEqual,
)
from arelle.typing import TypeGetText

_: TypeGetText


class ConstraintViolation(Exception):
    """Exception raised when a constraint is violated."""

    def __init__(self, errorCode: str, message: str, **kwargs: Any) -> None:
        self.errorCode = errorCode
        self.message = message
        self.kwargs = kwargs
        super().__init__(message)


class ValueValidator:
    """
    Validates individual values against Table Constraint rules.
    """

    def __init__(self, modelXbrl: ModelXbrl) -> None:
        self.modelXbrl = modelXbrl

    def validateValue(
        self,
        value: Any,
        constraint: Types.ConstraintDict,
        context: str,
        namespaces: dict[str, str],
        isParameter: bool = False,
    ) -> list[ConstraintViolation]:
        """
        Validate a value against a constraint definition.
        Returns list of violations (empty if valid).
        """
        violations = []

        optional = constraint.get(Const.CONSTRAINT_OPTIONAL, False)

        # If value is None (missing)
        if value is None:
            # For parameters, missing value when not optional is an error
            if isParameter and not optional:
                violations.append(
                    ConstraintViolation(Const.TCRE_MISSING_VALUE, f"Required value is missing: {context}")
                )
            # For columns, if not in CSV, no fact is created - skip validation
            return violations

        isNil = self.isNilValue(value)
        isNone = self.isNoneValue(value)
        isEmpty = self.isEmptyValue(value)
        isExplicitEmpty = value == Const.XBRL_CSV_EMPTY  # #empty marker

        # For optional columns, empty values are treated as "not provided"
        if optional and isEmpty:
            return violations

        # Distinguish between missing value (empty CSV cell) and explicit #empty
        # Empty CSV cell ("") when not optional → tcre:missingValue
        # Explicit #empty marker → empty string that should be type validated
        if not optional and isEmpty and not isExplicitEmpty:
            violations.append(ConstraintViolation(Const.TCRE_MISSING_VALUE, f"Required value is missing: {context}"))
            return violations

        typeStr = constraint.get(Const.CONSTRAINT_TYPE)
        if not typeStr:
            return violations

        nillable = constraint.get(Const.CONSTRAINT_NILLABLE, True)
        if not nillable and isNil:
            violations.append(ConstraintViolation(Const.TCRE_INVALID_VALUE, f"Nil value not allowed: {context}"))
            return violations

        if isNil or isNone:
            return violations

        typeViolation = self.validateType(value, typeStr, context, namespaces)
        if typeViolation:
            violations.append(typeViolation)
            return violations

        allowedValues = constraint.get(Const.CONSTRAINT_ALLOWED_VALUES)
        if allowedValues and not isEmpty:
            violation = self.validateAllowedValues(value, allowedValues, typeStr, context, namespaces)
            if violation:
                violations.append(violation)

        allowedPatterns = constraint.get(Const.CONSTRAINT_ALLOWED_PATTERNS)
        if allowedPatterns and not isEmpty:
            violation = self.validateAllowedPatterns(value, allowedPatterns, context)
            if violation:
                violations.append(violation)

        timeZone = constraint.get(Const.CONSTRAINT_TIMEZONE)
        if timeZone is not None:
            violation = self.validateTimezone(value, timeZone, typeStr, context)
            if violation:
                violations.append(violation)

        periodType = constraint.get(Const.CONSTRAINT_PERIOD_TYPE)
        if periodType:
            violation = self.validatePeriodType(value, periodType, context)
            if violation:
                violations.append(violation)

        durationType = constraint.get(Const.CONSTRAINT_DURATION_TYPE)
        if durationType:
            violation = self.validateDurationType(value, durationType, context)
            if violation:
                violations.append(violation)

        facetViolations = self.validateFacets(value, constraint, typeStr, context)
        violations.extend(facetViolations)

        return violations

    def validateType(
        self, value: str, typeStr: str, context: str, namespaces: dict[str, str]
    ) -> ConstraintViolation | None:
        """Validate value against its type constraint."""
        if isXmlSchemaBuiltInType(typeStr, namespaces):
            isValid, errorMsg = validateXmlSchemaValue(value, typeStr, namespaces)
            if not isValid:
                return ConstraintViolation(
                    Const.TCRE_INVALID_VALUE, f"Invalid {typeStr} value '{value}': {errorMsg} ({context})"
                )
            return None

        if typeStr in Const.XBRL_CSV_CORE_DIMENSIONS:
            return self.validateCoreDimension(value, typeStr, context, namespaces)

        if typeStr == Const.TYPE_DECIMALS:
            return self.validateDecimals(value, context)

        return ConstraintViolation(Const.TCRE_INVALID_VALUE, f"Unknown type '{typeStr}' ({context})")

    def validateCoreDimension(
        self, value: str, dimension: str, context: str, namespaces: dict[str, str]
    ) -> ConstraintViolation | None:
        """Validate xBRL-CSV core dimension values."""
        try:
            if dimension == "concept":
                self.parseQName(value, namespaces)
            elif dimension == "entity":
                # Entity values are QNames that must have valid namespace prefixes
                self.parseQName(value, namespaces)
            elif dimension == "period":
                if not value or not value.strip():
                    raise ValueError("period cannot be empty")
                # Validate period format (instant or duration)
                self._validatePeriodFormat(value)
            elif dimension == "unit":
                if not value or not value.strip():
                    raise ValueError("unit cannot be empty")
                # Validate unit format - check all QNames in the expression
                self._validateUnitFormat(value, namespaces)
            elif dimension == "language" and not regex.match(r"^[a-z]{2,3}(-[A-Z]{2})?$", value):
                raise ValueError("Invalid language code format")
            return None
        except (TypeError, ValueError) as e:
            return ConstraintViolation(
                Const.TCRE_INVALID_VALUE, f"Invalid {dimension} value '{value}': {str(e)} ({context})"
            )

    def _validatePeriodFormat(self, value: str) -> None:
        """Validate period format (instant or duration).

        Raises ValueError if format is invalid.
        """

        def parseDateWithTimezone(dateStr: str) -> None:
            """Parse a date that may include timezone suffix."""
            # Strip timezone suffix if present (Z or +/-HH:MM)
            dateOnly = regex.sub(r"(Z|[+-]\d{2}:\d{2})$", "", dateStr)
            try:
                isodate.parse_date(dateOnly)
            except ValueError as err:
                raise ValueError(f"Invalid date: {dateStr}") from err

        # Check for instant format: date@start or date@end
        if "@" in value:
            parts = value.split("@")
            if len(parts) != 2 or parts[1] not in ("start", "end"):
                raise ValueError(f"Invalid instant period format: {value}")
            parseDateWithTimezone(parts[0])
        # Check for duration format: date..date
        elif ".." in value:
            parts = value.split("..")
            if len(parts) != 2:
                raise ValueError(f"Invalid duration period format: {value}")
            # Validate both dates
            parseDateWithTimezone(parts[0])
            parseDateWithTimezone(parts[1])
        else:
            # Could be just a date or other abbreviated format
            parseDateWithTimezone(value)

    def _validateUnitFormat(self, value: str, namespaces: dict[str, str]) -> None:
        """Validate unit format - check all QNames have valid prefixes.

        Raises ValueError if format is invalid.
        """
        # Unit expressions can contain QNames separated by operators: * / ( )
        # Note: Subtraction (-) is NOT a valid operator in XBRL unit expressions

        # Check for invalid operators (like -)
        # Valid unit expression should only have: QNames, *, /, (, )
        # Split by valid operators and whitespace
        parts = regex.split(r"[*/()]", value)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            # Each part should be a QName
            # Match QName pattern: prefix:localname
            # Check for multiple colons which indicates invalid syntax
            colons = part.count(":")
            if colons > 1:
                raise ValueError(f"Invalid unit expression: multiple colons in '{part}'")
            if colons == 1:
                # Validate this as a QName
                self.parseQName(part, namespaces)

    def validateDecimals(self, value: str, context: str) -> ConstraintViolation | None:
        """Validate decimals property value.

        Note: INF is not allowed in Table Constraints - use #none instead.
        Only integer values are allowed.
        """
        try:
            int(value)
            return None
        except ValueError:
            return ConstraintViolation(Const.TCRE_INVALID_VALUE, f"Invalid decimals value '{value}' ({context})")

    def validateAllowedValues(
        self,
        value: str,
        allowedValues: list[Any],  # Can contain mixed types from JSON
        typeStr: str,
        context: str,
        namespaces: dict[str, str],
    ) -> ConstraintViolation | None:
        """Validate value is in allowed enum."""
        # Convert allowedValues to strings (CSV values are always strings)
        for allowedValue in allowedValues:
            allowedValueStr = str(allowedValue)
            if valuesEqual(value, allowedValueStr, typeStr, namespaces):
                return None
        return ConstraintViolation(Const.TCRE_INVALID_VALUE, f"Value '{value}' not in allowed values ({context})")

    def validateAllowedPatterns(self, value: str, patterns: list[str], context: str) -> ConstraintViolation | None:
        """Validate value matches at least one pattern."""
        for pattern in patterns:
            with contextlib.suppress(regex.error):
                if regex.fullmatch(pattern, value):
                    return None
        return ConstraintViolation(
            Const.TCRE_INVALID_VALUE, f"Value '{value}' does not match any allowed pattern ({context})"
        )

    def validateTimezone(self, value: str, required: bool, typeStr: str, context: str) -> ConstraintViolation | None:
        """Validate timezone presence/absence."""
        if typeStr != "period" and not isOptionallyTimezoned(typeStr):
            return None

        hasTimezoneComp = hasTimezone(value)

        if required and not hasTimezoneComp:
            return ConstraintViolation(
                Const.TCRE_MISSING_TIMEZONE, f"Timezone required but missing: {value} ({context})"
            )
        elif not required and hasTimezoneComp:
            return ConstraintViolation(Const.TCRE_UNEXPECTED_TIMEZONE, f"Timezone not allowed: {value} ({context})")
        return None

    def validatePeriodType(self, value: str, periodType: str, context: str) -> ConstraintViolation | None:
        """Validate period value matches required type."""
        # Abbreviated period formats per xBRL-CSV spec
        # Patterns must match ENTIRE string, not just prefix
        patterns = {
            "year": r"^\d{4}$",
            "half": r"^\d{4}H[12]$",
            "quarter": r"^\d{4}Q[1-4]$",
            "month": r"^\d{4}-\d{2}$",
            "week": r"^\d{4}W\d{2}$",
            "day": r"^\d{4}-\d{2}-\d{2}$",
            "instant": r"^.*@(?:start|end)$",
        }

        pattern = patterns.get(periodType)
        if not pattern:
            return None

        if not regex.match(pattern, value):
            return ConstraintViolation(
                Const.TCRE_INVALID_PERIOD_TYPE, f"Period value '{value}' does not match type '{periodType}' ({context})"
            )
        return None

    def validateDurationType(self, value: str, durationType: str, context: str) -> ConstraintViolation | None:
        """Validate duration matches required pattern."""
        if durationType == "yearMonth":
            if not isDurationYearMonth(value):
                return ConstraintViolation(
                    Const.TCRE_INVALID_DURATION_TYPE, f"Duration '{value}' is not yearMonth type ({context})"
                )
        elif durationType == "dayTime" and not isDurationDayTime(value):
            return ConstraintViolation(
                Const.TCRE_INVALID_DURATION_TYPE, f"Duration '{value}' is not dayTime type ({context})"
            )
        return None

    def validateFacets(
        self, value: str, constraint: Types.ConstraintDict, typeStr: str, context: str
    ) -> list[ConstraintViolation]:
        """Validate XML Schema facets."""
        violations = []

        # Length facets
        length = constraint.get(Const.CONSTRAINT_LENGTH)
        if length is not None and len(value) != length:
            violations.append(
                ConstraintViolation(Const.TCRE_INVALID_VALUE, f"Length {len(value)} != required {length} ({context})")
            )

        minLength = constraint.get(Const.CONSTRAINT_MIN_LENGTH)
        if minLength is not None and len(value) < minLength:
            violations.append(
                ConstraintViolation(Const.TCRE_INVALID_VALUE, f"Length {len(value)} < minimum {minLength} ({context})")
            )

        maxLength = constraint.get(Const.CONSTRAINT_MAX_LENGTH)
        if maxLength is not None and len(value) > maxLength:
            violations.append(
                ConstraintViolation(Const.TCRE_INVALID_VALUE, f"Length {len(value)} > maximum {maxLength} ({context})")
            )

        # Boundary facets (for numeric/date types)
        minInclusive = constraint.get(Const.CONSTRAINT_MIN_INCLUSIVE)
        if minInclusive is not None:
            with contextlib.suppress(Exception):
                if Decimal(value) < Decimal(minInclusive):
                    violations.append(
                        ConstraintViolation(
                            Const.TCRE_INVALID_VALUE, f"Value {value} < minimum {minInclusive} ({context})"
                        )
                    )

        maxInclusive = constraint.get(Const.CONSTRAINT_MAX_INCLUSIVE)
        if maxInclusive is not None:
            with contextlib.suppress(Exception):
                if Decimal(value) > Decimal(maxInclusive):
                    violations.append(
                        ConstraintViolation(
                            Const.TCRE_INVALID_VALUE, f"Value {value} > maximum {maxInclusive} ({context})"
                        )
                    )

        minExclusive = constraint.get(Const.CONSTRAINT_MIN_EXCLUSIVE)
        if minExclusive is not None:
            with contextlib.suppress(Exception):
                if Decimal(value) <= Decimal(minExclusive):
                    violations.append(
                        ConstraintViolation(
                            Const.TCRE_INVALID_VALUE, f"Value {value} <= exclusive minimum {minExclusive} ({context})"
                        )
                    )

        maxExclusive = constraint.get(Const.CONSTRAINT_MAX_EXCLUSIVE)
        if maxExclusive is not None:
            with contextlib.suppress(Exception):
                if Decimal(value) >= Decimal(maxExclusive):
                    violations.append(
                        ConstraintViolation(
                            Const.TCRE_INVALID_VALUE, f"Value {value} >= exclusive maximum {maxExclusive} ({context})"
                        )
                    )

        # Digit facets
        totalDigits = constraint.get(Const.CONSTRAINT_TOTAL_DIGITS)
        if totalDigits is not None:
            with contextlib.suppress(Exception):
                # Count significant digits
                d = Decimal(value)
                digits = len(str(d).replace(".", "").replace("-", "").lstrip("0")) or 1
                if digits > totalDigits:
                    violations.append(
                        ConstraintViolation(
                            Const.TCRE_INVALID_VALUE, f"Total digits {digits} > maximum {totalDigits} ({context})"
                        )
                    )

        fractionDigits = constraint.get(Const.CONSTRAINT_FRACTION_DIGITS)
        if fractionDigits is not None:
            with contextlib.suppress(Exception):
                d = Decimal(value)
                # Count decimal places
                strVal = str(d)
                if "." in strVal:
                    fracDigits = len(strVal.split(".")[1])
                    if fracDigits > fractionDigits:
                        violations.append(
                            ConstraintViolation(
                                Const.TCRE_INVALID_VALUE,
                                f"Fraction digits {fracDigits} > maximum {fractionDigits} ({context})",
                            )
                        )

        return violations

    def isNilValue(self, value: Any) -> bool:
        """Check if value represents nil."""
        return Utils.isNilValue(value)

    def isNoneValue(self, value: Any) -> bool:
        """Check if value represents none."""
        return isinstance(value, str) and value == Const.XBRL_CSV_NONE

    def isEmptyValue(self, value: Any) -> bool:
        """Check if value represents empty string."""
        return isinstance(value, str) and (value == Const.XBRL_CSV_EMPTY or value == "")

    def parseQName(self, value: str, namespaces: dict[str, str]) -> QName:
        """Parse a QName value with namespace resolution."""
        if ":" in value:
            prefix, localName = value.split(":", 1)
            namespaceURI = namespaces.get(prefix)
            if not namespaceURI:
                raise ValueError(f"Unknown prefix: {prefix}")
            return QName(prefix, namespaceURI, localName)
        else:
            # No prefix - default namespace
            return QName(None, None, value)
