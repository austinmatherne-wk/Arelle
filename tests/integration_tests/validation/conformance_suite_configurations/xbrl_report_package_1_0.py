from pathlib import PurePath, Path
from tests.integration_tests.validation.conformance_suite_config import ConformanceSuiteConfig, ConformanceSuiteAssetConfig

config = ConformanceSuiteConfig(
    assets=[
        ConformanceSuiteAssetConfig.conformance_suite(
            Path("report-package-conformance.zip"),
            entry_point=Path("report-package-conformance/index.csv"),
        ),
    ],
    info_url="https://specifications.xbrl.org/work-product-index-taxonomy-packages-report-packages-1.0.html",
    name=PurePath(__file__).stem,
    network_or_cache_required=False,
)
