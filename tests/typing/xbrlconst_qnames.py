"""
See COPYRIGHT.md for copyright information.
"""
from typing_extensions import assert_type

from arelle import XbrlConst
from arelle.ModelValue import QName

assert_type(XbrlConst.qnXsdSchema, QName)
assert_type(XbrlConst.qnXsiNil, QName)
assert_type(XbrlConst.qnNsmap, QName)
assert_type(XbrlConst.qnXbrlScenario, QName)
assert_type(XbrlConst.qnEaTestExpression, QName)
assert_type(XbrlConst.qnCaAcceptanceRadius, QName)
assert_type(XbrlConst.qnDateUnionXsdTypes, list[QName])
assert_type(XbrlConst.builtinAttributes, frozenset[QName])
assert_type(XbrlConst.ixAttributes, frozenset[QName])
assert_type(XbrlConst.dtrNoDecimalsItemTypes, frozenset[QName])
assert_type(XbrlConst.dtrSQNameNamesItemTypes, frozenset[QName])
assert_type(XbrlConst.standardExtLinkQnames, frozenset[QName])
assert_type(XbrlConst.qnIsoCurrency("USD"), QName | None)
