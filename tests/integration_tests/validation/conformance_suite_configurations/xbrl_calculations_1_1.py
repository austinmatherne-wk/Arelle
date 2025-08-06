from pathlib import PurePath, Path
from tests.integration_tests.validation.conformance_suite_config import ConformanceSuiteConfig, ConformanceSuiteAssetConfig

config = ConformanceSuiteConfig(
    args=[
        '--validateXmlOim',
    ],
    assets=[
        ConformanceSuiteAssetConfig.conformance_suite(
            Path('calculation-1.1-conformance-2023-12-20.zip'),
            entry_point=Path('calculation-1.1-conformance-2023-12-20/index.xml'),
        ),
    ],
    expected_testcase_errors={f'calculation-1.1-conformance-2023-12-20/{s}': val for s, val in {
        'calc11/index.xml:nonDecimal-doubles-round': {
            'calc11e:nonDecimalItemNode': 1
        },
        'calc11/index.xml:nonDecimal-doubles-truncate': {
            'calc11e:nonDecimalItemNode': 1
        },
        'calc11/index.xml:nonItem-hypercubes-round': {
            'calc11e:nonDecimalItemNode': 1,
            'oime:invalidTaxonomy': 1,
            'xbrl.5.2.5.2:nonNumericCalc': 2
        },
        'calc11/index.xml:nonItem-hypercubes-truncate': {
            'calc11e:nonDecimalItemNode': 1,
            'oime:invalidTaxonomy': 1,
            'xbrl.5.2.5.2:nonNumericCalc': 2
        },
        'calc11/index.xml:nonNumeric-strings-round': {
            'calc11e:nonDecimalItemNode': 1,
            'oime:invalidTaxonomy': 1,
            'xbrl.5.2.5.2:nonNumericCalc': 2
        },
        'calc11/index.xml:nonNumeric-strings-truncate': {
            'calc11e:nonDecimalItemNode': 1,
            'oime:invalidTaxonomy': 1,
            'xbrl.5.2.5.2:nonNumericCalc': 2
        },
        'calc11/index.xml:oim-tuple-inconsistent-round': {
            'calc11e:inconsistentCalculationUsingRounding': 1
        },
        'calc11/index.xml:oim-tuple-inconsistent-truncate': {
            'calc11e:inconsistentCalculationUsingTruncation': 1
        },
        'xbrl21/index.xml:nonDecimal-doubles-round': {
            'calc11e:nonDecimalItemNode': 1
        },
        'xbrl21/index.xml:nonDecimal-doubles-truncate': {
            'calc11e:nonDecimalItemNode': 1
        },
        'xbrl21/index.xml:nonItem-hypercubes-round': {
            'calc11e:nonDecimalItemNode': 1,
            'oime:invalidTaxonomy': 1,
            'xbrl.5.2.5.2:nonNumericCalc': 2
        },
        'xbrl21/index.xml:nonItem-hypercubes-truncate': {
            'calc11e:nonDecimalItemNode': 1,
            'oime:invalidTaxonomy': 1,
            'xbrl.5.2.5.2:nonNumericCalc': 2
        },
        'xbrl21/index.xml:nonNumeric-strings-round': {
            'calc11e:nonDecimalItemNode': 1,
            'oime:invalidTaxonomy': 1,
            'xbrl.5.2.5.2:nonNumericCalc': 2
        },
        'xbrl21/index.xml:nonNumeric-strings-truncate': {
            'calc11e:nonDecimalItemNode': 1,
            'oime:invalidTaxonomy': 1,
            'xbrl.5.2.5.2:nonNumericCalc': 2
        },
        'xbrl21/index.xml:oim-tuple-inconsistent-round': {
            'calc11e:inconsistentCalculationUsingRounding': 1
        },
        'xbrl21/index.xml:oim-tuple-inconsistent-truncate': {
            'calc11e:inconsistentCalculationUsingTruncation': 1
        }
    }.items()},
    info_url='https://specifications.xbrl.org/work-product-index-calculations-2-calculations-1-1.html',
    membership_url='https://www.xbrl.org/join',
    name=PurePath(__file__).stem,
    plugins=frozenset({'../../tests/plugin/testcaseCalc11ValidateSetup.py'}),
)
