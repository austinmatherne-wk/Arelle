# Inline XBRL Document Set

:::{index} Inline XBRL Document Set
:::

## Overview

The Inline XBRL Document Set plugin enables Arelle to process multiple Inline XBRL documents
as a single logical unit, producing a single target XBRL instance. This is essential for
multi-document filings like SEC submissions where a single report spans multiple HTML files.

:::{autodoc2-docstring} arelle.plugin.inlineXbrlDocumentSet
:::

## Command Line Usage

### Basic Document Set

To specify an Inline XBRL Document Set, use JSON syntax with the `--file` parameter:

```bash
arelleCmdLine --file '[{"ixds":[{"file":"doc1.htm"},{"file":"doc2.htm"}]}]' --validate
```

### SEC Multi-Instance Filing

For SEC filings with exhibits (like 8-K forms with EX-98 exhibits), specify submission metadata:

```bash
arelleCmdLine --file '[
  {
    "file": "primary-8k.htm",
    "submissionType": "8-K",
    "attachmentDocumentType": "8-K"
  },
  {
    "file": "ex98-exhibit.htm",
    "submissionType": "8-K",
    "exhibitType": "EX-98",
    "attachmentDocumentType": "EX-98"
  }
]' --validate --efm
```

### JSON Format Reference

The `--file` parameter accepts JSON with the following structure:

**Document Set Format (ixds)**:
```json
[{"ixds": [{"file": "file1.htm"}, {"file": "file2.htm"}]}]
```

**SEC Multi-Instance Format**:
```json
[
  {
    "file": "filename.htm",
    "submissionType": "10-K",
    "attachmentDocumentType": "10-K"
  }
]
```

**Common Properties**:

| Property | Description |
|----------|-------------|
| `file` | Path to the iXBRL document |
| `submissionType` | SEC form type (8-K, 10-K, 10-Q, etc.) |
| `attachmentDocumentType` | Document type within submission |
| `exhibitType` | Exhibit type (EX-98, EX-99.1, etc.) |

### Tips for JSON on Command Line

**Windows (cmd)**:
```cmd
arelleCmdLine --file "[{\"ixds\":[{\"file\":\"doc1.htm\"},{\"file\":\"doc2.htm\"}]}]"
```

**Windows (PowerShell)**:
```powershell
arelleCmdLine --file '[{\"ixds\":[{\"file\":\"doc1.htm\"},{\"file\":\"doc2.htm\"}]}]'
```

**Linux/macOS**:
```bash
arelleCmdLine --file '[{"ixds":[{"file":"doc1.htm"},{"file":"doc2.htm"}]}]'
```

## GUI Usage

In the GUI, you can load document sets by:
1. Opening the primary document
2. Using `File` > `Open Additional...` to add related documents
3. Or loading a manifest/index file that references all documents

## Related

- [Multi-Instance Documents Guide][multi-instance] - Comprehensive guide to multi-document filings
- [EDGAR Guide][edgar] - SEC-specific validation and filing requirements

[multi-instance]: project:../user_guides/multi_instance.md
[edgar]: project:../edgar.md
