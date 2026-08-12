"""See COPYRIGHT.md for copyright information."""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

import pytest
from lxml import etree

from scripts.build_viewer_demo_taxonomy_package import _downloadSources, buildPackage


def _writeZip(path: Path, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)


def _calculateSha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FailingResponse:
    def __enter__(self) -> FailingResponse:
        return self

    def __exit__(self, *args: object) -> None:
        pass

    def read(self, size: int = -1) -> bytes:
        raise OSError("download failed")


def test_downloadSources_removesPartialDownload(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "scripts.build_viewer_demo_taxonomy_package.urllib.request.urlopen",
        lambda url: FailingResponse(),
    )
    manifest = {
        "sources": [
            {
                "id": "source",
                "url": "https://example.com/source.zip",
                "sha256": "unused",
            },
        ],
    }

    with pytest.raises(OSError, match="download failed"):
        _downloadSources(manifest, tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_buildPackage_combinesUpstreamPackagesAndSelectedSecFiles(
    tmp_path: Path,
) -> None:
    tmpPath = tmp_path
    gaapPath = tmpPath / "gaap.zip"
    srtPath = tmpPath / "srt.zip"
    secPath = tmpPath / "sec.zip"
    _writeZip(gaapPath, {
        "us-gaap-2025/META-INF/catalog.xml": b"upstream metadata",
        "us-gaap-2025/elts/us-gaap-2025.xsd": b"gaap",
    })
    _writeZip(srtPath, {
        "srt-2025/META-INF/taxonomyPackage.xml": b"upstream metadata",
        "srt-2025/elts/srt-2025.xsd": b"srt",
    })
    _writeZip(secPath, {
        "2025/xbrl.sec.gov/country/2025/country-2025.xsd": b"country",
        "2025/xbrl.sec.gov/dei/2025/dei-2025.xsd": b"unused",
    })

    manifest = {
        "artifact": {
            "root": "viewer-demo-taxonomy-package-2025",
            "identifier": "https://arelle.org/taxonomy-packages/viewer-demo-2025",
            "name": "Arelle Viewer demo taxonomy package",
            "description": "Taxonomies needed by the Arelle Viewer demo filing.",
            "version": "2025",
            "publisher": "Arelle",
        },
        "sources": [
            {
                "id": "gaap",
                "sha256": _calculateSha256(gaapPath),
                "sourceRoot": "us-gaap-2025/",
                "targetRoot": "us-gaap/2025/",
            },
            {
                "id": "srt",
                "sha256": _calculateSha256(srtPath),
                "sourceRoot": "srt-2025/",
                "targetRoot": "srt/2025/",
            },
            {
                "id": "sec",
                "sha256": _calculateSha256(secPath),
                "files": ["xbrl.sec.gov/country/2025/country-2025.xsd"],
                "sourceRoot": "2025/",
                "targetRoot": "sec/",
            },
        ],
        "catalog": [
            {
                "uriStartString": "https://xbrl.fasb.org/us-gaap/2025/",
                "rewritePrefix": "../us-gaap/2025/",
            },
            {
                "uriStartString": "https://xbrl.sec.gov/",
                "rewritePrefix": "../sec/xbrl.sec.gov/",
            },
        ],
    }
    outputPath = tmpPath / "package.zip"

    digest = buildPackage(
        manifest,
        outputPath,
        {"gaap": gaapPath, "srt": srtPath, "sec": secPath},
    )

    assert digest == _calculateSha256(outputPath)
    with zipfile.ZipFile(outputPath) as archive:
        names = archive.namelist()
        root = "viewer-demo-taxonomy-package-2025/"
        assert names == sorted(names)
        assert f"{root}us-gaap/2025/elts/us-gaap-2025.xsd" in names
        assert f"{root}srt/2025/elts/srt-2025.xsd" in names
        assert f"{root}sec/xbrl.sec.gov/country/2025/country-2025.xsd" in names
        assert not any(
            "/META-INF/" in name and not name.startswith(f"{root}META-INF/")
            for name in names
        )
        assert f"{root}sec/xbrl.sec.gov/dei/2025/dei-2025.xsd" not in names

        metadata = etree.fromstring(archive.read(f"{root}META-INF/taxonomyPackage.xml"))
        namespace = {"tp": "http://xbrl.org/2016/taxonomy-package"}
        name = metadata.findtext("tp:name", namespaces=namespace)
        assert name == "Arelle Viewer demo taxonomy package"
        assert metadata.findtext("tp:publisher", namespaces=namespace) == "Arelle"

        catalog = etree.fromstring(archive.read(f"{root}META-INF/catalog.xml"))
        rewrites = catalog.findall(
            "{urn:oasis:names:tc:entity:xmlns:xml:catalog}rewriteURI"
        )
        assert [item.get("uriStartString") for item in rewrites] == [
            "https://xbrl.fasb.org/us-gaap/2025/",
            "https://xbrl.sec.gov/",
        ]
