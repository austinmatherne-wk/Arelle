---
title: Arelle
description: Arelle is the world's only free and open source XBRL platform.
aliases:
  - /arelle/
---

## Overview

Arelle was created in 2010 to improve the accessibility and usability of XBRL™ in order to increase the worldwide adoption of the standard. It seeks to provide the XBRL community with a free and easy to use open source platform for XBRL, supporting XBRL and its extension features in an extensible manner. It does this in a compact yet robust framework that can be used as a desktop application and can be integrated with other applications and languages utilizing its web service, command line interface, and Python API.

Today the Arelle project is used by a global community of over 50 regulators, banks and technology companies that depend on it for data quality and comparison.

Arelle is the world's only free and open source XBRL platform.

## Mission

The mission of Arelle is to standardize business reporting by facilitating the global adoption of XBRL.

## Vision

Arelle strives to be the free, open source platform that enables regulators, software providers, auditors and filers to build, validate and process structured data worldwide.

## Strategic Themes

Arelle will focus on the following themes to achieve our vision:

1. **Performance** — Improve the speed Arelle loads, validates and executes structured data regulations.
2. **Specification Support** — Arelle supports all XBRL International specifications and structured data regulations for business reporting.
3. **Usability and Functionality** — Regulators, software providers, auditors and consumers find Arelle easy to implement and use thanks to its modern GUI and ease of integration via API and plugins.
4. **Global Community** — Arelle accelerates the adoption of XBRL globally via an active, open source community of contributors.

## Product Principles

Arelle seeks to balance the following principles when building the platform:

- Open Source
- Free
- Global
- Standards Compliant
- Community Based
- Easily Consumable
- Performant
- Extensible

## Technical Details

Support for XBRL versioning was an initial goal. Validation is provided for existing versioning reports. New versioning reports content is produced by comparing two DTSes.

Arelle fully integrates test cases with the object models for XBRL instances and DTSes. This allows continual verification of tool performance as it is extended and adapted by its users.

Validation is provided for the Base Specification of XBRL 2.1, Dimensions, Inline XBRL, Generic Linkbases, Unit Types Registry, U.S. SEC Edgar Filer Manual, IFRS Global Filing Manual and HMRC, CIPC and ESMA Filing Checks.

Formula validation is complete for formula output instance creation, consistency assertions, existence assertions, value assertions, sequence partitioning and fallback value processing. REC and CR status filters and registry functions are provided. The extension modules are available, including validation messages, multi-instance and chaining, tuple generation and variables-scope chaining, custom function implementation, aspect cover and concept-relation filters. Additionally, a processor for Sphinx 2.0 is provided by a plug-in.

Instance creation is supported using forms defined by the table linkbase (Eurofiling version).

Tables defined by the table linkbase 1.0 specification are supported.

Users can explore the functionality and features from an interactive GUI, command line interface, or web services, and can develop their own controller interfaces as needed.

Taxonomy Packages (and Oasis Catalogs) used by EBA taxonomies are supported by a Package Manager.

The Web Service API allows XBRL integration with applications, such as those in Excel, Java or Oracle. The Web Service API can be run on your own server or Google App Engine. QuickBooks is supported by XBRL-GL.

The xbrlDB database plug-in provides database loading from RSS feeds or individual XBRL filings, using the XBRL-US Public Database SQL schema (Postgres only), or Abstract Model schemas in Graph and SQL databases (supporting Rexter for Titan/Cassandra, RDF using NanoSparqlServer or RDF files in Turtle or XML, JSON (currently files only) and SQL interfaces specific to Postgres, MySQL, MS SQL (2011), and Oracle (11g).

Participation and [feedback](mailto:support@arelle.org) is solicited.

There is an active Google Group [arelle-users](https://groups.google.com/forum/#!forum/arelle-users) — please visit it for community issues and assistance.

We welcome active contributors (to Arelle Support, Code Improvement, and EBA/Solvency II issues).

{{< image src="xbrl-certified-software-logo.png" alt="XBRL Certified Software" link="https://software.xbrl.org/consume/mark-v-systems-arelle" >}}

XBRL™ is a trademark of XBRL International, Inc. All rights reserved. The XBRL™ standards are open and freely licensed by way of the XBRL International License Agreement. Our use of these trademarks is permitted by XBRL International in accordance with the XBRL International Trademark Policy.
