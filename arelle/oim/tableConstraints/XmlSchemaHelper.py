"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

import base64
from decimal import Decimal
from typing import Any

import isodate
import regex

from arelle import FunctionXs, ModelValue, XbrlConst, XmlUtil
from arelle.oim.tableConstraints import Const
from arelle.typing import TypeGetText

_: TypeGetText


def isXmlSchemaBuiltInType(typeStr: str, namespaces: dict[str, str]) -> bool:
    """
    Check if a type string refers to an XML Schema built-in type.

    Uses core Arelle's FunctionXs.isXsType() to check against the complete
    set of XML Schema types supported by Arelle.

    Args:
        typeStr: QName string (e.g., "xs:string", "xsd:integer")
        namespaces: Namespace prefix mapping from xBRL-CSV metadata. If not provided,
                    assumes "xs:" prefix for XML Schema types.

    Returns:
        True if the type string refers to an XML Schema built-in type.
    """
    if not typeStr or ":" not in typeStr:
        return False

    # Parse QName
    prefix, localName = typeStr.split(":", 1)

    if namespaces.get(prefix) != XbrlConst.xsd:
        return False

    return FunctionXs.isXsType(localName)


def getXmlSchemaTypeName(typeStr: str, namespaces: dict[str, str]) -> str | None:
    """
    Extract the local name from an XML Schema type QName.

    Args:
        typeStr: QName string (e.g., "xs:string", "xsd:integer")
        namespaces: Namespace prefix mapping from xBRL-CSV metadata. If not provided,
                    assumes "xs:" prefix for XML Schema types.

    Returns:
        The local name if typeStr is an XML Schema type, None otherwise.
    """
    if not typeStr or ":" not in typeStr:
        return None

    # Parse QName
    prefix, localName = typeStr.split(":", 1)

    if namespaces.get(prefix) != XbrlConst.xsd:
        return None

    return localName


def isCoreDimension(typeStr: str) -> bool:
    """Check if a type string refers to an xBRL-CSV core dimension."""
    return typeStr in Const.XBRL_CSV_CORE_DIMENSIONS


def isOptionallyTimezoned(typeStr: str) -> bool:
    """Check if a type allows optional timezone component."""
    return typeStr in Const.OPTIONALLY_TIMEZONED_TYPES


def validateXmlSchemaValue(value: str, typeStr: str, namespaces: dict[str, str]) -> tuple[bool, str | None]:
    """
    Validate a value against an XML Schema built-in type.

    Uses core Arelle's ModelValue parsing functions for date/time, duration, and
    QName types to ensure consistency with the rest of Arelle's validation system.

    Args:
        value: The value to validate
        typeStr: QName string for the XML Schema type (e.g., "xs:string", "xsd:integer")
        namespaces: Namespace prefix mapping from xBRL-CSV metadata. If not provided,
                    assumes "xs:" prefix for XML Schema types.

    Returns:
        Tuple of (isValid, errorMessage).

    Note: This provides a simplified interface for Table Constraints validation.
    Core Arelle's arelle.XmlValidate.validateValue() provides more comprehensive
    validation including facets, but requires ModelObject elements and integrates
    with the full model validation system.
    """
    typeName = getXmlSchemaTypeName(typeStr, namespaces)
    if typeName is None:
        return False, f"Not an XML Schema type: {typeStr}"

    try:
        # Numeric types
        if typeName == "decimal":
            Decimal(value)
        elif typeName in (
            "integer",
            "int",
            "long",
            "short",
            "byte",
            "nonNegativeInteger",
            "positiveInteger",
            "unsignedLong",
            "unsignedInt",
            "unsignedShort",
            "unsignedByte",
            "nonPositiveInteger",
            "negativeInteger",
        ):
            int(value)
            if "." in value:
                return False, "Integer values cannot contain decimal point"
        elif typeName in ("float", "double"):
            float(value)

        # String types
        elif typeName == "string":
            pass  # Any string is valid

        # Date/time types - use core Arelle's ModelValue parsers
        elif typeName == "date":
            ModelValue.dateTime(value, type=ModelValue.DATE)
        elif typeName == "time":
            ModelValue.time(value)
        elif typeName == "dateTime":
            ModelValue.dateTime(value, type=ModelValue.DATETIME)
        elif typeName == "duration":
            # Validate duration format more strictly than isodate
            # ISO 8601: P[n]Y[n]M[n]DT[n]H[n]M[n]S
            # T should only be present if time components follow
            if "T" in value:
                tIndex = value.index("T")
                afterT = value[tIndex + 1 :]
                # If T is present, there must be at least one time component after it
                if not afterT or not any(c in afterT for c in "HMS"):
                    return False, "T designator must be followed by time components (H, M, or S)"
            ModelValue.isoDuration(value)  # Use core Arelle's duration parser
        elif typeName == "gYearMonth":
            # Format: YYYY-MM - use regex for validation
            if not regex.match(r"-?\d{4}-\d{2}(?:Z|[+-]\d{2}:\d{2})?$", value):
                return False, "Invalid gYearMonth format"
        elif typeName == "gMonthDay":
            # Format: --MM-DD
            if not regex.match(r"--\d{2}-\d{2}(?:Z|[+-]\d{2}:\d{2})?$", value):
                return False, "Invalid gMonthDay format"
        elif typeName == "gDay":
            # Format: ---DD
            if not regex.match(r"---\d{2}(?:Z|[+-]\d{2}:\d{2})?$", value):
                return False, "Invalid gDay format"

        # Boolean
        elif typeName == "boolean":
            if value not in ("true", "false", "1", "0"):
                return False, "Invalid boolean value"

        # QName - use core Arelle's QName parser (requires namespace context, so basic check)
        elif typeName == "QName":
            # Use regex for basic QName format validation
            # Full QName validation requires namespace context which table constraints don't have
            if not regex.match(r"^[a-zA-Z_][\w\-\.]*:[a-zA-Z_][\w\-\.]*$", value) and not regex.match(
                r"^[a-zA-Z_][\w\-\.]*$", value
            ):
                return False, "Invalid QName format"

        # anyURI - use core Arelle's anyURI parser
        elif typeName == "anyURI":
            ModelValue.anyURI(value)

        # base64Binary and hexBinary
        elif typeName == "base64Binary":
            base64.b64decode(value)
        elif typeName == "hexBinary":
            bytes.fromhex(value)

        else:
            # For other types, we accept the value
            # (Full XML Schema validation would require more complex checks)
            pass

        return True, None

    except (ValueError, TypeError, ArithmeticError) as e:
        return False, str(e)


def compareValues(val1: str, val2: str, typeStr: str, namespaces: dict[str, str]) -> int:
    """
    Compare two values according to their type for Table Constraints sorting validation.

    Uses core Arelle's ModelValue module for parsing dates, times, and durations
    to ensure consistency with the rest of Arelle's type system.

    Args:
        val1: First value to compare
        val2: Second value to compare
        typeStr: QName string for the type (e.g., "xs:string", "period", "xsd:integer")
        namespaces: Namespace prefix mapping from xBRL-CSV metadata. If not provided,
                    assumes "xs:" prefix for XML Schema types.

    Returns:
        -1 if val1 < val2
         0 if val1 == val2
         1 if val1 > val2

    Raises:
        ValueError: If durations are incomparable (yearMonth vs dayTime)

    This function provides a convenience wrapper for table constraints sort validation
    while leveraging core Arelle's typed value classes for proper comparison semantics.
    """
    # Handle nil values (nil < any non-nil)
    if val1 is None and val2 is None:
        return 0
    if val1 is None:
        return -1
    if val2 is None:
        return 1

    # Handle core dimension types before xs: types
    if typeStr == "period":
        # Check if periods are comparable
        # Per spec: Instant (contains @) and Duration (contains ..) can't be compared
        isInstant1 = "@" in val1
        isInstant2 = "@" in val2

        if isInstant1 != isInstant2:
            # One is instant, one is duration - incomparable
            raise ValueError(Const.TCRE_INCOMPARABLE_PERIODS)

        # Both same type, compare as strings
        # (Full period comparison would require parsing, but lexical is fine for sorting)
        if val1 < val2:
            return -1
        elif val1 > val2:
            return 1
        return 0

    typeName = getXmlSchemaTypeName(typeStr, namespaces)
    if typeName is None:
        # For non-XS types, use string comparison
        if val1 < val2:
            return -1
        elif val1 > val2:
            return 1
        return 0

    try:
        # Numeric types
        if typeName in ("decimal", "integer"):
            d1 = Decimal(val1)
            d2 = Decimal(val2)
            if d1 < d2:
                return -1
            elif d1 > d2:
                return 1
            return 0

        elif typeName in ("float", "double"):
            f1 = float(val1)
            f2 = float(val2)
            if f1 < f2:
                return -1
            elif f1 > f2:
                return 1
            return 0

        # Date/time types
        elif typeName in ("date", "time", "dateTime"):
            # Normalize timezone to UTC for comparison
            dt1 = parseDateTime(val1, typeName)
            dt2 = parseDateTime(val2, typeName)
            if dt1 < dt2:
                return -1
            elif dt1 > dt2:
                return 1
            return 0

        # Duration
        elif typeName == "duration":
            # Check if durations are comparable
            # Per Table Constraints spec: YearMonth and DayTime durations cannot be compared
            isYearMonth1 = isDurationYearMonth(val1)
            isYearMonth2 = isDurationYearMonth(val2)

            if isYearMonth1 != isYearMonth2:
                # One is YearMonth, one is DayTime - incomparable
                # Raise ValueError to be caught by the caller (SortValidator)
                raise ValueError(Const.TCRE_INCOMPARABLE_DURATIONS)

            # Use core Arelle's duration parsing which handles all ISO 8601 edge cases
            dur1 = ModelValue.isoDuration(val1)
            dur2 = ModelValue.isoDuration(val2)
            if dur1 < dur2:
                return -1
            elif dur1 > dur2:
                return 1
            return 0

        # Boolean
        elif typeName == "boolean":
            b1 = val1 in ("true", "1")
            b2 = val2 in ("true", "1")
            if b1 < b2:
                return -1
            elif b1 > b2:
                return 1
            return 0

        # String types and others - lexical comparison
        else:
            # Whitespace normalize and compare by codepoint
            s1 = XmlUtil.collapseWhitespace(val1)
            s2 = XmlUtil.collapseWhitespace(val2)
            if s1 < s2:
                return -1
            elif s1 > s2:
                return 1
            return 0

    except (TypeError, isodate.ISO8601Error, ArithmeticError):
        # If comparison fails for other reasons, treat as string comparison
        if val1 < val2:
            return -1
        elif val1 > val2:
            return 1
        return 0


def valuesEqual(val1: str, val2: str, typeStr: str, namespaces: dict[str, str]) -> bool:
    """
    Check if two values are equal according to XML Schema semantics.

    Args:
        val1: First value to compare
        val2: Second value to compare
        typeStr: QName string for the type (e.g., "xs:string", "period", "xsd:integer")
        namespaces: Namespace prefix mapping from xBRL-CSV metadata. If not provided,
                    assumes "xs:" prefix for XML Schema types.

    Returns:
        True if values are equal according to their type's semantics.
    """
    return compareValues(val1, val2, typeStr, namespaces) == 0


def parseDateTime(value: str, typeName: str) -> Any:
    """
    Parse date/time value using core Arelle ModelValue functions.

    Uses Arelle's ModelValue.dateTime() and ModelValue.time() which handle
    timezone normalization, hour 24:00:00, and other XML Schema edge cases.
    """
    # Add Z if no timezone specified (treat as UTC) - for xBRL-CSV compatibility
    if not hasTimezone(value):
        value = value + "Z"

    if typeName == "date":
        # ModelValue.dateTime() returns DateTime object with dateOnly flag for dates
        return ModelValue.dateTime(value, type=ModelValue.DATE)
    elif typeName == "time":
        return ModelValue.time(value)
    elif typeName == "dateTime":
        return ModelValue.dateTime(value, type=ModelValue.DATETIME)
    else:
        return value


def hasTimezone(value: str) -> bool:
    """Check if a date/time value has a timezone component."""
    if not value:
        return False
    # Check for Z or +/-HH:MM
    return bool(regex.search(r"Z|[+-]\d{2}:\d{2}$", value))


def isDurationYearMonth(value: str) -> bool:
    """Check if a duration contains only year/month components."""
    try:
        # Pattern that matches yearMonth duration (no D, H, M, S after T)
        return bool(regex.match(r"-?P(?:\d+Y)?(?:\d+M)?$", value))
    except regex.error:
        # Invalid regex pattern or value - treat as non-matching
        return False


def isDurationDayTime(value: str) -> bool:
    """Check if a duration contains only day/time components."""
    try:
        # Pattern that matches dayTime duration (no Y, M before T)
        return bool(regex.match(r"-?P(?:\d+D)?(?:T(?:\d+H)?(?:\d+M)?(?:\d+(?:\.\d+)?S)?)?$", value))
    except regex.error:
        # Invalid regex pattern or value - treat as non-matching
        return False


def isValidForFacet(facetName: str, typeStr: str, namespaces: dict[str, str]) -> bool:
    """
    Check if a facet is applicable to a type.
    Based on XML Schema Part 2, Appendix C: Applicable Facets.

    Args:
        facetName: Name of the facet (e.g., "length", "minInclusive")
        typeStr: QName string for the type (e.g., "xs:string", "xsd:integer", "decimals")
        namespaces: Namespace prefix mapping from xBRL-CSV metadata. If not provided,
                    assumes "xs:" prefix for XML Schema types.

    Returns:
        True if the facet is applicable to the type.

    Per spec: "The constraints that are valid for xs:integer are also valid for 'decimals'."
    """
    # Handle 'decimals' special type - treat as xs:integer for facet validation
    if typeStr == Const.TYPE_DECIMALS:
        typeStr = "xs:integer"

    typeName = getXmlSchemaTypeName(typeStr, namespaces)
    if typeName is None:
        return False

    # Length facets: string, base64Binary, hexBinary, QName, NOTATION, anyURI
    if facetName in ("length", "minLength", "maxLength"):
        return typeName in (
            "string",
            "base64Binary",
            "hexBinary",
            "QName",
            "NOTATION",
            "anyURI",
            "normalizedString",
            "token",
            "language",
            "Name",
            "NCName",
            "ID",
            "IDREF",
        )

    # Boundary facets: numeric and date/time types
    elif facetName in ("minInclusive", "maxInclusive", "minExclusive", "maxExclusive"):
        return typeName in (
            "decimal",
            "integer",
            "float",
            "double",
            "byte",
            "int",
            "long",
            "short",
            "unsignedByte",
            "unsignedInt",
            "unsignedLong",
            "unsignedShort",
            "date",
            "time",
            "dateTime",
            "duration",
            "gYearMonth",
            "gYear",
            "gMonthDay",
            "gDay",
            "gMonth",
            "positiveInteger",
            "negativeInteger",
            "nonNegativeInteger",
            "nonPositiveInteger",
        )

    # Digit facets: decimal and derived types
    elif facetName in ("totalDigits", "fractionDigits"):
        return typeName in (
            "decimal",
            "integer",
            "byte",
            "int",
            "long",
            "short",
            "unsignedByte",
            "unsignedInt",
            "unsignedLong",
            "unsignedShort",
            "positiveInteger",
            "negativeInteger",
            "nonNegativeInteger",
            "nonPositiveInteger",
        )

    return False
