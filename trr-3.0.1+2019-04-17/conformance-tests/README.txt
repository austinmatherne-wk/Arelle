README
------

* The conformance suite for the transforms is contained in a single file:
  tests.xml

* The suite conforms to the XML Schema in tests.xsd

* For display purposes, a simple XSLT 1.0 stylesheet is also included:
  tests.xsl

* Two stylesheets, with accompanying bash wrapper scripts are provided:

** extract.sh (extractVariations.xsl) creates an XML file containing all valid
   or all invalid test inputs with an xsi:type attribute indicating the input type.

** extractTestcase.sh (extractTestcase.xsl) extracts all test inputs and
   expected outputs into an XBRL conformance suite test case.

* A simple Bash script schema validates the valid test cases:
  schemaConformance.sh
