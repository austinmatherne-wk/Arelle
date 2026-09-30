"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from arelle.Validate import Validate


def _determineStatus(
        resultOption: str,
        expected: Any,
        userExpectedErrors: list[str],
        actualErrors: list[str],
) -> str:
    return _determineVariation(resultOption, expected, userExpectedErrors, actualErrors).status


def _determineVariation(
        resultOption: str,
        expected: Any,
        userExpectedErrors: list[str],
        actualErrors: list[str],
) -> MagicMock:
    modelXbrl = MagicMock()
    modelXbrl.modelManager.formulaOptions.testcaseResultOptions = resultOption
    modelXbrl.modelManager.formulaOptions.testcaseExpectedErrors = {"*": userExpectedErrors}
    modelXbrl.modelManager.formulaOptions.testcaseResultsCaptureWarnings = False
    modelXbrl.modelManager.cntlr.errors = []
    validator = Validate.__new__(Validate)
    validator.modelXbrl = modelXbrl
    validator.useFileSource = None
    variation = MagicMock(
        match=None,
        expected=expected,
        expectedCount=None,
        expectedReportCount=None,
        blockedMessageCodes=None,
        assertions=None,
    )
    variation.setUserExpectedErrors.return_value = userExpectedErrors
    validator.determineTestStatus(variation, list(actualErrors))
    return variation


@pytest.mark.parametrize("resultOption, expected, userExpectedErrors, actualErrors, status", [
    # Match-any ignores extra errors, so configured errors on a testcase that expects errors fail it.
    ("match-any", ["suite:required"], ["cfg:extra"], ["suite:required"], "fail"),
    ("match-any", ["suite:required"], ["cfg:extra"], ["suite:required", "cfg:extra"], "fail"),
    ("match-any", ["suite:required"], ["cfg:extra"], ["cfg:extra"], "fail"),
    ("match-any", "EFM.6.03.04", ["cfg:extra"], ["EFM.6.03.04"], "fail"),
    ("match-any", "invalid", ["cfg:extra"], ["other:error"], "fail"),
    ("match-any", ["suite:required"], [], ["suite:required"], "pass"),
    # A valid testcase with configured errors expects those errors instead.
    ("match-any", "valid", ["cfg:extra"], ["cfg:extra"], "pass"),
    ("match-any", "valid", ["cfg:extra"], [], "fail"),
    ("match-any", "valid", ["cfg:extra"], ["other:error"], "fail"),
    ("match-any", None, ["cfg:extra"], ["cfg:extra"], "pass"),
    # Match-all requires the testcase's errors and the configured errors, exactly.
    ("match-all", ["suite:required"], ["cfg:extra"], ["suite:required", "cfg:extra"], "pass"),
    ("match-all", ["suite:required"], ["cfg:extra"], ["suite:required"], "fail"),
    ("match-all", ["suite:required"], ["cfg:extra"], ["cfg:extra"], "fail"),
    ("match-all", "valid", ["cfg:extra"], ["cfg:extra"], "pass"),
    ("match-all", "valid", ["cfg:extra"], ["cfg:extra", "cfg:extra"], "fail"),
    ("match-all", "invalid", ["cfg:extra"], ["cfg:extra"], "pass"),
    # Single-string expected codes, including whitespace-separated lists.
    ("match-all", "EFM.6.03.04", ["cfg:extra"], ["EFM.6.03.04", "cfg:extra"], "pass"),
    ("match-all", "EFM.6.03.04", ["cfg:extra"], ["cfg:extra"], "fail"),
    ("match-all", "suite:a suite:b", ["cfg:extra"], ["suite:a", "suite:b", "cfg:extra"], "pass"),
    ("match-all", "suite:a suite:b", ["cfg:extra"], ["suite:a", "cfg:extra"], "fail"),
])
def test_determineTestStatus_userExpectedErrors(
        resultOption: str,
        expected: Any,
        userExpectedErrors: list[str],
        actualErrors: list[str],
        status: str,
) -> None:
    assert _determineStatus(resultOption, expected, userExpectedErrors, actualErrors) == status


@pytest.mark.parametrize("resultOption, expected, userExpectedErrors, unused", [
    ("match-any", ["suite:required"], ["cfg:extra"], True),
    ("match-any", "invalid", ["cfg:extra"], True),
    ("match-any", ["suite:required"], [], False),
    ("match-any", "valid", ["cfg:extra"], False),
    ("match-any", None, ["cfg:extra"], False),
    ("match-all", ["suite:required"], ["cfg:extra"], False),
])
def test_determineTestStatus_userExpectedErrorsUnused(
        resultOption: str,
        expected: Any,
        userExpectedErrors: list[str],
        unused: bool,
) -> None:
    variation = _determineVariation(resultOption, expected, userExpectedErrors, ["other:error"])
    assert ("conf:testcaseExpectedErrorsUnused" in variation.actual) is unused


ASSERTION_RESULTS = {"assertion1": (1, 0)}


@pytest.mark.parametrize("resultOption, expected, userExpectedErrors, actualErrors, status", [
    # A single expected code string, with or without configured errors.
    ("match-all", "EFM.6.03.04", [], ["EFM.6.03.04"], "pass"),
    ("match-all", "EFM.6.03.04", [], ["EFM.6.03.04", "other:error"], "fail"),
    ("match-all", "EFM.6.03.04", [], [], "fail"),
    # Expected formula assertion counts, with or without configured errors.
    ("match-all", ASSERTION_RESULTS, [], [ASSERTION_RESULTS], "pass"),
    ("match-all", ASSERTION_RESULTS, [], [{"assertion1": (0, 1)}], "fail"),
    ("match-all", ASSERTION_RESULTS, [], [ASSERTION_RESULTS, "other:error"], "fail"),
    ("match-all", ASSERTION_RESULTS, ["cfg:extra"], [ASSERTION_RESULTS, "cfg:extra"], "pass"),
    ("match-all", ASSERTION_RESULTS, ["cfg:extra"], [ASSERTION_RESULTS], "fail"),
    ("match-any", ASSERTION_RESULTS, [], [ASSERTION_RESULTS], "pass"),
    # Assertion results reported alongside expected error codes are not counted.
    ("match-all", ["suite:required"], [], ["suite:required", ASSERTION_RESULTS], "pass"),
])
def test_determineTestStatus_nonListExpected(
        resultOption: str,
        expected: Any,
        userExpectedErrors: list[str],
        actualErrors: list[Any],
        status: str,
) -> None:
    assert _determineStatus(resultOption, expected, userExpectedErrors, actualErrors) == status
