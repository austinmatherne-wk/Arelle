# FAQ

:::{index} FAQ
:::

## Why Won't Arelle Open?

Running into trouble opening Arelle? It might be a pesky corrupt configuration or
a missing installation file causing the problem. Don't worry! Usually, a [clean install][clean-install]
will set things straight. If that doesn't do the trick, please don't hesitate to
[report a bug][bug-report]. We're here to help, and we'll get to the bottom of it!

[bug-report]: project:index.md#bug-report-or-feature-request
[clean-install]: project:install.md#clean-install

## Why Am I Getting webCache:retrievalError?

This is one of the most common errors users encounter. It means Arelle tried to
download a file (usually a taxonomy schema) from the internet but failed. Common causes:

1. **Missing taxonomy package**: The taxonomy your report references isn't available
   online, or the URL has changed. Install the appropriate [taxonomy package][taxonomy-packages]
   for your jurisdiction.

2. **Network connectivity**: Check your internet connection and proxy settings.
   Use `--proxy=show` to see current proxy configuration.

3. **Firewall or security software**: Corporate firewalls may block Arelle's requests.
   Try using `--internetConnectivity=offline` with locally installed taxonomy packages.

4. **Temporary server issues**: The taxonomy host may be temporarily unavailable.
   Try again later or use offline mode with packages.

For detailed guidance, see the [Taxonomy Packages Guide][taxonomy-packages] and
[Troubleshooting Guide][troubleshooting].

[taxonomy-packages]: project:user_guides/taxonomy_packages.md
[troubleshooting]: project:troubleshooting.md

## Which Disclosure System Should I Use?

Disclosure systems define validation rules for specific regulatory frameworks.
Run `--disclosureSystem=help` to see all available options.

Common choices:

| Jurisdiction | Disclosure System | Notes |
|--------------|-------------------|-------|
| **SEC (US)** | `efm-pragmatic` | Recommended for most SEC filings |
| **SEC (US)** | `efm-strict` | Stricter validation |
| **ESEF (EU)** | `esef-2024` | Use year matching your filing |
| **HMRC (UK)** | `hmrc` | UK tax filings |

**Pragmatic vs Strict**: Pragmatic modes are more lenient and focus on errors that
would cause filing rejection. Strict modes catch additional warnings and style issues.

See the [ESEF Guide][esef] or [EDGAR Guide][edgar] for jurisdiction-specific details.

[esef]: project:esef.md
[edgar]: project:edgar.md

## How Do I Validate Offline?

Use `--internetConnectivity=offline` along with installed [taxonomy packages][taxonomy-packages]:

```bash
arelleCmdLine --file report.xbrl --validate --internetConnectivity=offline --packages=/path/to/packages/
```

This is useful when:
- Working in air-gapped environments
- Ensuring consistent validation across runs
- Avoiding dependency on external servers

## How Do I Validate Multiple Files Together?

For multi-document filings (like SEC Inline XBRL document sets), use JSON syntax
with the `--file` parameter. See the [Multi-Instance Documents Guide][multi-instance]
for detailed examples.

[multi-instance]: project:user_guides/multi_instance.md

## Why Am I Getting a Validation Error or Warning?

Disagree with an Arelle validation? Open a [change request][change-request] with
a document that triggers the rule and we'll take a look. Some jurisdiction based
validation rules are open to interpretation. In these cases we defer to the community
for consensus.

[change-request]: project:index.md#bug-report-or-feature-request

## Can I Optimize Validation Performance?

By default, Arelle validates the complete DTS (discoverable taxonomy set).
However, you can improve performance in cases where validating the entire
taxonomy set isn't necessary. For instance, when validating reports against a
known-valid taxonomy like US GAAP 2024, you may only need to validate your
report's documents rather than validating the base taxonomy.

To optimize performance in such cases:

- CLI: Use the `--baseTaxonomyValidation=none` option
- GUI: From the `Tools` menu select `Validation` then `Base taxonomy validation`
  and finally select `Don't validate any base files`.

This optimization is particularly useful for service providers who regularly
validate reports against standard taxonomies, reducing validation time while
maintaining the integrity of report-specific validation.

## Why Are Concept Details Missing From the Viewer?

Concept details missing from the Arelle ixbrl-viewer or Edgar Renderer? Check the
Arelle log for download errors. If Arelle can't download the referenced taxonomy
and schemas that define those concept details the viewers will fail to render them.

This typically means you need to install the appropriate [taxonomy package][taxonomy-packages]
for the taxonomies your report references.

## Is There a Newer Version of Arelle Available?

New versions of Arelle are typically released multiple times per week. If you're
using one of the [prepackaged distributions][prepackaged-distributions]
you can check for and install updates from the Help menu in the GUI.

[prepackaged-distributions]: project:install.md#prepackaged-distributions
