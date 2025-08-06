from pathlib import PurePath, Path
from tests.integration_tests.validation.conformance_suite_config import ConformanceSuiteConfig, ConformanceSuiteAssetConfig, AssetSource

config = ConformanceSuiteConfig(
    assets=[
        ConformanceSuiteAssetConfig.conformance_suite(
            Path('xdt-conf-cr4-2009-10-06.zip'),
            entry_point=Path('xdt.xml'),
            public_download_url='https://www.xbrl.org/2009/xdt-conf-cr4-2009-10-06.zip',
            source=AssetSource.S3_PUBLIC,
        ),
    ],
    args=[
        '--infoset',
    ],
    expected_testcase_errors={
    },
    info_url='https://specifications.xbrl.org/work-product-index-group-dimensions-dimensions.html',
    name=PurePath(__file__).stem,
)
