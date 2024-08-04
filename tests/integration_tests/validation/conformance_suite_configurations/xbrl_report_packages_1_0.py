from pathlib import Path, PurePath

from tests.integration_tests.validation.conformance_suite_config import (
    ConformanceSuiteAssetConfig,
    ConformanceSuiteConfig,
)

config = ConformanceSuiteConfig(
    args=[
        "--reportPackage"
    ],
    assets=[
        ConformanceSuiteAssetConfig.conformance_suite(
            Path("report-package-conformance.zip"),
            entry_point=Path("report-package-conformance/index.csv"),
        ),
    ],
    expected_additional_testcase_errors={f"report-package-conformance/index.csv:{s}": val for s, val in {
        # "Empty" iXBRL docs are missing schema required elements.
        "V-301-xbri-with-single-ixds": frozenset({"lxml.SCHEMAV_ELEMENT_CONTENT", "ix11.14.1.2:missingResources"}),
        "V-302-xbri-with-single-html": frozenset({"lxml.SCHEMAV_ELEMENT_CONTENT", "ix11.14.1.2:missingResources"}),
        "V-303-xbri-with-single-htm": frozenset({"lxml.SCHEMAV_ELEMENT_CONTENT", "ix11.14.1.2:missingResources"}),
        # Report package references a taxonomy which does not exist.
        "V-508-xbr-with-no-taxonomy": frozenset({"IOerror", "oime:invalidTaxonomy"}),
        "V-509-xbr-with-json-in-dot-xhtml-directory": frozenset({"IOerror", "oime:invalidTaxonomy"}),
        "V-701-zip-with-no-taxonomy": frozenset({"IOerror", "oime:invalidTaxonomy"}),
    }.items()},
    expected_failure_ids=frozenset(f"report-package-conformance/index.csv:{s}" for s in [
        # 2xx - co-constraints on documentType and package file extension
        "V-200-unsupportedReportPackageVersion",  # rpe:unsupportedReportPackageVersion,0,There will never be a version of the spec with this documentType
        "V-201-missing-report-package-json",  # rpe:documentTypeFileExtensionMismatch,0,"rpe:documentTypeFileExtensionMismatch is ... raised if ... The .xbr ... file extension is used, and reportPackage.json is absent"
        "V-202-missing-report-package-json",  # rpe:documentTypeFileExtensionMismatch,0,"rpe:documentTypeFileExtensionMismatch is ... raised if ... The .xbri ... file extension is used, and reportPackage.json is absent"
        "V-203-xbri-documentType",  # rpe:documentTypeFileExtensionMismatch,0,rpe:documentTypeFileExtensionMismatch is ... raised if ... One of the three document type URIs specified in Section 3.4 is used with the incorrect file extension
        "V-204-xbr-documentType",  # rpe:documentTypeFileExtensionMismatch,0,rpe:documentTypeFileExtensionMismatch is ... raised if ... One of the three document type URIs specified in Section 3.4 is used with the incorrect file extension
        "V-205-unconstrained-documentType",  # rpe:documentTypeFileExtensionMismatch,0,rpe:documentTypeFileExtensionMismatch is ... raised if ... One of the three document type URIs specified in Section 3.4 is used with the incorrect file extension
        "V-206-xbri-documentType",  # rpe:documentTypeFileExtensionMismatch,0,rpe:documentTypeFileExtensionMismatch is ... raised if ... One of the three document type URIs specified in Section 3.4 is used with the incorrect file extension
        "V-207-xbri-without-reportPackage-json",  # rpe:documentTypeFileExtensionMismatch,0,rpe:documentTypeFileExtensionMismatch is ... raised if ... One of the three document type URIs specified in Section 3.4 is used with the incorrect file extension
        "V-208-xbri-without-reportPackage-json-and-reports",  # rpe:documentTypeFileExtensionMismatch,0,rpe:documentTypeFileExtensionMismatch is ... raised if ... One of the three document type URIs specified in Section 3.4 is used with the incorrect file extension
        "V-209-xbr-without-reportPackage-json",  # rpe:documentTypeFileExtensionMismatch,0,rpe:documentTypeFileExtensionMismatch is ... raised if ... One of the three document type URIs specified in Section 3.4 is used with the incorrect file extension
        "V-210-xbr-without-reportPackage-json-and-reports",  # rpe:documentTypeFileExtensionMismatch,0,rpe:documentTypeFileExtensionMismatch is ... raised if ... One of the three document type URIs specified in Section 3.4 is used with the incorrect file extension
        "V-211-unsupported-file-extension",  # rpe:unsupportedFileExtension,0,Current report package with unsupported file extension (.xbrx)

        # 4xx - invalid.xbri packages
        "V-400-xbri-without-reports-directory",  # rpe:missingReportsDirectory,0,A report package MUST contain a directory called reports as a child of the STLD
        "V-401-xbri-with-only-txt-in-reports-directory",  # rpe:missingReport,0,.xbri file without recognised files in the reports directory
        "V-402-xbri-with-xhtml-too-deep",  # rpe:missingReport,0,.xbri file with .xhtml buried too deep to be recognised
        "V-403-xbri-with-multiple-reports",  # rpe:multipleReports,0,If the report package is an Inline XBRL report package ... then there MUST NOT be more than one report in the report package
        "V-404-xbri-with-json-report",  # rpe:incorrectReportType,0,If the report package is an Inline XBRL report package then the contained report MUST be an Inline XBRL Document Set 
        "V-405-xbri-with-xbrl-report",  # rpe:incorrectReportType,0,If the report package is an Inline XBRL report package then the contained report MUST be an Inline XBRL Document Set 
        "V-406-xbri-with-multiple-reports-in-a-subdirectory",  # rpe:multipleReportsInSubdirectory,0,.xbri file with multiple reports in a subdirectory

        # 6xx - invalid.xbr packages
        "V-600-xbr-without-reports-directory",  # rpe:missingReportsDirectory,0,A report package MUST contain a directory called reports as a child of the STLD
        "V-601-xbr-with-only-txt-in-reports-directory",  # rpe:missingReport,0,.xbr file without recognised files in the reports directory
        "V-603-xbr-with-invalid-jrr",  # rpe:invalidJSON,0,.xbr file with a single invalid JSON-rooted report
        "V-604-xbr-with-invalid-jrr-duplicate-keys",  # rpe:invalidJSON,0,.xbr file with a single invalid JSON-rooted report (duplicate keys)
        "V-605-xbr-with-invalid-jrr-utf32",  # rpe:invalidJSON,0,JSON documents MUST use the UTF-8 character encoding
        "V-606-xbr-with-invalid-jrr-utf16",  # rpe:invalidJSON,0,JSON documents MUST use the UTF-8 character encoding
        "V-607-xbr-with-invalid-jrr-utf7",  # rpe:invalidJSON,0,JSON documents MUST use the UTF-8 character encoding
        "V-608-xbr-with-invalid-jrr-missing-documentInfo",  # rpe:invalidJSONStructure,0,The JSON Pointer /documentInfo/documentType MUST resolve to a string (rpe:invalidJSONStructure).
        "V-609-xbr-with-invalid-jrr-missing-documentType",  # rpe:invalidJSONStructure,0,The JSON Pointer /documentInfo/documentType MUST resolve to a string (rpe:invalidJSONStructure).
        "V-610-xbr-with-invalid-jrr-non-string-documentType",  # rpe:invalidJSONStructure,0,The JSON Pointer /documentInfo/documentType MUST resolve to a string (rpe:invalidJSONStructure).
        "V-611-xbr-with-invalid-jrr-non-object-documentInfo",  # rpe:invalidJSONStructure,0,The JSON Pointer /documentInfo/documentType MUST resolve to a string (rpe:invalidJSONStructure).
        "V-612-xbr-with-multiple-reports",  # rpe:multipleReports,0,.xbr file with multiple reports
        "V-613-xbr-with-json-and-xbrl-too-deep",  # rpe:missingReport,0,.xbr file with .json and .xbrl buried too deep to be recognised
        "V-614-xbr-with-xhtml-report",  # rpe:incorrectReportType,0,If the report package is a non-Inline XBRL report package then the contained report MUST be either an XBRL v2.1 report or an JSON-rooted report
        "V-615-xbr-with-html-report",  # rpe:incorrectReportType,0,If the report package is a non-Inline XBRL report package then the contained report MUST be either an XBRL v2.1 report or an JSON-rooted report
        "V-616-xbr-with-htm-report",  # rpe:incorrectReportType,0,If the report package is a non-Inline XBRL report package then the contained report MUST be either an XBRL v2.1 report or an JSON-rooted report
        "V-617-xbr-with-multiple-reports-in-a-subdirectory",  # rpe:multipleReportsInSubdirectory,0,.xbr file with multiple reports in a subdirectory

        # 8xx - invalid.zip packages
        "V-800-zip-without-reports-directory",  # rpe:missingReportsDirectory,0,A report package MUST contain a directory called reports as a child of the STLD
        "V-801-zip-with-only-txt-in-reports-directory",  # rpe:missingReport,0,.zip file without recognised files in the reports directory
        "V-802-zip-with-reports-too-deep",  # rpe:missingReport,0,".zip file with .json, .xbrl and .xhtml buried too deep to be recognised"
        "V-803-zip-with-multiple-reports-in-a-subdirectory",  # rpe:multipleReportsInSubdirectory,0,.zip file with multiple reports in a subdirectory
        "V-804-zip-with-multiple-reports-in-a-subdirectory-uppercase",  # rpe:multipleReportsInSubdirectory,0,.ZIP file (uppercase) with multiple reports in a subdirectory

        # 9xx - future report packages
        "V-900-future-zip",  # rpe:unsupportedReportPackageVersion,0,A future report package with a .zip extension
        "V-901-future-xbri",  # rpe:unsupportedReportPackageVersion,0,A future report package with a .xbri extension
        "V-902-future-xbr",  # rpe:unsupportedReportPackageVersion,0,A future report package with a .xbr extension
        "V-903-future-xbrx",  # rpe:unsupportedFileExtension,0,A future report package with an as-yet-undefined extension (.xbrx)
        "V-904-future-package-with-invalid-reportPackage-json",  # rpe:invalidJSON,0,Future report package with invalid JSON in META-INF/reportPackage.json
        "V-905-future-package-with-invalid-reportPackage-json-duplicate-keys",  # rpe:invalidJSON,0,Future report package with invalid JSON in META-INF/reportPackage.json
        "V-906-future-package-with-invalid-reportPackage-json-utf32",  # rpe:invalidJSON,0,Future report package with invalid JSON in META-INF/reportPackage.json
        "V-907-future-package-with-invalid-reportPackage-json-utf16",  # rpe:invalidJSON,0,Future report package with invalid JSON in META-INF/reportPackage.json
        "V-908-future-package-with-invalid-reportPackage-json-utf7",  # rpe:invalidJSON,0,Future report package with invalid JSON in META-INF/reportPackage.json
        "V-909-future-package-with-invalid-reportPackage-json-missing-documentInfo",  # rpe:invalidJSONStructure,0,Future report package with invalid JSON in META-INF/reportPackage.json
        "V-910-future-package-with-invalid-reportPackage-json-missing-documentType",  # rpe:invalidJSONStructure,0,Future report package with invalid JSON in META-INF/reportPackage.json
        "V-911-future-package-with-invalid-reportPackage-json-non-string-documentType",  # rpe:invalidJSONStructure,0,Future report package with invalid JSON in META-INF/reportPackage.json
        "V-912-future-package-with-invalid-reportPackage-json-non-object-documentInfo",  # rpe:invalidJSONStructure,0,Future report package with invalid JSON in META-INF/reportPackage.json
        "V-913-future-package-with-bom-in-reportPackage-json",  # rpe:unsupportedReportPackageVersion,0,Future report package with Byte Order Mark in META-INF/reportPackage.json
        "V-914-current-and-future-package",  # rpe:unsupportedReportPackageVersion,0,META-INF as STLD means this gets interpreted as a future report package
    ]),
    info_url="https://specifications.xbrl.org/work-product-index-taxonomy-packages-report-packages-1.0.html",
    membership_url="https://www.xbrl.org/join",
    name=PurePath(__file__).stem,
    network_or_cache_required=False,
    plugins=frozenset(["inlineXbrlDocumentSet"]),
)
