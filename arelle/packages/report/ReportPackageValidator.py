"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arelle.FileSource import FileSource
    from arelle.utils.validate.Validation import Validation


class ReportPackageValidator:
    def __init__(self, filesource: FileSource) -> None:
        self._filesource = filesource

    def validate(self) -> Generator[Validation, None, None]:
        raise NotImplementedError()

    def _validateReportPackageZipStructure(self) -> Generator[Validation, None, None]:
        raise NotImplementedError()

    def _validateReportPackageJsonFile(self) -> Generator[Validation, None, None]:
        raise NotImplementedError()
