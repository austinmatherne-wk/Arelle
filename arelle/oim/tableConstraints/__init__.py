"""
See COPYRIGHT.md for copyright information.

Table Constraints 1.0 Validation for xBRL-CSV

This module provides validation of xBRL-CSV reports against the Table Constraints 1.0 specification.
It performs streaming validation that processes CSV data row-by-row without loading the entire
dataset into memory.
"""

from __future__ import annotations

import contextlib
import csv
import json
import os
from io import BytesIO
from typing import cast

from arelle.FileSource import FileSource
from arelle.ModelXbrl import ModelXbrl
from arelle.oim.tableConstraints import Const
from arelle.oim.tableConstraints.Metadata import loadMetadata
from arelle.oim.tableConstraints.validators.metadata import MetadataValidator
from arelle.oim.tableConstraints.validators.report import ReportValidator

_METADATA_PREVIEW_BYTES = 10000


def hasTableConstraints(filepath: str, fileSource: FileSource | None = None, _checked: set[str] | None = None) -> bool:
    """
    Check if a file contains Table Constraints metadata.
    Quick check for tc: prefixed properties, including in extended files.
    """
    if _checked is None:
        _checked = set()

    # Avoid infinite recursion
    if filepath in _checked:
        return False
    _checked.add(filepath)

    try:
        if fileSource is not None:
            with fileSource.file(filepath, binary=True)[0] as contentBytes:
                contentData = cast(BytesIO, contentBytes).read()
            content = contentData.decode("utf-8")
            contentPreview = content[:_METADATA_PREVIEW_BYTES]
        else:
            with open(filepath, encoding="utf-8") as f:
                contentPreview = f.read(_METADATA_PREVIEW_BYTES)
                content = None
    except (OSError, UnicodeDecodeError, AttributeError):
        return False

    if f"{Const.TC_RESERVED_PREFIX}:" in contentPreview:
        return True

    if '"documentInfo"' not in contentPreview or "xbrl-csv" not in contentPreview:
        return False

    try:
        if fileSource is not None and content is not None:
            # Already have full content from FileSource
            metadataDoc = json.loads(content)
        else:
            # Read full file for plain files
            with open(filepath, encoding="utf-8") as f:
                metadataDoc = json.load(f)
    except (OSError, json.JSONDecodeError, ValueError):
        # Not valid JSON or can't read file
        return False

    try:
        hasTc = any(
            key.startswith(f"{Const.TC_RESERVED_PREFIX}:")
            for obj in [metadataDoc] + list(metadataDoc.get("tableTemplates", {}).values())
            for key in obj
            if isinstance(obj, dict)
        )
        if hasTc:
            return True
    except (TypeError, AttributeError):
        return False

    # Check extended files recursively
    with contextlib.suppress(TypeError, AttributeError):
        extends = metadataDoc.get("documentInfo", {}).get("extends", [])
        if extends:
            basedir = os.path.dirname(filepath)
            for extendedFile in extends:
                extendedPath = os.path.normpath(os.path.join(basedir, extendedFile))
                # For archives, check if path exists in archive; for local, check filesystem
                if fileSource is None and not os.path.exists(extendedPath):
                    continue
                if hasTableConstraints(extendedPath, fileSource, _checked):
                    return True

    return False


def validateTableConstraints(
    modelXbrl: ModelXbrl, metadataPath: str, fileSource: FileSource | None = None, validateMetadata: bool = False
) -> bool:
    """
    Perform streaming validation of Table Constraints.

    This validates CSV files against Table Constraints metadata without loading
    the full dataset into memory. It should be called BEFORE normal OIM loading.
    """
    cntlr = modelXbrl.modelManager.cntlr

    cntlr.showStatus("Validating Table Constraints (streaming)...")

    try:
        hasErrors = False

        metadata = loadMetadata(metadataPath, fileSource)

        if validateMetadata:
            metadataValidator = MetadataValidator(modelXbrl, metadata)
            if metadataValidator.validate():
                hasErrors = True

        if not hasErrors:
            reportValidator = ReportValidator(modelXbrl, metadata, fileSource)
            if reportValidator.validate():
                hasErrors = True

        cntlr.showStatus("")

        return hasErrors

    except (OSError, RuntimeError, ValueError, KeyError, TypeError, csv.Error) as e:
        modelXbrl.error("tc:validationError", f"Table Constraints validation error: {str(e)}")
        return True
