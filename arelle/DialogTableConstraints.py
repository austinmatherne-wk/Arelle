"""
See COPYRIGHT.md for copyright information.

Table Constraints Options Dialog

GUI dialog for configuring Table Constraints validation options.
These options affect how xBRL-CSV files with Table Constraints metadata are processed.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arelle.CntlrWinMain import CntlrWinMain


class DialogTableConstraints(tk.Toplevel):
    """
    GUI dialog for Table Constraints validation options.

    Allows users to configure:
    - Validate only (don't load) - corresponds to --tc-only CLI flag
    - Force load on errors - corresponds to --tc-force-load CLI flag

    Options are stored in the controller's config and persist across sessions.
    """

    def __init__(self, cntlr: CntlrWinMain) -> None:
        """
        Initialize the Table Constraints options dialog.

        Args:
            cntlr: The GUI controller instance
        """
        super().__init__(cntlr.parent)
        self.cntlr = cntlr
        self.title("Table Constraints Options")
        self.geometry("500x350")

        # Get current config values
        config = cntlr.config
        self.currentValidateOnly = config.get("tableConstraintsValidateOnly", False) if config else False
        self.currentForceLoad = config.get("tableConstraintsForceLoad", False) if config else False
        self.currentValidateMetadata = config.get("tableConstraintsValidateMetadata", False) if config else False
        self.currentLint = config.get("tableConstraintsLint", False) if config else False

        self._createWidgets()

        # Center dialog on parent
        self.transient(cntlr.parent)
        self.grab_set()

        # Focus on dialog
        self.focus_set()

    def _createWidgets(self) -> None:
        """Create the dialog widgets."""
        # Title
        titleLabel = ttk.Label(
            self,
            text="Table Constraints Validation Options",
            font=("TkDefaultFont", 12, "bold")
        )
        titleLabel.pack(pady=(20, 10))

        # Description
        descLabel = ttk.Label(
            self,
            text="Configure how xBRL-CSV files with Table Constraints are validated.",
            foreground="gray"
        )
        descLabel.pack(pady=(0, 15))

        # Options frame
        optionsFrame = ttk.Frame(self, padding=20)
        optionsFrame.pack(fill=tk.BOTH, expand=True)

        # Validate only option
        self.validateOnlyVar = tk.BooleanVar(value=self.currentValidateOnly)
        validateOnlyCheck = ttk.Checkbutton(
            optionsFrame,
            text="Validate Table Constraints only (don't load report)",
            variable=self.validateOnlyVar
        )
        validateOnlyCheck.pack(anchor=tk.W, pady=(0, 5))

        validateOnlyHelp = ttk.Label(
            optionsFrame,
            text="Performs streaming table constraints validation without loading the full report.",
            font=("TkDefaultFont", 9),
            foreground="gray"
        )
        validateOnlyHelp.pack(anchor=tk.W, padx=25, pady=(0, 15))

        # Force load option
        self.forceLoadVar = tk.BooleanVar(value=self.currentForceLoad)
        forceLoadCheck = ttk.Checkbutton(
            optionsFrame,
            text="Load report even if there are Table Constraints errors",
            variable=self.forceLoadVar
        )
        forceLoadCheck.pack(anchor=tk.W, pady=(0, 5))

        forceLoadHelp = ttk.Label(
            optionsFrame,
            text="Continue loading report into memory even if Table Constraints",
            font=("TkDefaultFont", 9),
            foreground="gray"
        )
        forceLoadHelp.pack(anchor=tk.W, padx=25, pady=(0, 15))

        # Validate metadata option
        self.validateMetadataVar = tk.BooleanVar(value=self.currentValidateMetadata)
        validateMetadataCheck = ttk.Checkbutton(
            optionsFrame,
            text="Validate Table Constraints metadata structure",
            variable=self.validateMetadataVar
        )
        validateMetadataCheck.pack(anchor=tk.W, pady=(0, 5))

        validateMetadataHelp = ttk.Label(
            optionsFrame,
            text="Also validate the Table Constraints metadata for structural errors.",
            font=("TkDefaultFont", 9),
            foreground="gray"
        )
        validateMetadataHelp.pack(anchor=tk.W, padx=25, pady=(0, 15))

        # Lint option
        self.lintVar = tk.BooleanVar(value=self.currentLint)
        lintCheck = ttk.Checkbutton(
            optionsFrame,
            text="Run Table Constraints linter (check taxonomy consistency)",
            variable=self.lintVar
        )
        lintCheck.pack(anchor=tk.W, pady=(0, 5))

        lintHelp = ttk.Label(
            optionsFrame,
            text="Check metadata consistency with taxonomy (requires report to be loaded).",
            font=("TkDefaultFont", 9),
            foreground="gray"
        )
        lintHelp.pack(anchor=tk.W, padx=25)

        # Buttons
        buttonFrame = ttk.Frame(self)
        buttonFrame.pack(pady=15)

        okButton = ttk.Button(buttonFrame, text="OK", command=self._ok)
        okButton.pack(side=tk.LEFT, padx=5)

        cancelButton = ttk.Button(buttonFrame, text="Cancel", command=self._cancel)
        cancelButton.pack(side=tk.LEFT, padx=5)

        # Bind escape key
        self.bind("<Escape>", lambda e: self._cancel())

    def _ok(self) -> None:
        """Save options and close dialog."""
        # Save to config
        config = self.cntlr.config
        if config is not None:
            config["tableConstraintsValidateOnly"] = self.validateOnlyVar.get()
            config["tableConstraintsForceLoad"] = self.forceLoadVar.get()
            config["tableConstraintsValidateMetadata"] = self.validateMetadataVar.get()
            config["tableConstraintsLint"] = self.lintVar.get()

            # Save config to disk
            self.cntlr.saveConfig()

        self.destroy()

    def _cancel(self) -> None:
        """Close dialog without saving."""
        self.destroy()


def show(cntlr: CntlrWinMain) -> None:
    """
    Show the Table Constraints options dialog.

    This is the entry point called from the Tools menu.

    Args:
        cntlr: The GUI controller instance
    """
    DialogTableConstraints(cntlr)
