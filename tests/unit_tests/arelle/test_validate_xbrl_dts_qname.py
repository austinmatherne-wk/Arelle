from collections import defaultdict
from types import SimpleNamespace
from unittest.mock import Mock

from lxml import etree
import pytest

from arelle import ValidateXbrlDTS, XbrlConst, XmlValidate
from arelle.ModelDocumentType import ModelDocumentType
from arelle.ModelObject import ModelObject


@pytest.mark.parametrize("used_on, expected_prefix", [("undeclared:item", None), ("custom:item", "custom")])
def test_used_on_prefix_validation(used_on: str, expected_prefix: str | None, monkeypatch: pytest.MonkeyPatch) -> None:
    parser = etree.XMLParser()
    parser.set_element_class_lookup(etree.ElementDefaultClassLookup(element=ModelObject))
    parent = etree.fromstring(
        f'<xs:appinfo xmlns:xs="{XbrlConst.xsd}" xmlns:link="{XbrlConst.link}" xmlns:custom="urn:custom">'
        f'<link:roleType roleURI="urn:role" id="role"><link:usedOn>{used_on}</link:usedOn></link:roleType>'
        '</xs:appinfo>', parser,
    )
    model = SimpleNamespace(error=Mock(), roleTypes=defaultdict(list), arcroleTypes=defaultdict(list))
    document = SimpleNamespace(type=ModelDocumentType.SCHEMA, idObjects={})
    validator = SimpleNamespace(
        modelXbrl=model,
        validateSBRNL=True,
        validateEFM=False,
        validateEFMorGFMorSBRNL=True,
        validateXmlLang=False,
        schemaRoleTypes={},
        schemaArcroleTypes={},
        elementIDs={},
        conceptNames={},
        valUsedPrefixes=set(),
        disclosureSystem=SimpleNamespace(baseTaxonomyNamespaces={XbrlConst.xsd, XbrlConst.link, "urn:custom"}),
    )

    def validate_role(model_xbrl: object, role: ModelObject) -> None:
        for child in role:
            XmlValidate.validateValue(model_xbrl, child, None, "QName", child.text)

    monkeypatch.setattr(XmlValidate, "validate", validate_role)
    ValidateXbrlDTS.checkElements(validator, document, parent)

    if expected_prefix is None:
        assert model.error.call_args_list[0].args[0] == "xmlSchema:valueError"
        assert "undeclared" not in validator.valUsedPrefixes
    else:
        assert expected_prefix in validator.valUsedPrefixes
        model.error.assert_not_called()
