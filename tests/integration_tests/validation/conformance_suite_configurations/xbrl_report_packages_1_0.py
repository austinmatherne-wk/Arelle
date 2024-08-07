from pathlib import Path, PurePath

from tests.integration_tests.validation.conformance_suite_config import (
    ConformanceSuiteAssetConfig,
    ConformanceSuiteConfig,
)

config = ConformanceSuiteConfig(
    args=[
        "--reportPackage"
    ],
    assets=[
        ConformanceSuiteAssetConfig.conformance_suite(
            Path("report-package-conformance.zip"),
            entry_point=Path("report-package-conformance/index.csv"),
        ),
    ],
    expected_failure_ids=frozenset(f"report-package-conformance/index.csv:{s}" for s in [
        # Refers to nonexistent taxonomy which triggers IOError and oime:invalidTaxonomy.
        "V-701-zip-with-no-taxonomy",
    ]),
    info_url="https://specifications.xbrl.org/work-product-index-taxonomy-packages-report-packages-1.0.html",
    membership_url="https://www.xbrl.org/join",
    name=PurePath(__file__).stem,
    network_or_cache_required=False,
    plugins=frozenset({'inlineXbrlDocumentSet'}),
)
