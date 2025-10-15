"""
See COPYRIGHT.md for copyright information.

Metadata loading utilities for Table Constraints.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, cast

from arelle.FileSource import FileSource

MetadataDict = dict[str, Any]


@dataclass(frozen=True)
class Metadata:
    """
    Immutable wrapper around xBRL-CSV metadata dictionary providing convenient accessors.
    """

    _data: MetadataDict
    path: str | None = None  # Path to the metadata file, used for resolving relative paths

    @property
    def namespaces(self) -> dict[str, str]:
        return cast(dict[str, str], self._data.get("documentInfo", {}).get("namespaces", {}))

    @property
    def documentInfo(self) -> dict[str, Any]:
        return cast(dict[str, Any], self._data.get("documentInfo", {}))

    @property
    def tableTemplates(self) -> dict[str, dict[str, Any]]:
        return cast(dict[str, dict[str, Any]], self._data.get("tableTemplates", {}))

    @property
    def tables(self) -> dict[str, dict[str, Any]]:
        return cast(dict[str, dict[str, Any]], self._data.get("tables", {}))


def loadMetadata(metadataPath: str, fileSource: FileSource | None = None) -> Metadata:
    try:
        if fileSource is not None:
            fileStream = fileSource.file(metadataPath, encoding="utf-8")[0]
            metadata: MetadataDict = json.load(fileStream)
            fileStream.close()
        else:
            with open(metadataPath, encoding="utf-8") as f:
                metadata = json.load(f)

        extends = metadata.get("documentInfo", {}).get("extends", [])
        if extends:
            basedir = os.path.dirname(metadataPath)
            for extendedFile in extends:
                extendedPath = os.path.normpath(os.path.join(basedir, extendedFile))
                fileExists = fileSource is not None or os.path.exists(extendedPath)
                if fileExists:
                    if fileSource is not None:
                        fileStream = fileSource.file(extendedPath, encoding="utf-8")[0]
                        extendedData = json.load(fileStream)
                        fileStream.close()
                    else:
                        with open(extendedPath, encoding="utf-8") as f:
                            extendedData = json.load(f)
                    if "tableTemplates" in extendedData:
                        if "tableTemplates" not in metadata:
                            metadata["tableTemplates"] = {}
                        metadata["tableTemplates"].update(extendedData["tableTemplates"])
                    if "documentInfo" in extendedData and "namespaces" in extendedData["documentInfo"]:
                        if "documentInfo" not in metadata:
                            metadata["documentInfo"] = {}
                        if "namespaces" not in metadata["documentInfo"]:
                            metadata["documentInfo"]["namespaces"] = {}
                        metadata["documentInfo"]["namespaces"].update(extendedData["documentInfo"]["namespaces"])

        return Metadata(metadata, metadataPath)
    except (OSError, json.JSONDecodeError, KeyError) as e:
        raise RuntimeError(f"Failed to load metadata: {str(e)}") from e
