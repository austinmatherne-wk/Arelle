# SEC EDGAR Validation

:::{index} SEC EDGAR Validation
:::

This guide covers validating XBRL filings for the U.S. Securities and Exchange Commission (SEC)
Electronic Data Gathering, Analysis, and Retrieval (EDGAR) system.

## Overview

SEC filers must submit financial statements in Inline XBRL format. Arelle validates these
filings against the Edgar Filer Manual (EFM) requirements and SEC-specific rules.

## Required Components

### EDGAR Plugin

The EDGAR validation functionality requires the EDGAR plugin, which is included in the
[prepackaged distributions][install]. For pip installations:

```bash
pip install arelle-release[EFM]
```

The EDGAR plugin provides:
- EFM validation rules
- SEC-specific rendering
- XULE/DQC rules integration

### Taxonomy Packages

SEC filings reference US GAAP, SEC, and other taxonomies. Ensure you have the appropriate
[taxonomy packages][taxonomy-packages] installed for your filing year.

## Disclosure Systems

The EDGAR plugin provides several disclosure systems:

| Disclosure System | Description |
|-------------------|-------------|
| `efm-pragmatic` | Recommended for most filings. Reports errors that would cause rejection. |
| `efm-strict` | All EFM rules including warnings and style issues. |
| `efm-pragmatic-all-years` | Pragmatic mode supporting all US GAAP taxonomy years. |
| `efm-strict-all-years` | Strict mode supporting all US GAAP taxonomy years. |

**Recommendation**: Use `efm-pragmatic` for production validation to catch rejection-causing
errors. Run `efm-strict` optionally for quality checks.

## Basic Validation

### Single Document

```bash
arelleCmdLine \
  --plugins=EDGAR \
  --disclosureSystem=efm-pragmatic \
  --file filing.htm \
  --validate
```

### Filing Package (ZIP)

```bash
arelleCmdLine \
  --plugins=EDGAR \
  --disclosureSystem=efm-pragmatic \
  --file filing-package.zip \
  --validate
```

## Multi-Instance Filings

SEC filings often contain multiple Inline XBRL documents (e.g., 8-K with exhibits).
Use JSON syntax to specify the document set:

### 8-K with EX-98 Exhibit

```bash
arelleCmdLine --plugins=EDGAR --disclosureSystem=efm-pragmatic --file '[
  {
    "file": "form8k.htm",
    "submissionType": "8-K",
    "attachmentDocumentType": "8-K"
  },
  {
    "file": "ex98.htm",
    "submissionType": "8-K",
    "exhibitType": "EX-98",
    "attachmentDocumentType": "EX-98"
  }
]' --validate
```

### 10-K with Multiple Documents

```bash
arelleCmdLine --plugins=EDGAR --disclosureSystem=efm-pragmatic --file '[
  {
    "file": "form10k.htm",
    "submissionType": "10-K",
    "attachmentDocumentType": "10-K"
  },
  {
    "file": "form10k-2.htm",
    "submissionType": "10-K",
    "attachmentDocumentType": "10-K"
  }
]' --validate
```

For more details on multi-document syntax, see the [Multi-Instance Documents Guide][multi-instance].

## DQC Rules (Data Quality Committee)

The SEC uses XBRL US Data Quality Committee (DQC) rules for additional validation.
These are included in the EDGAR plugin via XULE integration.

DQC rules check for:
- Incorrect use of concepts
- Missing required disclosures
- Calculation inconsistencies
- Common tagging errors

DQC validation runs automatically when using EFM disclosure systems.

## GUI Validation

1. Load your filing document(s) via `File` > `Open`
2. Go to `Tools` > `Validation` > `Select Disclosure System`
3. Choose `efm-pragmatic` or `efm-strict`
4. Enable the EDGAR plugin via `Help` > `Manage plug-ins` if not loaded
5. Run validation via `Tools` > `Validation` > `Validate`

## Output and Rendering

### Validation Log

Save validation results to a file:

```bash
arelleCmdLine \
  --plugins=EDGAR \
  --disclosureSystem=efm-pragmatic \
  --file filing.htm \
  --validate \
  --logFile=validation-results.xml \
  --logFormat="[%(messageCode)s] %(message)s"
```

### EDGAR Renderer Output

Generate SEC-style rendered output:

```bash
arelleCmdLine \
  --plugins=EDGAR \
  --disclosureSystem=efm-pragmatic \
  --file filing.htm \
  --validate \
  --report=/output/directory/
```

### iXBRL Viewer

Create an interactive viewer for the filing:

```bash
arelleCmdLine \
  --plugins="EDGAR|iXBRLViewerPlugin" \
  --disclosureSystem=efm-pragmatic \
  --file filing.htm \
  --validate \
  --save-viewer viewer-output/
```

## Common EFM Errors

### EFM.6.5.x - Invalid Element Reference

**Cause**: Filing uses deprecated or invalid taxonomy elements.

**Solution**: Update to use current taxonomy concepts. Check the SEC's taxonomy change
documentation for deprecated elements.

### EFM.6.6.x - Context/Unit Issues

**Cause**: Context dates don't align with filing period, or units are incorrectly defined.

**Solution**: Verify context periods match the reporting period. Ensure units follow
SEC requirements (e.g., correct ISO currency codes).

### EFM.6.12.x - Calculation Inconsistencies

**Cause**: Reported values don't sum correctly according to calculation linkbase.

**Solution**: Review the flagged calculations. Note that XBRL allows legitimate
rounding differences within the specified decimals precision.

### DQC Rule Errors

DQC errors are identified by codes like `DQC.US.0001`. Each rule has specific
guidance on the XBRL US website for resolution.

## Offline Validation

For air-gapped environments or consistent validation:

```bash
arelleCmdLine \
  --plugins=EDGAR \
  --disclosureSystem=efm-pragmatic \
  --packages=/path/to/us-gaap-packages/ \
  --internetConnectivity=offline \
  --file filing.htm \
  --validate
```

## Resources

- [SEC EDGAR Filer Manual](https://www.sec.gov/info/edgar/edmanuals.htm)
- [SEC Taxonomy Information](https://www.sec.gov/info/edgar/edgartaxonomies.shtml)
- [XBRL US DQC Rules](https://xbrl.us/dqc-rules/)
- [EDGAR Plugin Documentation][edgar-plugin]

[install]: project:install.md
[taxonomy-packages]: project:user_guides/taxonomy_packages.md
[multi-instance]: project:user_guides/multi_instance.md
[edgar-plugin]: project:plugins/popular/edgar.md
