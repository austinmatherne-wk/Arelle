"""
See COPYRIGHT.md for copyright information.
"""
from typing_extensions import assert_type

from arelle.ModelValue import QName
from arelle.plugin import functionsMath, saveLoadableOIM
from arelle.plugin.validate.EDINET import Constants as EdinetConstants
from arelle.plugin.validate.EDINET.PluginValidationDataExtension import PluginValidationDataExtension
from arelle.plugin.validate.ESEF import Const as EsefConstants
from arelle.plugin.validate.IRD.ValidationPluginExtension import tcQn
from arelle.plugin.validate.NL.PluginValidationDataExtension import PluginValidationDataExtension as NlPluginData

assert_type(EdinetConstants.domainItemTypeQname, QName)
assert_type(EdinetConstants.qnEdinetManifestItem, QName)
assert_type(EsefConstants.PERCENT_TYPE, QName)
assert_type(EsefConstants.PERCENT_TYPES, set[QName])
assert_type(saveLoadableOIM.qnOimConceptAspect, QName)
assert_type(saveLoadableOIM.qnOimLangAspect, QName)
assert_type(saveLoadableOIM.qnOimPeriodAspect, QName)
assert_type(saveLoadableOIM.qnOimEntityAspect, QName)
assert_type(saveLoadableOIM.qnOimUnitAspect, QName)
assert_type(next(iter(functionsMath.xfmMathFunctions())), QName)
assert_type(tcQn("CompanyName"), QName)


def plugin_data_qnames(edinet: PluginValidationDataExtension, nl: NlPluginData) -> None:
    assert_type(edinet.qname("jpdei_cor", "FilerNameInJapaneseDEI"), QName)
    assert_type(edinet.accountingStandardsDeiQn, QName)
    assert_type(edinet.deiItems, tuple[QName, ...])
    assert_type(nl.mandatoryFactQNames, frozenset[QName] | None)
    assert_type(nl.permissibleGAAPRootAbstracts, frozenset[QName])
    assert_type(nl.permissibleIFRSRootAbstracts, frozenset[QName])
