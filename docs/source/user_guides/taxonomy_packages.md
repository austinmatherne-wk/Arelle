# Taxonomy Packages

:::{index} Taxonomy Packages
:::

## What is a Taxonomy Package?

A taxonomy package is a ZIP archive that contains:

1. **Taxonomy files**: The XSD schemas and linkbase files that define concepts, labels,
   and relationships
2. **URL remapping rules**: Instructions that tell Arelle to use local files instead of
   downloading from remote URLs

**Important distinction**: A taxonomy package is *not* the same as a taxonomy. The package
*contains* taxonomy files and tells Arelle where to find them locally.

## Why Do You Need Taxonomy Packages?

When validating an XBRL report, Arelle needs access to the taxonomies referenced by that report.
By default, Arelle downloads these from the internet. Taxonomy packages help by:

- **Providing offline access**: Work without internet connectivity
- **Ensuring consistency**: Use specific versions of taxonomies
- **Avoiding download errors**: Bypass servers that may be slow or unavailable
- **Resolving URL changes**: Handle cases where taxonomy URLs have moved

If you see `webCache:retrievalError` messages, installing the appropriate taxonomy package
usually resolves the issue.

## Where to Get Taxonomy Packages

Obtain taxonomy packages from your regulatory authority or taxonomy publisher:

| Jurisdiction | Source |
|--------------|--------|
| **SEC (US)** | Contact SEC or use taxonomies bundled with EDGAR plugin |
| **ESEF (EU)** | ESMA website or your national competent authority |
| **HMRC (UK)** | HMRC developer resources |
| **EBA/EIOPA** | European Banking/Insurance Authority websites |
| **IFRS** | IFRS Foundation website |

Check your regulator's website for official taxonomy packages. Many provide packages specifically
formatted for use with XBRL processors like Arelle.

## Installing Taxonomy Packages

### GUI Installation

1. Go to `Help` > `Manage Packages`
2. Click `Add` or `Browse` to select a package ZIP file
3. The package will be installed and available for future sessions

### CLI Installation (Persistent)

To install packages for all future CLI runs:

```bash
# This saves the package configuration
arelleCmdLine --packages=/path/to/package.zip
```

### CLI Usage (Per-Run)

To use packages for a single validation run without installing:

```bash
arelleCmdLine --packages=/path/to/package.zip --file report.xbrl --validate
```

### Multiple Packages

Load multiple packages by separating paths with `|` or using multiple `--packages` flags:

```bash
# Using pipe separator
arelleCmdLine --packages="/path/to/pkg1.zip|/path/to/pkg2.zip" --file report.xbrl --validate

# Using multiple flags
arelleCmdLine --packages=/path/to/pkg1.zip --packages=/path/to/pkg2.zip --file report.xbrl --validate
```

### Loading All Packages in a Directory

Point to a directory to load all ZIP files within it:

```bash
arelleCmdLine --packages=/path/to/packages/ --file report.xbrl --validate
```

## Offline Validation

To validate completely offline, combine taxonomy packages with the offline connectivity flag:

```bash
arelleCmdLine \
  --packages=/path/to/packages/ \
  --internetConnectivity=offline \
  --file report.xbrl \
  --validate
```

This ensures Arelle doesn't attempt any network requests and relies entirely on local files.

## Package Structure

A taxonomy package typically contains:

```
package.zip
├── META-INF/
│   ├── catalog.xml          # URL remapping rules
│   └── taxonomyPackage.xml  # Package metadata
└── taxonomies/
    └── ...                   # Taxonomy schema and linkbase files
```

The `catalog.xml` file contains URL rewriting rules that map remote URLs to local paths:

```xml
<catalog xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">
  <rewriteURI uriStartString="http://example.com/taxonomy/"
              rewritePrefix="taxonomies/"/>
</catalog>
```

## Troubleshooting

### webCache:retrievalError

This error means Arelle couldn't download a required file. Solutions:

1. **Install the appropriate taxonomy package** for your report's jurisdiction
2. **Check network connectivity** if you're online
3. **Verify proxy settings** with `--proxy=show`
4. **Use offline mode** with packages: `--internetConnectivity=offline --packages=...`

### Package Not Found

If Arelle doesn't recognize your package:

1. Verify the ZIP file is not corrupted
2. Check that `META-INF/catalog.xml` exists inside the ZIP
3. Ensure the package format matches XBRL International's Taxonomy Package specification

### Wrong Taxonomy Version

If validation uses the wrong taxonomy version:

1. Check which packages are loaded (GUI: `Help` > `Manage Packages`)
2. Ensure you're loading the correct year's package
3. For multiple versions, load only the one matching your report

## Related

- [Installation Guide][install] - Initial Arelle setup
- [Troubleshooting Guide][troubleshooting] - Common error solutions
- [Command Line Reference][cli] - All CLI options including `--packages`

[install]: project:../install.md
[troubleshooting]: project:../troubleshooting.md
[cli]: project:../command_line.md
