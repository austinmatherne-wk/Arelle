'''
This plug-in provides an error code when a testcase variation does not load any iXBRL document.

See COPYRIGHT.md for copyright information.
'''
from arelle.ModelDocument import Type
from arelle.Version import authorLabel, copyrightLabel

def variationInstanceLoaded(testcaseInstance, variationInstance, extraErrors, inputDTSes, *args, **kwargs):
    # test case variations which have xhtml documents which are not inline blissfully load as unrecognized plain xml
    # provide an error code that no iXBRL document was loaded so test case script can honor variation's expectation that this is an error
    for inputDTS in inputDTSes.values():
        for ixds in inputDTS:
            if ixds.modelDocument.type not in (Type.INLINEXBRL, Type.INLINEXBRLDOCUMENTSET):
                extraErrors.append( "NotAnIxbrlDocument" )

__pluginInfo__ = {
    "name": "Testcase report variations without inline XBRL documents",
    "version": "0.9",
    "description": "Reports testcase variations that load no iXBRL document.",
    "license": "Apache-2",
    "author": authorLabel,
    "copyright": copyrightLabel,
    # classes of mount points (required)
    "TestcaseVariation.Validated": variationInstanceLoaded,
}
