"""
An example of reading a report with Arelle's Python API, published on
arelle.org. Run it from the directory holding the filing.
"""
from __future__ import annotations

from arelle.RuntimeOptions import RuntimeOptions
from arelle.api.Session import Session

options = RuntimeOptions(
    entrypointFile="demo-20251231.xbrl",
    keepOpen=True,
    logLevel="warning",
)

with Session() as session:
    session.run(options)
    report = session.get_models()[0]

    concept = report.nameConcepts["Revenue"][0]
    revenue = {
        fact.context.endDate: fact.effectiveValue
        for fact in report.factsByQname[concept.qname]
    }
    for periodEnd, value in sorted(revenue.items(), reverse=True):
        print(f"{periodEnd}  {value:>12}")
