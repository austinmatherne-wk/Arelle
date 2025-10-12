"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from typing import Any

from arelle.oim.tableConstraints import Const


def isNilValue(value: object) -> bool:
    """
    Check if a value represents nil in xBRL-CSV.

    Nil values include: None, #nil marker, or empty string.

    Args:
        value: Value to check

    Returns:
        True if value is nil, False otherwise
    """
    return value is None or value == Const.XBRL_CSV_NIL or value == ""


def normalizeKeyArray(keyData: dict[str, Any] | list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """
    Normalize key data to always be a list of dictionaries.

    The Table Constraints spec allows keys to be specified as either
    a single object or an array of objects. This helper normalizes
    both formats to a list for consistent processing.

    Args:
        keyData: Key specification from JSON (dict, list, or None)

    Returns:
        List of key dictionaries (empty list if keyData is None or invalid)
    """
    if isinstance(keyData, dict):
        return [keyData]
    elif isinstance(keyData, list):
        return keyData
    return []
