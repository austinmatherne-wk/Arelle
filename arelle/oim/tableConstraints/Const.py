"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

# Reserved prefix
TC_PREFIX = "tc"

# TC namespace patterns (accepting version template patterns)
TC_NAMESPACE_PATTERNS = (
    "https://xbrl.org/2025/tc",
    "https://xbrl.org/${STATUS_DATE_URI}/tc",
    "https://xbrl.org/CR-2025-07-01/tc",
    "https://xbrl.org/PWD-2025-04-01/tc",
    "https://xbrl.org/YYYY-MM-DD/tc",
)

# xBRL-CSV namespace patterns for compatibility
CSV_NAMESPACE_PATTERNS = (
    "https://xbrl.org/2021/xbrl-csv",
    "http://www.xbrl.org/WGWD/YYYY-MM-DD/xbrl-csv",
    "http://xbrl.org/YYYY/xbrl-csv",
    "https://xbrl.org/((~status_date_uri~))/xbrl-csv",
)

# xBRL-CSV core dimensions (identifiers for OIM core dimensions)
XBRL_CSV_CORE_DIMENSIONS = {"concept", "entity", "period", "unit", "language"}

# Special type identifier for decimals property
TYPE_DECIMALS = "decimals"

# XML Schema optionally-timezoned types
OPTIONALLY_TIMEZONED_TYPES = {"xs:date", "xs:time", "xs:dateTime", "xs:gYearMonth", "xs:gMonthDay", "xs:gDay"}

# Valid period types
PERIOD_TYPES = {"year", "half", "quarter", "week", "month", "day", "instant"}

# Valid duration types
DURATION_TYPES = {"yearMonth", "dayTime"}

# Valid key severity values
KEY_SEVERITY_VALUES = {"error", "warning"}

# Table Constraints property names
TC_CONSTRAINTS = f"{TC_PREFIX}:constraints"
TC_PARAMETERS = f"{TC_PREFIX}:parameters"
TC_KEYS = f"{TC_PREFIX}:keys"
TC_TABLE_CONSTRAINTS = f"{TC_PREFIX}:tableConstraints"

# Constraint properties
CONSTRAINT_TYPE = "type"
CONSTRAINT_OPTIONAL = "optional"
CONSTRAINT_NILLABLE = "nillable"
CONSTRAINT_ALLOWED_VALUES = "allowedValues"
CONSTRAINT_ALLOWED_PATTERNS = "allowedPatterns"
CONSTRAINT_TIMEZONE = "timeZone"
CONSTRAINT_PERIOD_TYPE = "periodType"
CONSTRAINT_DURATION_TYPE = "durationType"
CONSTRAINT_LENGTH = "length"
CONSTRAINT_MIN_LENGTH = "minLength"
CONSTRAINT_MAX_LENGTH = "maxLength"
CONSTRAINT_MIN_INCLUSIVE = "minInclusive"
CONSTRAINT_MAX_INCLUSIVE = "maxInclusive"
CONSTRAINT_MIN_EXCLUSIVE = "minExclusive"
CONSTRAINT_MAX_EXCLUSIVE = "maxExclusive"
CONSTRAINT_TOTAL_DIGITS = "totalDigits"
CONSTRAINT_FRACTION_DIGITS = "fractionDigits"

# Valid constraint properties set (for unknown property detection)
VALID_CONSTRAINT_PROPERTIES = {
    CONSTRAINT_TYPE,
    CONSTRAINT_OPTIONAL,
    CONSTRAINT_NILLABLE,
    CONSTRAINT_ALLOWED_VALUES,
    CONSTRAINT_ALLOWED_PATTERNS,
    CONSTRAINT_TIMEZONE,
    CONSTRAINT_PERIOD_TYPE,
    CONSTRAINT_DURATION_TYPE,
    CONSTRAINT_LENGTH,
    CONSTRAINT_MIN_LENGTH,
    CONSTRAINT_MAX_LENGTH,
    CONSTRAINT_MIN_INCLUSIVE,
    CONSTRAINT_MAX_INCLUSIVE,
    CONSTRAINT_MIN_EXCLUSIVE,
    CONSTRAINT_MAX_EXCLUSIVE,
    CONSTRAINT_TOTAL_DIGITS,
    CONSTRAINT_FRACTION_DIGITS,
}

# Keys properties
KEYS_UNIQUE = "unique"
KEYS_REFERENCE = "reference"
KEYS_SORT_KEY = "sortKey"

# Key object properties
KEY_NAME = "name"
KEY_FIELDS = "fields"
KEY_SEVERITY = "severity"
KEY_REFERENCED_KEY_NAME = "referencedKeyName"
KEY_NEGATE = "negate"
KEY_SKIP_NILS = "skipNils"

# Table constraint properties
TC_MIN_TABLES = "minTables"
TC_MAX_TABLES = "maxTables"
TC_MIN_TABLE_ROWS = "minTableRows"
TC_MAX_TABLE_ROWS = "maxTableRows"

# Column order property
TC_COLUMN_ORDER = f"{TC_PREFIX}:columnOrder"

# Metadata error codes
TCME_INVALID_NAMESPACE_PREFIX = "tcme:invalidNamespacePrefix"
TCME_INVALID_JSON_STRUCTURE = "tcme:invalidJSONStructure"
TCME_MISPLACED_OR_UNKNOWN_PROPERTY = "tcme:misplacedOrUnknownProperty"
TCME_INVALID_COMMENT_COLUMN_CONSTRAINT = "tcme:invalidCommentColumnConstraint"
TCME_INVALID_TYPE_CONSTRAINT = "tcme:invalidTypeConstraint"
TCME_ILLEGAL_ALLOWED_VALUE = "tcme:illegalAllowedValue"
TCME_UNKNOWN_TIMEZONE = "tcme:unknownTimeZone"
TCME_ILLEGAL_PERIOD_TYPE = "tcme:illegalPeriodType"
TCME_UNKNOWN_PERIOD_TYPE = "tcme:unknownPeriodType"
TCME_ILLEGAL_DURATION_TYPE = "tcme:illegalDurationType"
TCME_UNKNOWN_DURATION_TYPE = "tcme:unknownDurationType"
TCME_INVALID_LENGTH_TYPE = "tcme:invalidLengthType"
TCME_INVALID_BOUNDARY_TYPE = "tcme:invalidBoundaryType"
TCME_INVALID_DIGITS_TYPE = "tcme:invalidDigitsType"
TCME_DUPLICATE_KEY_NAME = "tcme:duplicateKeyName"
TCME_ILLEGAL_UNIQUE_KEY_FIELD = "tcme:illegalUniqueKeyField"
TCME_ILLEGAL_REFERENCE_KEY_FIELD = "tcme:illegalReferenceKeyField"
TCME_INVALID_KEY_SEVERITY = "tcme:invalidKeySeverity"
TCME_INCONSISTENT_SHARED_KEY_SEVERITY = "tcme:inconsistentSharedKeySeverity"
TCME_INCONSISTENT_SHARED_KEY_SORTING = "tcme:inconsistentSharedKeySorting"
TCME_INCONSISTENT_SHARED_KEY_FIELDS = "tcme:inconsistentSharedKeyFields"
TCME_INVALID_KEY_IDENTIFIER = "tcme:invalidKeyIdentifier"
TCME_INVALID_REFERENCE_KEY = "tcme:invalidReferenceKey"
TCME_INCONSISTENT_REFERENCED_FIELD_TYPE = "tcme:inconsistentReferencedFieldType"
TCME_COLUMN_PARAMETER_TYPE_CONFLICT = "tcme:columnParameterTypeConflict"
TCME_MISSING_KEY_PROPERTY = "tcme:missingKeyProperty"
TCME_UNKNOWN_UNIQUE_KEY = "tcme:unknownUniqueKey"
TCME_INCONSISTENT_COLUMN_ORDER_DEFINITION = "tcme:inconsistentColumnOrderDefinition"

# Report error codes
TCRE_INVALID_VALUE = "tcre:invalidValue"
TCRE_INVALID_BOUNDARY_VALUE = "tcre:invalidBoundaryValue"
TCRE_MISSING_TIMEZONE = "tcre:missingTimeZone"
TCRE_UNEXPECTED_TIMEZONE = "tcre:unexpectedTimeZone"
TCRE_INVALID_PERIOD_TYPE = "tcre:invalidPeriodType"
TCRE_INVALID_DURATION_TYPE = "tcre:invalidDurationType"
TCRE_MISSING_VALUE = "tcre:missingValue"
TCRE_UNIQUE_KEY_VIOLATION = "tcre:uniqueKeyViolation"
TCRE_UNIQUE_KEY_NIL_VIOLATION = "tcre:uniqueKeyNilViolation"
TCRE_REFERENCE_KEY_VIOLATION = "tcre:referenceKeyViolation"
TCRE_KEY_SORT_VIOLATION = "tcre:keySortViolation"
TCRE_INCOMPARABLE_DURATIONS = "tcre:incomparableDurations"
TCRE_INCOMPARABLE_PERIODS = "tcre:incomparablePeriods"
TCRE_MIN_TABLES_VIOLATION = "tcre:minTablesViolation"
TCRE_MAX_TABLES_VIOLATION = "tcre:maxTablesViolation"
TCRE_MIN_TABLE_ROWS_VIOLATION = "tcre:minTableRowsViolation"
TCRE_MAX_TABLE_ROWS_VIOLATION = "tcre:maxTableRowsViolation"
TCRE_INVALID_COLUMN_ORDER = "tcre:invalidColumnOrder"

# Special values in xBRL-CSV
XBRL_CSV_NIL = "#nil"
XBRL_CSV_EMPTY = "#empty"
XBRL_CSV_NONE = "#none"
