# Table Constraints Validation

:::{index} Table Constraints
:::

Table Constraints is an XBRL specification that defines validation rules for xBRL-CSV reports.
It allows report authors to specify constraints on column values, enforce relationships between columns, and validate the structure of CSV data files.

Arelle provides comprehensive support for Table Constraints validation, including structural validation, data validation, and optional taxonomy consistency linting.

## Overview

Table Constraints validation in Arelle operates at three levels:

1. **Metadata Validation** - Validates the Table Constraints metadata structure itself
2. **Report Validation** - Validates CSV data against the defined constraints
3. **Linting** - Checks metadata consistency with the XBRL taxonomy (optional, non-normative)

### Specification

Table Constraints is defined by the [XBRL Table Constraints specification](https://www.xbrl.org/Specification/table-constraints/).

## Validation Types

### Metadata Validation (tcme:* errors)

Metadata validation checks the **structural correctness** of Table Constraints metadata. This validation ensures:

- JSON structure is valid
- Required properties are present
- Property types are correct
- References between metadata elements are valid
- Column order constraints are consistent
- Key definitions are properly structured

**Error codes**: `tcme:*` (Table Constraints Metadata Errors)

**When to use**: Always recommended for metadata authors. Can be run once when publishing metadata and doesn't need to be repeated for every report.

### Report Validation (tcre:* errors)

Report validation checks **CSV data** against the constraints defined in metadata. This validation:

- Uses streaming processing (constant memory usage)
- Validates column values against type constraints
- Enforces allowedValues restrictions
- Checks minValue/maxValue bounds
- Validates key uniqueness and foreign key relationships
- Verifies sort order requirements
- Validates row/table count constraints

**Error codes**: `tcre:*` (Table Constraints Report Errors)

**When to use**: For every report submission to ensure data meets requirements.

**Performance**: Optimized for large CSV files using streaming validation - reports are validated without loading into memory.

### Linting (tcl:* warnings)

Linting validates **metadata consistency with the XBRL taxonomy**. This optional validation:

- Checks that constraint types match or derive from taxonomy types
- Validates allowedValues against taxonomy type definitions
- Requires the taxonomy to be loaded
- Produces non-normative warnings

**Warning codes**: `tcl:*` (Table Constraints Linter)

**When to use**: Optional quality check for metadata authors to ensure taxonomy alignment.

**Note**: Linting checks are recommendations, not requirements. The Table Constraints specification does not define standardized linter checks.

## CLI Usage

### Basic Validation

To validate an xBRL-CSV file with Table Constraints:

```bash
# Report validation only (streaming, fast)
python arelleCmdLine.py --file report.json

# Validate metadata structure + report data
python arelleCmdLine.py --file report.json --tc-validate-metadata
```

### Validation-Only Mode (No Loading)

For large CSV files, you can perform streaming validation without loading the report into memory:

```bash
# Validate only, don't load report (saves memory and time)
python arelleCmdLine.py --file report.json --tc-only

# With metadata validation
python arelleCmdLine.py --file report.json --tc-only --tc-validate-metadata
```

**Use case**: Quick validation of large CSV reports (hundreds of MB) without consuming memory for full OIM loading.

**Limitation**: Cannot be combined with `--tc-lint` (which requires loading).

### Force Loading After Errors

By default, if Table Constraints validation fails, the report is not loaded. To override this:

```bash
# Load report even if validation fails
python arelleCmdLine.py --file report.json --tc-force-load --validate
```

**Use case**: Investigating validation errors by examining the loaded data model.

### Linting with Taxonomy Consistency Checks

To check metadata consistency with the taxonomy:

```bash
# Run linter (requires report to be loaded)
python arelleCmdLine.py --file report.json --tc-lint --validate

# Combine all validation types
python arelleCmdLine.py --file report.json \
  --tc-validate-metadata \
  --tc-lint \
  --validate
```

**Note**: Linting requires the taxonomy to be loaded, so it cannot be used with `--tc-only`.

### Complete Validation Pipeline

For comprehensive validation:

```bash
python arelleCmdLine.py \
  --file report.json \
  --tc-validate-metadata \
  --tc-lint \
  --validate \
  --logFile validation.log
```

This performs:
1. Pre-loading: Metadata + report validation (streaming)
2. Loading: Full OIM loading with taxonomy
3. Post-loading: Linter checks + standard XBRL validation

## GUI Usage

### Opening Table Constraints Options

1. Go to **Tools → Table Constraints Options**
2. Configure validation settings
3. Click **OK** to save

Settings are persisted across sessions.

### Option Descriptions

**Validate Table Constraints only (don't load report)**
- Performs streaming validation without loading
- Equivalent to `--tc-only`
- Useful for large CSV files
- Cannot be used with linting

**Load report even if there are Table Constraints errors**
- Equivalent to `--tc-force-load`
- Allows examining data despite validation errors
- Useful for debugging

**Validate Table Constraints metadata structure**
- Equivalent to `--tc-validate-metadata`
- Checks metadata for structural errors
- Recommended for metadata authors

**Run Table Constraints linter (check taxonomy consistency)**
- Equivalent to `--tc-lint`
- Requires report to be loaded
- Produces non-normative warnings
- Checks metadata consistency with taxonomy

### Workflow Example

**For Metadata Authors:**
1. Enable "Validate Table Constraints metadata structure"
2. Enable "Run Table Constraints linter"
3. Load your xBRL-CSV file
4. Review `tcme:*` and `tcl:*` messages

**For Report Submitters:**
1. Keep default settings (report validation only)
2. Load and validate your report
3. Review `tcre:*` error messages
4. Fix errors and revalidate

**For Large Files:**
1. Enable "Validate Table Constraints only"
2. Load the file (validation runs, report not loaded)
3. Check for errors in log
4. Once clean, disable and perform full loading

## Error Codes Reference

### tcme:* - Metadata Errors (Normative)

Metadata validation errors indicate structural problems in the Table Constraints metadata JSON.

Common errors:
- `tcme:invalidJSON` - Malformed JSON
- `tcme:missingProperty` - Required property missing
- `tcme:invalidType` - Property has wrong type
- `tcme:invalidReference` - Reference to non-existent element
- `tcme:invalidColumnOrder` - Column order constraint invalid

**Impact**: Metadata must be fixed before reports can be validated.

### tcre:* - Report Errors (Normative)

Report validation errors indicate CSV data does not meet constraint requirements.

Common errors:
- `tcre:typeViolation` - Value doesn't match declared type
- `tcre:allowedValuesViolation` - Value not in allowedValues list
- `tcre:minValueViolation` - Value below minimum
- `tcre:maxValueViolation` - Value exceeds maximum
- `tcre:uniqueKeyViolation` - Duplicate key values
- `tcre:foreignKeyViolation` - Foreign key reference not found
- `tcre:sortOrderViolation` - Rows not in required sort order
- `tcre:minTableRowsViolation` - Too few rows in table
- `tcre:maxTableRowsViolation` - Too many rows in table

**Impact**: Report data must be corrected before submission.

### tcl:* - Linter Warnings (Non-Normative)

Linter warnings suggest potential inconsistencies between metadata and taxonomy.

Common warnings:
- `tcl:inconsistentType` - Constraint type doesn't match taxonomy type
- `tcl:invalidAllowedValue` - Allowed value invalid for taxonomy type

**Impact**: Recommendations only. Reports are valid but metadata may have quality issues.

**Note**: These are Arelle-specific checks. The Table Constraints specification does not define standardized linter error codes.

## Use Cases

### Use Case 1: Quick Validation Without Loading

**Scenario**: You have a 500MB CSV file and want to quickly check for constraint violations.

**Solution**:
```bash
python arelleCmdLine.py --file large-report.json --tc-only
```

**Benefits**:
- Constant memory usage (streaming validation)
- Fast execution (no taxonomy loading)
- Immediate feedback on data quality

### Use Case 2: Metadata Development with Linting

**Scenario**: You're developing Table Constraints metadata and want to ensure taxonomy consistency.

**Solution**:
```bash
python arelleCmdLine.py \
  --file test-report.json \
  --tc-validate-metadata \
  --tc-lint \
  --validate
```

**Benefits**:
- Structural validation (`tcme:*`)
- Taxonomy consistency checks (`tcl:*`)
- Full XBRL validation
- Catch issues early in development

### Use Case 3: Production Report Submission

**Scenario**: Submitting a report to a regulator with Table Constraints requirements.

**Solution**:
```bash
python arelleCmdLine.py \
  --file submission.json \
  --tc-validate-metadata \
  --validate \
  --logFile submission-validation.log
```

**Benefits**:
- Complete validation coverage
- Detailed error log for debugging
- Both constraint and XBRL validation

### Use Case 4: Debugging Validation Errors

**Scenario**: Report has validation errors and you need to examine the loaded data model.

**Solution**:
```bash
python arelleCmdLine.py \
  --file problematic-report.json \
  --tc-force-load \
  --validate
```

**Benefits**:
- Report loads despite constraint errors
- Can examine facts, contexts, units
- Can use GUI tools for inspection

## Architecture Notes

### Pre-loading vs Post-loading Validation

Table Constraints validation happens at two stages:

**Pre-loading (Streaming)**
- Runs **before** OIM loading
- Validates: Metadata structure, CSV data
- Error codes: `tcme:*`, `tcre:*`
- Memory: Constant (streaming)
- Options: `--tc-only`, `--tc-validate-metadata`

**Post-loading (Linter)**
- Runs **after** OIM loading completes
- Validates: Metadata/taxonomy consistency
- Warning codes: `tcl:*`
- Memory: Full taxonomy in memory
- Options: `--tc-lint`

### Streaming Validation

Report validation uses streaming to process CSV files:
- One row at a time
- Constant memory usage (O(1) not O(n))
- Efficient for large files (GB+)
- No limit on file size

**Technical details**:
- Uses Python's `csv.DictReader`
- Maintains only current row in memory
- Key indexes stored for foreign key validation
- Sort state tracked for order validation

### Memory Considerations

| Validation Mode | Memory Usage | File Size Limit |
|-----------------|--------------|-----------------|
| `--tc-only` | Constant | None (streaming) |
| Normal loading | Proportional to data | System memory |
| With `--tc-lint` | Taxonomy + data | System memory |

For very large CSV files (>1GB), use `--tc-only` for validation without loading.

## Troubleshooting

### "Cannot use --tc-only with --tc-lint"

**Cause**: These options are incompatible. `--tc-only` prevents loading, but `--tc-lint` requires the taxonomy to be loaded.

**Solution**: Remove one of the options:
- For fast validation: Use only `--tc-only`
- For linting: Remove `--tc-only`, use `--tc-lint` with `--validate`

### Linter produces no warnings

**Possible causes**:
1. **Linter not enabled**: Add `--tc-lint` flag
2. **Simple column types**: Linter only checks columns with fixed concepts/dimensions
3. **No taxonomy loaded**: Linter requires taxonomy from metadata

**Verify linter is running**: Look for "Running Table Constraints linter..." in status messages.

### Validation is slow

**If using `--tc-only`**: Streaming validation should be fast. Check:
- Disk I/O speed
- CSV file structure (malformed CSV?)
- Number of unique keys (memory for key indexes)

**If not using `--tc-only`**: Slowness likely from OIM loading, not Table Constraints. Consider:
- Use `--tc-only` for faster validation
- Optimize taxonomy caching
- Use faster storage (SSD)

## Related Resources

- [XBRL Table Constraints Specification](https://www.xbrl.org/Specification/table-constraints/)
- [xBRL-CSV Specification](https://www.xbrl.org/Specification/xbrl-csv/)
- [Command Line Reference](../command_line.md)

## See Also

- [Fact Deduplication](fact_deduplication.md) - Related data quality feature
- [Command Line Usage](../command_line.md) - Complete CLI reference
