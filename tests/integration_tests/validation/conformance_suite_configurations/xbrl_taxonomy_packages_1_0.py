from pathlib import PurePath, Path
from tests.integration_tests.validation.conformance_suite_config import ConformanceSuiteConfig, ConformanceSuiteAssetConfig

config = ConformanceSuiteConfig(
    assets=[
        ConformanceSuiteAssetConfig.conformance_suite(
            Path('taxonomy-package-conformance.zip'),
            entry_point=Path('index.xml'),
        ),
    ],
    expected_testcase_errors={f'index.xml:{s}': val for s, val in {
        'V-003-missing-meta-inf-directory': {
            'tpe:metadataFileNotFound': 1,
        },
        'V-008-invalid-missing-xml-lang': {
            'tpe:missingLanguageAttribute': 1,
        },
        'V-011-invalid-path-separator': {
            'tpe:invalidDirectoryStructure': -1,
        }
    }.items()},
    info_url='https://specifications.xbrl.org/work-product-index-taxonomy-packages-taxonomy-packages-1.0.html',
    membership_url='https://www.xbrl.org/join',
    name=PurePath(__file__).stem,
)
