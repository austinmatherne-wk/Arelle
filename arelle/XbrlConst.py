"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, cast

import regex as re

from arelle.ModelValue import QName, qname, qnameNsLocalName
from arelle.typing import TypeGetText
from arelle.utils.deprecation import ModuleDeprecations

if TYPE_CHECKING:
    from arelle.ModelObject import ModelObject

_: TypeGetText


# Not a normative XBRL constant, but a value used internally in Arelle
# to represent the default/unspecified target name in multi-target filings.
DEFAULT_TARGET = "(default)"


xsd = "http://www.w3.org/2001/XMLSchema"
qnXsdComplexType = QName("xsd", "http://www.w3.org/2001/XMLSchema", "complexType")
qnXsdDocumentation = QName("xsd", "http://www.w3.org/2001/XMLSchema", "documentation")
qnXsdInclude = QName("xsd", "http://www.w3.org/2001/XMLSchema", "include")
qnXsdImport = QName("xsd", "http://www.w3.org/2001/XMLSchema", "import")
qnXsdSchema = QName("xsd", "http://www.w3.org/2001/XMLSchema", "schema")
qnXsdAppinfo = QName("xsd", "http://www.w3.org/2001/XMLSchema", "appinfo")
qnXsdDefaultType = QName("xsd", "http://www.w3.org/2001/XMLSchema", "anyType")
qnXsdElement = QName("xsd", "http://www.w3.org/2001/XMLSchema", "element")
qnXsdAttribute = QName("xsd", "http://www.w3.org/2001/XMLSchema", "attribute")
xsi = "http://www.w3.org/2001/XMLSchema-instance"
qnXsiNil = QName("xsi", xsi, "nil")
qnXsiType = QName("xsi", xsi, "type")
qnXsiSchemaLocation = QName("xsi", xsi, "schemaLocation")
qnXsiNoNamespaceSchemaLocation = QName("xsi", xsi, "noNamespaceSchemaLocation")
qnXmlLang = QName("xml", "http://www.w3.org/XML/1998/namespace", "lang")
builtinAttributes = frozenset({
    qnXsiNil,
    qnXsiType,
    qnXsiSchemaLocation,
    qnXsiNoNamespaceSchemaLocation,
})
ref2004 = "http://www.xbrl.org/2004/ref"
ref2006 = "http://www.xbrl.org/2006/ref"
svg = "http://www.w3.org/2000/svg"
xml = "http://www.w3.org/XML/1998/namespace"
xbrli = "http://www.xbrl.org/2003/instance"
xhtmlBaseIdentifier = "{http://www.w3.org/1999/xhtml}base"
xmlBaseIdentifier = "{http://www.w3.org/XML/1998/namespace}base"
eurofilingModelNamespace = "http://www.eurofiling.info/xbrl/ext/model"
eurofilingModelPrefix = "model"
qnNsmap = qnameNsLocalName(None, "nsmap")  # artificial parent for insertion of xmlns in saving xml documents
qnXbrlScenario = qnameNsLocalName("http://www.xbrl.org/2003/instance", "scenario")
qnXbrliXbrl = QName("xbrli", "http://www.xbrl.org/2003/instance", "xbrl")
qnPrototypeXbrliXbrl = qnameNsLocalName("http://arelle.org/prototype/xbrli", "xbrl")  # prototype for inline derived xbrl instance
qnXbrliItem = QName("xbrli", "http://www.xbrl.org/2003/instance", "item")
qnXbrliNumerator = QName("xbrli", "http://www.xbrl.org/2003/instance", "numerator")
qnXbrliDenominator = QName("xbrli", "http://www.xbrl.org/2003/instance", "denominator")
qnXbrliTuple = QName("xbrli", "http://www.xbrl.org/2003/instance", "tuple")
qnXbrliContext = QName("xbrli", "http://www.xbrl.org/2003/instance", "context")
qnXbrliPeriod = QName("xbrli", "http://www.xbrl.org/2003/instance", "period")
qnXbrliStartDate = QName("xbrli", "http://www.xbrl.org/2003/instance", "startDate")
qnXbrliEndDate = QName("xbrli", "http://www.xbrl.org/2003/instance", "endDate")
qnXbrliInstant = QName("xbrli", "http://www.xbrl.org/2003/instance", "instant")
xbrliPeriodElementTags = (qnXbrliStartDate.clarkNotation, qnXbrliEndDate.clarkNotation, qnXbrliInstant.clarkNotation)
qnXbrliForever = QName("xbrli", "http://www.xbrl.org/2003/instance", "forever")
qnXbrliIdentifier = QName("xbrli", "http://www.xbrl.org/2003/instance", "identifier")
qnXbrliUnit = QName("xbrli", "http://www.xbrl.org/2003/instance", "unit")
qnXbrliStringItemType = QName("xbrli", "http://www.xbrl.org/2003/instance", "stringItemType")
qnXbrliMonetaryItemType = QName("xbrli", "http://www.xbrl.org/2003/instance", "monetaryItemType")
qnXbrliDateItemType = QName("xbrli", "http://www.xbrl.org/2003/instance", "dateItemType")
qnXbrliDurationItemType = QName("xbrli", "http://www.xbrl.org/2003/instance", "durationItemType")
qnXbrliBooleanItemType = QName("xbrli", "http://www.xbrl.org/2003/instance", "booleanItemType")
qnXbrliQNameItemType = QName("xbrli", "http://www.xbrl.org/2003/instance", "QNameItemType")
qnXbrliPure = QName("xbrli", "http://www.xbrl.org/2003/instance", "pure")
qnXbrliShares = QName("xbrli", "http://www.xbrl.org/2003/instance", "shares")
qnInvalidMeasure = QName("arelle", "http://arelle.org", "invalidMeasureQName")
qnXbrliDateUnion = QName("xbrli", "http://www.xbrl.org/2003/instance", "dateUnion")
qnDateUnionXsdTypes = [
    QName("xsd", "http://www.w3.org/2001/XMLSchema", "date"),
    QName("xsd", "http://www.w3.org/2001/XMLSchema", "dateTime"),
]
qnXbrliDecimalsUnion = QName("xbrli", "http://www.xbrl.org/2003/instance", "decimalsType")
qnXbrliPrecisionUnion = QName("xbrli", "http://www.xbrl.org/2003/instance", "precisionType")
qnXbrliNonZeroDecimalUnion = QName("xbrli", "http://www.xbrl.org/2003/instance", "nonZeroDecimal")
link = "http://www.xbrl.org/2003/linkbase"
qnLinkArcroleRef = QName("link", "http://www.xbrl.org/2003/linkbase", "arcroleRef")
qnLinkLinkbase = QName("link", "http://www.xbrl.org/2003/linkbase", "linkbase")
qnLinkLinkbaseRef = QName("link", "http://www.xbrl.org/2003/linkbase", "linkbaseRef")
qnLinkLoc = QName("link", "http://www.xbrl.org/2003/linkbase", "loc")
qnLinkLabelLink = QName("link", "http://www.xbrl.org/2003/linkbase", "labelLink")
qnLinkLabelArc = QName("link", "http://www.xbrl.org/2003/linkbase", "labelArc")
qnLinkLabel = QName("link", "http://www.xbrl.org/2003/linkbase", "label")
qnLinkReferenceLink = QName("link", "http://www.xbrl.org/2003/linkbase", "referenceLink")
qnLinkReferenceArc = QName("link", "http://www.xbrl.org/2003/linkbase", "referenceArc")
qnLinkReference = QName("link", "http://www.xbrl.org/2003/linkbase", "reference")
qnLinkRoleRef = QName("link", "http://www.xbrl.org/2003/linkbase", "roleRef")
qnLinkSchemaRef = QName("link", "http://www.xbrl.org/2003/linkbase", "schemaRef")
qnLinkPart = QName("link", "http://www.xbrl.org/2003/linkbase", "part")
qnLinkFootnoteLink = QName("link", "http://www.xbrl.org/2003/linkbase", "footnoteLink")
qnLinkFootnoteArc = QName("link", "http://www.xbrl.org/2003/linkbase", "footnoteArc")
qnLinkFootnote = QName("link", "http://www.xbrl.org/2003/linkbase", "footnote")
qnLinkPresentationLink = QName("link", "http://www.xbrl.org/2003/linkbase", "presentationLink")
qnLinkPresentationArc = QName("link", "http://www.xbrl.org/2003/linkbase", "presentationArc")
qnLinkCalculationLink = QName("link", "http://www.xbrl.org/2003/linkbase", "calculationLink")
qnLinkCalculationArc = QName("link", "http://www.xbrl.org/2003/linkbase", "calculationArc")
qnLinkDefinitionLink = QName("link", "http://www.xbrl.org/2003/linkbase", "definitionLink")
qnLinkDefinitionArc = QName("link", "http://www.xbrl.org/2003/linkbase", "definitionArc")
gen = "http://xbrl.org/2008/generic"
qnGenLink = QName("gen", "http://xbrl.org/2008/generic", "link")
qnGenArc = QName("gen", "http://xbrl.org/2008/generic", "arc")
elementReference = "http://xbrl.org/arcrole/2008/element-reference"
genReference = "http://xbrl.org/2008/reference"
qnGenReference = qnameNsLocalName("http://xbrl.org/2008/reference", "reference")
elementLabel = "http://xbrl.org/arcrole/2008/element-label"
genLabel = "http://xbrl.org/2008/label"
qnGenLabel = qnameNsLocalName("http://xbrl.org/2008/label", "label")
xbrldt = "http://xbrl.org/2005/xbrldt"
qnXbrldtClosed = QName("xbrldt", "http://xbrl.org/2005/xbrldt", "closed")
qnXbrldtHypercubeItem = QName("xbrldt", "http://xbrl.org/2005/xbrldt", "hypercubeItem")
qnXbrldtDimensionItem = QName("xbrldt", "http://xbrl.org/2005/xbrldt", "dimensionItem")
qnXbrldtContextElement = QName("xbrldt", "http://xbrl.org/2005/xbrldt", "contextElement")
xbrldi = "http://xbrl.org/2006/xbrldi"
qnXbrldiExplicitMember = QName("xbrldi", "http://xbrl.org/2006/xbrldi", "explicitMember")
qnXbrldiTypedMember = QName("xbrldi", "http://xbrl.org/2006/xbrldi", "typedMember")
xlink = "http://www.w3.org/1999/xlink"
qnXlinkArcRole = QName("xlink", "http://www.w3.org/1999/xlink", "arcrole")
qnXlinkFrom = QName("xlink", "http://www.w3.org/1999/xlink", "from")
qnXlinkHref = QName("xlink", "http://www.w3.org/1999/xlink", "href")
qnXlinkLabel = QName("xlink", "http://www.w3.org/1999/xlink", "label")
qnXlinkRole = QName("xlink", "http://www.w3.org/1999/xlink", "role")
qnXlinkTo = QName("xlink", "http://www.w3.org/1999/xlink", "to")
qnXlinkType = QName("xlink", "http://www.w3.org/1999/xlink", "type")
xl = "http://www.xbrl.org/2003/XLink"
qnXlExtended = QName("xl", "http://www.xbrl.org/2003/XLink", "extended")
qnXlLocator = QName("xl", "http://www.xbrl.org/2003/XLink", "locator")
qnXlResource = QName("xl", "http://www.xbrl.org/2003/XLink", "resource")
qnXlExtendedType = QName("xl", "http://www.xbrl.org/2003/XLink", "extendedType")
qnXlLocatorType = QName("xl", "http://www.xbrl.org/2003/XLink", "locatorType")
qnXlResourceType = QName("xl", "http://www.xbrl.org/2003/XLink", "resourceType")
qnXlArcType = QName("xl", "http://www.xbrl.org/2003/XLink", "arcType")
xhtml = "http://www.w3.org/1999/xhtml"
qnXhtmlMeta = qnameNsLocalName("http://www.w3.org/1999/xhtml", "meta")
qnXhtmlImg = qnameNsLocalName("http://www.w3.org/1999/xhtml", "img")
qnXhtmlDel = qnameNsLocalName("http://www.w3.org/1999/xhtml", "del")
ixbrl = "http://www.xbrl.org/2008/inlineXBRL"
ixbrl11 = "http://www.xbrl.org/2013/inlineXBRL"
ixbrlAll = frozenset({ixbrl, ixbrl11})
ixbrlTags = ("{http://www.xbrl.org/2013/inlineXBRL}*", "{http://www.xbrl.org/2008/inlineXBRL}*")
ixbrlTagPattern = re.compile("[{]http://www.xbrl.org/(2008|2013)/inlineXBRL[}]")
ixt = "http://www.xbrl.org/inlineXBRL/transformation/2010-04-20"
qnIXbrlResources = qnameNsLocalName("http://www.xbrl.org/2008/inlineXBRL", "resources")
qnIXbrlTuple = qnameNsLocalName("http://www.xbrl.org/2008/inlineXBRL", "tuple")
qnIXbrlNonNumeric = qnameNsLocalName("http://www.xbrl.org/2008/inlineXBRL", "nonNumeric")
qnIXbrlNonFraction = qnameNsLocalName("http://www.xbrl.org/2008/inlineXBRL", "nonFraction")
qnIXbrlFraction = qnameNsLocalName("http://www.xbrl.org/2008/inlineXBRL", "fraction")
qnIXbrlNumerator = qnameNsLocalName("http://www.xbrl.org/2008/inlineXBRL", "numerator")
qnIXbrlDenominator = qnameNsLocalName("http://www.xbrl.org/2008/inlineXBRL", "denominator")
qnIXbrlFootnote = qnameNsLocalName("http://www.xbrl.org/2008/inlineXBRL", "footnote")
qnIXbrl11Resources = qnameNsLocalName("http://www.xbrl.org/2013/inlineXBRL", "resources")
qnIXbrl11Tuple = qnameNsLocalName("http://www.xbrl.org/2013/inlineXBRL", "tuple")
qnIXbrl11NonNumeric = qnameNsLocalName("http://www.xbrl.org/2013/inlineXBRL", "nonNumeric")
qnIXbrl11NonFraction = qnameNsLocalName("http://www.xbrl.org/2013/inlineXBRL", "nonFraction")
qnIXbrl11Fraction = qnameNsLocalName("http://www.xbrl.org/2013/inlineXBRL", "fraction")
qnIXbrl11Numerator = qnameNsLocalName("http://www.xbrl.org/2013/inlineXBRL", "numerator")
qnIXbrl11Denominator = qnameNsLocalName("http://www.xbrl.org/2013/inlineXBRL", "denominator")
qnIXbrl11Footnote = qnameNsLocalName("http://www.xbrl.org/2013/inlineXBRL", "footnote")
qnIXbrl11Relationship = qnameNsLocalName("http://www.xbrl.org/2013/inlineXBRL", "relationship")
qnIXbrl11Hidden = qnameNsLocalName("http://www.xbrl.org/2013/inlineXBRL", "hidden")
ixAttributes = frozenset(
    qnameNsLocalName(None, n)
    for n in (
        "continuedAt",
        "escape",
        "footnoteRefs",
        "format",
        "name",
        "order",
        "scale",
        "sign",
        "target",
        "tupleRef",
        "tupleID",
    )
)
ixbrlTargetElements = frozenset({
    qnIXbrlFraction,
    qnIXbrlNonFraction,
    qnIXbrlNonNumeric,
    qnIXbrlResources,
    qnIXbrlTuple,
})
ixbrl11TargetElements = frozenset({
    qnIXbrl11Fraction,
    qnIXbrl11NonFraction,
    qnIXbrl11NonNumeric,
    qnIXbrl11Resources,
    qnIXbrl11Tuple,
})
ixbrlAllTargetElements = ixbrlTargetElements | ixbrl11TargetElements
conceptLabel = "http://www.xbrl.org/2003/arcrole/concept-label"
conceptReference = "http://www.xbrl.org/2003/arcrole/concept-reference"
footnote = "http://www.xbrl.org/2003/role/footnote"
factFootnote = "http://www.xbrl.org/2003/arcrole/fact-footnote"
factExplanatoryFact = "http://www.xbrl.org/2009/arcrole/fact-explanatoryFact"
parentChild = "http://www.xbrl.org/2003/arcrole/parent-child"
summationItem = "http://www.xbrl.org/2003/arcrole/summation-item"
summationItem11 = "https://xbrl.org/2023/arcrole/summation-item"
summationItems = (summationItem, summationItem11)
essenceAlias = "http://www.xbrl.org/2003/arcrole/essence-alias"
similarTuples = "http://www.xbrl.org/2003/arcrole/similar-tuples"
requiresElement = "http://www.xbrl.org/2003/arcrole/requires-element"
generalSpecial = "http://www.xbrl.org/2003/arcrole/general-special"
all = "http://xbrl.org/int/dim/arcrole/all"
notAll = "http://xbrl.org/int/dim/arcrole/notAll"
hypercubeDimension = "http://xbrl.org/int/dim/arcrole/hypercube-dimension"
dimensionDomain = "http://xbrl.org/int/dim/arcrole/dimension-domain"
domainMember = "http://xbrl.org/int/dim/arcrole/domain-member"
dimensionDefault = "http://xbrl.org/int/dim/arcrole/dimension-default"
defaultLinkRole = "http://www.xbrl.org/2003/role/link"
defaultGenLinkRole = "http://www.xbrl.org/2008/role/link"
iso4217 = "http://www.xbrl.org/2003/iso4217"
iso17442 = "http://standards.iso.org/iso/17442"


def qnIsoCurrency(token: str | None) -> QName | None:
    return qname(iso4217, "iso4217:" + token) if token else None


standardLabel = "http://www.xbrl.org/2003/role/label"
genStandardLabel = "http://www.xbrl.org/2008/role/label"
documentationLabel = "http://www.xbrl.org/2003/role/documentation"
genDocumentationLabel = "http://www.xbrl.org/2008/role/documentation"
standardReference = "http://www.xbrl.org/2003/role/reference"
genStandardReference = "http://www.xbrl.org/2010/role/reference"
periodStartLabel = "http://www.xbrl.org/2003/role/periodStartLabel"
periodEndLabel = "http://www.xbrl.org/2003/role/periodEndLabel"
verboseLabel = "http://www.xbrl.org/2003/role/verboseLabel"
terseLabel = "http://www.xbrl.org/2003/role/terseLabel"
conceptNameLabelRole = "XBRL-concept-name"  # fake label role to show concept QName instead of label
xlinkLinkbase = "http://www.w3.org/1999/xlink/properties/linkbase"

utr = "http://www.xbrl.org/2009/utr"


_dtrTypesStartsWith = "http://www.xbrl.org/dtr/type/"

def isDtrTypeNamespace(namespace: str | None) -> bool:
    return namespace.startswith(_dtrTypesStartsWith) if namespace else False

dtr = "http://www.xbrl.org/2009/dtr"
dtrNumeric = "http://www.xbrl.org/dtr/type/numeric"
dtrTypeNamespace_2018_01_17_CR = f"{_dtrTypesStartsWith}CR/2018-01-17"
dtrTypeNamespace_2018_07_11_CR = f"{_dtrTypesStartsWith}CR/2018-07-11"
dtrTypeNamespace_2019_04_19_CR = f"{_dtrTypesStartsWith}CR/2019-04-19"
dtrTypeNamespace_2020_01_21 = f"{_dtrTypesStartsWith}2020-01-21"
dtrTypeNamespace_2021_12_08_CR = f"{_dtrTypesStartsWith}CR/2021-12-08"
dtrTypeNamespace_2022_03_31 = f"{_dtrTypesStartsWith}2022-03-31"
dtrTypeNamespace_2023_12_20_CR = f"{_dtrTypesStartsWith}CR/2023-12-20"
dtrTypeNamespace_2024_01_31 = f"{_dtrTypesStartsWith}2024-01-31"
dtrTypeNamespace_WGWD = f"{_dtrTypesStartsWith}WGWD/YYYY-MM-DD"

_dtrTypeNamespaces2019AndNewer = frozenset({
    dtrTypeNamespace_2019_04_19_CR,
    dtrTypeNamespace_2020_01_21,
    dtrTypeNamespace_2021_12_08_CR,
    dtrTypeNamespace_2022_03_31,
    dtrTypeNamespace_2023_12_20_CR,
    dtrTypeNamespace_2024_01_31,
    dtrTypeNamespace_WGWD,
})
_dtrTypeNamespaces2018_07_11AndNewer = _dtrTypeNamespaces2019AndNewer | frozenset({dtrTypeNamespace_2018_07_11_CR})
_dtrTypeNamespacesAll = _dtrTypeNamespaces2018_07_11AndNewer | frozenset({dtrTypeNamespace_2018_01_17_CR})

dtrNoDecimalsItemTypes = frozenset(
    qnameNsLocalName(namespace, typeName)
    for namespace in _dtrTypeNamespaces2018_07_11AndNewer
    for typeName in [
        "noDecimalsMonetaryItemType",
        "nonNegativeNoDecimalsMonetaryItemType",
    ]
)
dtrPrefixedContentItemTypes = frozenset(
    qnameNsLocalName(namespace, "prefixedContentItemType")
    for namespace in _dtrTypeNamespaces2019AndNewer
)
dtrPrefixedContentTypes = frozenset(
    qnameNsLocalName(namespace, "prefixedContentType")
    for namespace in _dtrTypeNamespaces2019AndNewer
)
dtrSQNameItemTypes = frozenset(
    qnameNsLocalName(namespace, "SQNameItemType")
    for namespace in _dtrTypeNamespaces2018_07_11AndNewer
)
dtrSQNameTypes = frozenset(
    qnameNsLocalName(namespace, "SQNameType")
    for namespace in _dtrTypeNamespaces2019AndNewer
)
dtrSQNamesItemTypes = frozenset(
    qnameNsLocalName(namespace, "SQNamesItemType")
    for namespace in _dtrTypeNamespaces2019AndNewer
)
dtrSQNamesTypes = frozenset(
    qnameNsLocalName(namespace, "SQNamesType")
    for namespace in _dtrTypeNamespaces2019AndNewer
)
dtrSQNameNamesItemTypes = dtrSQNameItemTypes | dtrSQNamesItemTypes
dtrSQNameNamesTypes = dtrSQNameTypes | dtrSQNamesTypes

wgnStringItemTypeNames = frozenset({"stringItemType", "normalizedStringItemType"})
dtrNoLangItemTypeNames = frozenset({"domainItemType", "noLangTokenItemType", "noLangStringItemType"})
xsdNoLangTypeNames = frozenset({"language", "Name"})
xsdStringTypeNames = frozenset({
    "string",
    "normalizedString",
    "token",
    "language",
    "Name",
    "NCName",
    "ID",
    "IDREF",
    "IDREFS",
    "ENTITY",
    "ENTITIES",
    "NMTOKEN",
    "NMTOKENS",
})

ver10 = "http://xbrl.org/2010/versioning-base"
# 2010 names
vercb = "http://xbrl.org/2010/versioning-concept-basic"
verce = "http://xbrl.org/2010/versioning-concept-extended"
verrels = "http://xbrl.org/2010/versioning-relationship-sets"
veria = "http://xbrl.org/2010/versioning-instance-aspects"
# 2013 names
ver = "http://xbrl.org/2013/versioning-base"
vercu = "http://xbrl.org/2013/versioning-concept-use"
vercd = "http://xbrl.org/2013/versioning-concept-details"
verdim = "http://xbrl.org/2013/versioning-dimensions"

verPrefixNS: dict[str, str] = {
    "ver": ver,
    "vercu": vercu,
    "vercd": vercd,
    "verrels": verrels,
    "verdim": verdim,
}

# extended enumeration spec
enum2s = frozenset({
    "http://xbrl.org/2020/extensible-enumerations-2.0",
    "http://xbrl.org/WGWD/YYYY-MM-DD/extensible-enumerations-2.0",
})
enum_1x = frozenset({
    "http://xbrl.org/2014/extensible-enumerations",
    "http://xbrl.org/PWD/2016-10-12/extensible-enumerations-1.1",
    "http://xbrl.org/WGWD/YYYY-MM-DD/extensible-enumerations-1.1",
})
enums = enum_1x | enum2s

qnEnumerationItemType2014 = QName("enum", "http://xbrl.org/2014/extensible-enumerations", "enumerationItemType")
qnEnumerationItemType2020 = QName("enum2", "http://xbrl.org/2020/extensible-enumerations-2.0", "enumerationItemType")
qnEnumerationItemTypeYYYY = QName(
    "enum2", "http://xbrl.org/WGWD/YYYY-MM-DD/extensible-enumerations-2.0", "enumerationItemType"
)
qnEnumerationSetItemType2020 = QName(
    "enum2", "http://xbrl.org/2020/extensible-enumerations-2.0", "enumerationSetItemType"
)
qnEnumerationSetItemTypeYYYY = QName(
    "enum2", "http://xbrl.org/WGWD/YYYY-MM-DD/extensible-enumerations-2.0", "enumerationSetItemType"
)
qnEnumerationSetValDimType2020 = QName(
    "enum2", "http://xbrl.org/2020/extensible-enumerations-2.0", "setValueDimensionType"
)
qnEnumerationSetValDimTypeYYYY = QName(
    "enum2", "http://xbrl.org/WGWD/YYYY-MM-DD/extensible-enumerations-2.0", "setValueDimensionType"
)
qnEnumerationItemType11YYYY = QName(
    "enum", "http://xbrl.org/WGWD/YYYY-MM-DD/extensible-enumerations-1.1", "enumerationItemType"
)
qnEnumerationSetItemType11YYYY = QName(
    "enum", "http://xbrl.org/WGWD/YYYY-MM-DD/extensible-enumerations-1.1", "enumerationSetItemType"
)
qnEnumerationListItemType11YYYY = QName(
    "enum", "http://xbrl.org/WGWD/YYYY-MM-DD/extensible-enumerations-1.1", "enumerationListItemType"
)
qnEnumerationItemType2016 = QName(
    "enum", "http://xbrl.org/PWD/2016-10-12/extensible-enumerations-1.1", "enumerationItemType"
)
qnEnumerationsItemType2016 = QName(
    "enum", "http://xbrl.org/PWD/2016-10-12/extensible-enumerations-1.1", "enumerationsItemType"
)
qnEnumerationListItemTypes = frozenset({
    qnEnumerationListItemType11YYYY,
    qnEnumerationSetItemType11YYYY,
    qnEnumerationsItemType2016,
})
qnEnumerationSetItemTypes = frozenset({
    qnEnumerationSetItemType11YYYY,
    qnEnumerationSetItemType2020,
    qnEnumerationSetItemTypeYYYY,
})
qnEnumerationItemTypes = frozenset({
    qnEnumerationItemType2014,
    qnEnumerationItemType2020,
    qnEnumerationItemTypeYYYY,
    qnEnumerationSetItemType2020,
    qnEnumerationSetItemTypeYYYY,
    qnEnumerationItemType11YYYY,
    qnEnumerationSetItemType11YYYY,
    qnEnumerationListItemType11YYYY,
    qnEnumerationItemType2016,
    qnEnumerationsItemType2016,
})
qnEnumerationTypes = qnEnumerationItemTypes | {
    qnEnumerationSetValDimType2020,
    qnEnumerationSetValDimTypeYYYY,
}
qnEnumeration2ItemTypes = frozenset({qnEnumerationItemType2020, qnEnumerationSetItemType2020})
attrEnumerationDomain2014 = "{http://xbrl.org/2014/extensible-enumerations}domain"
attrEnumerationDomain2020 = "{http://xbrl.org/2020/extensible-enumerations-2.0}domain"
attrEnumerationDomainYYYY = "{http://xbrl.org/WGWD/YYYY-MM-DD/extensible-enumerations-2.0}domain"
attrEnumerationDomain11YYYY = "{http://xbrl.org/WGWD/YYYY-MM-DD/extensible-enumerations-1.1}domain"
attrEnumerationDomain2016 = "{http://xbrl.org/PWD/2016-10-12/extensible-enumerations-1.1}domain"
attrEnumerationLinkrole2014 = "{http://xbrl.org/2014/extensible-enumerations}linkrole"
attrEnumerationLinkrole2020 = "{http://xbrl.org/2020/extensible-enumerations-2.0}linkrole"
attrEnumerationLinkroleYYYY = "{http://xbrl.org/WGWD/YYYY-MM-DD/extensible-enumerations-2.0}linkrole"
attrEnumerationLinkrole11YYYY = "{http://xbrl.org/WGWD/YYYY-MM-DD/extensible-enumerations-1.1}linkrole"
attrEnumerationLinkrole2016 = "{http://xbrl.org/PWD/2016-10-12/extensible-enumerations-1.1}linkrole"
attrEnumerationUsable2014 = "{http://xbrl.org/2014/extensible-enumerations}headUsable"
attrEnumerationUsable2020 = "{http://xbrl.org/2020/extensible-enumerations-2.0}headUsable"
attrEnumerationUsableYYYY = "{http://xbrl.org/WGWD/YYYY-MM-DD/extensible-enumerations-2.0}headUsable"
attrEnumerationUsable11YYYY = "{http://xbrl.org/WGWD/YYYY-MM-DD/extensible-enumerations-1.1}headUsable"
attrEnumerationUsable2016 = "{http://xbrl.org/PWD/2016-10-12/extensible-enumerations-1.1}headUsable"

# formula specs
variable = "http://xbrl.org/2008/variable"
qnVariableSet = QName("variable", "http://xbrl.org/2008/variable", "variableSet")
qnVariableVariable = QName("variable", "http://xbrl.org/2008/variable", "variable")
qnVariableFilter = QName("variable", "http://xbrl.org/2008/variable", "filter")
qnVariableFilterArc = QName("variable", "http://xbrl.org/2008/variable", "variableFilterArc")
qnParameter = QName("variable", "http://xbrl.org/2008/variable", "parameter")
qnFactVariable = QName("variable", "http://xbrl.org/2008/variable", "factVariable")
qnGeneralVariable = QName("variable", "http://xbrl.org/2008/variable", "generalVariable")
qnPrecondition = QName("variable", "http://xbrl.org/2008/variable", "precondition")
qnEqualityDefinition = QName("variable", "http://xbrl.org/2008/variable", "equalityDefinition")
qnEqualityTestA = QName("aspectTest", "http://xbrl.org/2008/variable/aspectTest", "a")
qnEqualityTestB = QName("aspectTest", "http://xbrl.org/2008/variable/aspectTest", "b")
formula = "http://xbrl.org/2008/formula"
formulaTuple = "http://xbrl.org/2010/formula/tuple"
qnFormula = QName("formula", "http://xbrl.org/2008/formula", "formula")
qnTuple = QName("tuple", "http://xbrl.org/2010/formula/tuple", "tuple")
qnFormulaUncovered = QName("formula", "http://xbrl.org/2008/formula", "uncovered")
qnFormulaDimensionSAV = qnameNsLocalName("http://xbrl.org/2008/formula", "DimensionSAV")  # signal that dimension aspect should use SAV of this dimension
qnFormulaOccEmpty = qnameNsLocalName("http://xbrl.org/2008/formula", "occEmpty")  # signal that OCC aspect should omit the SAV values
ca = "http://xbrl.org/2008/assertion/consistency"
qnConsistencyAssertion = QName("ca", "http://xbrl.org/2008/assertion/consistency", "consistencyAssertion")
qnCaAspectMatchedFacts = QName("ca", "http://xbrl.org/2008/assertion/consistency", "aspect-matched-facts")
qnCaAcceptanceRadius = QName("ca:ca", "http://xbrl.org/2008/assertion/consistency", "acceptance-radius")
qnCaAbsoluteAcceptanceRadiusExpression = QName(
    "ca", "http://xbrl.org/2008/assertion/consistency", "absolute-acceptance-radius-expression"
)
qnCaProportionalAcceptanceRadiusExpression = QName(
    "ca", "http://xbrl.org/2008/assertion/consistency", "proportional-acceptance-radius-expression"
)
ea = "http://xbrl.org/2008/assertion/existence"
qnExistenceAssertion = QName("ea", "http://xbrl.org/2008/assertion/existence", "existenceAssertion")
qnEaTestExpression = qnameNsLocalName(ea, "test-expression")
va = "http://xbrl.org/2008/assertion/value"
qnValueAssertion = QName("va", "http://xbrl.org/2008/assertion/value", "valueAssertion")
qnVaTestExpression = qnameNsLocalName(va, "test-expression")
formulaStartsWith = "http://xbrl.org/arcrole/20"
equalityDefinition = "http://xbrl.org/arcrole/2008/equality-definition"
variableSet = "http://xbrl.org/arcrole/2008/variable-set"
variableSetFilter = "http://xbrl.org/arcrole/2008/variable-set-filter"
variableFilter = "http://xbrl.org/arcrole/2008/variable-filter"
variableSetPrecondition = "http://xbrl.org/arcrole/2008/variable-set-precondition"
consistencyAssertionFormula = "http://xbrl.org/arcrole/2008/consistency-assertion-formula"
consistencyAssertionParameter = "http://xbrl.org/arcrole/2008/consistency-assertion-parameter"
validation = "http://xbrl.org/2008/validation"
qnAssertion = QName("validation", "http://xbrl.org/2008/validation", "assertion")
qnVariableSetAssertion = QName("validation", "http://xbrl.org/2008/validation", "variableSetAssertion")
qnAssertionSet = QName("validation", "http://xbrl.org/2008/validation", "assertionSet")
assertionSet = "http://xbrl.org/arcrole/2008/assertion-set"
assertionUnsatisfiedSeverity = "http://xbrl.org/arcrole/2016/assertion-unsatisfied-severity"
assertionUnsatisfiedSeverity20 = "http://xbrl.org/arcrole/2022/assertion-unsatisfied-severity"
assertionUnsatisfiedSeverities = (assertionUnsatisfiedSeverity, assertionUnsatisfiedSeverity20)
qnAssertionSeverityError = QName("sev", "http://xbrl.org/2016/assertion-severity", "error")
qnAssertionSeverityWarning = QName("sev", "http://xbrl.org/2016/assertion-severity", "warning")
qnAssertionSeverityOk = QName("sev", "http://xbrl.org/2016/assertion-severity", "ok")
qnAssertionSeverityError20 = QName("sev", "http://xbrl.org/2022/assertion-severity", "error")
qnAssertionSeverityWarning20 = QName("sev", "http://xbrl.org/2022/assertion-severity", "warning")
qnAssertionSeverityOk20 = QName("sev", "http://xbrl.org/2022/assertion-severity", "ok")
qnAssertionSeverityExpression20 = QName("sev", "http://xbrl.org/2022/assertion-severity", "expression")

acf = "http://xbrl.org/2010/filter/aspect-cover"
qnAspectCover = QName("acf", "http://xbrl.org/2010/filter/aspect-cover", "aspectCover")
bf = "http://xbrl.org/2008/filter/boolean"
qnAndFilter = QName("bf", "http://xbrl.org/2008/filter/boolean", "andFilter")
qnOrFilter = QName("bf", "http://xbrl.org/2008/filter/boolean", "orFilter")
booleanFilter = "http://xbrl.org/arcrole/2008/boolean-filter"
cfi = "http://xbrl.org/2010/custom-function"
functionImplementation = "http://xbrl.org/arcrole/2010/function-implementation"
qnCustomFunctionSignature = QName("cfi", "http://xbrl.org/2008/variable", "function")
qnCustomFunctionImplementation = QName("cfi", "http://xbrl.org/2010/custom-function", "implementation")
crf = "http://xbrl.org/2010/filter/concept-relation"
qnConceptRelation = QName("crf", "http://xbrl.org/2010/filter/concept-relation", "conceptRelation")
cf = "http://xbrl.org/2008/filter/concept"
qnConceptName = QName("cf", "http://xbrl.org/2008/filter/concept", "conceptName")
qnConceptPeriodType = QName("cf", "http://xbrl.org/2008/filter/concept", "conceptPeriodType")
qnConceptBalance = QName("cf", "http://xbrl.org/2008/filter/concept", "conceptBalance")
qnConceptCustomAttribute = QName("cf", "http://xbrl.org/2008/filter/concept", "conceptCustomAttribute")
qnConceptDataType = QName("cf", "http://xbrl.org/2008/filter/concept", "conceptDataType")
qnConceptSubstitutionGroup = QName("cf", "http://xbrl.org/2008/filter/concept", "conceptSubstitutionGroup")
cfcn = "http://xbrl.org/2008/conformance/function"
df = "http://xbrl.org/2008/filter/dimension"
qnExplicitDimension = QName("df", "http://xbrl.org/2008/filter/dimension", "explicitDimension")
qnTypedDimension = QName("df", "http://xbrl.org/2008/filter/dimension", "typedDimension")
ef = "http://xbrl.org/2008/filter/entity"
qnEntityIdentifier = QName("ef", "http://xbrl.org/2008/filter/entity", "identifier")
qnEntitySpecificIdentifier = QName("ef", "http://xbrl.org/2008/filter/entity", "specificIdentifier")
qnEntitySpecificScheme = QName("ef", "http://xbrl.org/2008/filter/entity", "specificScheme")
qnEntityRegexpIdentifier = QName("ef", "http://xbrl.org/2008/filter/entity", "regexpIdentifier")
qnEntityRegexpScheme = QName("ef", "http://xbrl.org/2008/filter/entity", "regexpScheme")
function = "http://xbrl.org/2008/function"
fn = "http://www.w3.org/2005/xpath-functions"
xfi = "http://www.xbrl.org/2008/function/instance"
qnXfiRoot = QName("xfi", "http://www.xbrl.org/2008/function/instance", "root")
xff = "http://www.xbrl.org/2010/function/formula"
gf = "http://xbrl.org/2008/filter/general"
qnGeneral = QName("gf", "http://xbrl.org/2008/filter/general", "general")
instances = "http://xbrl.org/2010/variable/instance"
qnInstance = QName("instances", instances, "instance")
instanceVariable = "http://xbrl.org/arcrole/2010/instance-variable"
formulaInstance = "http://xbrl.org/arcrole/2010/formula-instance"
qnStandardInputInstance = QName("instances", instances, "standard-input-instance")
qnStandardOutputInstance = QName("instances", instances, "standard-output-instance")
mf = "http://xbrl.org/2008/filter/match"
qnMatchConcept = QName("mf", "http://xbrl.org/2008/filter/match", "matchConcept")
qnMatchDimension = QName("mf", "http://xbrl.org/2008/filter/match", "matchDimension")
qnMatchEntityIdentifier = QName("mf", "http://xbrl.org/2008/filter/match", "matchEntityIdentifier")
qnMatchLocation = QName("mf", "http://xbrl.org/2008/filter/match", "matchLocation")
qnMatchPeriod = QName("mf", "http://xbrl.org/2008/filter/match", "matchPeriod")
qnMatchSegment = QName("mf", "http://xbrl.org/2008/filter/match", "matchSegment")
qnMatchScenario = QName("mf", "http://xbrl.org/2008/filter/match", "matchScenario")
qnMatchNonXDTSegment = QName("mf", "http://xbrl.org/2008/filter/match", "matchNonXDTSegment")
qnMatchNonXDTScenario = QName("mf", "http://xbrl.org/2008/filter/match", "matchNonXDTScenario")
qnMatchUnit = QName("mf", "http://xbrl.org/2008/filter/match", "matchUnit")
msg = "http://xbrl.org/2010/message"
qnMessage = qnameNsLocalName("http://xbrl.org/2010/message", "message")
assertionSatisfiedMessage = "http://xbrl.org/arcrole/2010/assertion-satisfied-message"
assertionUnsatisfiedMessage = "http://xbrl.org/arcrole/2010/assertion-unsatisfied-message"
standardMessage = "http://www.xbrl.org/2010/role/message"
terseMessage = "http://www.xbrl.org/2010/role/terseMessage"
verboseMessage = "http://www.xbrl.org/2010/role/verboseMessage"
pf = "http://xbrl.org/2008/filter/period"
qnPeriod = QName("pf", "http://xbrl.org/2008/filter/period", "period")
qnPeriodStart = QName("pf", "http://xbrl.org/2008/filter/period", "periodStart")
qnPeriodEnd = QName("pf", "http://xbrl.org/2008/filter/period", "periodEnd")
qnPeriodInstant = QName("pf", "http://xbrl.org/2008/filter/period", "periodInstant")
qnForever = QName("pf", "http://xbrl.org/2008/filter/period", "forever")
qnInstantDuration = QName("pf", "http://xbrl.org/2008/filter/period", "instantDuration")
registry = "http://xbrl.org/2008/registry"
rf = "http://xbrl.org/2008/filter/relative"
qnRelativeFilter = QName("rf", "http://xbrl.org/2008/filter/relative", "relativeFilter")
ssf = "http://xbrl.org/2008/filter/segment-scenario"
qnSegmentFilter = QName("ssf", "http://xbrl.org/2008/filter/segment-scenario", "segment")
qnScenarioFilter = QName("ssf", "http://xbrl.org/2008/filter/segment-scenario", "scenario")
tf = "http://xbrl.org/2008/filter/tuple"
qnAncestorFilter = QName("tf", "http://xbrl.org/2008/filter/tuple", "ancestorFilter")
qnLocationFilter = QName("tf", "http://xbrl.org/2008/filter/tuple", "locationFilter")
qnParentFilter = QName("tf", "http://xbrl.org/2008/filter/tuple", "parentFilter")
qnSiblingFilter = QName("tf", "http://xbrl.org/2008/filter/tuple", "siblingFilter")
uf = "http://xbrl.org/2008/filter/unit"
qnSingleMeasure = QName("uf", "http://xbrl.org/2008/filter/unit", "singleMeasure")
qnGeneralMeasures = QName("uf", "http://xbrl.org/2008/filter/unit", "generalMeasures")
vf = "http://xbrl.org/2008/filter/value"
qnNilFilter = QName("vf", "http://xbrl.org/2008/filter/value", "nil")
qnPrecisionFilter = QName("vf", "http://xbrl.org/2008/filter/value", "precision")
xpath2err = "http://www.w3.org/2005/xqt-errors"
variablesScope = "http://xbrl.org/arcrole/2010/variables-scope"

# 2014-MM-DD current IWD
tableMMDD = "http://xbrl.org/PWD/2016-MM-DD/table"
tableModelMMDD = "http://xbrl.org/PWD/2016-MM-DD/table/model"
tableBreakdownMMDD = "http://xbrl.org/arcrole/PWD/2014-MM-DD/table-breakdown"
tableBreakdownTreeMMDD = "http://xbrl.org/arcrole/PWD/2014-MM-DD/breakdown-tree"
tableDefinitionNodeSubtreeMMDD = "http://xbrl.org/arcrole/PWD/2014-MM-DD/definition-node-subtree"
tableFilterMMDD = "http://xbrl.org/arcrole/PWD/2014-MM-DD/table-filter"
tableAspectNodeFilterMMDD = "http://xbrl.org/arcrole/PWD/2014-MM-DD/aspect-node-filter"
tableParameterMMDD = "http://xbrl.org/arcrole/PWD/2014-MM-DD/table-parameter"
qnTableTableMMDD = QName("table", "http://xbrl.org/PWD/2016-MM-DD/table", "table")
qnTableBreakdownMMDD = QName("table", "http://xbrl.org/PWD/2016-MM-DD/table", "breakdown")
qnTableRuleNodeMMDD = QName("table", "http://xbrl.org/PWD/2016-MM-DD/table", "ruleNode")
qnTableRuleSetMMDD = QName("table", "http://xbrl.org/PWD/2016-MM-DD/table", "ruleSet")
qnTableDefinitionNodeMMDD = QName("table", "http://xbrl.org/PWD/2016-MM-DD/table", "definitionNode")
qnTableClosedDefinitionNodeMMDD = QName("table", "http://xbrl.org/PWD/2016-MM-DD/table", "closedDefinitionNode")
qnTableConceptRelationshipNodeMMDD = QName("table", "http://xbrl.org/PWD/2016-MM-DD/table", "conceptRelationshipNode")
qnTableDimensionRelationshipNodeMMDD = QName(
    "table", "http://xbrl.org/PWD/2016-MM-DD/table", "dimensionRelationshipNode"
)
qnTableAspectNodeMMDD = QName("table", "http://xbrl.org/PWD/2016-MM-DD/table", "aspectNode")

# REC
table = "http://xbrl.org/2014/table"
tableModel = "http://xbrl.org/2014/table/model"
tableBreakdown = "http://xbrl.org/arcrole/2014/table-breakdown"
tableBreakdownTree = "http://xbrl.org/arcrole/2014/breakdown-tree"
tableDefinitionNodeSubtree = "http://xbrl.org/arcrole/2014/definition-node-subtree"
tableFilter = "http://xbrl.org/arcrole/2014/table-filter"
tableAspectNodeFilter = "http://xbrl.org/arcrole/2014/aspect-node-filter"
tableParameter = "http://xbrl.org/arcrole/2014/table-parameter"
qnTableTable = QName("table", "http://xbrl.org/2014/table", "table")
qnTableBreakdown = QName("table", "http://xbrl.org/2014/table", "breakdown")
qnTableRuleNode = QName("table", "http://xbrl.org/2014/table", "ruleNode")
qnTableRuleSet = QName("table", "http://xbrl.org/2014/table", "ruleSet")
qnTableDefinitionNode = QName("table", "http://xbrl.org/2014/table", "definitionNode")
qnTableClosedDefinitionNode = QName("table", "http://xbrl.org/2014/table", "closedDefinitionNode")
qnTableConceptRelationshipNode = QName("table", "http://xbrl.org/2014/table", "conceptRelationshipNode")
qnTableDimensionRelationshipNode = QName("table", "http://xbrl.org/2014/table", "dimensionRelationshipNode")
qnTableAspectNode = QName("table", "http://xbrl.org/2014/table", "aspectNode")

# current PWD 1.1
tableMMDD = "http://xbrl.org/PWD/2017-07-12/table-1.1"
tableModelMMDD = "http://xbrl.org/PWD/2017-07-12/table-1.1/model"
tableBreakdownMMDD = "http://xbrl.org/arcrole/PWD/2017-07-12/table-breakdown-1.1"
tableBreakdownTreeMMDD = "http://xbrl.org/arcrole/PWD/2017-07-12/breakdown-tree-1.1"
tableDefinitionNodeSubtreeMMDD = "http://xbrl.org/arcrole/PWD/2017-07-12/definition-node-subtree-1.1"
tableFilterMMDD = "http://xbrl.org/arcrole/PWD/2017-07-12/table-filter-1.1"
tableAspectNodeFilterMMDD = "http://xbrl.org/arcrole/PWD/2017-07-12/aspect-node-filter-1.1"
tableParameterMMDD = "http://xbrl.org/arcrole/PWD/2017-07-12/table-parameter-1.1"
qnTableTableMMDD = QName("table", "http://xbrl.org/PWD/2017-07-12/table-1.1", "table")
qnTableBreakdownMMDD = QName("table", "http://xbrl.org/PWD/2017-07-12/table-1.1", "breakdown")
qnTableRuleNodeMMDD = QName("table", "http://xbrl.org/PWD/2017-07-12/table-1.1", "ruleNode")
qnTableRuleSetMMDD = QName("table", "http://xbrl.org/PWD/2017-07-12/table-1.1", "ruleSet")
qnTableDefinitionNodeMMDD = QName("table", "http://xbrl.org/PWD/2017-07-12/table-1.1", "definitionNode")
qnTableClosedDefinitionNodeMMDD = QName("table", "http://xbrl.org/PWD/2017-07-12/table-1.1", "closedDefinitionNode")
qnTableConceptRelationshipNodeMMDD = QName("table", "http://xbrl.org/PWD/2017-07-12/table-1.1", "conceptRelationshipNode")
qnTableDimensionRelationshipNodeMMDD = QName("table", "http://xbrl.org/PWD/2017-07-12/table-1.1", "dimensionRelationshipNode")
qnTableAspectNodeMMDD = QName("table", "http://xbrl.org/PWD/2017-07-12/table-1.1", "aspectNode")

booleanValueTrue = "true"
booleanValueFalse = "false"

# Eurofiling 2010 table linkbase
euRend = "http://www.eurofiling.info/2010/rendering"
euTableAxis = "http://www.eurofiling.info/arcrole/2010/table-axis"
euAxisMember = "http://www.eurofiling.info/arcrole/2010/axis-member"
qnEuTable = QName("rendering", "http://www.eurofiling.info/2010/rendering", "table")
qnEuAxisCoord = QName("rendering", "http://www.eurofiling.info/2010/rendering", "axisCoord")
euGroupTable = "http://www.eurofiling.info/xbrl/arcrole/group-table"

# Anchoring (ESEF and allowed by SEC)
widerNarrower = "http://www.esma.europa.eu/xbrl/esef/arcrole/wider-narrower"

xdtSchemaErrorNS = "http://www.xbrl.org/2005/genericXmlSchemaError"
errMsgPrefixNS = {  # err prefixes which are not declared, such as XPath's "err" prefix
    "err": xpath2err,
    "xmlSchema": xdtSchemaErrorNS,
    "utre": "http://www.xbrl.org/2009/utr/errors",
}

# Filing Indicators
qnEuFiTuple = QName("ef-find", "http://www.eurofiling.info/xbrl/ext/filing-indicators", "fIndicators")
qnEuFiIndFact = QName("ef-find", "http://www.eurofiling.info/xbrl/ext/filing-indicators", "filingIndicator")
cnEuFiIndAttr = "{http://www.eurofiling.info/xbrl/ext/filing-indicators}filed"  # clark name
qnFiFact = QName("fi", "http://www.xbrl.org/taxonomy/int/filing-indicators/REC/2021-02-03", "filed")
qnFiDim = QName("fi", "http://www.xbrl.org/taxonomy/int/filing-indicators/REC/2021-02-03", "template")

defaultLocale = "en-GB"

standardNamespaces = frozenset({xsd, xbrli, link, gen, xbrldt, xbrldi})
xsdOrXbrliNamespaces = frozenset({xsd, xbrli})

def isStandardNamespace(namespaceURI: str | None) -> bool:
    return namespaceURI in standardNamespaces

def isXsdOrXbrliNamespace(namespaceURI: str | None) -> bool:
    return namespaceURI in xsdOrXbrliNamespaces

def isUSTypesNamespace(namespaceURI: str | None) -> bool:
    return "/us-types/" in namespaceURI if namespaceURI else False

standardNamespaceSchemaLocations: dict[str, str] = {
    xbrli: "http://www.xbrl.org/2003/xbrl-instance-2003-12-31.xsd",
    link: "http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd",
    xl: "http://www.xbrl.org/2003/xl-2003-12-31.xsd",
    xlink: "http://www.xbrl.org/2003/xlink-2003-12-31.xsd",
    xbrldt: "http://www.xbrl.org/2005/xbrldt-2005.xsd",
    xbrldi: "http://www.xbrl.org/2006/xbrldi-2006.xsd",
    gen: "http://www.xbrl.org/2008/generic-link.xsd",
    genLabel: "http://www.xbrl.org/2008/generic-label.xsd",
    genReference: "http://www.xbrl.org/2008/generic-reference.xsd",
}


numericXsdTypes = frozenset({
        "integer",
        "positiveInteger",
        "negativeInteger",
        "nonNegativeInteger",
        "nonPositiveInteger",
        "long",
        "unsignedLong",
        "int",
        "unsignedInt",
        "short",
        "unsignedShort",
        "byte",
        "unsignedByte",
        "decimal",
        "float",
        "double",
    }
)
decimalXsdTypes = frozenset({
        "integer",
        "positiveInteger",
        "negativeInteger",
        "nonNegativeInteger",
        "nonPositiveInteger",
        "long",
        "unsignedLong",
        "int",
        "unsignedInt",
        "short",
        "unsignedShort",
        "byte",
        "unsignedByte",
        "decimal",
    }
)
integerXsdTypes = frozenset({
        "integer",
        "positiveInteger",
        "negativeInteger",
        "nonNegativeInteger",
        "nonPositiveInteger",
        "long",
        "unsignedLong",
        "int",
        "unsignedInt",
        "short",
        "unsignedShort",
        "byte",
        "unsignedByte",
    }
)

def isNumericXsdType(xsdType: str | None) -> bool:
    return xsdType in numericXsdTypes


def isDecimalXsdType(xsdType: str | None) -> bool:
    return xsdType in decimalXsdTypes


def isIntegerXsdType(xsdType: str | None) -> bool:
    return xsdType in integerXsdTypes


baseXbrliTypes = frozenset({
    "decimalItemType", "floatItemType", "doubleItemType", "integerItemType",
    "nonPositiveIntegerItemType", "negativeIntegerItemType", "longItemType", "intItemType",
    "shortItemType", "byteItemType", "nonNegativeIntegerItemType", "unsignedLongItemType",
    "unsignedIntItemType", "unsignedShortItemType", "unsignedByteItemType",
    "positiveIntegerItemType", "monetaryItemType", "sharesItemType", "pureItemType",
    "fractionItemType", "stringItemType", "booleanItemType", "hexBinaryItemType",
    "base64BinaryItemType", "anyURIItemType", "QNameItemType", "durationItemType",
    "dateTimeItemType", "timeItemType", "dateItemType", "gYearMonthItemType",
    "gYearItemType", "gMonthDayItemType", "gDayItemType", "gMonthItemType",
    "normalizedStringItemType", "tokenItemType", "languageItemType", "NameItemType", "NCNameItemType"
})
standardLabelRoles = frozenset({
    "http://www.xbrl.org/2003/role/label",
    "http://www.xbrl.org/2003/role/terseLabel",
    "http://www.xbrl.org/2003/role/verboseLabel",
    "http://www.xbrl.org/2003/role/positiveLabel",
    "http://www.xbrl.org/2003/role/positiveTerseLabel",
    "http://www.xbrl.org/2003/role/positiveVerboseLabel",
    "http://www.xbrl.org/2003/role/negativeLabel",
    "http://www.xbrl.org/2003/role/negativeTerseLabel",
    "http://www.xbrl.org/2003/role/negativeVerboseLabel",
    "http://www.xbrl.org/2003/role/zeroLabel",
    "http://www.xbrl.org/2003/role/zeroTerseLabel",
    "http://www.xbrl.org/2003/role/zeroVerboseLabel",
    "http://www.xbrl.org/2003/role/totalLabel",
    "http://www.xbrl.org/2003/role/periodStartLabel",
    "http://www.xbrl.org/2003/role/periodEndLabel",
    "http://www.xbrl.org/2003/role/documentation",
    "http://www.xbrl.org/2003/role/definitionGuidance",
    "http://www.xbrl.org/2003/role/disclosureGuidance",
    "http://www.xbrl.org/2003/role/presentationGuidance",
    "http://www.xbrl.org/2003/role/measurementGuidance",
    "http://www.xbrl.org/2003/role/commentaryGuidance",
    "http://www.xbrl.org/2003/role/exampleGuidance",
})
standardReferenceRoles = frozenset({
    "http://www.xbrl.org/2003/role/reference",
    "http://www.xbrl.org/2003/role/definitionRef",
    "http://www.xbrl.org/2003/role/disclosureRef",
    "http://www.xbrl.org/2003/role/mandatoryDisclosureRef",
    "http://www.xbrl.org/2003/role/recommendedDisclosureRef",
    "http://www.xbrl.org/2003/role/unspecifiedDisclosureRef",
    "http://www.xbrl.org/2003/role/presentationRef",
    "http://www.xbrl.org/2003/role/measurementRef",
    "http://www.xbrl.org/2003/role/commentaryRef",
    "http://www.xbrl.org/2003/role/exampleRef",
})
standardLinkbaseRefRoles = frozenset({
    "http://www.xbrl.org/2003/role/calculationLinkbaseRef",
    "http://www.xbrl.org/2003/role/definitionLinkbaseRef",
    "http://www.xbrl.org/2003/role/labelLinkbaseRef",
    "http://www.xbrl.org/2003/role/presentationLinkbaseRef",
    "http://www.xbrl.org/2003/role/referenceLinkbaseRef",
})
standardRoles = (
    standardLabelRoles
    | standardReferenceRoles
    | standardLinkbaseRefRoles
    | {"http://www.xbrl.org/2003/role/link", "http://www.xbrl.org/2003/role/footnote"}
)
totalRoles = frozenset({
        "http://www.xbrl.org/2003/role/totalLabel",
        "http://xbrl.us/us-gaap/role/label/negatedTotal",
        "http://www.xbrl.org/2009/role/negatedTotalLabel",
    })
netRoles = frozenset(
    {
        "http://www.xbrl.org/2009/role/netLabel",
        "http://www.xbrl.org/2009/role/negatedNetLabel"
    }
)
numericRoles = frozenset(
    {
        "http://www.xbrl.org/2003/role/totalLabel",
        "http://www.xbrl.org/2003/role/positiveLabel",
        "http://www.xbrl.org/2003/role/negativeLabel",
        "http://www.xbrl.org/2003/role/zeroLabel",
        "http://www.xbrl.org/2003/role/positiveTerseLabel",
        "http://www.xbrl.org/2003/role/negativeTerseLabel",
        "http://www.xbrl.org/2003/role/zeroTerseLabel",
        "http://www.xbrl.org/2003/role/positiveVerboseLabel",
        "http://www.xbrl.org/2003/role/negativeVerboseLabel",
        "http://www.xbrl.org/2003/role/zeroVerboseLabel",
        "http://www.xbrl.org/2009/role/negatedLabel",
        "http://www.xbrl.org/2009/role/negatedPeriodEndLabel",
        "http://www.xbrl.org/2009/role/negatedPeriodStartLabel",
        "http://www.xbrl.org/2009/role/negatedTotalLabel",
        "http://www.xbrl.org/2009/role/negatedNetLabel",
        "http://www.xbrl.org/2009/role/negatedTerseLabel",
    }
)

def isStandardRole(role: str | None) -> bool:
    return role in standardRoles


def isTotalRole(role: str | None) -> bool:
    return role in totalRoles


def isNetRole(role: str | None) -> bool:
    return role in netRoles


def isLabelRole(role: str | None) -> bool:
    return role in standardLabelRoles or role == genLabel


def isNumericRole(role: str | None) -> bool:
    return role in numericRoles


dimensionsSpecArcroles = frozenset({
    all,
    notAll,
    hypercubeDimension,
    dimensionDomain,
    domainMember,
    dimensionDefault,
})
standardDimensionArcroles = dimensionsSpecArcroles

baseSpecDefinitionArcroles =  frozenset({
    essenceAlias,
    generalSpecial,
    requiresElement,
    similarTuples,
})

standardDefinitionArcroles = baseSpecDefinitionArcroles | dimensionsSpecArcroles


standardArcroles = baseSpecDefinitionArcroles | {
        "http://www.w3.org/1999/xlink/properties/linkbase",
        "http://www.xbrl.org/2003/arcrole/concept-label",
        "http://www.xbrl.org/2003/arcrole/concept-reference",
        "http://www.xbrl.org/2003/arcrole/fact-footnote",
        "http://www.xbrl.org/2003/arcrole/parent-child",
        "http://www.xbrl.org/2003/arcrole/summation-item",
}


def isStandardArcrole(role: str) -> bool:
    return role in standardArcroles


standardArcroleCyclesAllowed: dict[str, tuple[str, str | None]] = {
    "http://www.xbrl.org/2003/arcrole/concept-label": ("any", None),
    "http://www.xbrl.org/2003/arcrole/concept-reference": ("any", None),
    "http://www.xbrl.org/2003/arcrole/fact-footnote": ("any", None),
    "http://www.xbrl.org/2003/arcrole/parent-child": ("undirected", "xbrl.5.2.4.2"),
    "http://www.xbrl.org/2003/arcrole/summation-item": ("any", "xbrl.5.2.5.2"),
    "http://www.xbrl.org/2003/arcrole/general-special": ("undirected", "xbrl.5.2.6.2.1"),
    "http://www.xbrl.org/2003/arcrole/essence-alias": ("undirected", "xbrl.5.2.6.2.1"),
    "http://www.xbrl.org/2003/arcrole/similar-tuples": ("any", "xbrl.5.2.6.2.3"),
    "http://www.xbrl.org/2003/arcrole/requires-element": ("any", "xbrl.5.2.6.2.4"),
}


def standardArcroleArcElement(arcrole: str) -> str:
    return {
        "http://www.xbrl.org/2003/arcrole/concept-label": "labelArc",
        "http://www.xbrl.org/2003/arcrole/concept-reference": "referenceArc",
        "http://www.xbrl.org/2003/arcrole/fact-footnote": "footnoteArc",
        "http://www.xbrl.org/2003/arcrole/parent-child": "presentationArc",
        "http://www.xbrl.org/2003/arcrole/summation-item": "calculationArc",
        "http://www.xbrl.org/2003/arcrole/general-special": "definitionArc",
        "http://www.xbrl.org/2003/arcrole/essence-alias": "definitionArc",
        "http://www.xbrl.org/2003/arcrole/similar-tuples": "definitionArc",
        "http://www.xbrl.org/2003/arcrole/requires-element": "definitionArc",
    }[arcrole]


def isDefinitionOrXdtArcrole(arcrole: str) -> bool:
    return arcrole in standardDefinitionArcroles


def isStandardResourceOrExtLinkElement(element: ModelObject) -> bool:
    return (
        element.namespaceURI == link
        and element.localName
        in {
            "definitionLink",
            "calculationLink",
            "presentationLink",
            "labelLink",
            "referenceLink",
            "footnoteLink",
            "label",
            "footnote",
            "reference",
        }
        or element.qname == qnIXbrl11Relationship
    )


def isStandardArcElement(element: ModelObject) -> bool:
    return (
        element.namespaceURI == link
        and element.localName
        in {"definitionArc", "calculationArc", "presentationArc", "labelArc", "referenceArc", "footnoteArc"}
        or element.qname == qnIXbrl11Relationship
    )


def isStandardArcInExtLinkElement(element: ModelObject) -> bool:
    return (
        isStandardArcElement(element) and isStandardResourceOrExtLinkElement(cast("ModelObject", element.getparent()))
    ) or element.qname == qnIXbrl11Relationship


standardExtLinkQnames = frozenset({
    qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "definitionLink"),
    qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "calculationLink"),
    qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "presentationLink"),
    qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "labelLink"),
    qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "referenceLink"),
    qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "footnoteLink"),
})

standardExtLinkQnamesAndResources = frozenset({
    qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "definitionLink"),
    qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "calculationLink"),
    qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "presentationLink"),
    qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "labelLink"),
    qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "referenceLink"),
    qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "footnoteLink"),
    qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "label"),
    qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "footnote"),
    qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "reference"),
})


def isStandardExtLinkQname(qName: QName) -> bool:
    return qName in standardExtLinkQnamesAndResources


def isStandardArcQname(qName: QName) -> bool:
    return qName in {
        qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "definitionArc"),
        qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "calculationArc"),
        qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "presentationArc"),
        qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "labelArc"),
        qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "referenceArc"),
        qnameNsLocalName("http://www.xbrl.org/2003/linkbase", "footnoteArc"),
    }


def isDimensionArcrole(arcrole: str) -> bool:
    return arcrole in dimensionsSpecArcroles


consecutiveArcrole: dict[str, str | tuple[str, ...]] = {  # can be list of or single arcrole
    all: (dimensionDomain, hypercubeDimension),
    notAll: (dimensionDomain, hypercubeDimension),
    hypercubeDimension: dimensionDomain,
    dimensionDomain: (domainMember, all, notAll),
    domainMember: (domainMember, all, notAll),
    dimensionDefault: (),
}


tableRenderingArcroles = frozenset({
    # current PWD 2013-05-17
    tableBreakdown,
    tableBreakdownTree,
    tableFilter,
    tableParameter,
    tableDefinitionNodeSubtree,
    tableAspectNodeFilter,
    # current IWD
    tableBreakdownMMDD,
    tableBreakdownTreeMMDD,
    tableFilterMMDD,
    tableParameterMMDD,
    tableDefinitionNodeSubtreeMMDD,
    tableAspectNodeFilterMMDD,
})

def isTableRenderingArcrole(arcrole: str | None) -> bool:
    return arcrole in tableRenderingArcroles


tableIndexingArcroles = frozenset({
    euGroupTable,
})

def isTableIndexingArcrole(arcrole: str | None) -> bool:
    return arcrole in tableIndexingArcroles


formulaArcroles = frozenset({
    "http://xbrl.org/arcrole/2008/assertion-set",
    "http://xbrl.org/arcrole/2008/variable-set",
    "http://xbrl.org/arcrole/2008/variable-set-filter",
    "http://xbrl.org/arcrole/2008/variable-filter",
    "http://xbrl.org/arcrole/2008/boolean-filter",
    "http://xbrl.org/arcrole/2008/variable-set-precondition",
    "http://xbrl.org/arcrole/2008/consistency-assertion-formula",
    "http://xbrl.org/arcrole/2010/function-implementation",
    "http://xbrl.org/arcrole/2010/assertion-satisfied-message",
    "http://xbrl.org/arcrole/2010/assertion-unsatisfied-message",
    "http://xbrl.org/arcrole/PR/2015-11-18/assertion-unsatisfied-severity",
    "http://xbrl.org/arcrole/2010/instance-variable",
    "http://xbrl.org/arcrole/2010/formula-instance",
    "http://xbrl.org/arcrole/2010/function-implementation",
    "http://xbrl.org/arcrole/2010/variables-scope",
})

def isFormulaArcrole(arcrole: str | None) -> bool:
    return arcrole in formulaArcroles


resourceArcroles = frozenset({
    "http://www.xbrl.org/2003/arcrole/concept-label",
    "http://www.xbrl.org/2003/arcrole/concept-reference",
    "http://www.xbrl.org/2003/arcrole/fact-footnote",
    "http://xbrl.org/arcrole/2008/element-label",
    "http://xbrl.org/arcrole/2008/element-reference",
}) | formulaArcroles


def isResourceArcrole(arcrole: str | None) -> bool:
    return arcrole in resourceArcroles


# LRR (https://specifications.xbrl.org/registries/lrr-2.0/index.html)
lrrRoleHrefs = {
    "http://www.xbrl.org/2006/role/restatedLabel": "http://www.xbrl.org/lrr/role/restated-2006-02-21.xsd#restatedLabel",
    "http://xbrl.us/us-gaap/role/label/negated": "http://www.xbrl.org/lrr/role/negated-2008-03-31.xsd#negated",
    "http://xbrl.us/us-gaap/role/label/negatedPeriodEnd": "http://www.xbrl.org/lrr/role/negated-2008-03-31.xsd#negatedPeriodEnd",
    "http://xbrl.us/us-gaap/role/label/negatedPeriodStart": "http://www.xbrl.org/lrr/role/negated-2008-03-31.xsd#negatedPeriodStart",
    "http://xbrl.us/us-gaap/role/label/negatedTotal": "http://www.xbrl.org/lrr/role/negated-2008-03-31.xsd#negatedTotal",
    "http://info.edinet-fsa.go.jp/jp/fr/gaap/role/periodStartNegativeLabel": "http://www.xbrl.org/lrr/role/jpfr-role-2007-11-07.xsd#RolePeriodStartNegativeLabel",
    "http://info.edinet-fsa.go.jp/jp/fr/gaap/role/periodEndNegativeLabel": "http://www.xbrl.org/lrr/role/jpfr-role-2007-11-07.xsd#RolePeriodEndNegativeLabel",
    "http://info.edinet-fsa.go.jp/jp/fr/gaap/role/positiveOrNegativeLabel": "http://www.xbrl.org/lrr/role/jpfr-role-2007-11-07.xsd#RolePositiveOrNegativeLabel",
    "http://info.edinet-fsa.go.jp/jp/fr/gaap/role/periodStartPositiveOrNegativeLabel": "http://www.xbrl.org/lrr/role/jpfr-role-2007-11-07.xsd#RolePeriodStartPositiveOrNegativeLabel",
    "http://info.edinet-fsa.go.jp/jp/fr/gaap/role/periodEndPositiveOrNegativeLabel": "http://www.xbrl.org/lrr/role/jpfr-role-2007-11-07.xsd#RolePeriodEndPositiveOrNegativeLabel",
    "http://info.edinet-fsa.go.jp/jp/fr/gaap/role/NotesNumber": "http://www.xbrl.org/lrr/role/jpfr-role-2007-11-07.xsd#RoleNotesNumber",
    "http://info.edinet-fsa.go.jp/jp/fr/gaap/role/NotesNumberPeriodStart": "http://www.xbrl.org/lrr/role/jpfr-role-2007-11-07.xsd#RoleNotesNumberPeriodStart",
    "http://info.edinet-fsa.go.jp/jp/fr/gaap/role/NotesNumberPeriodEnd": "http://www.xbrl.org/lrr/role/jpfr-role-2007-11-07.xsd#RoleNotesNumberPeriodEnd",
    "http://www.xbrl.org/2009/role/negatedLabel": "http://www.xbrl.org/lrr/role/negated-2009-12-16.xsd#negatedLabel",
    "http://www.xbrl.org/2009/role/negatedPeriodEndLabel": "http://www.xbrl.org/lrr/role/negated-2009-12-16.xsd#negatedPeriodEndLabel",
    "http://www.xbrl.org/2009/role/negatedPeriodStartLabel": "http://www.xbrl.org/lrr/role/negated-2009-12-16.xsd#negatedPeriodStartLabel",
    "http://www.xbrl.org/2009/role/negatedTotalLabel": "http://www.xbrl.org/lrr/role/negated-2009-12-16.xsd#negatedTotalLabel",
    "http://www.xbrl.org/2009/role/negatedNetLabel": "http://www.xbrl.org/lrr/role/negated-2009-12-16.xsd#negatedNetLabel",
    "http://www.xbrl.org/2009/role/negatedTerseLabel": "http://www.xbrl.org/lrr/role/negated-2009-12-16.xsd#negatedTerseLabel",
    "http://www.xbrl.org/2009/role/negativePeriodStartLabel": "http://www.xbrl.org/lrr/role/negative-2009-12-16.xsd#negativePeriodStartLabel",
    "http://www.xbrl.org/2009/role/negativePeriodEndLabel": "http://www.xbrl.org/lrr/role/negative-2009-12-16.xsd#negativePeriodEndLabel",
    "http://www.xbrl.org/2009/role/negativePeriodStartTotalLabel": "http://www.xbrl.org/lrr/role/negative-2009-12-16.xsd#negativePeriodStartTotalLabel",
    "http://www.xbrl.org/2009/role/negativePeriodEndTotalLabel": "http://www.xbrl.org/lrr/role/negative-2009-12-16.xsd#negativePeriodEndTotalLabel",
    "http://www.xbrl.org/2009/role/positivePeriodStartLabel": "http://www.xbrl.org/lrr/role/positive-2009-12-16.xsd#positivePeriodStartLabel",
    "http://www.xbrl.org/2009/role/positivePeriodEndLabel": "http://www.xbrl.org/lrr/role/positive-2009-12-16.xsd#positivePeriodEndLabel",
    "http://www.xbrl.org/2009/role/positivePeriodStartTotalLabel": "http://www.xbrl.org/lrr/role/positive-2009-12-16.xsd#positivePeriodStartTotalLabel",
    "http://www.xbrl.org/2009/role/positivePeriodEndTotalLabel": "http://www.xbrl.org/lrr/role/positive-2009-12-16.xsd#positivePeriodEndTotalLabel",
    "http://www.xbrl.org/2009/role/netLabel": "http://www.xbrl.org/lrr/role/net-2009-12-16.xsd#netLabel",
    "http://www.xbrl.org/2009/role/deprecatedLabel": "http://www.xbrl.org/lrr/role/deprecated-2009-12-16.xsd#deprecatedLabel",
    "http://www.xbrl.org/2009/role/deprecatedDateLabel": "http://www.xbrl.org/lrr/role/deprecated-2009-12-16.xsd#deprecatedDateLabel",
    "http://www.xbrl.org/2009/role/commonPracticeRef": "http://www.xbrl.org/lrr/role/reference-2009-12-16.xsd#commonPracticeRef",
    "http://www.xbrl.org/2009/role/nonauthoritativeLiteratureRef": "http://www.xbrl.org/lrr/role/reference-2009-12-16.xsd#nonauthoritativeLiteratureRef",
    "http://www.xbrl.org/2009/role/recognitionRef": "http://www.xbrl.org/lrr/role/reference-2009-12-16.xsd#recognitionRef",
}
lrrArcroleHrefs = {
    "http://info.edinet-fsa.go.jp/jp/fr/gaap/arcrole/Gross-Net": "http://www.xbrl.org/lrr/arcrole/jpfr-arcrole-2007-11-07.xsd#ArcroleGrossNet",
    "http://info.edinet-fsa.go.jp/jp/fr/gaap/arcrole/Gross-Allowance": "http://www.xbrl.org/lrr/arcrole/jpfr-arcrole-2007-11-07.xsd#ArcroleGrossAllowance",
    "http://info.edinet-fsa.go.jp/jp/fr/gaap/arcrole/Gross-AccumulatedDepreciation": "http://www.xbrl.org/lrr/arcrole/jpfr-arcrole-2007-11-07.xsd#ArcroleGrossAccumulatedDepreciation",
    "http://info.edinet-fsa.go.jp/jp/fr/gaap/arcrole/Gross-AccumulatedImpairmentLoss": "http://www.xbrl.org/lrr/arcrole/jpfr-arcrole-2007-11-07.xsd#ArcroleGrossAccumulatedImpairmentLoss",
    "http://info.edinet-fsa.go.jp/jp/fr/gaap/arcrole/Gross-AccumulatedDepreciationAndImpairmentLoss": "http://www.xbrl.org/lrr/arcrole/jpfr-arcrole-2007-11-07.xsd#ArcroleGrossAccumulatedDepreciationAndImpairmentLoss",
    "http://www.xbrl.org/2009/arcrole/fact-explanatoryFact": "http://www.xbrl.org/lrr/arcrole/factExplanatory-2009-12-16.xsd#fact-explanatoryFact",
    "http://www.xbrl.org/2009/arcrole/dep-concept-deprecatedConcept": "http://www.xbrl.org/lrr/arcrole/deprecated-2009-12-16.xsd#dep-concept-deprecatedConcept",
    "http://www.xbrl.org/2009/arcrole/dep-aggregateConcept-deprecatedPartConcept": "http://www.xbrl.org/lrr/arcrole/deprecated-2009-12-16.xsd#dep-aggregateConcept-deprecatedPartConcept",
    "http://www.xbrl.org/2009/arcrole/dep-dimensionallyQualifiedConcept-deprecatedConcept": "http://www.xbrl.org/lrr/arcrole/deprecated-2009-12-16.xsd#dep-dimensionallyQualifiedConcept-deprecatedConcept",
    "http://www.xbrl.org/2009/arcrole/dep-mutuallyExclusiveConcept-deprecatedConcept": "http://www.xbrl.org/lrr/arcrole/deprecated-2009-12-16.xsd#dep-mutuallyExclusiveConcept-deprecatedConcept",
    "http://www.xbrl.org/2009/arcrole/dep-partConcept-deprecatedAggregateConcept": "http://www.xbrl.org/lrr/arcrole/deprecated-2009-12-16.xsd#dep-partConcept-deprecatedAggregateConcept",
    "http://www.xbrl.org/2013/arcrole/parent-child": "http://www.xbrl.org/lrr/arcrole/parent-child-2013-09-19.xsd#parent-child",
    "http://www.esma.europa.eu/xbrl/esef/arcrole/wider-narrower": "http://www.xbrl.org/lrr/arcrole/esma-arcrole-2018-11-21.xsd#wider-narrower",
}
lrrUnapprovedRoles = {  # lrr entries which are not REC or ACK status
    "http://info.edinet-fsa.go.jp/jp/fr/gaap/role/NotesNumber": "IWD",
    "http://info.edinet-fsa.go.jp/jp/fr/gaap/role/NotesNumberPeriodStart": "IWD",
    "http://info.edinet-fsa.go.jp/jp/fr/gaap/role/NotesNumberPeriodEnd": "IWD",
    # proposed but commented out in lrr
    "http://www.xbrl.org/2013/arcrole/item-enumeration": "PROPOSED",
    # only for test case use
    "http://www.xbrl.org/2005/role/nieRole": "NIE",
}
lrrUnapprovedArcroles = {  # lrr entries which are not REC or ACK status
    # only for test case use
    "http://www.xbrl.org/2005/arcrole/nieRole": "NIE",
}


_DEPRECATIONS = ModuleDeprecations(__name__)
_DEPRECATIONS.add("tuple", formulaTuple, "use XbrlConst.formulaTuple instead.")
_DEPRECATIONS.add("dimStartsWith", "http://xbrl.org/int/dim", "use XbrlConst.isDimensionArcrole() instead.")
_DEPRECATIONS.add("dtrTypesStartsWith", _dtrTypesStartsWith, "use XbrlConst.isDtrTypeNamespace() instead.")


def __getattr__(name: str) -> Any:
    return _DEPRECATIONS.resolve(name)
