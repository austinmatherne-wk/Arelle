#!/bin/bash
java -jar ../../spec/common/bin/saxon9.jar tests.xml extractTestcase.xsl  > testcase.xml
