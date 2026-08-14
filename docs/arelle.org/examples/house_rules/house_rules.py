"""
An example Arelle validation rule, published on arelle.org.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from arelle.ValidateXbrl import ValidateXbrl
from arelle.utils.PluginData import PluginData
from arelle.utils.PluginHooks import ValidationHook
from arelle.utils.validate.Decorator import validation
from arelle.utils.validate.Validation import Validation

from .DisclosureSystems import DISCLOSURE_SYSTEM_HOUSE_RULES


# include start
@validation(
    hook=ValidationHook.XBRL_FINALLY,
    disclosureSystems=DISCLOSURE_SYSTEM_HOUSE_RULES,
)
def ruleMandatoryConcept(
    pluginData: PluginData,
    val: ValidateXbrl,
    *args: Any,
    **kwargs: Any,
) -> Iterable[Validation]:
    mandatoryConcept = "AuditReport"
    if mandatoryConcept not in val.modelXbrl.factsByLocalName:
        yield Validation.error(
            codes="house.01.01",
            msg=f"{mandatoryConcept} must be reported.",
            modelObject=val.modelXbrl,
        )
# include end
