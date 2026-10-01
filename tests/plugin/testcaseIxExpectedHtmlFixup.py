'''
This plug-in resolves relative URIs in escaped html of expected instance footnotes
the same way inline XBRL extraction does.

It also provides an error code when a testcase variation does not load any iXBRL document.

See COPYRIGHT.md for copyright information.
'''
from arelle.ModelDocument import Type
from arelle.Version import authorLabel, copyrightLabel
from arelle.XhtmlInlineUtil import htmlEltUriAttrs, resolveHtmlUri

def variationInstanceLoaded(testcaseInstance, variationInstance, extraErrors, inputDTSes, *args, **kwargs):
    # test case variations which have xhtml documents which are not inline blissfully load as unrecognized plain xml
    # provide an error code that no iXBRL document was loaded so test case script can honor variation's expectation that this is an error
    for inputDTS in inputDTSes.values():
        for ixds in inputDTS:
            if ixds.modelDocument.type not in (Type.INLINEXBRL, Type.INLINEXBRLDOCUMENTSET):
                extraErrors.append( "NotAnIxbrlDocument" )

def compareInstanceLoaded(expectedInstance, outputInstanceToCompare):
    # fixup relative urls in fact footnotes
    for elt in expectedInstance.modelDocument.xmlRootElement.iterdescendants(tag="{http://www.w3.org/1999/xhtml}*"):
        for n in htmlEltUriAttrs.get(elt.localName, ()):
            v = elt.get(n)
            if v:
                v = resolveHtmlUri(elt, n, v).replace(" ", "%20")
                elt.set(n, v)

__pluginInfo__ = {
    "name": "Testcase fixup expected inline XBRL output",
    "version": "0.9",
    "description": "Resolves relative URIs in expected escaped html and reports testcase variations that load no iXBRL document.",
    "license": "Apache-2",
    "author": authorLabel,
    "copyright": copyrightLabel,
    # classes of mount points (required)
    "CompareInstance.Loaded": compareInstanceLoaded,
    "TestcaseVariation.Validated": variationInstanceLoaded,
}
