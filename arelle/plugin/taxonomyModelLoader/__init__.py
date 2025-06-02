"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations

from typing import Any

from arelle.ModelXbrl import ModelXbrl
from arelle.oim.Load import isOimLoadable
from arelle.utils.PluginHooks import PluginHooks
from arelle.Version import authorLabel, copyrightLabel

from .const import TAXONOMY_MODEL_DOCUMENT_TYPE


class TaxonomyModelLoader(PluginHooks):
    @staticmethod
    def modelDocumentIsPullLoadable(
        modelXbrl: ModelXbrl,
        mappedUri: str,
        normalizedUri: str,
        filepath: str,
        isEntry: bool,
        namespace: str,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        return isOimLoadable(normalizedUri, filepath, docTypes={TAXONOMY_MODEL_DOCUMENT_TYPE})


__pluginInfo__ = {
    "name": "Experimental Taxonomy Model Loader",
    "version": "0.0.1",
    "description": "Experimental support for loading JSON taxonomies.",
    "license": "Apache-2",
    "author": authorLabel,
    "copyright": copyrightLabel,
    "ModelDocument.IsPullLoadable": TaxonomyModelLoader.modelDocumentIsPullLoadable,
}
