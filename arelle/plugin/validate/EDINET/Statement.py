from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from regex import regex

from arelle.ModelInstanceObject import ModelFact

CONSOLIDATED_ROLE_URI_PATTERN = regex.compile(r'.*rol_[\w]*Consolidated')

MAJOR_SHAREHOLDERS_ROLE_URIS = frozenset([
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_MajorShareholders-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_MajorShareholders-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_MajorShareholders-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_MajorShareholders-02',
])

CONSOLIDATED_BALANCE_SHEET_ROLE_URIS = frozenset([
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_ConsolidatedBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_ConsolidatedBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_SemiAnnualConsolidatedBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_SemiAnnualConsolidatedBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_Type1SemiAnnualConsolidatedBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_Type1SemiAnnualConsolidatedBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_QuarterlyConsolidatedBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_QuarterlyConsolidatedBalanceSheet',
])

BALANCE_SHEET_ROLE_URIS = frozenset([
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_BalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_BalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_SemiAnnualBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_SemiAnnualBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_Type1SemiAnnualBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_Type1SemiAnnualBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_QuarterlyBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_QuarterlyBalanceSheet',
])

CONSOLIDATED_INCOME_STATEMENT_ROLE_URIS = frozenset([
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_ConsolidatedStatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_ConsolidatedStatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_SemiAnnualConsolidatedStatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_SemiAnnualConsolidatedStatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_Type1SemiAnnualConsolidatedStatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_Type1SemiAnnualConsolidatedStatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_YearToQuarterEndConsolidatedStatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_YearToQuarterEndConsolidatedStatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_QuarterPeriodConsolidatedStatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_QuarterPeriodConsolidatedStatementOfIncome',
])

INCOME_STATEMENT_ROLE_URIS = frozenset([
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_StatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_StatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_SemiAnnualStatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_SemiAnnualStatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_Type1SemiAnnualStatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_Type1SemiAnnualStatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_YearToQuarterEndStatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_YearToQuarterEndStatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_QuarterPeriodStatementOfIncome',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_QuarterPeriodStatementOfIncome',
])

INCOME_AND_RETAINED_EARNINGS_ROLE_URIS = frozenset([
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_StatementOfIncomeAndRetainedEarnings',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_StatementOfIncomeAndRetainedEarnings',
])

CONSOLIDATED_EQUITY_STATEMENT_ROLE_URIS = frozenset([
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_ConsolidatedStatementOfChangesInEquity',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_ConsolidatedStatementOfChangesInEquity',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_ConsolidatedStatementOfChangesInNetAssets',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_ConsolidatedStatementOfChangesInNetAssets',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_SemiAnnualConsolidatedStatementOfChangesInEquity',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_SemiAnnualConsolidatedStatementOfChangesInEquity',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_SemiAnnualConsolidatedStatementOfChangesInNetAssets',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_SemiAnnualConsolidatedStatementOfChangesInNetAssets',
])

EQUITY_STATEMENT_ROLE_URIS = frozenset([
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_StatementOfChangesInEquity',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_StatementOfChangesInEquity',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_StatementOfChangesInNetAssets',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_StatementOfChangesInNetAssets',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_SemiAnnualStatementOfChangesInEquity',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_SemiAnnualStatementOfChangesInEquity',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_SemiAnnualStatementOfChangesInNetAssets',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_SemiAnnualStatementOfChangesInNetAssets',
])

UNITHOLDERS_EQUITY_ROLE_URIS = frozenset([
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_StatementOfUnitholdersEquity',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_StatementOfUnitholdersEquity',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_SemiAnnualStatementOfUnitholdersEquity',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_SemiAnnualStatementOfUnitholdersEquity',
])

MEMBERS_EQUITY_ROLE_URIS = frozenset([
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_StatementOfMembersEquity',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_StatementOfMembersEquity',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_SemiAnnualStatementOfMembersEquity',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_SemiAnnualStatementOfMembersEquity',
])

CONSOLIDATED_CASH_FLOW_ROLE_URIS = frozenset([
    # Japan GAAP
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_ConsolidatedStatementOfCashFlows-direct',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_ConsolidatedStatementOfCashFlows-direct',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_SemiAnnualConsolidatedStatementOfCashFlows-direct',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_SemiAnnualConsolidatedStatementOfCashFlows-direct',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_Type1SemiAnnualConsolidatedStatementOfCashFlows-direct',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_Type1SemiAnnualConsolidatedStatementOfCashFlows-direct',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_QuarterlyConsolidatedStatementOfCashFlows-direct',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_QuarterlyConsolidatedStatementOfCashFlows-direct',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_ConsolidatedStatementOfCashFlows-indirect',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_ConsolidatedStatementOfCashFlows-indirect',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_SemiAnnualConsolidatedStatementOfCashFlows-indirect',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_SemiAnnualConsolidatedStatementOfCashFlows-indirect',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_Type1SemiAnnualConsolidatedStatementOfCashFlows-indirect',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_Type1SemiAnnualConsolidatedStatementOfCashFlows-indirect',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_QuarterlyConsolidatedStatementOfCashFlows-indirect',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_QuarterlyConsolidatedStatementOfCashFlows-indirect',
    # IFRS
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_ConsolidatedStatementOfCashFlowsIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_std_ConsolidatedStatementOfCashFlowsIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedSemiAnnualConsolidatedStatementOfCashFlowsIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterlyConsolidatedStatementOfCashFlowsIFRS',
])

CASH_FLOW_ROLE_URIS = frozenset([
    # Japan GAAP
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_StatementOfCashFlows-direct',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_StatementOfCashFlows-direct',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_SemiAnnualStatementOfCashFlows-direct',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_SemiAnnualStatementOfCashFlows-direct',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_Type1SemiAnnualStatementOfCashFlows-direct',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_Type1SemiAnnualStatementOfCashFlows-direct',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_QuarterlyStatementOfCashFlows-direct',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_QuarterlyStatementOfCashFlows-direct',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_StatementOfCashFlows-indirect',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_StatementOfCashFlows-indirect',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_SemiAnnualStatementOfCashFlows-indirect',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_SemiAnnualStatementOfCashFlows-indirect',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_Type1SemiAnnualStatementOfCashFlows-indirect',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_Type1SemiAnnualStatementOfCashFlows-indirect',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_QuarterlyStatementOfCashFlows-indirect',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_QuarterlyStatementOfCashFlows-indirect',
    # IFRS
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_StatementOfCashFlowsIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedSemiAnnualStatementOfCashFlowsIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterlyStatementOfCashFlowsIFRS',
])

SEGMENT_INFORMATION_ROLE_URIS = frozenset([
    # IFRS
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_std_NotesSegmentInformationConsolidatedFinancialStatementsIFRS-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_std_NotesSegmentInformationConsolidatedFinancialStatementsIFRS-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_std_NotesSegmentInformationConsolidatedFinancialStatementsIFRS-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationFinancialStatementsIFRS-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationFinancialStatementsIFRS-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationFinancialStatementsIFRS-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationConsolidatedFinancialStatementsIFRS-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationConsolidatedFinancialStatementsIFRS-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationConsolidatedFinancialStatementsIFRS-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationCondensedSemiAnnualFinancialStatementsIFRS-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationCondensedSemiAnnualFinancialStatementsIFRS-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationCondensedSemiAnnualFinancialStatementsIFRS-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationCondensedSemiAnnualConsolidatedFinancialStatementsIFRS-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationCondensedSemiAnnualConsolidatedFinancialStatementsIFRS-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationCondensedSemiAnnualConsolidatedFinancialStatementsIFRS-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationCondensedQuarterlyFinancialStatementsIFRS-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationCondensedQuarterlyFinancialStatementsIFRS-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationCondensedQuarterlyFinancialStatementsIFRS-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationCondensedQuarterlyConsolidatedFinancialStatementsIFRS-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationCondensedQuarterlyConsolidatedFinancialStatementsIFRS-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_NotesSegmentInformationCondensedQuarterlyConsolidatedFinancialStatementsIFRS-01',
    # Japan GAAP
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcType1SemiAnnualFinancialStatements-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcType1SemiAnnualFinancialStatements-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcType1SemiAnnualFinancialStatements-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcType1SemiAnnualConsolidatedFinancialStatements-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcType1SemiAnnualConsolidatedFinancialStatements-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcType1SemiAnnualConsolidatedFinancialStatements-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualFinancialStatements-09',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualFinancialStatements-08',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualFinancialStatements-07',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualFinancialStatements-06',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualFinancialStatements-05',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualFinancialStatements-04',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualFinancialStatements-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualFinancialStatements-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualFinancialStatements-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-09',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-08',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-07',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-06',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-05',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-04',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcQuarterlyFinancialStatements-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcQuarterlyFinancialStatements-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcQuarterlyFinancialStatements-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcQuarterlyConsolidatedFinancialStatements-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcQuarterlyConsolidatedFinancialStatements-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcQuarterlyConsolidatedFinancialStatements-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcFinancialStatements-09',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcFinancialStatements-08',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcFinancialStatements-07',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcFinancialStatements-06',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcFinancialStatements-05',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcFinancialStatements-04',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcFinancialStatements-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcFinancialStatements-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcFinancialStatements-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcConsolidatedFinancialStatements-09',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcConsolidatedFinancialStatements-08',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcConsolidatedFinancialStatements-07',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcConsolidatedFinancialStatements-06',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcConsolidatedFinancialStatements-05',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcConsolidatedFinancialStatements-04',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcConsolidatedFinancialStatements-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcConsolidatedFinancialStatements-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_std_NotesSegmentInformationEtcConsolidatedFinancialStatements-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcType1SemiAnnualFinancialStatements-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcType1SemiAnnualFinancialStatements-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcType1SemiAnnualFinancialStatements-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcType1SemiAnnualConsolidatedFinancialStatements-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcType1SemiAnnualConsolidatedFinancialStatements-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcType1SemiAnnualConsolidatedFinancialStatements-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualFinancialStatements-09',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualFinancialStatements-08',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualFinancialStatements-07',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualFinancialStatements-06',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualFinancialStatements-05',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualFinancialStatements-04',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualFinancialStatements-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualFinancialStatements-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualFinancialStatements-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-09',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-08',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-07',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-06',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-05',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-04',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcSemiAnnualConsolidatedFinancialStatements-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcQuarterlyFinancialStatements-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcQuarterlyFinancialStatements-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcQuarterlyFinancialStatements-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcQuarterlyConsolidatedFinancialStatements-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcQuarterlyConsolidatedFinancialStatements-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcQuarterlyConsolidatedFinancialStatements-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcFinancialStatements-09',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcFinancialStatements-08',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcFinancialStatements-07',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcFinancialStatements-06',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcFinancialStatements-05',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcFinancialStatements-04',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcFinancialStatements-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcFinancialStatements-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcFinancialStatements-01',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcConsolidatedFinancialStatements-09',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcConsolidatedFinancialStatements-08',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcConsolidatedFinancialStatements-07',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcConsolidatedFinancialStatements-06',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcConsolidatedFinancialStatements-05',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcConsolidatedFinancialStatements-04',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcConsolidatedFinancialStatements-03',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcConsolidatedFinancialStatements-02',
    'http://disclosure.edinet-fsa.go.jp/role/jpcrp/rol_NotesSegmentInformationEtcConsolidatedFinancialStatements-01',
])

STATEMENT_ROLE_URIS = frozenset([
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterPeriodConsolidatedStatementOfComprehensiveIncomeIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterPeriodConsolidatedStatementOfComprehensiveIncomeSingleStatementIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterPeriodConsolidatedStatementOfProfitOrLossIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterPeriodStatementOfComprehensiveIncomeIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterPeriodStatementOfComprehensiveIncomeSingleStatementIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterPeriodStatementOfProfitOrLossIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterlyConsolidatedStatementOfCashFlowsIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterlyConsolidatedStatementOfChangesInEquityIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterlyConsolidatedStatementOfComprehensiveIncomeIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterlyConsolidatedStatementOfComprehensiveIncomeSingleStatementIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterlyConsolidatedStatementOfFinancialPositionIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterlyConsolidatedStatementOfProfitOrLossIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterlyStatementOfCashFlowsIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterlyStatementOfChangesInEquityIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterlyStatementOfComprehensiveIncomeIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterlyStatementOfComprehensiveIncomeSingleStatementIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterlyStatementOfFinancialPositionIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedQuarterlyStatementOfProfitOrLossIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedSemiAnnualConsolidatedStatementOfCashFlowsIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedSemiAnnualConsolidatedStatementOfChangesInEquityIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedSemiAnnualConsolidatedStatementOfComprehensiveIncomeIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedSemiAnnualConsolidatedStatementOfComprehensiveIncomeSingleStatementIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedSemiAnnualConsolidatedStatementOfFinancialPositionIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedSemiAnnualConsolidatedStatementOfProfitOrLossIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedSemiAnnualStatementOfCashFlowsIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedSemiAnnualStatementOfChangesInEquityIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedSemiAnnualStatementOfComprehensiveIncomeIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedSemiAnnualStatementOfComprehensiveIncomeSingleStatementIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedSemiAnnualStatementOfFinancialPositionIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedSemiAnnualStatementOfProfitOrLossIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedYearToQuarterEndConsolidatedStatementOfComprehensiveIncomeIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedYearToQuarterEndConsolidatedStatementOfComprehensiveIncomeSingleStatementIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedYearToQuarterEndConsolidatedStatementOfProfitOrLossIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedYearToQuarterEndStatementOfComprehensiveIncomeIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedYearToQuarterEndStatementOfComprehensiveIncomeSingleStatementIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_CondensedYearToQuarterEndStatementOfProfitOrLossIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_ConsolidatedStatementOfCashFlowsIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_ConsolidatedStatementOfChangesInEquityIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_ConsolidatedStatementOfComprehensiveIncomeIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_ConsolidatedStatementOfComprehensiveIncomeSingleStatementIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_ConsolidatedStatementOfFinancialPositionIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_ConsolidatedStatementOfProfitOrLossIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_StatementOfCashFlowsIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_StatementOfChangesInEquityIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_StatementOfComprehensiveIncomeIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_StatementOfComprehensiveIncomeSingleStatementIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_StatementOfFinancialPositionIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_StatementOfProfitOrLossIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_std_ConsolidatedStatementOfCashFlowsIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_std_ConsolidatedStatementOfChangesInEquityIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_std_ConsolidatedStatementOfComprehensiveIncomeIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_std_ConsolidatedStatementOfFinancialPositionIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jpigp/rol_std_ConsolidatedStatementOfProfitOrLossIFRS',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_BalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_ConsolidatedBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_QuarterlyBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_QuarterlyConsolidatedBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_SemiAnnualBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_SemiAnnualConsolidatedBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_Type1SemiAnnualBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_Type1SemiAnnualConsolidatedBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_BalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_ConsolidatedBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_QuarterlyBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_QuarterlyConsolidatedBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_SemiAnnualBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_SemiAnnualConsolidatedBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_Type1SemiAnnualBalanceSheet',
    'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_std_Type1SemiAnnualConsolidatedBalanceSheet',
])


class StatementType(Enum):
    BALANCE_SHEET = 'BalanceSheet'
    CONSOLIDATED_BALANCE_SHEET = 'ConsolidatedBalanceSheetIFRS'
    STATEMENT_OF_CASH_FLOWS = 'StatementOfCashFlowsIFRS'
    STATEMENT_OF_CHANGES_IN_EQUITY = 'StatementOfChangesInEquityIFRS'
    STATEMENT_OF_COMPREHENSIVE_INCOME = 'StatementOfComprehensiveIncomeIFRS'
    STATEMENT_OF_COMPREHENSIVE_INCOME_SINGLE_STATEMENT = 'StatementOfComprehensiveIncomeSingleStatementIFRS'
    STATEMENT_OF_FINANCIAL_POSITION = 'StatementOfFinancialPositionIFRS'
    STATEMENT_OF_PROFIT_OR_LOSS = 'StatementOfProfitOrLossIFRS'


@dataclass(frozen=True)
class Statement:
    isConsolidated: bool
    roleUri: str
    statementType: StatementType


@dataclass(frozen=True)
class BalanceSheet:
    creditSum: Decimal
    contextId: str
    facts: list[ModelFact]
    debitSum: Decimal
    unitId: str


@dataclass(frozen=True)
class StatementInstance:
    balanceSheets: list[BalanceSheet]
    statement: Statement

def _buildStatements() -> frozenset[Statement]:
    """
    Build a frozenset of Statement objects from the STATEMENT_ROLE_URIS.
    This is done to avoid re-evaluating the set comprehension multiple times.
    """
    statements = []
    for roleUri in STATEMENT_ROLE_URIS:
        isConsolidated = bool(CONSOLIDATED_ROLE_URI_PATTERN.match(roleUri))
        statementType=next(
            statementType
            for statementType in StatementType
            if roleUri.endswith(statementType.value)
        )
        statements.append(
            Statement(
                isConsolidated=isConsolidated,
                roleUri=roleUri,
                statementType=statementType
            )
        )
    return frozenset(statements)


STATEMENTS = _buildStatements()
