from collections import defaultdict
from typing import Any
from typing_extensions import assert_type

from arelle import FunctionCustom, FunctionFn, FunctionXfi, ValidateXbrlDTS
from arelle.Aspect import Aspect
from arelle.conformance.CSVTestcaseLoader import _conformanceQName
from arelle.formula.FormulaEvaluator import VariableBinding
from arelle.formula.XPathContext import ContextItem, ResultStack, XPathContext
from arelle.formula.XPathParser import OperationDef
from arelle.ModelFormulaObject import FormulaOptions, ModelAspectCover, ModelFormulaRules
from arelle.ModelObject import ModelObject
from arelle.ModelRenderingObject import DefnMdlAspectNode
from arelle.ModelValue import QName


def check_core_qname_types(
    xc: XPathContext,
    p: OperationDef,
    context_item: ContextItem,
    args: ResultStack,
    rules: ModelFormulaRules,
    node: DefnMdlAspectNode,
    cover: ModelAspectCover,
    binding: VariableBinding,
) -> None:
    assert_type(_conformanceQName("variation"), QName)
    assert_type(ValidateXbrlDTS.xsd1_1datatypes, set[QName])
    assert_type(next(iter(FunctionCustom.customFunctions)), QName)
    assert_type(FunctionFn.node_name(xc, p, context_item, args), tuple[()] | QName | None)
    assert_type(FunctionXfi.element_name(xc, p, args), QName | None)
    assert_type(FormulaOptions().parameterValues, dict[QName | None, Any])
    assert_type(rules.aspectValues, defaultdict[int | QName | None, list[QName | None] | QName | ModelObject | str | None])
    assert_type(rules.typedDimProgAspects, set[QName | None])
    assert_type(node.aspectsCovered(), set[int | QName | None])
    assert_type(node.aspectValue(xc, Aspect.DIMENSIONS), set[QName | None] | None)
    assert_type(cover.aspectsCovered(binding, xc), set[int | QName | None])
