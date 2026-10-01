from pathlib import PurePath, Path
from tests.integration_tests.validation.conformance_suite_config import (
    ConformanceSuiteConfig, ConformanceSuiteAssetConfig, AssetType, AssetSource
)

config = ConformanceSuiteConfig(
    assets=[
        ConformanceSuiteAssetConfig.conformance_suite(
            Path("utr/registry/utr-conf-cr-2013-05-17.zip"),
            entry_point=Path("utr-conf-cr-2013-05-17/2013-05-17/index.xml"),
            public_download_url="https://www.xbrl.org/utr/utr-conf-cr-2013-05-17.zip",
            source=AssetSource.S3_PUBLIC,
        ),
        ConformanceSuiteAssetConfig(
            local_filename=Path("utr/registry/utr.xml"),
            source=AssetSource.S3_PUBLIC,
            type=AssetType.CONFORMANCE_SUITE,
            public_download_url="https://www.xbrl.org/utr/utr.xml",
            s3_key="utr/registry/utr.xml",
        )
    ],
    baseline=Path(__file__).with_suffix(".json"),
    info_url="https://specifications.xbrl.org/work-product-index-registries-units-registry-1.0.html",
    name=PurePath(__file__).stem,
)
