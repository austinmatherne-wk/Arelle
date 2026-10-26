# Arelle Conformance Suites Manual Run

Download the suites into the root of the Arelle repository and run every command
from there. Each command reads its suite from the repository root and writes a
log and a CSV test report to the repository root, named after the suite.
For example, the XBRL 2.1 command writes `xbrl-2.1.log` and `xbrl-2.1.csv`.

## Arelle Version

Verified against Arelle [2.47.3](https://github.com/Arelle/Arelle/releases/tag/2.47.3).

## Run on Other Platforms

From Python source, the commands below are the same on Linux, macOS, and Windows.

The commands are split across lines with a trailing `\`, which works in bash and zsh.
In Windows Command Prompt, replace each trailing `\` with `^`.
In PowerShell, replace each trailing `\` with a backtick (`` ` ``).

From a frozen prepackaged build, still run from the folder that holds the suites,
which keeps the inputs and outputs there.

| Build | Replace `python arelleCmdLine.py` with |
| --- | --- |
| Linux | `/path/to/arelle/arelleCmdLine`, where `/path/to/arelle` is the folder the build archive extracted to |
| macOS | `/Applications/Arelle.app/Contents/MacOS/arelleCmdLine` |
| Windows | `"C:\Program Files\Arelle\arelleCmdLine.exe"` |

## Set up Python

Python 3.11-3.14 is currently supported. From the repository root, install the
runtime requirements.

```bash
python -m pip install -r requirements.txt
```

## Suites

Download each suite into the repository root.
The commands expect the filenames shown.

These commands run Arelle from source on Linux. Run them from the repository root.

### XBRL 2.1

[XBRL-CONF-2025-07-16.zip](https://www.xbrl.org/2025/XBRL-CONF-2025-07-16.zip)

```bash
python arelleCmdLine.py \
  --internetConnectivity offline \
  --logFile xbrl-2.1.log \
  --csvTestReport xbrl-2.1.csv \
  --validate \
  --calc xbrl21 \
  --file XBRL-CONF-2025-07-16.zip/XBRL-CONF-2025-07-16/xbrl.xml
```

### Dimensions 1.0

[XBRL-XDT-CONF-2025-09-09.zip](https://www.xbrl.org/2025/XBRL-XDT-CONF-2025-09-09.zip)

```bash
python arelleCmdLine.py \
  --internetConnectivity offline \
  --logFile dimensions-1.0.log \
  --csvTestReport dimensions-1.0.csv \
  --validate \
  --file XBRL-XDT-CONF-2025-09-09.zip/XBRL-XDT-CONF-2025-09-09/xdt.xml
```

### Inline XBRL 1.1

[inlineXBRL-1.1-conformanceSuite-2020-04-08.zip](https://www.xbrl.org/2020/inlineXBRL-1.1-conformanceSuite-2020-04-08.zip)

Arelle fails `baseURIs/PASS-baseURI-on-ix-references-multiRefs.xml` (V-1003) with
`xbrl:multipleTopLevelSchemasForNamespace`. The test references two unconnected
schemas for the same namespace, which the new XBRL 2.1 rule in
[base-spec#304](https://gitlab.xbrl.org/base-spec/base-spec/-/work_items/304) forbids.
The suite fix is in [ixbrl!28](https://gitlab.xbrl.org/base-spec/ixbrl/-/merge_requests/28).

```bash
python arelleCmdLine.py \
  --internetConnectivity offline \
  --logFile inline-xbrl-1.1.log \
  --csvTestReport inline-xbrl-1.1.csv \
  --validate \
  --plugins inlineXbrlDocumentSet \
  --requireInlineXbrl \
  --packages inlineXBRL-1.1-conformanceSuite-2020-04-08.zip/inlineXBRL-1.1-conformanceSuite-2020-04-08/schemas/www.example.com.zip \
  --file inlineXBRL-1.1-conformanceSuite-2020-04-08.zip/inlineXBRL-1.1-conformanceSuite-2020-04-08/index.xml
```

### Transformation Rules Registry v3

[trr-3.0.1+2019-04-17.zip](https://gitlab.xbrl.org/base-spec/trr/-/archive/3.0.1+2019-04-17/trr-3.0.1+2019-04-17.zip)

Extract the archive into the repository root and build
`trr-3.0.1+2019-04-17/conformance-tests/testcase.xml` as the suite instructs.

```bash
python arelleCmdLine.py \
  --internetConnectivity offline \
  --logFile transformation-registry-3.log \
  --csvTestReport transformation-registry-3.csv \
  --validate \
  --file trr-3.0.1+2019-04-17/conformance-tests/testcase.xml
```

### Transformation Rules Registry v4

[trr-4.0.zip](https://gitlab.xbrl.org/base-spec/trr/-/archive/4.0/trr-4.0.zip)


```bash
python arelleCmdLine.py \
  --internetConnectivity offline \
  --logFile transformation-registry-4.log \
  --csvTestReport transformation-registry-4.csv \
  --validate \
  --file trr-4.0.zip/trr-4.0/conformance-tests/testcase.xml
```

### Transformation Rules Registry v5

[trr-5.0.zip](https://gitlab.xbrl.org/base-spec/trr/-/archive/5.0/trr-5.0.zip)


```bash
python arelleCmdLine.py \
  --internetConnectivity offline \
  --logFile transformation-registry-5.log \
  --csvTestReport transformation-registry-5.csv \
  --validate \
  --file trr-5.0.zip/trr-5.0/conformance-tests/testcase.xml
```

### Calculations 1.1

[calculation-1.1-conformance-2024-02-14.zip](https://base-spec.ci.xbrl.org/calculations/1-1-0-rec1-calc11-2024-02-14/conformance/calculation-1.1-conformance-2024-02-14.zip)

```bash
python arelleCmdLine.py \
  --internetConnectivity offline \
  --logFile calculations-1.1.log \
  --csvTestReport calculations-1.1.csv \
  --validate \
  --testcaseResultsCaptureWarnings \
  --validateXmlOim \
  --file calculation-1.1-conformance-2024-02-14.zip/calculation-1.1-conformance-2024-02-14/index.xml
```

### Taxonomy Packages 1.0

[taxonomy-package-conformance.zip](https://base-spec.ci.xbrl.org/taxonomy-package/1-0-0-conf-2021-05-17/taxonomy-package-conformance.zip)

```bash
python arelleCmdLine.py \
  --internetConnectivity offline \
  --logFile taxonomy-packages-1.0.log \
  --csvTestReport taxonomy-packages-1.0.csv \
  --validate \
  --skipPackageContentLoading \
  --file taxonomy-package-conformance.zip/taxonomy-package-conformance/index.xml
```

### Report Packages 1.0

[report-package-conformance.zip](https://base-spec.ci.xbrl.org/report-package/1-0-1-rec-2025-03-11/report-package-conformance.zip)

```bash
python arelleCmdLine.py \
  --internetConnectivity offline \
  --logFile report-packages-1.0.log \
  --csvTestReport report-packages-1.0.csv \
  --validate \
  --reportPackage \
  --skipPackageContentLoading \
  --file report-package-conformance.zip/report-package-conformance/index.csv
```

### Extensible Enumerations 1.0

[extensible-enumerations-CONF-2014-10-29.zip](https://www.xbrl.org/2014/extensible-enumerations-CONF-2014-10-29.zip)

```bash
python arelleCmdLine.py \
  --internetConnectivity offline \
  --logFile extensible-enumerations-1.0.log \
  --csvTestReport extensible-enumerations-1.0.csv \
  --validate \
  --file extensible-enumerations-CONF-2014-10-29.zip/extensible-enumerations-CONF-2014-10-29/enumerations-index.xml
```

### Extensible Enumerations 2.0

[extensible-enumerations-2.0-2020-02-12.zip](https://base-spec.ci.xbrl.org/extensible-enumerations/2-0-0-2020-02-12/conformance/extensible-enumerations-2.0-2020-02-12.zip)

```bash
python arelleCmdLine.py \
  --internetConnectivity offline \
  --logFile extensible-enumerations-2.0.log \
  --csvTestReport extensible-enumerations-2.0.csv \
  --validate \
  --file extensible-enumerations-2.0-2020-02-12.zip/extensible-enumerations-2.0-2020-02-12/enumerations-index.xml
```

### Formula 1.0

[formula-conformance-2022-07-21.zip](https://xbrl.org/Specification/formula/REC-2011-10-24/conformance/formula-conformance-2022-07-21.zip)

```bash
python arelleCmdLine.py \
  --internetConnectivity offline \
  --logFile formula-1.0.log \
  --csvTestReport formula-1.0.csv \
  --validate \
  --file formula-conformance-2022-07-21.zip/formula-conformance-2022-07-21/index.xml
```

### Units Registry 1.0

[utr-conf-cr-2013-05-17.zip](https://www.xbrl.org/utr/utr-conf-cr-2013-05-17.zip)

```bash
python arelleCmdLine.py \
  --internetConnectivity offline \
  --logFile units-registry-1.0.log \
  --csvTestReport units-registry-1.0.csv \
  --validate \
  --utr \
  --file utr-conf-cr-2013-05-17.zip/utr-conf-cr-2013-05-17/2013-05-17/index.xml
```

### Units Registry 1.0 structure

[utr-structure-conf-cr-2013-11-18.zip](https://www.xbrl.org/2013/utr-structure-conf-cr-2013-11-18.zip)

```bash
python arelleCmdLine.py \
  --internetConnectivity offline \
  --logFile units-registry-structure-1.0.log \
  --csvTestReport units-registry-structure-1.0.csv \
  --validate \
  --utr \
  --utrUrl utr-structure-conf-cr-2013-11-18.zip/conf/utr-structure/utr-for-structure-conformance-tests.xml \
  --file utr-structure-conf-cr-2013-11-18.zip/conf/utr-structure/index.xml
```

### Open Information Model 1.0

[oim-conformance-2023-04-19.zip](https://oim.ci.xbrl.org/oim/1-0-1-rec-2023-04-19/conformance/oim-conformance-2023-04-19.zip)

Arelle fails `600-xml/index-xbrl-xml.xml` V-05 and V-06, which expect
`xbrlxe:unexpectedContextContent`. The tests check the container a dimension is
defined for rather than the one it's used in, as described in
[oim#615](https://gitlab.xbrl.org/oim/oim/-/work_items/615).

```bash
python arelleCmdLine.py \
  --internetConnectivity offline \
  --logFile oim-1.0.log \
  --csvTestReport oim-1.0.csv \
  --validate \
  --validateXmlOim \
  --file oim-conformance-2023-04-19.zip/oim-conformance-2023-04-19/oim-index.xml
```

### xBRL-CSV Table Constraints 1.0

[table-constraints-conformance-2026-09-10.zip](https://oim.ci.xbrl.org/oim/1-0-0-rec-table-constraints-2026-09-10/conformance/table-constraints-conformance-2026-09-10.zip)

```bash
python arelleCmdLine.py \
  --internetConnectivity offline \
  --logFile table-constraints-1.0.log \
  --csvTestReport table-constraints-1.0.csv \
  --validate \
  --testcaseResultsCaptureWarnings \
  --validateTableConstraintsSkipLoading \
  --file table-constraints-conformance-2026-09-10.zip/table-constraints-conformance-2026-09-10/table-constraints-index.xml
```

### Table Linkbase 1.0

[table-linkbase-conformance-2024-12-17.zip](https://www.xbrl.org/2024/table-linkbase-conformance-2024-12-17.zip)

Included only for completeness. Arelle doesn't pass the suite.

```bash
python arelleCmdLine.py \
  --internetConnectivity offline \
  --logFile table-linkbase-1.0.log \
  --csvTestReport table-linkbase-1.0.csv \
  --validate \
  --file table-linkbase-conformance-2024-12-17.zip/table-linkbase-conformance-2024-12-17/testcases-index.xml
```
