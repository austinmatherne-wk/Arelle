"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, cast

from arelle.packages import PackageUtils
from arelle.packages.report import ReportPackageConst as Const

if TYPE_CHECKING:
    from arelle.FileSource import FileSource


def _getReportPackageTopLevelDirectory(filesource: FileSource) -> str | None:
    packageEntries = set(filesource.dir or [])
    potentialTopLevelReportDirs = {
        topLevelDir
        for topLevelDir in PackageUtils.getPackageTopLevelDirectories(filesource)
        if any(f"{topLevelDir}/{path}" in packageEntries for path in Const.REPORT_PACKAGE_PATHS)
    }
    if len(potentialTopLevelReportDirs) == 1:
        return next(iter(potentialTopLevelReportDirs))
    return None


def _getReportPackageJson(filesource: FileSource, stld: str | None) -> Any | None:
    packageJsonPath = f"{stld}/{Const.REPORT_PACKAGE_FILE}"
    if stld is None or packageJsonPath not in (filesource.dir or []):
        return None
    try:
        filesource.select(packageJsonPath)
        fullPackageJsonPath = cast(str, filesource.url)
        with filesource.file(fullPackageJsonPath, binary=True)[0] as rpj:
            return json.load(rpj)
    except (OSError, zipfile.BadZipFile, json.JSONDecodeError):
        return None
    finally:
        filesource.select(None)


def _getReportsDirEntries(filesource: FileSource, stld: str | None) -> list[str] | None:
    if stld is None:
        return None
    entries = filesource.dir or []
    topReportEntries = []
    subDirReportEntries = []
    for entry in entries:
        path = PurePosixPath(entry)
        if path.suffix not in Const.REPORT_FILE_EXTENSIONS:
            continue
        if not (2 < len(path.parts) < 5):
            continue
        if not (path.parts[0] == stld and path.parts[1] == Const.REPORTS_DIRECTORY):
            continue
        if len(path.parts) == 3:
            topReportEntries.append(entry)
        else:
            subDirReportEntries.append(entry)
    reportEntries = topReportEntries or subDirReportEntries
    return sorted(reportEntries) if reportEntries else None


class ReportPackage:
    def __init__(
        self,
        filesource: FileSource,
        reportPackageZip: zipfile.ZipFile | None = None,
        stld: str | None = None,
        reportType: Const.ReportType | None = None,
        reportPackageJson: dict[str, Any] | None = None,
        reports: list[str] | None = None,
    ) -> None:
        if not isinstance(filesource.basefile, str):
            raise ValueError(f"Report Package base file must be a string: {filesource.basefile}")
        self._filesource = filesource
        self._reportPackageZip = reportPackageZip
        self._stld = stld
        self._reportType = reportType
        self._reportPackageJson = reportPackageJson
        self._reports = reports

    @staticmethod
    def fromFileSource(filesource: FileSource) -> ReportPackage | None:
        if not isinstance(filesource.basefile, str):
            raise ValueError(f"Report Package base file must be a string: {filesource.basefile}")
        if not isinstance(filesource.fs, zipfile.ZipFile):
            raise ValueError(f"Report Package source must be a zip file: {filesource.basefile}")
        reportType = Const.ReportType.fromExtension(Path(filesource.basefile).suffix)
        if reportType is None:
            return None
        stld = _getReportPackageTopLevelDirectory(filesource)
        if stld is None:
            return None
        reportPackageJson = _getReportPackageJson(filesource, stld)
        reports = _getReportsDirEntries(filesource, stld)
        if reportPackageJson is None and reports is None:
            return None
        return ReportPackage(
            filesource=filesource,
            reportPackageZip=filesource.fs,
            stld=stld,
            reportType=reportType,
            reportPackageJson=reportPackageJson,
            reports=reports,
        )

    @property
    def documentType(self) -> Any:
        if self._reportPackageJson is None:
            return None
        return self._reportPackageJson.get("documentInfo", {}).get("documentType")

    @property
    def reportType(self) -> Const.ReportType | None:
        return self._reportType

    @property
    def reports(self) -> list[str] | None:
        return self._reports

    @property
    def reportPackageJson(self) -> dict[str, Any] | None:
        return self._reportPackageJson

    @property
    def reportPackageZip(self) -> zipfile.ZipFile | None:
        return self._reportPackageZip
