"""
Compatibility shim providing optparse-style API over argparse.

This module allows plugins written for the legacy optparse API to continue
working after Arelle's migration to argparse. Plugins can use add_option()
as before, and the shim translates calls to argparse's add_argument().

New plugins should use argparse's add_argument() directly on the underlying
parser available via OptparseShim._parser.
"""
from __future__ import annotations

import argparse
from optparse import Option
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    import optparse
    from argparse import Action


class OptionGroup:
    """Compatibility class for optparse.OptionGroup.

    Provides the same interface as optparse.OptionGroup while delegating
    to an argparse argument group internally.
    """

    def __init__(
        self,
        parser: OptparseShim | argparse.ArgumentParser,
        title: str,
        description: str = "",
    ) -> None:
        self.title = title
        self.description = description
        self._parser = parser
        # Handle both OptparseShim and raw ArgumentParser
        if isinstance(parser, OptparseShim):
            self._argparseGroup = parser._parser.add_argument_group(title, description)
        else:
            self._argparseGroup = parser.add_argument_group(title, description)
        self.option_list: list[Action] = []

    def add_option(self, *args: Any, **kwargs: Any) -> Action:
        """Add an option to this group using optparse-style arguments."""
        translated = _translateOptionKwargs(kwargs)
        action = self._argparseGroup.add_argument(*args, **translated)
        self.option_list.append(action)
        return action


class OptparseShim:
    """Wraps argparse.ArgumentParser with optparse-compatible API.

    This shim allows legacy plugin code using optparse's add_option() method
    to work with argparse. The shim translates:
    - add_option() -> add_argument()
    - type="int" -> type=int
    - OptionGroup usage patterns

    Plugins can access the underlying argparse.ArgumentParser via the _parser
    attribute if they need native argparse functionality.

    Also provides attributes required by optparse.OptionGroup constructor
    so that plugins importing OptionGroup from optparse will still work.
    """

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        self._parser = parser
        self.option_list: list[Action] = []
        self.option_groups: list[OptionGroup] = []
        # Attributes required for optparse.OptionGroup compatibility
        self.option_class = Option
        self.conflict_handler = "resolve"
        self.description = parser.description or ""

    def add_option(self, *args: Any, **kwargs: Any) -> Action:
        """Add an option using optparse-style arguments.

        Translates optparse conventions to argparse:
        - type="int" becomes type=int
        - type is removed for store_true/store_false actions
        """
        translated = _translateOptionKwargs(kwargs)
        action = self._parser.add_argument(*args, **translated)
        self.option_list.append(action)
        return action

    def add_option_group(self, group: Union[OptionGroup, optparse.OptionGroup]) -> None:
        """Register an option group with this parser.

        Handles both the shim's OptionGroup and optparse.OptionGroup.
        For optparse.OptionGroup, translates the options to argparse.
        """
        import optparse as optparse_module
        if isinstance(group, optparse_module.OptionGroup):
            # Convert optparse.OptionGroup to argparse
            argparseGroup = self._parser.add_argument_group(group.title, group.description)
            shimGroup = OptionGroup.__new__(OptionGroup)
            shimGroup.title = group.title
            shimGroup.description = group.description or ""
            shimGroup._parser = self
            shimGroup._argparseGroup = argparseGroup
            shimGroup.option_list = []
            # Translate each option from the optparse group
            for opt in group.option_list:
                kwargs = {
                    "dest": opt.dest,
                    "action": opt.action or "store",
                    "default": opt.default,
                    "help": opt.help,
                }
                if opt.type:
                    kwargs["type"] = opt.type
                if opt.choices:
                    kwargs["choices"] = opt.choices
                translated = _translateOptionKwargs(kwargs)
                optStrings = list(opt._short_opts) + list(opt._long_opts)
                action = argparseGroup.add_argument(*optStrings, **translated)
                shimGroup.option_list.append(action)
            self.option_groups.append(shimGroup)
        else:
            self.option_groups.append(group)


def _translateOptionKwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Translate optparse keyword arguments to argparse equivalents."""
    result = kwargs.copy()

    # optparse uses type="int", argparse uses type=int
    if "type" in result and isinstance(result["type"], str):
        typeMap = {"int": int, "float": float, "string": str, "long": int}
        result["type"] = typeMap.get(result["type"], str)

    # argparse doesn't accept type parameter with these actions
    if result.get("action") in ("store_true", "store_false", "store_const", "count", "append_const"):
        result.pop("type", None)

    return result
