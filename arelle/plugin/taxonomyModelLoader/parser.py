"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations

from typing import cast

from pydantic import TypeAdapter

from arelle.ModelDocument import ModelDocument
from arelle.plugin.taxonomyModelLoader.model import TaxonomyModule


class TaxonomyModelParser:

    def __init__(self) -> None:
        self.taxonomy_module_adapter = TypeAdapter(TaxonomyModule)

    def parse(self, filepath: str) -> ModelDocument:
        with open(filepath, encoding="utf-8") as f:
            doc = self.taxonomy_module_adapter.validate_json(f.read())
        return cast(ModelDocument, doc)
