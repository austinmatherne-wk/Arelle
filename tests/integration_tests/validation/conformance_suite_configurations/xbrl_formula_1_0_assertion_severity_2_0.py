from pathlib import PurePath, Path
from tests.integration_tests.validation.conformance_suite_config import ConformanceSuiteConfig, ConformanceSuiteAssetConfig

config = ConformanceSuiteConfig(
    assets=[
        ConformanceSuiteAssetConfig.conformance_suite(
            Path('60111 AssertionSeverity-2.0-Processing.zip'),
            entry_point=Path('60111 AssertionSeverity-2.0-Processing/60111 Assertion Severity 2.0 Processing.xml'),
        ),
    ],
    expected_testcase_errors={f'60111 AssertionSeverity-2.0-Processing/60111 Assertion Severity 2.0 Processing.xml:/{s}': val for s, val in {
        'V-01': {
            'test-assertion': -1
        },
        'V-03': {
            'seve:assertionSeverityTargetError': 1
        },
        'V-10': {
            'test-assertion': -1
        },
        'V-11': {
            'seve:invalidSeverityExpressionResultError': 1,
            'test-assertion': -1
        },
        'V-13': {
            'test-assertion': -1
        },
        'V-15': {
            'seve:invalidSeverityExpressionResultError': 1
        },
        'V-16': {
            'seve:invalidSeverityExpressionResultError': 2
        }
    }.items()},
    info_url='https://specifications.xbrl.org/release-history-formula-1.0-formula-conf.html',
    name=PurePath(__file__).stem,
)
