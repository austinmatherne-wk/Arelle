from pathlib import Path, PurePath

from tests.integration_tests.validation.conformance_suite_config import (
    ConformanceSuiteAssetConfig,
    ConformanceSuiteConfig,
)

config = ConformanceSuiteConfig(
    args=["--tc-validate-metadata", "--tc-force-load"],
    expected_additional_testcase_errors={
        f"table-constraints-conformance-DRAFT-YYYY-MM-DD/{s}": val
        for s, val in {
            "720-tc-report-processor/index-tc-report-table.xml:V-30": {
                "xbrlce:invalidReferenceTarget": 1,
                "xbrlce:unmappedCellValue": 1,
            },
            "720-tc-report-processor/index-tc-report-table.xml:V-30c": {
                "oime:misplacedDecimalsProperty": 1,
            },
            "720-tc-report-processor/index-tc-report-table.xml:V-30d": {
                "oime:misplacedDecimalsProperty": 1,
            },
            "720-tc-report-processor/index-tc-report-table.xml:V-30e": {
                "oime:invalidXBRL": 1,
            },
            "720-tc-report-processor/index-tc-report-table.xml:V-30g": {
                "oime:misplacedDecimalsProperty": 1,
            },
            "720-tc-report-processor/index-tc-report-table.xml:V-30h": {
                "oime:misplacedDecimalsProperty": 1,
            },
            "720-tc-report-processor/index-tc-report-table.xml:V-39b": {
                "oime:invalidXBRL": 1,
            },
            "720-tc-report-processor/index-tc-report-table.xml:V-39c": {
                "oime:invalidXBRL": 1,
            },
            "720-tc-report-processor/index-tc-report-table.xml:V-548-8": {
                "oime:invalidXBRL": 1,
            },
        }.items()
    },
    assets=[
        ConformanceSuiteAssetConfig.conformance_suite(
            Path("table-constraints-conformance-DRAFT-YYYY-MM-DD.zip"),
            entry_point=Path("table-constraints-conformance-DRAFT-YYYY-MM-DD/table-constraints-index.xml"),
        ),
    ],
    info_url="https://www.xbrl.org/Specification/table-constraints/CR-2025-07-01/table-constraints-CR-2025-07-01.html",
    membership_url="https://www.xbrl.org/join",
    name=PurePath(__file__).stem,
    test_case_result_options="match-any",
)
