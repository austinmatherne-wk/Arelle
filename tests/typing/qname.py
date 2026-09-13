"""
See COPYRIGHT.md for copyright information.
"""
from typing_extensions import assert_type

from arelle.ModelObject import ModelObject
from arelle.ModelValue import QName, qname


def qname_contract(
    element: ModelObject,
    existing: QName,
    text: str,
    namespaces: dict[str, str],
    default_namespaces: dict[str | None, str],
    unknown: object,
) -> None:
    assert_type(qname(existing), QName)
    assert_type(qname(existing, element), QName)
    assert_type(qname(existing, existing), QName)
    assert_type(qname(element), QName)
    assert_type(qname(element, None), QName)
    assert_type(qname(element, ""), QName)
    assert_type(qname(element, existing), QName)
    assert_type(qname(element, existing, True), QName)
    assert_type(qname("undeclared:item"), QName | None)
    assert_type(qname("{urn:example}item"), QName | None)
    assert_type(qname(text), QName | None)
    assert_type(qname("", "p:item"), QName | None)
    assert_type(qname(element, text), QName | None)
    assert_type(qname(text, element), QName | None)
    assert_type(qname(element, element), QName | None)
    assert_type(qname(text, namespaces), QName | None)
    assert_type(qname(text, default_namespaces), QName | None)
    assert_type(qname(text, noPrefixIsNoNamespace=True), QName | None)
    assert_type(qname(None), QName | None)
    assert_type(qname(unknown), QName | None)
    assert_type(qname(text, prefixException=ValueError), QName | None)
    assert_type(qname(text, prefixException=ValueError("prefix")), QName | None)
    assert_type(qname(unknown, castException=TypeError), QName | None)
    assert_type(qname(text, namespaces, False, TypeError, ValueError), QName | None)
    assert_type(qname(element, existing, castException=TypeError, prefixException=ValueError), QName)
