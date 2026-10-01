"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from arelle import CompareInstance


def test_compareInstance_expectedFactMissingValues() -> None:
    expectedFact = MagicMock(xValue="expected")
    targetFact = MagicMock(xValue="extracted")
    expectedInstance = MagicMock(facts=[expectedFact])
    expectedInstance.modelManager.cntlr.plugins.hooks.return_value = []
    targetInstance = MagicMock(facts=[targetFact])
    targetInstance.matchFact.return_value = None
    targetInstance.factsByQname.get.return_value = {targetFact}
    with patch.object(CompareInstance, "ModelRelationshipSet"):
        CompareInstance._compareInstance(MagicMock(), expectedInstance, targetInstance, matchById=False)
    targetInstance.error.assert_called_once()
    assert targetInstance.error.call_args.kwargs["value1"] == "extracted"
    assert targetInstance.error.call_args.kwargs["value2"] == "expected"
