"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

# TC namespace URIs (tuple pattern matches nsOims in Load.py)
TC_NAMESPACES = (
    "https://xbrl.org/2025/tc",
    "https://xbrl.org/WGWD/YYYY-MM-DD/tc",
)
TC_NAMESPACES_SET = frozenset(TC_NAMESPACES)

TCME_NAMESPACES = (
    "https://xbrl.org/2025/tc/metadataerror",
    "https://xbrl.org/WGWD/YYYY-MM-DD/tc/metadataerror",
)

TCRE_NAMESPACES = (
    "https://xbrl.org/2025/tc/reporterror",
    "https://xbrl.org/WGWD/YYYY-MM-DD/tc/reporterror",
)

# TC prefix (spec requires TC namespace MUST be bound to "tc")
TC_PREFIX = "tc"

# TC property names (JSON keys in xBRL-CSV metadata)
TC_CONSTRAINTS = "tc:constraints"
TC_PARAMETERS = "tc:parameters"
TC_KEYS = "tc:keys"
TC_COLUMN_ORDER = "tc:columnOrder"
TC_TABLE_CONSTRAINTS = "tc:tableConstraints"

TC_PROPERTIES = frozenset(
    {
        TC_CONSTRAINTS,
        TC_PARAMETERS,
        TC_KEYS,
        TC_COLUMN_ORDER,
        TC_TABLE_CONSTRAINTS,
    }
)

# Valid TC datatypes

XS_DATATYPES = frozenset(
    {
        "xs:string",
        "xs:boolean",
        "xs:decimal",
        "xs:float",
        "xs:double",
        "xs:duration",
        "xs:dateTime",
        "xs:time",
        "xs:date",
        "xs:gYearMonth",
        "xs:gYear",
        "xs:gMonthDay",
        "xs:gDay",
        "xs:gMonth",
        "xs:hexBinary",
        "xs:base64Binary",
        "xs:anyURI",
        "xs:QName",
        "xs:normalizedString",
        "xs:token",
        "xs:language",
        "xs:NMTOKEN",
        "xs:Name",
        "xs:NCName",
        "xs:integer",
        "xs:nonPositiveInteger",
        "xs:negativeInteger",
        "xs:long",
        "xs:int",
        "xs:short",
        "xs:byte",
        "xs:nonNegativeInteger",
        "xs:unsignedLong",
        "xs:unsignedInt",
        "xs:unsignedShort",
        "xs:unsignedByte",
        "xs:positiveInteger",
    }
)

CORE_DIMENSION_TYPES = frozenset(
    {
        "concept",
        "entity",
        "period",
        "unit",
        "language",
    }
)

SPECIAL_TYPES = frozenset(
    {
        "decimals",
    }
)

VALID_TC_TYPES = XS_DATATYPES | CORE_DIMENSION_TYPES | SPECIAL_TYPES

DISALLOWED_OIM_TYPES = frozenset(
    {
        "xs:ENTITY",
        "xs:ENTITIES",
        "xs:ID",
        "xs:IDREF",
        "xs:IDREFS",
        "xs:NMTOKENS",
        "xs:NOTATION",
    }
)

OPTIONALLY_TIME_ZONED_TYPES = frozenset(
    {
        "xs:date",
        "xs:time",
        "xs:dateTime",
        "xs:gYearMonth",
        "xs:gMonthDay",
        "xs:gDay",
    }
)

PERIOD_TYPE_VALUES = frozenset(
    {
        "year",
        "half",
        "quarter",
        "week",
        "month",
        "day",
        "instant",
    }
)

DURATION_TYPE_VALUES = frozenset(
    {
        "yearMonth",
        "dayTime",
    }
)

KEY_SEVERITY_VALUES = frozenset(
    {
        "error",
        "warning",
    }
)

TYPES_NOT_ALLOWED_IN_KEYS = frozenset(
    {
        "xs:double",
        "xs:float",
        "xs:hexBinary",
        "xs:base64Binary",
    }
)

# Core dimension type mapping (lexical and semantic base types)
CORE_DIMENSION_TYPE_MAP: dict[str, dict[str, str]] = {
    "concept": {"lexical_base": "xs:QName", "semantic_base": "xs:QName"},
    "entity": {"lexical_base": "xs:token", "semantic_base": "xs:token"},
    "period": {"lexical_base": "xs:token", "semantic_base": "xs:dateTime"},
    "unit": {"lexical_base": "xs:token", "semantic_base": "xs:token"},
    "language": {"lexical_base": "xs:language", "semantic_base": "xs:language"},
}

# Metadata error codes (tcme:)
TCME_INVALID_JSON_STRUCTURE = "tcme:invalidJSONStructure"
TCME_INVALID_NAMESPACE_PREFIX = "tcme:invalidNamespacePrefix"
TCME_MISPLACED_OR_UNKNOWN_PROPERTY = "tcme:misplacedOrUnknownProperty"
TCME_UNKNOWN_TYPE = "tcme:unknownType"
TCME_UNKNOWN_PERIOD_TYPE = "tcme:unknownPeriodType"
TCME_UNKNOWN_DURATION_TYPE = "tcme:unknownDurationType"
TCME_INVALID_BOUNDARY_TYPE = "tcme:invalidBoundaryType"
TCME_INVALID_LENGTH_TYPE = "tcme:invalidLengthType"
TCME_INVALID_DIGITS_TYPE = "tcme:invalidDigitsType"
TCME_ILLEGAL_CONSTRAINT = "tcme:illegalConstraint"
TCME_INVALID_COMMENT_COLUMN_CONSTRAINT = "tcme:invalidCommentColumnConstraint"
TCME_ILLEGAL_ALLOWED_VALUE = "tcme:illegalAllowedValue"
TCME_INVALID_BOUNDARY_VALUE = "tcme:invalidBoundaryValue"
TCME_UNKNOWN_TIME_ZONE = "tcme:unknownTimeZone"
TCME_MISSING_KEY_PROPERTY = "tcme:missingKeyProperty"
TCME_DUPLICATE_KEY_NAME = "tcme:duplicateKeyName"
TCME_ILLEGAL_KEY_FIELD = "tcme:illegalKeyField"
TCME_ILLEGAL_UNIQUE_KEY_FIELD = "tcme:illegalUniqueKeyField"
TCME_UNKNOWN_UNIQUE_KEY = "tcme:unknownUniqueKey"
TCME_INVALID_REFERENCE_KEY = "tcme:invalidReferenceKey"
TCME_ILLEGAL_REFERENCE_KEY_FIELD = "tcme:illegalReferenceKeyField"
TCME_INVALID_KEY_IDENTIFIER = "tcme:invalidKeyIdentifier"
TCME_UNKNOWN_SEVERITY = "tcme:unknownSeverity"
TCME_UNKNOWN_KEY = "tcme:unknownKey"
TCME_INCONSISTENT_SHARED_KEY_SEVERITY = "tcme:inconsistentSharedKeySeverity"
TCME_INCONSISTENT_SHARED_KEY_FIELDS = "tcme:inconsistentSharedKeyFields"
TCME_INCONSISTENT_REFERENCE_KEY_FIELDS = "tcme:inconsistentReferenceKeyFields"
TCME_ILLEGAL_UNIQUE_KEY_ORDER = "tcme:illegalUniqueKeyOrder"
TCME_ILLEGAL_OPTIONAL_SORT_KEY_COLUMN = "tcme:illegalOptionalSortKeyColumn"
TCME_INCONSISTENT_COLUMN_ORDER_DEFINITION = "tcme:inconsistentColumnOrderDefinition"
TCME_COLUMN_PARAMETER_CONFLICT = "tcme:columnParameterConflict"

# Report error codes (tcre:)
TCRE_INVALID_VALUE = "tcre:invalidValue"
TCRE_INVALID_BOUNDARY_VALUE = "tcre:invalidBoundaryValue"
TCRE_INVALID_PERIOD_TYPE = "tcre:invalidPeriodType"
TCRE_INVALID_DURATION_TYPE = "tcre:invalidDurationType"
TCRE_INCOMPARABLE_PERIODS = "tcre:incomparablePeriods"
TCRE_INCOMPARABLE_DURATIONS = "tcre:incomparableDurations"
TCRE_MISSING_TIME_ZONE = "tcre:missingTimeZone"
TCRE_UNEXPECTED_TIME_ZONE = "tcre:unexpectedTimeZone"
TCRE_MISSING_COLUMN = "tcre:missingColumn"
TCRE_INVALID_COLUMN_ORDER = "tcre:invalidColumnOrder"
TCRE_UNIQUE_KEY_VIOLATION = "tcre:uniqueKeyViolation"
TCRE_UNIQUE_KEY_NIL_VIOLATION = "tcre:uniqueKeyNilViolation"
TCRE_SORT_KEY_VIOLATION = "tcre:sortKeyViolation"
TCRE_REFERENCE_KEY_VIOLATION = "tcre:referenceKeyViolation"
TCRE_COLUMN_PARAMETER_CONFLICT = "tcre:columnParameterConflict"
TCRE_MIN_TABLES_VIOLATION = "tcre:minTablesViolation"
TCRE_MAX_TABLES_VIOLATION = "tcre:maxTablesViolation"
TCRE_MIN_TABLE_ROWS_VIOLATION = "tcre:minTableRowsViolation"
TCRE_MAX_TABLE_ROWS_VIOLATION = "tcre:maxTableRowsViolation"
