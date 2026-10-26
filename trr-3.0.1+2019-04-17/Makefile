BIN = ../spec/common/bin
JAVA_APP=saxon9.jar
DATE=$(shell date '+%F')
REV=$(shell svn info | grep 'Last Changed Rev:' | sed 's/Last Changed Rev: //')
SPEC_NAME=inlineXBRL-transformationRegistry
DIST_DIR=${SPEC_NAME}-${DATE}-r${REV}
EXCLUDE='*/Makefile' '*/common/*' '*/boilerplate/*' '*/spec/*' '*/inlineXBRL-transformationRegistry.*' '*/styles.css'
TESTS_DIR=conformance-tests

all: build

help:	
	@echo "make                                           Generate this version of the registry document"
	@echo "make inlineXBRL-transformationRegistry.html    Generate this version of the registry document"
	@echo ""
	@echo "make clean                                     Remove all generated output files"
	@echo "make dist                                      Produce a zip from a clean SVN checkout"
	@echo "make help                                      This help message"

%.html:	%.xml
	./build.sh ${SPEC_NAME}

testcase:
	java -jar ${BIN}/${JAVA_APP} ${TESTS_DIR}/tests.xml ${TESTS_DIR}/extractTestcase.xsl  > ${TESTS_DIR}/testcase.xml

build: ${SPEC_NAME}/${SPEC_NAME}.html testcase

clean:	
	rm -rf ${SPEC_NAME}.html location.txt build
	rm -f ${TESTS_DIR}/testcase.xml 

export: clean
	svn export -r ${REV} . build/${DIST_DIR}
	svn export -r ${REV} ../spec build/spec
	svn export -r ${REV} ${SPEC_NAME}.xml build/${DIST_DIR}/${SPEC_NAME}.xml

dist: export build/${DIST_DIR}/${SPEC_NAME}.html
	cp build/spec/styles.css build/${DIST_DIR}/
	mkdir -p pub
	cd build; zip -r ${DIST_DIR}.zip ${DIST_DIR} -x ${EXCLUDE}; mv ${DIST_DIR}.zip ../pub
	@echo ""
	@echo "Zip file available at pub/${DIST_DIR}.zip"


.PHONY: help clean export dist
