#!/bin/bash
# This generates valid.xml from valid test cases in test.xml and schema validates the result.
javac SchemaConformance.java && ./extract.sh valid > valid.xml && java -cp . SchemaConformance
