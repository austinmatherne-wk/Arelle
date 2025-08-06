from pathlib import PurePath, Path
from tests.integration_tests.validation.conformance_suite_config import ConformanceSuiteConfig, ConformanceSuiteAssetConfig, AssetSource

config = ConformanceSuiteConfig(
    args=[
        '--disclosureSystem', 'esef-unconsolidated-2021',
        '--baseTaxonomyValidation', 'none',
    ],
    assets=[
        ConformanceSuiteAssetConfig.conformance_suite(
            Path('esef_conformance_suite_2021.zip'),
            entry_point=Path('esef_conformance_suite_2021/esef_conformance_suite_2021/index_pure_xhtml.xml'),
            public_download_url='https://www.esma.europa.eu/sites/default/files/library/esef_conformance_suite_2021.zip',
            source=AssetSource.S3_PUBLIC,
        ),
    ],
    expected_testcase_errors={f'esef_conformance_suite_2021/esef_conformance_suite_2021/tests/pure_xhtml/{s}': val for s, val in {
        'G4-1-3_3/index.xml:TC3_invalid': {
            'ESEF.4.1.3.MIMETypeNotSpecified': 1,
            'MIMETypeNotSpecified': -1,
            'exception:TypeError': 1
        },
        'G4-1-3_4/index.xml:TC2_invalid': {
            'ESEF.4.1.3.imageFormatNotSupported': 2,
            'imageFormatNotSupported': -1
        }
    }.items()},
    info_url='https://www.esma.europa.eu/document/conformance-suite-2021',
    name=PurePath(__file__).stem,
    plugins=frozenset({'validate/ESEF'}),
)
