from pathlib import PurePath, Path
from tests.integration_tests.validation.conformance_suite_config import ConformanceSuiteConfig, ConformanceSuiteAssetConfig

config = ConformanceSuiteConfig(
    args=[
        '--validateXmlOim',
    ],
    assets=[
        ConformanceSuiteAssetConfig.conformance_suite(
            Path('oim-conformance-2023-04-19.zip'),
            entry_point=Path('oim-conformance-2023-04-19/oim-index.xml'),
        ),
    ],
    expected_testcase_errors={f'oim-conformance-2023-04-19/{s}': val for s, val in {
        '100-json-conformant-processor/index-json.xml:V-01b': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-01c': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-01d': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-01e': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-01f': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-01g': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-01h': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-02': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-02a': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-03': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-04': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-04a': {
            'arelle:notLoaded': 1,
            'xbrlje:invalidJSONStructure': 1
        },
        '100-json-conformant-processor/index-json.xml:V-04b': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-05a': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-08a': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-08b': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-08c': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-08e': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-08f': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-08g': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-08h': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-08o': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-08q': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-09': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-09a': {
            'oimce:invalidAliasForReservedURI': 1,
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-10': {
            'oimce:multipleAliasesForURI': 1,
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-102': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-104': {
            'xmlSchema:valueError': 1
        },
        '100-json-conformant-processor/index-json.xml:V-104a': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-104b': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-105a': {
            'oime:invalidTaxonomy': 1,
            'xbrldie:ExplicitMemberUndefinedQNameError': 1,
            'xmlSchema:valueError': 1
        },
        '100-json-conformant-processor/index-json.xml:V-105b': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-105c': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-105d': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-105e': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-105g': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-105h': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-105i': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-105j': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-105k': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-105l': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-105m': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-105n': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-105o': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-105p': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-105q': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-10a': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-10d': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-10f': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-10j': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-11a': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-11b': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-11c': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-220m': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-224m': {
            'arelle:notLoaded': 1,
            'xbrlje:invalidJSONStructure': 1
        },
        '100-json-conformant-processor/index-json.xml:V-252m': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-253m': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-254m': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-255m': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-256m': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-260m': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-341m': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-342m': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-343m': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-370a': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-370b': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-370c': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-370e': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-370h': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-370i': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-410': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-552': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-553': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-557': {
            'IOerror': 1,
            'oime:unknownConcept': 1
        },
        '100-json-conformant-processor/index-json.xml:V-558': {
            'xbrl.5.1.1.3:itemType': 1
        },
        '100-json-conformant-processor/index-json.xml:V-559': {
            'xbrl.3.5.3.9.2:arcResource': 1
        },
        '100-json-conformant-processor/index-json.xml:V-601': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-70a': {
            'oime:invalidTaxonomy': 1,
            'xbrl.4.11.1.3.1:factFootnoteArcTo': 1
        },
        '100-json-conformant-processor/index-json.xml:V-70b': {
            'xbrl.4.11.1.2.1:footnoteLang': 1
        },
        '100-json-conformant-processor/index-json.xml:V-70e': {
            'oime:invalidXBRL': 1
        },
        '100-json-conformant-processor/index-json.xml:V-70h': {
            'oime:invalidTaxonomy': 1,
            'xbrl.4.11.1.3.1:factFootnoteArcTo': 1
        },
        '100-json-conformant-processor/index-json.xml:V-75': {
            'arelle:notLoaded': 1
        },
        '100-json-conformant-processor/index-json.xml:V-76': {
            'arelle:notLoaded': 1
        },
        '200-json-validating-conformant-processor/index-json-validating.xml:V-001': {
            'oime:invalidTaxonomy': 1
        },
        '200-json-validating-conformant-processor/index-json-validating.xml:V-002': {
            'oime:invalidTaxonomy': 1
        },
        '200-json-validating-conformant-processor/index-json-validating.xml:V-010': {
            'oime:invalidTaxonomy': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-02': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-02-m': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-02b': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-02b-m': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-02c': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-02d': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-02e': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-02f': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-03': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-04': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-05': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-06': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-07': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-09b': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-09c': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-09d': {
            'oime:invalidXBRL': 1,
            'xml.3.3.1:idMustBeUnique': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-09e': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-112a': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-112b': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-112c': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-112d': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-112e': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-113a': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-113b': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-114': {
            'arelle:notLoaded': 1,
            'xbrlce:unreferencedParameter': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-116': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-117': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-118': {
            'arelle:notLoaded': 1,
            'xbrlce:invalidIdentifier': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-118a': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-119': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-13': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-135': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-135a': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-135c': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-136a': {
            'xbrlce:unmappedCellValue': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-138': {
            'xbrlce:unmappedCellValue': 1,
            'xml.3.3.1:idMustBeUnique': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-138a': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-138b': {
            'xbrlce:repeatedRowIdentifier': -1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-138d': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-14': {
            'oime:invalidXBRL': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-141': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-142': {
            'oime:missingPeriodDimension': 1,
            'xbrlce:unmappedCellValue': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-143': {
            'oime:missingPeriodDimension': 1,
            'xbrlce:unmappedCellValue': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-146': {
            'xbrlce:unmappedCellValue': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-149': {
            'xbrlce:invalidReferenceTarget': 1,
            'xbrlce:unmappedCellValue': 2
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-15': {
            'oimce:multipleAliasesForURI': 1,
            'oime:invalidXBRL': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-150': {
            'xbrlce:invalidReferenceTarget': 1,
            'xbrlce:unmappedCellValue': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-15a': {
            'oime:invalidXBRL': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-15b': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-160a': {
            'oime:invalidXBRL': 1,
            'xbrlce:invalidPeriodRepresentation': 1,
            'xbrlce:unmappedCellValue': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-160b': {
            'oime:invalidXBRL': 1,
            'xbrlce:unmappedCellValue': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-162': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-163': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-164': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-165': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-166': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-167': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-170': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-19a': {
            'xbrlce:unmappedCellValue': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-19b': {
            'oime:invalidXBRL': 1,
            'xbrlce:invalidDecimalsValue': 1,
            'xbrlce:unmappedCellValue': 2
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-19c': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-19d': {
            'xbrlce:unmappedCellValue': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-19e': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-19f': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-201d': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-201e': {
            'arelle:notLoaded': 1,
            'xbrlce:conflictingMetadataValue': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-201f': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-201h': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-202': {
            'arelle:notLoaded': 1,
            'oimce:unsupportedDocumentType': -1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-203': {
            'arelle:notLoaded': 1,
            'xbrlce:illegalExtensionOfFinalProperty': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-204': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-206': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-207': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-20a': {
            'oime:invalidXBRL': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-20b': {
            'oime:invalidXBRL': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-22': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-221': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-222': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-232b': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-232d': {
            'oime:unknownConcept': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-234': {
            'arelle:notLoaded': 1,
            'oime:unknownConcept': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-236': {
            'xbrlce:unknownPropertyGroup': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-236b': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-237': {
            'xbrlce:unmappedCellValue': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-238': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-238a': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-239': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-239a': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-240': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-241': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-242': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-243': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-244': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-272': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-273': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-275': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-280': {
            'xmlSchema:valueError': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-281': {
            'xmlSchema:valueError': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-283': {
            'xmlSchema:nilNonNillableElement': 1,
            'xmlSchema:valueError': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-306': {
            'oime:disallowedDuplicateFacts': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-320': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-320a': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-321': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-322': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-330': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-331': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-332': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-34': {
            'xbrlce:unmappedCellValue': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-340': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-341': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-342': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-342a': {
            'oime:missingPeriodDimension': 1,
            'xbrlce:unmappedCellValue': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-35': {
            'xbrlce:unmappedCellValue': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-350': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-351': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-352': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-353': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-36': {
            'xbrlce:unmappedCellValue': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-370': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-371': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-372': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-373': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-374': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-38': {
            'xbrlce:unmappedCellValue': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-383': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-383a': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-383b': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-384': {
            'oime:invalidXBRL': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-385': {
            'oime:invalidXBRL': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-39': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-400': {
            'IOerror': 1,
            'arelle:notLoaded': 1,
            'oime:invalidTaxonomy': 1,
            'oime:unknownConcept': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-404': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-405': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-410': {
            'oime:invalidUseOfReservedIdentifier': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-412': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-41a1': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-41b': {
            'xmlSchema:valueError': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-420': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-430': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-440': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-441': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-450': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-451': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-452': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-511': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-514': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-515': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-517': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-518': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-519': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-520': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-523': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-525': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-561': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-564': {
            'oime:invalidXBRL': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-567': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-574': {
            'xmlSchema:valueError': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-575': {
            'xmlSchema:valueError': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-579': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-579a': {
            'arelle:notLoaded': 1,
            'xbrlce:illegalExtensionOfFinalProperty': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-580': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-580b': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-581': {
            'arelle:notLoaded': 1,
            'xbrlce:unknownTableTemplate': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-584': {
            'IOerror': 1,
            'arelle:notLoaded': 1,
            'oime:unknownConcept': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-585': {
            'xbrl.5.1.1.3:itemType': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-586': {
            'xbrl.3.5.3.9.2:arcResource': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-60a': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-62': {
            'xmlSchema:nilNonNillableElement': 1,
            'xmlSchema:valueError': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-81': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-82': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-86a': {
            'xbrl.3.5.4:hrefIdNotFound': 1,
            'xbrl.4.11.1.1:footnoteLinkLocTarget': 1,
            'xbrl.4.11.1.1:instanceLoc': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-88': {
            'oime:invalidXBRL': 1,
            'oime:misplacedNoteFactDimension': 3
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-88a': {
            'oime:invalidXBRL': 1,
            'oime:misplacedNoteFactDimension': 3
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-88b': {
            'oime:invalidXBRL': 1,
            'oime:misplacedNoteFactDimension': 3
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-89': {
            'oime:invalidTaxonomy': 1,
            'xbrl.4.11.1.3.1:factFootnoteArcTo': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-89a': {
            'arelle:notLoaded': 1,
            'oimce:unboundPrefix': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-90a': {
            'arelle:notLoaded': 1
        },
        '300-csv-conformant-processor/index-csv-table.xml:V-92': {
            'arelle:notLoaded': 1
        },
        '400-csv-validating-conformant-processor/index-csv-table.xml:V-001': {
            'xbrlxe:nonStandardRoleDefinitionNotInDTS': 1
        },
        '600-xml/index-xbrl-xml.xml:V-05': {
            'xbrlxe:unexpectedContextContent': -1
        },
        '600-xml/index-xbrl-xml.xml:V-06': {
            'xbrlxe:unexpectedContextContent': -1
        }
    }.items()},
    info_url='https://specifications.xbrl.org/work-product-index-open-information-model-open-information-model.html',
    membership_url='https://www.xbrl.org/join',
    name=PurePath(__file__).stem,
)
