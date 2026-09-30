"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from lxml import etree

from arelle.ModelTestcaseObject import ModelTestcaseVariation


def _calcMode(resultXml: str | None) -> str | None:
    resultElement = etree.fromstring(resultXml) if resultXml is not None else None
    with patch("arelle.ModelTestcaseObject.XmlUtil.descendant", return_value=resultElement):
        return ModelTestcaseVariation.calcMode.fget(MagicMock())  # type: ignore[attr-defined, no-any-return]


@pytest.mark.parametrize("resultXml, calcMode", [
    ('<result xmlns:c="https://xbrl.org/2023/conformance" c:mode="round-to-nearest"/>', "round-to-nearest"),
    ('<result xmlns:c="https://xbrl.org/2023/conformance" c:mode="truncate"/>', "truncate"),
    ('<result xmlns:c="https://example.com/other/conformance" c:mode="truncate"/>', "truncate"),
    ('<result mode="truncate"/>', None),
    ('<result xmlns:c="https://xbrl.org/2023/conformance" c:mode="unknown"/>', None),
    ('<result xmlns:c="https://xbrl.org/2023/conformance" c:othermode="truncate"/>', None),
    ("<result/>", None),
    (None, None),
])
def test_calcMode(resultXml: str | None, calcMode: str | None) -> None:
    assert _calcMode(resultXml) == calcMode
