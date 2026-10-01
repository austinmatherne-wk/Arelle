"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from arelle import XbrlConst
from arelle.ModelDocument import Type
from arelle.plugin import inlineXbrlDocumentSet


def _modelXbrl(docType: int | None, rootTag: str | None = None, hasGui: bool = False, config: dict | None = None) -> MagicMock:
    modelXbrl = MagicMock()
    if docType is None:
        modelXbrl.modelDocument = None
    else:
        modelXbrl.modelDocument = SimpleNamespace(type=docType)
        if rootTag is not None:
            modelXbrl.modelDocument.xmlRootElement = SimpleNamespace(tag=rootTag)
    modelXbrl.modelManager.cntlr.hasGui = hasGui
    modelXbrl.modelManager.cntlr.config = config or {}
    return modelXbrl


@pytest.fixture
def validateAllFilesAsInlineXbrl(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(inlineXbrlDocumentSet, "validateAllFilesAsInlineXbrl", True)


@pytest.mark.usefixtures("validateAllFilesAsInlineXbrl")
@pytest.mark.parametrize(
    "docType, rootTag, expectedCode",
    [
        (Type.UnknownXML, f"{{{XbrlConst.xhtml}}}html", "ix11.8.1.3:missingHeader"),
        (Type.UnknownXML, "body", "ix11.3.3.1:rootElement"),
        (Type.UnknownXML, "html", "ix11.3.3.1:rootElement"),
        (Type.INSTANCE, f"{{{XbrlConst.xbrli}}}xbrl", "ix11.3.3.1:rootElement"),
        (Type.UnknownNonXML, None, "ix11.3.3.1:rootElement"),
    ],
)
def test_reportNonInlineXbrlEntry_reportsError(docType: int, rootTag: str | None, expectedCode: str) -> None:
    modelXbrl = _modelXbrl(docType, rootTag)
    inlineXbrlDocumentSet.reportNonInlineXbrlEntry(modelXbrl)
    modelXbrl.error.assert_called_once()
    assert modelXbrl.error.call_args.args[0] == expectedCode


@pytest.mark.usefixtures("validateAllFilesAsInlineXbrl")
@pytest.mark.parametrize(
    "docType",
    [None, Type.INLINEXBRL, Type.INLINEXBRLDOCUMENTSET, Type.RSSFEED, *Type.TESTCASETYPES],
)
def test_reportNonInlineXbrlEntry_ignoresInlineAndContainerEntries(docType: int | None) -> None:
    modelXbrl = _modelXbrl(docType, "body")
    inlineXbrlDocumentSet.reportNonInlineXbrlEntry(modelXbrl)
    modelXbrl.error.assert_not_called()


def test_reportNonInlineXbrlEntry_optionOff() -> None:
    modelXbrl = _modelXbrl(Type.UnknownXML, "body")
    inlineXbrlDocumentSet.reportNonInlineXbrlEntry(modelXbrl)
    modelXbrl.error.assert_not_called()


@pytest.mark.parametrize("configValue, expectError", [(True, True), (False, False)])
def test_reportNonInlineXbrlEntry_guiUsesConfig(configValue: bool, expectError: bool) -> None:
    modelXbrl = _modelXbrl(Type.UnknownXML, "body", hasGui=True, config={"validateAllFilesAsInlineXbrl": configValue})
    inlineXbrlDocumentSet.reportNonInlineXbrlEntry(modelXbrl)
    assert modelXbrl.error.called == expectError


@pytest.mark.parametrize("optionValue", [True, False])
def test_commandLineUtilityRun_setsOption(monkeypatch: pytest.MonkeyPatch, optionValue: bool) -> None:
    monkeypatch.setattr(inlineXbrlDocumentSet, "validateAllFilesAsInlineXbrl", not optionValue)
    inlineXbrlDocumentSet.commandLineUtilityRun(MagicMock(), SimpleNamespace(validateAllFilesAsInlineXbrl=optionValue))
    assert inlineXbrlDocumentSet.validateAllFilesAsInlineXbrl is optionValue
