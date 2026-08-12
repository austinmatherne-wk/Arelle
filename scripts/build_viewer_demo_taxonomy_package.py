"""See COPYRIGHT.md for copyright information."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse
from xml.etree import ElementTree


TAXONOMY_PACKAGE_NAMESPACE = "http://xbrl.org/2016/taxonomy-package"
CATALOG_NAMESPACE = "urn:oasis:names:tc:entity:xmlns:xml:catalog"
XML_NAMESPACE = "http://www.w3.org/XML/1998/namespace"
ZIP_TIMESTAMP = (2025, 1, 1, 0, 0, 0)


def _calculateSha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verifyChecksum(path: Path, expected: str) -> None:
    actual = _calculateSha256(path)
    if actual != expected:
        raise ValueError(f"Checksum mismatch for {path}: expected {expected}, got {actual}")


def _requireSafeRelativePath(value: str) -> None:
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"Unsafe archive path: {value}")


def _serializeXml(root: ElementTree.Element) -> bytes:
    document: bytes = ElementTree.tostring(
        root,
        encoding="utf-8",
        xml_declaration=True,
    )
    return document


def _metadataXml(artifact: dict[str, str]) -> bytes:
    ElementTree.register_namespace("tp", TAXONOMY_PACKAGE_NAMESPACE)
    root = ElementTree.Element(
        f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}taxonomyPackage",
        {f"{{{XML_NAMESPACE}}}lang": "en"},
    )
    for key in ("identifier", "name", "description", "version", "publisher"):
        element = ElementTree.SubElement(root, f"{{{TAXONOMY_PACKAGE_NAMESPACE}}}{key}")
        element.text = artifact[key]
    return _serializeXml(root)


def _catalogXml(rewrites: list[dict[str, str]]) -> bytes:
    ElementTree.register_namespace("", CATALOG_NAMESPACE)
    root = ElementTree.Element(f"{{{CATALOG_NAMESPACE}}}catalog")
    for rewrite in rewrites:
        ElementTree.SubElement(
            root,
            f"{{{CATALOG_NAMESPACE}}}rewriteURI",
            {
                "uriStartString": rewrite["uriStartString"],
                "rewritePrefix": rewrite["rewritePrefix"],
            },
        )
    return _serializeXml(root)


def _sourceMembers(
    source: dict[str, Any],
    archive: zipfile.ZipFile,
) -> list[tuple[str, str]]:
    sourceRoot = source["sourceRoot"]
    targetRoot = source["targetRoot"]
    if not sourceRoot.endswith("/") or not targetRoot.endswith("/"):
        raise ValueError("sourceRoot and targetRoot must end with '/'")

    requestedFiles = source.get("files")
    if requestedFiles is None:
        matchedNames = [
            name
            for name in archive.namelist()
            if name.startswith(sourceRoot)
            and not name.endswith("/")
            and not name.startswith(f"{sourceRoot}META-INF/")
        ]
        if not matchedNames:
            raise ValueError(f"No files found below source root {sourceRoot}")
        return [
            (name, f"{targetRoot}{name.removeprefix(sourceRoot)}")
            for name in matchedNames
        ]

    availableNames = set(archive.namelist())
    members: list[tuple[str, str]] = []
    for relativeName in requestedFiles:
        _requireSafeRelativePath(relativeName)
        sourceName = f"{sourceRoot}{relativeName}"
        if sourceName not in availableNames:
            raise ValueError(f"Missing requested source file {sourceName}")
        members.append((sourceName, f"{targetRoot}{relativeName}"))
    return members


def _writeMember(archive: zipfile.ZipFile, name: str, content: bytes) -> None:
    _requireSafeRelativePath(name)
    info = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, content)


def buildPackage(
    manifest: dict[str, Any],
    outputPath: Path,
    sourceArchives: dict[str, Path],
) -> str:
    artifact = manifest["artifact"]
    root = artifact["root"]
    _requireSafeRelativePath(root)

    files: dict[str, bytes] = {}
    for source in manifest["sources"]:
        sourcePath = sourceArchives[source["id"]]
        _verifyChecksum(sourcePath, source["sha256"])
        with zipfile.ZipFile(sourcePath) as sourceZip:
            for sourceName, targetName in _sourceMembers(source, sourceZip):
                targetPath = f"{root}/{targetName}"
                if targetPath in files:
                    raise ValueError(f"Duplicate target path: {targetPath}")
                files[targetPath] = sourceZip.read(sourceName)

    metadataRoot = f"{root}/META-INF"
    files[f"{metadataRoot}/taxonomyPackage.xml"] = _metadataXml(artifact)
    files[f"{metadataRoot}/catalog.xml"] = _catalogXml(manifest["catalog"])

    outputPath.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(outputPath, "w") as outputZip:
        for name in sorted(files):
            _writeMember(outputZip, name, files[name])

    digest = _calculateSha256(outputPath)
    expectedDigest = artifact.get("sha256")
    if expectedDigest and digest != expectedDigest:
        outputPath.unlink()
        raise ValueError(
            f"Artifact checksum mismatch: expected {expectedDigest}, got {digest}"
        )
    return digest


def _downloadSources(manifest: dict[str, Any], cacheDirectory: Path) -> dict[str, Path]:
    cacheDirectory.mkdir(parents=True, exist_ok=True)
    sourceArchives = {}
    for source in manifest["sources"]:
        filename = Path(urlparse(source["url"]).path).name
        destination = cacheDirectory / filename
        if (
            not destination.exists()
            or _calculateSha256(destination) != source["sha256"]
        ):
            temporaryPath: Path | None = None
            try:
                with (
                    urllib.request.urlopen(source["url"]) as response,
                    tempfile.NamedTemporaryFile(
                        dir=cacheDirectory,
                        delete=False,
                    ) as temporaryFile,
                ):
                    temporaryPath = Path(temporaryFile.name)
                    shutil.copyfileobj(response, temporaryFile)
                _verifyChecksum(temporaryPath, source["sha256"])
                temporaryPath.replace(destination)
            finally:
                if temporaryPath is not None:
                    temporaryPath.unlink(missing_ok=True)
        sourceArchives[source["id"]] = destination
    return sourceArchives


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the offline taxonomy package for the arelle.org Viewer demo."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--cache-directory",
        type=Path,
        default=Path(tempfile.gettempdir()) / "arelle-viewer-demo-taxonomies",
    )
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    sources = _downloadSources(manifest, args.cache_directory)
    digest = buildPackage(manifest, args.output, sources)
    print(f"{digest}  {args.output}")


if __name__ == "__main__":
    main()
