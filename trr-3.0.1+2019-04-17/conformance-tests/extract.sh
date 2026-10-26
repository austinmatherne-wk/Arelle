#!/bin/bash


if [ "$1" != "valid" ] && [ "$1" != "invalid" ] ; then
    cat <<EOF

Usage: $0 ( valid | invalid )

Produces an XML document containing a list of all valid or invalid test inputs
defined in the conformance suite.

EOF
    exit 1
fi

java -jar ../../spec/common/bin/saxon9.jar tests.xml extractVariations.xsl result=$1 
