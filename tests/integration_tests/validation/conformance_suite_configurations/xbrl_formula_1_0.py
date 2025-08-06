from pathlib import PurePath, Path
from tests.integration_tests.validation.conformance_suite_config import ConformanceSuiteConfig, ConformanceSuiteAssetConfig

config = ConformanceSuiteConfig(
    assets=[
        ConformanceSuiteAssetConfig.conformance_suite(
            Path('formula.zip'),
            entry_point=Path('formula/tests/index.xml'),
        ),
    ],
    expected_testcase_errors={f"formula/tests/{s}": val for s, val in {
        "10000 Formula/11204-Formula-StaticAnalysis-sequenceSAVConflicts/11204-sequenceSAVConflicts_testcase.xml:V-02": {
            "xbrlfe:sequenceSAVConflicts": 1
        },
        "20000 Variables/21221-VariableStaticAnalysis-parameterNameClash/21221-parameterNameClash_testcase.xml:V-01": {
            "xbrlve:duplicateVariableNames": 1
        },
        "20000 Variables/21222-VariableStaticAnalysis-parameterCyclicDependencies/21222-parameterCyclicDependencies_testcase.xml:V-01": {
            "xbrlve:parameterCyclicDependencies": 2
        },
        "20000 Variables/21233-VariableStaticAnalysis-GeneralVariables/21233 General Variable Static Analysis.xml:V-02": {
            "xbrlve:unresolvedDependency": 1
        },
        "20000 Variables/21233-VariableStaticAnalysis-GeneralVariables/21233 General Variable Static Analysis.xml:V-03": {
            "xbrlve:unresolvedDependency": 2
        },
        # "20000 Variables/21251-VariableStaticAnalysis-VariableSetDuplicateNames/21251 Variable Set Duplicate Names.xml:V-04": {
        #     "assertion": -1
        # },
        "20000 Variables/21251-VariableStaticAnalysis-VariableSetDuplicateNames/21251 Variable Set Duplicate Names.xml:V-05": {
            "assertion": -1,
            "assertion2": -1
        },
        "20000 Variables/21251-VariableStaticAnalysis-VariableSetDuplicateNames/21251 Variable Set Duplicate Names.xml:V-06": {
            "assertion": -1,
            "assertion2": -1
        },
        "20000 Variables/21851-VariableStaticAnalysis-factVariableReferenceNotAllowed/21851-factVariableReferenceNotAllowed_testcase.xml:V-01": {
            "xbrlfe:bindEmptySourceVariable": 1
        },
        "20000 Variables/21851-VariableStaticAnalysis-factVariableReferenceNotAllowed/21851-factVariableReferenceNotAllowed_testcase.xml:V-02": {
            "xbrlfe:bindEmptySourceVariable": 1
        },
        "20000 Variables/21930-VariableStaticAnalysis-cyclicDependencies/21930-cyclicDependencies_testcase.xml:V-01": {
            "xbrlfe:bindEmptySourceVariable": 1,
            "xbrlve:cyclicDependencies": 2
        },
        "20000 Variables/22030-Variable-Processing-GeneralVariables/22030 General Variables.xml:V-05": {
            "assertion": -1
        },
        "20000 Variables/22040-Variable-Processing-FactVariables/22040 Fact Variables.xml:V-08": {
            "assertion": -1
        },
        "20000 Variables/22060-Variable-Processing-VariableNames/22060 Variable Names.xml:V-09": {
            "xbrlve:unresolvedDependency": 1
        },
        "20000 Variables/22170-Variable-Processing-BindAsSequence/22170 Bind As Sequence.xml:V-03b": {
            "assertion": -2
        },
        "20000 Variables/22170-Variable-Processing-BindAsSequence/22170 Bind As Sequence.xml:V-04": {
            "assertion": 1
        },
        "20000 Variables/22180-Variable-Processing-BindEmpty/22180 Bind To Empty Sequence.xml:V-20": {
            "assertion": -1
        },
        "20000 Variables/22180-Variable-Processing-BindEmpty/22180 Bind To Empty Sequence.xml:V-41": {
            "assertion": -1
        },
        "20000 Variables/22180-Variable-Processing-BindEmpty/22180 Bind To Empty Sequence.xml:V-42": {
            "assertion": -1
        },
        "20000 Variables/22180-Variable-Processing-BindEmpty/22180 Bind To Empty Sequence.xml:V-43": {
            "assertion": -1
        },
        "20000 Variables/22180-Variable-Processing-BindEmpty/22180 Bind To Empty Sequence.xml:V-51": {
            "existence-assertion": -1,
            "value-assertion": -1
        },
        "20000 Variables/22180-Variable-Processing-BindEmpty/22180 Bind To Empty Sequence.xml:V-52": {
            "existence-assertion": -1,
            "value-assertion": -1
        },
        "20000 Variables/22180-Variable-Processing-BindEmpty/22180 Bind To Empty Sequence.xml:V-53": {
            "existence-assertion": -1,
            "value-assertion": -1
        },
        "20000 Variables/22180-Variable-Processing-BindEmpty/22180 Bind To Empty Sequence.xml:V-54": {
            "existence-assertion": -1,
            "value-assertion": -1
        },
        "20000 Variables/22180-Variable-Processing-BindEmpty/22180 Bind To Empty Sequence.xml:V-55": {
            "existence-assertion": -1,
            "value-assertion": -1
        },
        "20000 Variables/22180-Variable-Processing-BindEmpty/22180 Bind To Empty Sequence.xml:V-56": {
            "existence-assertion": -1,
            "value-assertion": -1
        },
        "20000 Variables/22180-Variable-Processing-BindEmpty/22180 Bind To Empty Sequence.xml:V-57": {
            "existence-assertion": -1,
            "value-assertion": -1
        },
        "20000 Variables/23020-Variable-AspectTests-TypedDimension/23020 AspectTests TypedDimension.xml:V-01": {
            "assertion": -1
        },
        "20000 Variables/23020-Variable-AspectTests-TypedDimension/23020 AspectTests TypedDimension.xml:V-02": {
            "assertion": -1
        },
        "20000 Variables/23020-Variable-AspectTests-TypedDimension/23020 AspectTests TypedDimension.xml:V-03": {
            "assertion": -1
        },
        "20000 Variables/23020-Variable-AspectTests-TypedDimension/23020 AspectTests TypedDimension.xml:V-03a": {
            "assertion": -1
        },
        "20000 Variables/23020-Variable-AspectTests-TypedDimension/23020 AspectTests TypedDimension.xml:V-04": {
            "assertion": -1
        },
        "20000 Variables/23020-Variable-AspectTests-TypedDimension/23020 AspectTests TypedDimension.xml:V-50": {
            "assertion": -1
        },
        "20000 Variables/23020-Variable-AspectTests-TypedDimension/23020 AspectTests TypedDimension.xml:V-51": {
            "assertion": -1
        },
        "20000 Variables/23030-Variable-AspectTests-DefaultDimension/23030 AspectTests DefaultDimension.xml:V-01": {
            "assertion": -1
        },
        "30000 Assertions/31140-ConsistencyAssertion-StaticAnalysis-missingFormulae/31140 Consistency Assertion Missing Formulae.xml:V-01": {
            "assertion": -1
        },
        "30000 Assertions/32120-ExistenceAssertion-StaticAnalysis-Relationships/32120 Existence Assertion Relationship Static Analysis.xml:V-01": {
            "assertion": -1
        },
        "30000 Assertions/32210-ExistenceAssertion-Processing/32210 Existence Assertion Processing.xml:V-01": {
            "assertion": -1
        },
        "30000 Assertions/32210-ExistenceAssertion-Processing/32210 Existence Assertion Processing.xml:V-02": {
            "assertion": -1
        },
        "30000 Assertions/32210-ExistenceAssertion-Processing/32210 Existence Assertion Processing.xml:V-03": {
            "assertion": -1
        },
        "30000 Assertions/32210-ExistenceAssertion-Processing/32210 Existence Assertion Processing.xml:V-05": {
            "assertion": -1
        },
        "30000 Assertions/32210-ExistenceAssertion-Processing/32210 Existence Assertion Processing.xml:V-06": {
            "assertion": -1
        },
        "30000 Assertions/32210-ExistenceAssertion-Processing/32210 Existence Assertion Processing.xml:V-07": {
            "assertion": -1
        },
        "30000 Assertions/33210-ValueAssertion-Processing/33210 Value Assertion Processing.xml:V-01": {
            "assertion": -1
        },
        "30000 Assertions/33210-ValueAssertion-Processing/33210 Value Assertion Processing.xml:V-03": {
            "assertion": -1
        },
        "30000 Assertions/33210-ValueAssertion-Processing/33210 Value Assertion Processing.xml:V-04": {
            "assertion": -1
        },
        "30000 Assertions/33210-ValueAssertion-Processing/33210 Value Assertion Processing.xml:V-05": {
            "assertion": -1
        },
        "30000 Assertions/33210-ValueAssertion-Processing/33210 Value Assertion Processing.xml:V-06": {
            "assertion": -1
        },
        "30000 Assertions/33210-ValueAssertion-Processing/33210 Value Assertion Processing.xml:V-07": {
            "assertion": -1
        },
        "30000 Assertions/33210-ValueAssertion-Processing/33210 Value Assertion Processing.xml:V-08": {
            "dupCheck": -1
        },
        "30000 Assertions/33210-ValueAssertion-Processing/33210 Value Assertion Processing.xml:V-09": {
            "dupCheck": -1
        },
        "30000 Assertions/33210-ValueAssertion-Processing/33210 Value Assertion Processing.xml:V-13": {
            "dupCheck": -1
        },
        "30000 Assertions/33210-ValueAssertion-Processing/33210 Value Assertion Processing.xml:V-14": {
            "dupCheck": -1
        },
        "30000 Assertions/33210-ValueAssertion-Processing/33210 Value Assertion Processing.xml:V-15": {
            "dupCheck": -1
        },
        "30000 Assertions/34110-MultiAssertion-Processing/34110 Multi Assertion Processing.xml:V-02": {
            "existence_assertion": -1,
            "value_assertion": -1
        },
        "30000 Assertions/34110-MultiAssertion-Processing/34110 Multi Assertion Processing.xml:V-03": {
            "existence_assertion": -1,
            "value_assertion": -1
        },
        "30000 Assertions/34110-MultiAssertion-Processing/34110 Multi Assertion Processing.xml:V-04": {
            "existence_assertion": -1,
            "value_assertion": -1
        },
        "30000 Assertions/34110-MultiAssertion-Processing/34110 Multi Assertion Processing.xml:V-05": {
            "existence_assertion": -1,
            "value_assertion": -1
        },
        "40000 Filters/41210-BooleanFilter-Processing-And/41210 Boolean And Filter Processing.xml:V-03": {
            "assertion": -1
        },
        "40000 Filters/41220-BooleanFilter-Processing-Or/41220 Boolean Or Filter Processing.xml:V-02": {
            "assertion": -1
        },
        "40000 Filters/43130-DimensionFilter-StaticAnalysis-DimensionMember Filter/43130 DimensionMember Filter.xml:V-02": {
            "assertion": -1
        },
        "40000 Filters/43130-DimensionFilter-StaticAnalysis-DimensionMember Filter/43130 DimensionMember Filter.xml:V-03": {
            "assertion": -1
        },
        "40000 Filters/43130-DimensionFilter-StaticAnalysis-DimensionMember Filter/43130 DimensionMember Filter.xml:V-04": {
            "assertion": -1
        },
        "40000 Filters/52210-UnitFilter-Processing-SingleMeasure/52210 Unit Single Measure Processing.xml:V-03": {
            "assertion": -1
        },
        "60000 Extensions/60100 GenericMessages-Processing/60100 GenericMessages Processing.xml:V-01": {
            "test-assertion": -1
        },
        "60000 Extensions/60100 GenericMessages-Processing/60100 GenericMessages Processing.xml:V-02": {
            "test-assertion": -1
        },
        "60000 Extensions/60100 GenericMessages-Processing/60100 GenericMessages Processing.xml:V-09": {
            "test-assertion": 1,
        },
        "60000 Extensions/60110 AssertionSeverity-Processing/60110 Assertion Severity Processing.xml:V-01": {
            "test-assertion": -1
        },
        "60000 Extensions/60110 AssertionSeverity-Processing/60110 Assertion Severity Processing.xml:V-03": {
            "seve:assertionSeverityTargetError": 1
        },
        "60000 Extensions/61000 AspectCoverFilter-Processing/61000 AspectCoverFilter Processing.xml:V-10": {
            "assertion": -1
        },
        "60000 Extensions/61000 AspectCoverFilter-Processing/61000 AspectCoverFilter Processing.xml:V-11": {
            "assertion": -1
        },
        "60000 Extensions/61000 AspectCoverFilter-Processing/61000 AspectCoverFilter Processing.xml:V-12": {
            "assertion": -1
        },
        "60000 Extensions/61000 AspectCoverFilter-Processing/61000 AspectCoverFilter Processing.xml:V-13": {
            "assertion": -1
        },
        "60000 Extensions/61000 AspectCoverFilter-Processing/61000 AspectCoverFilter Processing.xml:V-14": {
            "assertion": -1
        },
        "60000 Extensions/61000 AspectCoverFilter-Processing/61000 AspectCoverFilter Processing.xml:V-15": {
            "assertion": -1
        },
        "60000 Extensions/61000 AspectCoverFilter-Processing/61000 AspectCoverFilter Processing.xml:V-16": {
            "assertion": -1
        },
        "60000 Extensions/61000 AspectCoverFilter-Processing/61000 AspectCoverFilter Processing.xml:V-16a": {
            "assertion": -1
        },
        "60000 Extensions/61000 AspectCoverFilter-Processing/61000 AspectCoverFilter Processing.xml:V-17": {
            "assertion": -1
        },
        "60000 Extensions/61000 AspectCoverFilter-Processing/61000 AspectCoverFilter Processing.xml:V-17a": {
            "assertion": -1
        },
        "60000 Extensions/61100 ConceptRelationsFilter-Processing/61100 ConceptRelationsFilter Processing.xml:V-20": {
            "calc-linkbase-assertion": -1
        },
        "60000 Extensions/61100 ConceptRelationsFilter-Processing/61100 ConceptRelationsFilter Processing.xml:V-20a": {
            "calc-linkbase-assertion": -1
        },
        "60000 Extensions/61100 ConceptRelationsFilter-Processing/61100 ConceptRelationsFilter Processing.xml:V-21": {
            "calc-linkbase-assertion": -1
        },
        "60000 Extensions/61100 ConceptRelationsFilter-Processing/61100 ConceptRelationsFilter Processing.xml:V-21a": {
            "calc-linkbase-assertion": -1
        },
        "60000 Extensions/61100 ConceptRelationsFilter-Processing/61100 ConceptRelationsFilter Processing.xml:V-21b": {
            "calc-linkbase-assertion": -1
        },
        "60000 Extensions/61100 ConceptRelationsFilter-Processing/61100 ConceptRelationsFilter Processing.xml:V-41": {
            "min-required-precision-assertion": 2,
        },
        "60000 Extensions/61100 ConceptRelationsFilter-Processing/61100 ConceptRelationsFilter Processing.xml:V-42": {
            "min-required-precision-assertion": 2,
        }
    }.items()},
    info_url='https://specifications.xbrl.org/release-history-formula-1.0-formula-conf.html',
    name=PurePath(__file__).stem,
    shards=4,
)
