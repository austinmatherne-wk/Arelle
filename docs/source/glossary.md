# Glossary

:::{index} Glossary
:::

This glossary defines common XBRL and Arelle terminology.

## A

### Arcrole
A URI that identifies the type of relationship between two concepts in a linkbase.
Common arcroles include parent-child (presentation), summation-item (calculation),
and domain-member (dimensions).

## C

### Calculation Linkbase
An XBRL linkbase that defines mathematical relationships between concepts, such as
which items sum to a total. Used for validation to verify that reported values
are mathematically consistent.

### Concept
A defined data point in an XBRL taxonomy. Concepts have properties like data type,
period type, and balance type. In reports, concepts are tagged to facts.

### Context
Metadata that identifies the entity, time period, and dimensional qualifiers for
a fact. Every fact must have a context that specifies when and to whom it applies.

## D

### Dimension
A mechanism for categorizing and disaggregating facts beyond the basic concept.
For example, revenue might be broken down by geographic region or product line.
See also: Hypercube.

### Disclosure System
A predefined set of validation rules for a specific regulatory framework.
Examples: `efm-pragmatic` (SEC), `esef-2024` (European ESEF), `hmrc` (UK tax).
Disclosure systems determine which validation checks are performed.

### DTS (Discoverable Taxonomy Set)
The complete set of taxonomy schemas and linkbases that are discovered starting
from an entry point. The DTS includes all imported and referenced files needed
to fully define the taxonomy.

## E

### EFM (Edgar Filer Manual)
The SEC's technical specification for XBRL filings submitted through EDGAR.
Arelle's EFM validation checks compliance with these requirements.

### Entry Point
The starting file for loading an XBRL taxonomy or instance. For a report, this
is typically the instance document or primary iXBRL file. For a taxonomy, it's
usually a schema file.

### ESEF (European Single Electronic Format)
A European Union regulation requiring listed companies to file annual reports
in XHTML format with XBRL tags (Inline XBRL). See the [ESEF Guide][esef].

## F

### Fact
A single data value in an XBRL report, combining a concept, context, optional
unit, and the value itself. Facts are the atomic pieces of information in XBRL.

### Formula
XBRL formulas define business rules and calculations that can validate or
derive values in reports. More powerful than calculation linkbase validation.

## H

### Hypercube
A dimensional structure that defines valid combinations of dimensions for facts.
Also known as a "table" in XBRL dimensions terminology.

## I

### Inline XBRL (iXBRL)
A format that embeds XBRL tags within human-readable HTML/XHTML documents.
This allows a single document to serve both human readers and machine processing.

### Instance Document
An XBRL file containing reported facts, contexts, and units. Traditional XBRL
instances are XML files; Inline XBRL instances are HTML files with embedded tags.

### IXDS (Inline XBRL Document Set)
Multiple Inline XBRL documents that together represent a single logical XBRL
instance. Common in SEC filings where a report spans multiple HTML pages.
All documents in an IXDS share the same target instance.

## L

### Label
Human-readable text associated with a concept. Labels can vary by language
and role (standard, terse, verbose, documentation, etc.).

### Linkbase
An XBRL file that defines relationships between concepts or between concepts
and resources. Types include: presentation, calculation, definition, label,
and reference linkbases.

## O

### OIM (Open Information Model)
A format-independent representation of XBRL data. OIM defines XBRL semantically
independent of XML syntax, enabling alternative formats like JSON-based xBRL-JSON.

## P

### Pragmatic Validation
A validation mode that focuses on errors that would cause filing rejection,
ignoring some warnings and style issues. Compare with "strict" validation
which reports all potential issues.

### Presentation Linkbase
An XBRL linkbase that organizes concepts into hierarchies for display purposes.
Defines the structure users see when viewing taxonomy concepts.

## R

### Reference Linkbase
An XBRL linkbase that connects concepts to authoritative references like
accounting standards, regulations, or other documentation.

### Role
A URI that identifies the purpose or context of elements in XBRL. Link roles
group relationships; label roles distinguish label types (standard, verbose, etc.).

## S

### Schema
An XSD (XML Schema Definition) file that defines concepts, data types, and
other structural elements of a taxonomy.

### Strict Validation
A validation mode that reports all potential issues including warnings and
style recommendations. Compare with "pragmatic" validation which focuses
only on blocking errors.

## T

### Taxonomy
A collection of schemas and linkbases that define the concepts, relationships,
and validation rules for a reporting framework. Examples: US GAAP, IFRS, ESEF.

### Taxonomy Package
A ZIP archive containing taxonomy files and URL remapping rules. Packages
enable offline validation and ensure consistent taxonomy versions. See the
[Taxonomy Packages Guide][taxonomy-packages].

### Target Document
In Inline XBRL, the logical XBRL instance that is constructed from the iXBRL
tags. Multiple source documents in an IXDS produce a single target document.

## U

### Unit
Specifies the measurement for numeric facts (e.g., USD, shares, pure number).
Required for all numeric facts except fractions.

### UTR (Unit Type Registry)
A registry of standard units and their acceptable uses with specific data types.
UTR validation ensures facts use appropriate units for their concepts.

## V

### Validation
The process of checking an XBRL document for compliance with specifications
and rules. Includes XML schema validation, XBRL 2.1 validation, calculation
checks, and disclosure system rules.

## X

### XBRL (eXtensible Business Reporting Language)
An open standard for digital business reporting. XBRL enables structured,
machine-readable financial and business data exchange.

### XULE
A rule language for XBRL developed by XBRL US. Used by the SEC's Data Quality
Committee (DQC) rules and FERC validation rules.

[esef]: project:esef.md
[taxonomy-packages]: project:user_guides/taxonomy_packages.md
