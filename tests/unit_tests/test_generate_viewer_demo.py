"""See COPYRIGHT.md for copyright information."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "docs" / "arelle.org" / "scripts"))

from generate_viewer_demo import CONCEPT_COUNT_FLOOR, _verifyViewer  # noqa: E402


def _viewerData(*, conceptCount: int = CONCEPT_COUNT_FLOOR) -> dict[str, object]:
    return {
        "features": {
            "highlight_facts_on_startup": True,
            "home_link_label": "arelle.org",
            "home_link_url": "/",
            "review": False,
        },
        "sourceReports": [{
            "targetReports": [{
                "concepts": {f"c{i}": {} for i in range(conceptCount)},
            }],
        }],
    }


def _writeViewer(path: Path, data: dict[str, object], *, includeFilingMarkup: bool = False) -> None:
    markup = 'format="ixt-sec:num"' if includeFilingMarkup else ""
    bodyClass = "" if includeFilingMarkup else ' class="ixv-stub-viewer"'
    path.write_text(
        f"<html><body{bodyClass}>"
        f"{markup}"
        '<script type="application/x.ixbrl-viewer+json">'
        f"{json.dumps(data)}"
        "</script></body></html>"
    )


def _writeFiling(path: Path, *, includeViewerData: bool = False) -> None:
    extra = ""
    if includeViewerData:
        extra = '<script type="application/x.ixbrl-viewer+json">{}</script>'
    path.write_text(f'<html><body>format="ixt-sec:num"{extra}</body></html>')


def test_verifyViewer_acceptsStubViewer(tmp_path: Path) -> None:
    viewerPath = tmp_path / "ixbrlviewer.html"
    filingPath = tmp_path / "wk-20251231.htm"
    _writeViewer(viewerPath, _viewerData())
    _writeFiling(filingPath)

    _verifyViewer(viewerPath, filingPath, "/")


def test_verifyViewer_rejectsViewerThatContainsTheFiling(tmp_path: Path) -> None:
    viewerPath = tmp_path / "ixbrlviewer.html"
    filingPath = tmp_path / "wk-20251231.htm"
    _writeViewer(viewerPath, _viewerData(), includeFilingMarkup=True)
    _writeFiling(filingPath)

    with pytest.raises(ValueError, match="stub"):
        _verifyViewer(viewerPath, filingPath, "/")


def test_verifyViewer_rejectsFilingThatContainsViewerData(tmp_path: Path) -> None:
    viewerPath = tmp_path / "ixbrlviewer.html"
    filingPath = tmp_path / "wk-20251231.htm"
    _writeViewer(viewerPath, _viewerData())
    _writeFiling(filingPath, includeViewerData=True)

    with pytest.raises(ValueError, match="embedded viewer data"):
        _verifyViewer(viewerPath, filingPath, "/")
