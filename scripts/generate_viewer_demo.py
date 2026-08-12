"""See COPYRIGHT.md for copyright information."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any


CONCEPT_COUNT_FLOOR = 800
SEC_TRANSFORM_FACT_COUNT = 48
VIEWER_DATA_PATTERN = re.compile(
    r'<script[^>]*type=["\']application/x\.ixbrl-viewer\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL,
)
FILING_SHA256 = {
    "exhibit1019-formofemployme.htm": "3e6edc8ef649128484ef28ba956dbb4eaf7147de2f7b37ef70e740ca9bda2e96",
    "exhibit1022-herrenofferlet.htm": "ed60a84605d29846d2e95364f13428d7aef671809b38a1c8e0c60438d152d2aa",
    "exhibit1023-peekofferletter.htm": "dd6a74c60bb4004091dcbde99b33444f78b5306dd7b452a3eaa1fcf9a0c07d64",
    "exhibit211subsidiaries1231.htm": "1fd1fdfccaa4d62fecdb266c54c38b1191f6f53bb25855aae08c2c9e93e464cf",
    "exhibit231consentofauditor.htm": "3b6d2131a189ab6ec5d5f917845ab2332dda34a1e6e4405988fb1d347948c0a2",
    "exhibit311-section302xceoc.htm": "3facba2e89dbb258ffa382bf73341adf3441dff1c7f73227b6912285a61bd34a",
    "exhibit312-section302xcfoc.htm": "87bf366d6bff556865e2fd7916317a1cb3d465f48b103ec18bd5f8eb564e79ef",
    "exhibit321-section906xceoc.htm": "2c6e81e56109c0bf11b045871db40e528ff3bcef91d98d4d651eb4d71b78c284",
    "exhibit322-section906xcfoc.htm": "00fc89c40712768bd86b93845c6edf761cbf62dccbeb15d8f5018db7a395ce68",
    "exhibit404-descriptionofse.htm": "1cdca69fc499cfb27a5a5c270604081947372fe9cb1dd7249e7b00e7ea69f241",
    "wk-20251231.htm": "b61afaaaa9a34ddeebea05b938e56f90d46ae7b81840f0955df1e631e2a3cc70",
    "wk-20251231.xsd": "e39ba6915e95cba709feaaa7d8a1d640b42b78fdd3fc76c4a583fdf045b18c67",
    "wk-20251231_cal.xml": "13adc695e5668e85f39bda8ef07697ba08250cab0acd40120e6fb53256135d18",
    "wk-20251231_def.xml": "d4d151f124b57176bce157ec1ce7ae62bba264d94da2bef97524cefd0b3aabb0",
    "wk-20251231_g1.jpg": "c4116a043b028f1a4c4273f81bfc0033a5c62fdc4411b660f8d0c5896d08dda8",
    "wk-20251231_lab.xml": "4e4356ddcace207b71937311b69f8537e946a92b4510ac73ff15e344d9cc8dfb",
    "wk-20251231_pre.xml": "b8340fe6043e8822818fa256d17ad39a31533daf3dc4af1daa319d9db9747bac",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verifyFiling(filingDirectory: Path) -> None:
    actualNames = {path.name for path in filingDirectory.iterdir() if path.is_file()}
    expectedNames = set(FILING_SHA256)
    if actualNames != expectedNames:
        missing = sorted(expectedNames - actualNames)
        unexpected = sorted(actualNames - expectedNames)
        raise ValueError(f"Filing contents differ: missing={missing}, unexpected={unexpected}")
    for name, expectedDigest in FILING_SHA256.items():
        actualDigest = _sha256(filingDirectory / name)
        if actualDigest != expectedDigest:
            raise ValueError(
                f"Filing checksum mismatch for {name}: "
                f"expected {expectedDigest}, got {actualDigest}"
            )
    secTransformFactCount = (filingDirectory / "wk-20251231.htm").read_text().count(
        'format="ixt-sec:'
    )
    if secTransformFactCount != SEC_TRANSFORM_FACT_COUNT:
        raise ValueError(
            f"Filing contains {secTransformFactCount} SEC-transformed facts; "
            f"expected {SEC_TRANSFORM_FACT_COUNT}"
        )


def _downloadTaxonomyPackage(definitionPath: Path, destination: Path) -> None:
    definition = json.loads(definitionPath.read_text())
    artifact = definition["artifact"]
    with urllib.request.urlopen(artifact["publicUrl"], timeout=60) as response:
        destination.write_bytes(response.read())
    actualDigest = _sha256(destination)
    if actualDigest != artifact["sha256"]:
        raise ValueError(
            f"Taxonomy package checksum mismatch: "
            f"expected {artifact['sha256']}, got {actualDigest}"
        )


def _verifyViewer(viewerPath: Path, baseUrl: str) -> None:
    match = VIEWER_DATA_PATTERN.search(viewerPath.read_text())
    if match is None:
        raise ValueError(f"Viewer data is absent from {viewerPath}")
    source = match.group(1)
    data: dict[str, Any] = json.loads(source)
    expectedFeatures = {
        "highlight_facts_on_startup": True,
        "home_link_label": "Arelle",
        "home_link_url": baseUrl,
        "review": False,
    }
    if data["features"] != expectedFeatures:
        raise ValueError(f"Unexpected Viewer features: {data['features']}")
    conceptCount = sum(
        len(targetReport["concepts"])
        for sourceReport in data["sourceReports"]
        for targetReport in sourceReport["targetReports"]
    )
    if conceptCount < CONCEPT_COUNT_FLOOR:
        raise ValueError(
            f"Viewer contains {conceptCount} concepts; "
            f"expected at least {CONCEPT_COUNT_FLOOR}"
        )
    for sentinel in ("INVALID_IX_VALUE", "ixTransformValueError"):
        if sentinel in source:
            raise ValueError(f"Viewer contains invalid transformation sentinel {sentinel}")


def generateViewer(
    siteDirectory: Path,
    edgarDirectory: Path,
    baseUrl: str,
) -> None:
    filingDirectory = siteDirectory / "demo" / "filing"
    definitionPath = siteDirectory / "demo" / "taxonomy-package.json"
    publishDirectory = siteDirectory / "public" / "demo" / "ixbrl-viewer"
    transformPlugin = edgarDirectory / "transform"
    if not transformPlugin.is_dir():
        raise ValueError(f"EDGAR transform plugin is absent from {transformPlugin}")
    _verifyFiling(filingDirectory)

    with tempfile.TemporaryDirectory() as temporaryDirectory:
        temporaryPath = Path(temporaryDirectory)
        taxonomyPackage = temporaryPath / "arelle-viewer-demo.zip"
        stagingDirectory = temporaryPath / "ixbrl-viewer"
        viewerPath = stagingDirectory / "viewer.htm"
        logPath = temporaryPath / "arelle.log"
        cacheDirectory = temporaryPath / "cache"
        _downloadTaxonomyPackage(definitionPath, taxonomyPackage)
        shutil.copytree(filingDirectory, stagingDirectory)
        cacheDirectory.mkdir()

        command = [
            sys.executable,
            "-m",
            "arelle.CntlrCmdLine",
            f"--file={filingDirectory / 'wk-20251231.htm'}",
            f"--save-viewer={viewerPath}",
            f"--plugins=ixbrl-viewer|{transformPlugin}",
            f"--packages={taxonomyPackage}",
            "--internetConnectivity=offline",
            f"--cacheDirectory={cacheDirectory}",
            "--disablePersistentConfig",
            "--viewer-feature-highlight-facts-on-startup",
            f"--viewer-feature-home-link-url={baseUrl}",
            "--viewer-feature-home-link-label=Arelle",
            f"--logFile={logPath}",
            "--logLevel=warning",
            "--logFormat=%(messageCode)s %(message)s",
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"Viewer generation failed with exit code {result.returncode}:\n"
                f"{result.stdout}{result.stderr}"
            )
        generationLog = logPath.read_text().strip() if logPath.exists() else ""
        if generationLog:
            raise RuntimeError(f"Viewer generation produced log messages:\n{generationLog}")

        _verifyViewer(viewerPath, baseUrl)
        (stagingDirectory / "ixbrlviewer.config.json").write_text(
            json.dumps({"skin": {"faviconUrl": "../../favicon.ico"}}) + "\n"
        )
        shutil.rmtree(publishDirectory, ignore_errors=True)
        publishDirectory.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(stagingDirectory, publishDirectory)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("siteDirectory", type=Path)
    parser.add_argument("edgarDirectory", type=Path)
    parser.add_argument("--base-url", default="/")
    args = parser.parse_args()
    generateViewer(args.siteDirectory.resolve(), args.edgarDirectory.resolve(), args.base_url)


if __name__ == "__main__":
    main()
