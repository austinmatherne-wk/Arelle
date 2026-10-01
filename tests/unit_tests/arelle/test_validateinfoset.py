"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from arelle import ValidateInfoset
from arelle.ModelDocument import Type

PTV = "{http://www.xbrl.org/2003/ptv}"


def _validateInstanceInfoset(ptvAttributes: dict[str, str], instInferred: str, infosetInferred: str) -> MagicMock:
    instFact = MagicMock(isTuple=False, isItem=True)
    infosetFact = MagicMock(isTuple=False, isItem=True, qname=instFact.qname)
    infosetFact.get.side_effect = lambda name: ptvAttributes.get(name)
    modelXbrl = MagicMock(facts=[instFact], factsInInstance=[instFact])
    infosetModelXbrl = MagicMock(facts=[infosetFact], factsInInstance=[infosetFact])
    infosetModelXbrl.modelDocument.type = Type.INSTANCE
    inferred = {id(instFact): instInferred, id(infosetFact): infosetInferred}
    with (
        patch.object(ValidateInfoset, "inferredDecimals", side_effect=lambda f: inferred[id(f)]),
        patch.object(ValidateInfoset, "inferredPrecision", side_effect=lambda f: inferred[id(f)]),
    ):
        ValidateInfoset.validate(MagicMock(), modelXbrl, infosetModelXbrl)
    return modelXbrl


@pytest.mark.parametrize("ptvAttributes", [
    {f"{PTV}decimals": "2"},
    {f"{PTV}precision": "2"},
])
@pytest.mark.parametrize("instInferred, infosetInferred, mismatch", [
    ("2", "2", False),
    ("3", "2", True),
    ("2", "3", False),
])
def test_validate_inferredAccuracyUsesInstanceFact(
        ptvAttributes: dict[str, str],
        instInferred: str,
        infosetInferred: str,
        mismatch: bool,
) -> None:
    modelXbrl = _validateInstanceInfoset(ptvAttributes, instInferred, infosetInferred)
    assert modelXbrl.error.called is mismatch
