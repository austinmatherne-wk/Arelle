"""
See COPYRIGHT.md for copyright information.
"""
from typing_extensions import assert_type

from arelle.ModelValue import QName, qnameNsLocalName
from arelle.plugin.validate.DBA.ValidationPluginExtension import NAMESPACE_FSA


local_name: str = "Assets"
assert_type(qnameNsLocalName(NAMESPACE_FSA, local_name), QName)
assert_type(frozenset([qnameNsLocalName(NAMESPACE_FSA, local_name)]), frozenset[QName])
