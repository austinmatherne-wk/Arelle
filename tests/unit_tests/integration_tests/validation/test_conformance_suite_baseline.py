"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tests.integration_tests.validation.conformance_suite_config import (
    ConformanceSuiteAssetConfig,
    ConformanceSuiteConfig,
)
from tests.integration_tests.validation.validation_util import get_conformance_suite_arguments

ENTRY_POINT = "tests/resources/conformance_suites/suite.zip/index.xml"


def _baseline(tmp_path: Path, **overrides: Any) -> Path:
    options = {
        "entrypointFile": ENTRY_POINT,
        "validate": True,
        "testcaseResultOptions": "match-any",
        "plugins": "inlineXbrlDocumentSet",
        "calcs": "xbrl21",
        "testcaseResultsCaptureWarnings": True,
    }
    options.update(overrides)
    for name in [name for name, value in options.items() if value is None]:
        del options[name]
    path = tmp_path / "suite.json"
    path.write_text(json.dumps(options))
    return path


def _config(baseline: Path | None = None, **kwargs: Any) -> ConformanceSuiteConfig:
    return ConformanceSuiteConfig(
        assets=[ConformanceSuiteAssetConfig.local_conformance_suite(Path("suite.zip"), entry_point=Path("index.xml"))],
        baseline=baseline,
        info_url="https://example.com",
        name="suite",
        **kwargs,
    )


def _arguments(config: ConformanceSuiteConfig, additional_plugins: frozenset[str] = frozenset()) -> list[str]:
    args, _ = get_conformance_suite_arguments(
        config=config, filename=config.entry_point_path.as_posix(), disclosure_system=None,
        additional_plugins=additional_plugins, build_cache=False, offline=False, log_to_file=False,
        expected_additional_testcase_errors={"*index.xml:V-1": {"code": 2}},
        expected_failure_ids=frozenset(), shard=None, testcase_filters=[],
    )
    return args


def test_baseline_arguments(tmp_path: Path) -> None:
    baseline = _baseline(tmp_path)
    args = _arguments(_config(baseline))
    assert args == [
        "--optionsFile", baseline.as_posix(),
        "--keepOpen",
        "--testcaseResultOptions", "match-all",
        "--plugins", "inlineXbrlDocumentSet",
        "--internetConnectivity", "offline",
        "--testcaseExpectedErrors", "*index.xml:V-1|code,code",
    ]


def test_baseline_plugins_merged_with_additional_plugins(tmp_path: Path) -> None:
    args = _arguments(_config(_baseline(tmp_path)), additional_plugins=frozenset({"EDGAR/render"}))
    assert args[args.index("--plugins") + 1] == "EDGAR/render|inlineXbrlDocumentSet"


def test_arguments_without_baseline() -> None:
    args = _arguments(_config(args=["--calc", "xbrl21"], plugins=frozenset({"inlineXbrlDocumentSet"})))
    assert args[:6] == [
        "--file", ENTRY_POINT,
        "--validate",
        "--keepOpen",
        "--testcaseResultOptions", "match-all",
    ]
    assert "--optionsFile" not in args
    assert "--testcaseResultsCaptureWarnings" in args
    assert args[-2:] == ["--calc", "xbrl21"]


@pytest.mark.parametrize("kwargs", [
    {"args": ["--calc", "xbrl21"]},
    {"plugins": frozenset({"inlineXbrlDocumentSet"})},
    {"disclosure_system": "efm-pragmatic"},
    {"base_taxonomy_validation": "none"},
])
def test_baseline_rejects_settings_in_both_layers(tmp_path: Path, kwargs: dict[str, Any]) -> None:
    with pytest.raises(AssertionError, match="baseline options file instead"):
        _config(_baseline(tmp_path), **kwargs)


@pytest.mark.parametrize("overrides, message", [
    ({"entrypointFile": "other/index.xml"}, "entrypointFile"),
    ({"validate": None}, "validate"),
    ({"testcaseResultOptions": "match-all"}, "match-any"),
    ({"testcaseExpectedErrors": ["index.xml:V-1|code"]}, "Expected errors"),
])
def test_baseline_rejects_invalid_options(tmp_path: Path, overrides: dict[str, Any], message: str) -> None:
    with pytest.raises(AssertionError, match=message):
        _config(_baseline(tmp_path, **overrides))


def test_baseline_without_warning_capture(tmp_path: Path) -> None:
    args = _arguments(_config(_baseline(tmp_path, testcaseResultsCaptureWarnings=None), capture_warnings=False))
    assert "--testcaseResultsCaptureWarnings" not in args


@pytest.mark.parametrize("baseline_captures, capture_warnings", [(True, False), (None, True)])
def test_baseline_warning_capture_must_match_config(
        tmp_path: Path, baseline_captures: bool | None, capture_warnings: bool) -> None:
    with pytest.raises(AssertionError, match="capture_warnings"):
        _config(_baseline(tmp_path, testcaseResultsCaptureWarnings=baseline_captures), capture_warnings=capture_warnings)
