from pathlib import Path, PurePath

from tests.integration_tests.validation.assets import ESEF_PACKAGES, LEI_2020_07_02
from tests.integration_tests.validation.conformance_suite_config import (
    AssetSource,
    ConformanceSuiteAssetConfig,
    ConformanceSuiteConfig,
)

config = ConformanceSuiteConfig(
    args=[
        '--disclosureSystem', 'esef-2024',
        '--baseTaxonomyValidation', 'none',
        '--formula', 'none'
    ],
    assets=[
        ConformanceSuiteAssetConfig.conformance_suite(
            Path('esef_conformance_suite_2024.zip'),
            entry_point=Path('esef_conformance_suite_2024/index_inline_xbrl.xml'),
            public_download_url='https://www.esma.europa.eu/sites/default/files/2025-01/esef_conformance_suite_2024.zip',
            source=AssetSource.S3_PUBLIC,
        ),
    ] + [
        package for year in [2017, 2019, 2020, 2021, 2022, 2024] for package in ESEF_PACKAGES[year]
    ],
    expected_additional_testcase_errors={f"esef_conformance_suite_2024/tests/inline_xbrl/{s}": val for s, val in {
        # Typo in the test case namespace declaration: incorrectly uses the Extensible Enumeration 1 namespace with the
        # commonly used Extensible Enumeration 2 prefix: xmlns:enum2="http://xbrl.org/2014/extensible-enumerations"
        'G2-4-1_1/index.xml:TC2_valid': {
            'differentExtensionDataType': 1,
        },
        'G3-1-1_1/index.xml:TC3_invalid': {
            'UsableConceptsNotIncludedInPresentationLink': 1,
            'missingPrimaryFinancialStatement': 1,
        },
        'G3-1-2/index.xml:TC4_invalid': {
            'domainMemberWrongDataType': 1,
        },
        'G3-1-5/index.xml:TC3_invalid': {
            'extensionTaxonomyDocumentNameDoesNotFollowNamingConvention': 4,
        },
        'G3-1-5/index.xml:TC8_invalid': {
            'extensionTaxonomyDocumentNameDoesNotFollowNamingConvention': 3,
        },
        'RTS_Annex_III_Par_1/index.xml:TC2_invalid': {
            'ix11.10.1.2:unitReference': 1,
            'lxml.SCHEMAV_CVC_COMPLEX_TYPE_4': 1,
            'lxml.SCHEMAV_CVC_PATTERN_VALID': 1,
            'xmlSchema:valueError': 1,
        },
        'RTS_Annex_IV_Par_11_G3-2-2/index.xml:TC3_invalid': {
            'differentExtensionDataType': 1,
        },
        'RTS_Annex_IV_Par_8_G3-4-5/index.xml:TC2_invalid': {
            'invalidInlineXBRL': 1,
            'xbrl.5.2.3.1:referenceLinkLocTarget': 1,
        },
        'RTS_Art_6_a/index.xml:TC2_invalid': {
            'missingOrInvalidTaxonomyPackage': 1,
        },
        'G2-1-2/index.xml:TC2_invalid': {
            
        },
        'G2-1-2/index.xml:TC3_invalid': {
            
        },
        'G2-1-2/index.xml:TC4_invalid': {
            
        },
        'G2-1-3_1/index.xml:TC2_invalid': {
            
        },
        'G2-2-1/index.xml:TC2_invalid': {
            
        },
        'G2-2-2/index.xml:TC2_invalid': {
            
        },
        'G2-2-3/index.xml:TC3_invalid': {
            
        },
        'G2-2-7_1/index.xml:TC3_invalid': {
            
        },
        'G2-2-7_1/index.xml:TC4_invalid': {
            
        },
        'G2-2-7_2/index.xml:TC3_invalid': {
            
        },
        'G2-2-7_2/index.xml:TC4_invalid': {
            
        },
        'G2-4-1_1/index.xml:TC3_invalid': {
            
        },
        'G2-4-1_1/index.xml:TC4_invalid': {
            
        },
        'G2-4-1_2/index.xml:TC2_invalid': {
            
        },
        'G2-4-1_3/index.xml:TC2_invalid': {
            
        },
        'G2-5-1_2/index.xml:TC3_invalid': {
            
        },
        'G2-5-1_3/index.xml:TC2_invalid': {
            
        },
        'G2-5-4_2/index.xml:TC2_invalid': {
            
        },
        'G2-7-1_1/index.xml:TC2_invalid': {
            
        },
        'G2-7-1_2/index.xml:TC2_invalid': {
            
        },
        'G3-1-1_1/index.xml:TC4_invalid': {
            
        },
        'G3-1-1_1/index.xml:TC5_invalid': {
            
        },
        'G3-1-1_1/index.xml:TC6_invalid': {
            
        },
        'G3-1-1_2/index.xml:TC2_invalid': {
            
        },
        'G3-1-2/index.xml:TC3_invalid': {
            
        },
        'G3-1-2/index.xml:TC5_invalid': {
            
        },
        'G3-1-2/index.xml:TC6_invalid': {
            
        },
        'G3-1-2/index.xml:TC7_invalid': {
            
        },
        'G3-1-2/index.xml:TC8_invalid': {
            
        },
        'G3-1-5/index.xml:TC4_invalid': {
            
        },
        'G3-1-5/index.xml:TC5_invalid': {
            
        },
        'G3-1-5/index.xml:TC6_invalid': {
            
        },
        'G3-2-2/index.xml:TC2_invalid': {
            
        },
        'G3-2-3/index.xml:TC2_invalid': {
            
        },
        'G3-4-1/index.xml:TC2_invalid': {
            
        },
        'G3-4-2_4/index.xml:TC3_invalid': {
            
        },
        'G3-4-3_1/index.xml:TC2_invalid': {
            
        },
        'G3-4-3_1/index.xml:TC3_invalid': {
            
        },
        'G3-4-3_2/index.xml:TC2_invalid': {
            
        },
        'RTS_Annex_III_Par_1/index.xml:TC3_invalid': {
            
        },
        'RTS_Annex_IV_Par_11_G3-2-2/index.xml:TC2_invalid': {
            
        },
        'RTS_Annex_IV_Par_12_G2-2-4/index.xml:TC6_invalid': {
            
        },
        'RTS_Annex_IV_Par_12_G2-2-4/index.xml:TC7_invalid': {
            
        },
        'RTS_Annex_IV_Par_14_G2-5-1/index.xml:TC2_invalid': {
            
        },
        'RTS_Annex_IV_Par_1_G2-1-4/index.xml:TC2_invalid': {
            
        },
        'RTS_Annex_IV_Par_2_G2-1-1/index.xml:TC2_invalid': {
            
        },
        'RTS_Annex_IV_Par_2_G2-1-1/index.xml:TC3_invalid': {
            
        },
        'RTS_Annex_IV_Par_4_G1-1-1_G3-4-5/index.xml:TC4_invalid': {
            
        },
        'RTS_Annex_IV_Par_4_G1-1-1_G3-4-5/index.xml:TC5_invalid': {
            
        },
        'RTS_Annex_IV_Par_9_Par_10_G1-4-1_G1-4-2_G3-3-1_G3-3-2/index.xml:TC4_invalid': {
            
        },
        'RTS_Annex_IV_Par_9_Par_10_G1-4-1_G1-4-2_G3-3-1_G3-3-2/index.xml:TC5_invalid': {
            
        },
        'RTS_Annex_IV_Par_9_Par_10_G1-4-1_G1-4-2_G3-3-1_G3-3-2/index.xml:TC6_invalid': {
            
        },
        'RTS_Annex_IV_Par_9_Par_10_G1-4-1_G1-4-2_G3-3-1_G3-3-2/index.xml:TC7_invalid': {
            
        },
        'RTS_Annex_IV_Par_9_Par_10_G1-4-1_G1-4-2_G3-3-1_G3-3-2/index.xml:TC8_invalid': {
            
        },
        'RTS_Art_6_a/index.xml:TC3_invalid': {
            
        },
    }.items()},
    info_url='https://www.esma.europa.eu/document/esef-conformance-suite-2024',
    name=PurePath(__file__).stem,
    network_or_cache_required=False,
    plugins=frozenset({'validate/ESEF'}),
    shards=8,
)
