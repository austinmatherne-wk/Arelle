"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from arelle.ModelInstanceObject import ModelFact


def _textFact(value: str) -> MagicMock:
    fact = MagicMock(isTuple=False, isNil=False, value=value)
    fact.concept.isNumeric = False
    fact.concept.isFraction = False
    fact.context.isEqualTo.return_value = True
    return fact


@pytest.mark.parametrize("value, otherValue, ignoreEscapedXhtmlNamespace, isVEqual", [
    ('<b xmlns="http://www.w3.org/1999/xhtml">text</b>', "<b>text</b>", True, True),
    ("<b xmlns='http://www.w3.org/1999/xhtml'>text</b>", "<b>text</b>", True, True),
    ('<a href="x" xmlns="http://www.w3.org/1999/xhtml">text</a>', '<a href="x">text</a>', True, True),
    ('<b xmlns="http://www.w3.org/1999/xhtml">text</b>', '<b xmlns="http://www.w3.org/1999/xhtml">text</b>', True, True),
    ('<b xmlns="http://www.w3.org/1999/xhtml">text</b>', "<b>text</b>", False, False),
    ('<b xmlns="http://example.com/other">text</b>', "<b>text</b>", True, False),
    ('&lt;b xmlns="http://www.w3.org/1999/xhtml"&gt;', "&lt;b&gt;", True, False),
    ('<b xmlns="http://www.w3.org/1999/xhtml">text</b>', "<b>other</b>", True, False),
])
def test_isVEqualTo_ignoreEscapedXhtmlNamespace(
        value: str,
        otherValue: str,
        ignoreEscapedXhtmlNamespace: bool,
        isVEqual: bool,
) -> None:
    result = ModelFact.isVEqualTo(
        _textFact(value),  # type: ignore[arg-type]
        _textFact(otherValue),  # type: ignore[arg-type]
        ignoreEscapedXhtmlNamespace=ignoreEscapedXhtmlNamespace,
    )
    assert result is isVEqual
