# Arelle iXBRL Viewer

:::{index} Arelle iXBRL Viewer
:::

## Overview

The [Arelle iXBRL Viewer][github] is an interactive tool developed by the Arelle team for viewing Inline XBRL (iXBRL)
reports in web browsers. It enables users to access and interact with XBRL data embedded in iXBRL reports. This viewer
is designed with extensibility in mind, allowing users to adapt it to their needs.

## Key Features

- **Interactive Viewing**: Experience interactive viewing of iXBRL reports in any web browser.
- **Data Accessibility**: Easily access the XBRL data embedded within iXBRL reports.
- **Global Usage**: Adapted and customized by various service providers and regulators.

## Installation

The iXBRL Viewer plugin is included in the [prepackaged distributions][install]. For pip installations:

```bash
pip install ixbrl-viewer
```

## Command Line Usage

### Basic Usage

To create an `ixbrl-viewer.htm` viewer file:

```bash
arelleCmdLine --plugins=iXBRLViewerPlugin --file filing.htm --save-viewer ixbrl-viewer.htm
```

### Output Options

The `--save-viewer` parameter accepts either a file path or a directory:

**Single file output** (for single-document filings):
```bash
arelleCmdLine --plugins=iXBRLViewerPlugin --file filing.htm --save-viewer viewer.htm
```

**Directory output** (required for multi-document filings):
```bash
arelleCmdLine --plugins=iXBRLViewerPlugin --file filing.zip --save-viewer viewer-output/
```

When using a directory, the viewer creates multiple files including the HTML viewer
and supporting JavaScript/JSON data files.

### With Validation

Combine viewer generation with validation:

```bash
arelleCmdLine \
  --plugins="EDGAR|iXBRLViewerPlugin" \
  --disclosureSystem=efm-pragmatic \
  --file filing.htm \
  --validate \
  --save-viewer viewer.htm
```

### Multi-Document Filings

For document sets, always use a directory for output:

```bash
arelleCmdLine \
  --plugins=iXBRLViewerPlugin \
  --file '[{"ixds":[{"file":"doc1.htm"},{"file":"doc2.htm"}]}]' \
  --save-viewer viewer-output/
```

### From ZIP Package

Process a filing package and generate a viewer:

```bash
arelleCmdLine --plugins=iXBRLViewerPlugin --file filing-package.zip --save-viewer viewer-output/
```

## Viewing the Output

The generated viewer is an HTML file that requires a web server to function properly
(due to browser security restrictions on local file access).

**Using Python's built-in server**:
```bash
cd viewer-output/
python -m http.server 8000
# Then open http://localhost:8000 in your browser
```

**Using Node.js**:
```bash
npx serve viewer-output/
```

**Using other servers**: Any web server (Apache, nginx, etc.) can serve the viewer files.

## GUI Usage

The Arelle iXBRL Viewer can also be configured and utilized via the graphical user interface (GUI):

1. Load an Inline XBRL document via `File` > `Open`
2. Navigate to `Tools` > `iXBRL Viewer`
3. Choose output location and options
4. Generate the viewer

## Troubleshooting

### Viewer Shows Facts But No Labels/Details

**Cause**: Taxonomy files couldn't be loaded during viewer generation.

**Solution**: Ensure the appropriate [taxonomy packages][taxonomy-packages] are installed:
```bash
arelleCmdLine \
  --plugins=iXBRLViewerPlugin \
  --packages=/path/to/taxonomy-packages/ \
  --file filing.htm \
  --save-viewer viewer.htm
```

### Viewer Won't Load in Browser

**Cause**: Browsers block local file access for security reasons.

**Solution**: Serve the viewer through a web server (see "Viewing the Output" above).

### Blank or Error Page

**Cause**: JavaScript files not found or path issues.

**Solution**: When processing multi-document filings, use a directory path for `--save-viewer`
instead of a single file path.

## Additional Resources

For a comprehensive list of options and advanced features, please refer to the [project readme][readme].

[github]: https://github.com/Arelle/ixbrl-viewer
[readme]: https://github.com/Arelle/ixbrl-viewer/blob/master/README.md
[install]: project:../../install.md
[taxonomy-packages]: project:../../user_guides/taxonomy_packages.md
