from pathlib import Path, PurePath

from arelle.plugin import inlineXbrlDocumentSet
from tests.integration_tests.validation.conformance_suite_config import (
    ConformanceSuiteAssetConfig,
    ConformanceSuiteConfig,
)

config = ConformanceSuiteConfig(
    # plugins=frozenset(["inlineXbrlDocumentSet"]),
    args=[
        "--reportPackage"
    ],
    assets=[
        ConformanceSuiteAssetConfig.conformance_suite(
            Path("report-package-conformance.zip"),
            entry_point=Path("report-package-conformance/index.csv"),
        ),
    ],
    expected_additional_testcase_errors={f"report-package-conformance/index.csv:{s}": val for s, val in {
        # Report package references a taxonomy which does not exist.
        "V-701-zip-with-no-taxonomy": frozenset({"IOerror", "oime:invalidTaxonomy"}),
        # Empty html report templates raise schema validation errors.
        "V-301-xbri-with-single-ixds": frozenset({"ix11.14.1.2:missingResources", "lxml.SCHEMAV_ELEMENT_CONTENT"}),
    }.items()},
    info_url="https://specifications.xbrl.org/work-product-index-taxonomy-packages-report-packages-1.0.html",
    membership_url="https://www.xbrl.org/join",
    name=PurePath(__file__).stem,
    network_or_cache_required=False,
    shards=2,
)
