"""
An example Arelle validation rule, published on arelle.org.

Costs are reported as positive values, so a negative one is a sign error.
Nothing in the XBRL specifications forbids it, which is the point: the filing
is valid, and this rule catches what validity cannot.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from arelle.ValidateXbrl import ValidateXbrl
from arelle.typing import TypeGetText
from arelle.utils.PluginData import PluginData
from arelle.utils.PluginHooks import ValidationHook
from arelle.utils.validate.Decorator import validation
from arelle.utils.validate.Validation import Validation

from .DisclosureSystems import DISCLOSURE_SYSTEM_HOUSE_RULES

_: TypeGetText


# include start
@validation(
    hook=ValidationHook.XBRL_FINALLY,
    disclosureSystems=DISCLOSURE_SYSTEM_HOUSE_RULES,
)
def negativeCost(
    pluginData: PluginData,
    val: ValidateXbrl,
    *args: Any,
    **kwargs: Any,
) -> Iterable[Validation]:
    for fact in val.modelXbrl.facts:
        if fact.isNil or not fact.isNumeric or fact.concept.balance != "debit":
            continue
        if fact.xValue < 0:
            yield Validation.error(
                codes="house.01.01",
                msg=_("%(concept)s is a cost and must not be negative, "
                      "but was reported as %(value)s."),
                modelObject=fact,
                concept=fact.qname,
                value=fact.effectiveValue,
            )
# include end
