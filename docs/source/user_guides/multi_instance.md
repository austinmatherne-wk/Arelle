# Multi-Instance Documents

:::{index} Multi-Instance Documents
:::

This guide explains how to work with multi-document Inline XBRL filings, including
IXDS (Inline XBRL Document Sets) and SEC multi-instance submissions.

## Understanding Multi-Document Filings

### What is an IXDS?

An Inline XBRL Document Set (IXDS) consists of multiple HTML/XHTML files that together
represent a single XBRL instance. Key characteristics:

- All documents share the same target instance
- Facts from all documents combine into one logical report
- Contexts and units are shared across documents
- Common in regulatory filings that span multiple pages

### IXDS vs. Separate Instances

| Scenario | Type | Example |
|----------|------|---------|
| Multi-page 10-K | IXDS | Primary filing + continuation pages |
| 8-K with exhibits | Multi-instance | Main filing + separate exhibit instances |
| ESEF report | Single or IXDS | Depends on structure |

**Key distinction**: In an IXDS, all documents produce *one* target instance.
Multi-instance filings (like SEC 8-K with EX-98) contain *separate* XBRL instances.

## Specifying Document Sets

### JSON Syntax Overview

Use JSON with the `--file` parameter to specify multiple documents:

```bash
arelleCmdLine --file '[JSON_STRUCTURE]' --validate
```

### IXDS Format

For documents that combine into a single instance:

```bash
arelleCmdLine --file '[{"ixds":[{"file":"doc1.htm"},{"file":"doc2.htm"},{"file":"doc3.htm"}]}]' --validate
```

### SEC Multi-Instance Format

For SEC filings with separate instances (e.g., 8-K with exhibits):

```bash
arelleCmdLine --file '[
  {"file":"form8k.htm","submissionType":"8-K","attachmentDocumentType":"8-K"},
  {"file":"ex98.htm","submissionType":"8-K","exhibitType":"EX-98","attachmentDocumentType":"EX-98"}
]' --validate --efm
```

## Common Filing Scenarios

### SEC 10-K (Multi-Page)

A 10-K that spans multiple HTML files as a single document set:

```bash
arelleCmdLine --plugins=EDGAR --disclosureSystem=efm-pragmatic --file '[
  {"ixds": [
    {"file": "form10k-part1.htm"},
    {"file": "form10k-part2.htm"},
    {"file": "form10k-part3.htm"}
  ]}
]' --validate
```

### SEC 8-K with EX-98 (Separate Instances)

An 8-K with a separate XBRL-tagged exhibit:

```bash
arelleCmdLine --plugins=EDGAR --disclosureSystem=efm-pragmatic --file '[
  {
    "file": "form8k.htm",
    "submissionType": "8-K",
    "attachmentDocumentType": "8-K"
  },
  {
    "file": "ex98-tagging.htm",
    "submissionType": "8-K",
    "exhibitType": "EX-98",
    "attachmentDocumentType": "EX-98"
  }
]' --validate
```

### SEC 10-Q with Cover Page

A quarterly report where the cover page is in a separate file:

```bash
arelleCmdLine --plugins=EDGAR --disclosureSystem=efm-pragmatic --file '[
  {"ixds": [
    {"file": "coverpage.htm"},
    {"file": "form10q.htm"}
  ]}
]' --validate
```

### ESEF Multi-Page Report

An ESEF annual report across multiple pages:

```bash
arelleCmdLine --disclosureSystem=esef-2024 --file '[
  {"ixds": [
    {"file": "report-page1.xhtml"},
    {"file": "report-page2.xhtml"},
    {"file": "report-page3.xhtml"}
  ]}
]' --validate
```

## JSON Properties Reference

### Document Properties

| Property | Description | Required |
|----------|-------------|----------|
| `file` | Path to the document file | Yes |
| `submissionType` | SEC form type (10-K, 10-Q, 8-K, etc.) | SEC filings |
| `attachmentDocumentType` | Document type within submission | SEC filings |
| `exhibitType` | Exhibit identifier (EX-98, EX-99.1, etc.) | SEC exhibits |

### IXDS Properties

| Property | Description |
|----------|-------------|
| `ixds` | Array of document objects forming a single instance |

## Platform-Specific JSON Tips

### Windows Command Prompt (cmd)

Escape double quotes with backslashes:

```cmd
arelleCmdLine --file "[{\"ixds\":[{\"file\":\"doc1.htm\"},{\"file\":\"doc2.htm\"}]}]" --validate
```

### Windows PowerShell

Use single quotes for the outer string:

```powershell
arelleCmdLine --file '[{\"ixds\":[{\"file\":\"doc1.htm\"},{\"file\":\"doc2.htm\"}]}]' --validate
```

### Linux/macOS Bash

Single quotes work without escaping:

```bash
arelleCmdLine --file '[{"ixds":[{"file":"doc1.htm"},{"file":"doc2.htm"}]}]' --validate
```

### Using a JSON File

For complex structures, put the JSON in a file:

```bash
# Create filing-structure.json with your document specification
arelleCmdLine --file "$(cat filing-structure.json)" --validate
```

## Generating Output

### Extracted Instance

Save the combined XBRL instance from an IXDS:

```bash
arelleCmdLine --file '[{"ixds":[{"file":"doc1.htm"},{"file":"doc2.htm"}]}]' \
  --validate \
  --saveInstance extracted-instance.xml
```

### iXBRL Viewer for Document Set

When generating a viewer for multi-document filings, specify a directory:

```bash
arelleCmdLine --plugins=iXBRLViewerPlugin \
  --file '[{"ixds":[{"file":"doc1.htm"},{"file":"doc2.htm"}]}]' \
  --save-viewer viewer-output/
```

## Common Mistakes

### 1. Using IXDS When Instances Are Separate

**Wrong**: Treating an 8-K and its EX-98 exhibit as one IXDS:
```bash
# INCORRECT - these are separate instances, not one document set
--file '[{"ixds":[{"file":"form8k.htm"},{"file":"ex98.htm"}]}]'
```

**Correct**: Specify them as separate instances with SEC metadata:
```bash
--file '[{"file":"form8k.htm",...},{"file":"ex98.htm",...}]'
```

### 2. Missing Submission Metadata for SEC Filings

**Wrong**: Omitting required SEC metadata:
```bash
--file '[{"file":"form8k.htm"},{"file":"ex98.htm"}]'
```

**Correct**: Include `submissionType` and `attachmentDocumentType`:
```bash
--file '[{"file":"form8k.htm","submissionType":"8-K","attachmentDocumentType":"8-K"}]'
```

### 3. Incorrect Quote Escaping

JSON errors often stem from incorrect quoting. Test your JSON structure
separately before running the full command.

## GUI Usage

In the Arelle GUI:

1. **Open Primary Document**: `File` > `Open` and select the main document
2. **Add Additional Documents**: `File` > `Import` to add related files to the DTS
3. **For SEC Multi-Instance**: Load each instance separately for validation

The GUI automatically handles document sets when loading from a ZIP package
that contains the appropriate manifest.

## Related

- [Inline XBRL Document Set Plugin][ixds-plugin] - Plugin reference
- [EDGAR Guide][edgar] - SEC-specific validation
- [Command Line Reference][cli] - All CLI options

[ixds-plugin]: project:../plugins/popular/inline_xbrl_document_set.md
[edgar]: project:../edgar.md
[cli]: project:../command_line.md
