README
------

ixt-reference-transforms.xsl provides a non-validating XSLT2 implementation for
all of the transforms in the registry.

ixt-reference-transforms-conformance.xsl provides a conformance suite harness,
also written in XSLT2, which runs the reference transforms over the conformance
suite. Since ixt-reference-transforms.xsl does not perform Schema validation,
invalid variations in the conformance suite are skipped.

It can be invoked as follows:

java -jar saxon9.jar ../conformance-tests/tests.xml ixt-reference-transforms-conformance.xsl > results.html
