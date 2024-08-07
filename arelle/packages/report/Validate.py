"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable, Generator
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Any, cast

from arelle.packages import PackageConst, PackageUtils, PackageValidation
from arelle.packages.PackageType import PackageType
from arelle.packages.report import Const
from arelle.typing import TypeGetText
from arelle.utils.validate.Validation import Validation

if TYPE_CHECKING:
    from arelle.Cntlr import Cntlr
    from arelle.FileSource import FileSource

_: TypeGetText

REPORT_PACKAGE_TYPE = PackageType("Report", "rpe")

REPORT_PACKAGE_JSON_FILE = "reportPackage.json"

TAXONOMY_PACKAGE_ABORTING_VALIDATIONS = (
    PackageValidation.validatePackageZipFormat,
    PackageValidation.validateZipFileSeparators,
    PackageValidation.validatePackageNotEncrypted,
    PackageValidation.validateTopLevelFiles,
    PackageValidation.validateTopLevelDirectories,
    PackageValidation.validateDuplicateEntries,
    PackageValidation.validateConflictingEntries,
    PackageValidation.validateEntries,
)

TAXONOMY_PACKAGE_NON_ABORTING_VALIDATIONS = (
    PackageValidation.validateMetadataDirectory,
)


def validateReportPackage(
    cntlr: Cntlr,
    filesource: FileSource,
    validateAllFilesAsReportPackage: bool = False,
    errors: list[str] = [],
) -> None:
    if not isinstance(filesource.basefile, str):
        return
    filePath = PurePosixPath(filesource.basefile)
    if not (
        filePath.suffix in Const.REPORT_PACKAGE_EXTENSIONS
        or validateAllFilesAsReportPackage
    ):
        return
    if filePath.suffix in Const.UNCONSTRAINED_REPORT_PACKAGE_EXTENSION:
        if not (validateAllFilesAsReportPackage or _isZipFileReportPackage(filesource)):
            # Zip file is not a report package.
            return
    if not validateReportPackageZipStructure(cntlr, filesource, errors):
        return
    reportPackageDirectory = getReportPackageTopLevelDirectory(filesource)
    reportPackageJsonFile = None
    if reportPackageDirectory is not None:
        reportPackageJsonFile = getReportPackageJsonFile(
            filesource, reportPackageDirectory, reportPackageDirectory
        )
    if not validateReportPackageJsonFile(
        cntlr, filesource, reportPackageJsonFile, errors
    ):
        return
    if filePath.suffix not in Const.REPORT_PACKAGE_EXTENSIONS:
        code = "rpe:unsupportedFileExtension"
        cntlr.addToLog(
            _("File does not have a Report Package file extension: %(filename)s"),
            messageCode=code,
            file=str(filesource.urlBasename),
            level=logging.ERROR,
            messageArgs={"filename": filePath.name},
        )
        errors.append(code)
        return


def validateReportPackageZipStructure(
    cntlr: Cntlr,
    filesource: FileSource,
    errors: list[str] = [],
) -> bool:
    zipStructureValidators = [
        PackageValidation.validatePackageZipFormat,
        PackageValidation.validatePackageNotEncrypted,
        PackageValidation.validateTopLevelDirectories,
        PackageValidation.validateTopLevelFiles,
        PackageValidation.validateEntries,
        PackageValidation.validateZipFileSeparators,
        PackageValidation.validateDuplicateEntries,
        PackageValidation.validateConflictingEntries,
        PackageValidation.validateMetadataDirectory,
    ]
    for valid in executeValidations(cntlr, filesource, zipStructureValidators, errors):
        if not valid:
            return False
    return True


def validateReportPackageJsonFile(
    cntlr: Cntlr,
    filesource: FileSource,
    reportPackageJsonFilePath: str | None,
    errors: list[str] = [],
) -> bool:
    parsedReportPackage = None
    if reportPackageJsonFilePath is not None:
        filesource.select(reportPackageJsonFilePath)
        with filesource.file(cast(str, filesource.url), binary=True)[0] as rp:
            parsedReportPackage = json.load(rp)
    if parsedReportPackage is not None:
        if val := validateDocumentTypeValueType(filesource, parsedReportPackage):
            codes = (
                (val.codes,)
                if isinstance(val.codes, str)
                else val.codes
            )
            for code in codes:
                cntlr.addToLog(
                    val.msg,
                    messageCode=code,
                    file=str(filesource.urlBasename),
                    level=logging.ERROR,
                )
                errors.append(code)
    return False


def getReportPackageTopLevelDirectory(filesource: FileSource) -> str | None:
    topLevelDirs = PackageUtils.getPackageTopLevelDirectories(filesource)
    potentialTopLevelDir = {
        topLevelDir
        for topLevelDir in topLevelDirs
        if _isReportPackageTopLevelDirectory(topLevelDir, filesource.dir or [])
    }
    if len(potentialTopLevelDir) == 1:
        return next(iter(potentialTopLevelDir))
    return None


def getReportPackageJsonFile(
    filesource: FileSource, tld: str, reportPackageJsonFile: str
) -> str | None:
    expectedPackageJsonFilePath = (
        f"{tld}/{PackageConst.META_INF_DIRECTORY}/{REPORT_PACKAGE_JSON_FILE}"
    )
    if expectedPackageJsonFilePath in (filesource.dir or []):
        return expectedPackageJsonFilePath
    return None


def executeValidations(
    cntlr: Cntlr,
    filesource: FileSource,
    validators: list[Callable[[PackageType, FileSource], Validation | None]],
    errors: list[str],
) -> Generator[bool, None, None]:
    for validator in validators:
        if validation := validator(REPORT_PACKAGE_TYPE, filesource):
            codes = (
                (validation.codes,)
                if isinstance(validation.codes, str)
                else validation.codes
            )
            for code in codes:
                cntlr.addToLog(
                    validation.msg,
                    messageCode=code,
                    file=str(filesource.urlBasename),
                    level=logging.ERROR,
                    messageArgs=validation.args,
                )
                errors.append(code)
            yield False
        yield True


def _isReportPackageTopLevelDirectory(
    topLevelDirectory: str, entryPaths: list[str]
) -> bool:
    potentialReportPackagePaths = [
        f"{topLevelDirectory}/{reportPackagePath}"
        for reportPackagePath in Const.REPORT_PACKAGE_PATHS
    ]
    for entryPath in entryPaths:
        for p in potentialReportPackagePaths:
            if entryPath.startswith(p):
                return True
    return False


def _isZipFileReportPackage(filesource: FileSource) -> bool:
    if not filesource.dir:
        return False
    reportPackagePaths = (Const.REPORT_PACKAGE_FILE, Const.REPORTS_DIRECTORY)
    return any(path in filesource.dir for path in reportPackagePaths)


def validateDocumentTypeValueType(
    filesource: FileSource, reportPackageJsonFile: dict[str, Any]
) -> Validation | None:
    documentType = reportPackageJsonFile.get("documentInfo", {}).get("documentType")
    if not isinstance(documentType, str):
        return Validation.error(
            "rpe:invalidJSONStructure",
            _(
                "Report Package document type wasn't parsed as a string: %(documentType)s"
            ),
            args={
                "documentType": documentType,
                "file": filesource.urlBasename,
            },
        )
    return None
