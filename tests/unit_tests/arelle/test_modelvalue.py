from __future__ import annotations

import datetime

import pytest
from lxml import etree

from arelle.ModelObject import ModelObject
from arelle.ModelValue import QName, gDay, gMonthDay, qname, qnameFromNsmap

NSMAP = {
    None: "http://default.ns",
    "pfx": "http://pfx.ns",
    "other": "http://other.ns",
}


class TestQname:
    @pytest.mark.parametrize("value, name, expected", [
        ("undeclared:item", None, None),
        ("", "p:item", None),
        ("item", None, (None, None, "item")),
        ("", None, (None, None, "")),
        ("{urn:p}p:item", None, ("p", "urn:p", "item")),
        ("{urn:p}p:a:b", None, ("p:a", "urn:p", "b")),
        ("urn:p", "p:a:b", ("p", "urn:p", "a:b")),
        ("urn:p", "", (None, None, "")),
        ("{}p:item", None, None),
        ("{oops", None, (None, None, "oops")),
        ("  p:item  ", {"p": "urn:p"}, ("p", "urn:p", "item")),
        ("p:item", {}, None),
        ("item", {None: "urn:default"}, (None, "urn:default", "item")),
        ("p:item", {"p": ""}, ("p", "", "item")),
        ("{urn:p}item", {"urn:p": "p"}, ("p", "urn:p", "item")),
        ("{urn:p}item", {"p": "urn:p"}, ("p", "urn:p", "item")),
        (None, None, None),
        (42, None, None),
        ([], None, None),
    ])
    def test_result_fields(self, value, name, expected):
        result = qname(value, name)
        fields = None if result is None else (result.prefix, result.namespaceURI, result.localName)
        assert fields == expected

    @pytest.fixture
    def element(self):
        parser = etree.XMLParser()
        parser.set_element_class_lookup(etree.ElementDefaultClassLookup(element=ModelObject))
        return etree.fromstring(b'<p:root xmlns:p="urn:p" xmlns="urn:default"><child/></p:root>', parser)

    def test_qname_input_preserves_identity(self):
        for value in (QName("p", "urn:p", "item"), QName(None, None, "")):
            assert qname(value) is value

    def test_element_and_qname_names(self, element):
        expected = ("p", "urn:p", "root")
        for result in (qname(element), qname(element, None), qname(element, ""), qname(element, QName(None, None, ""))):
            assert (result.prefix, result.namespaceURI, result.localName) == expected
        name = QName("other", "urn:other", "item")
        assert qname(element, name) is name

    def test_element_namespace_resolution(self, element):
        for result in (qname(element, "p:item"), qname("p:item", element)):
            assert (result.prefix, result.namespaceURI, result.localName) == ("p", "urn:p", "item")
        assert qname(element, "undeclared:item") is None
        xml_name = qname(element, "xml:lang")
        assert (xml_name.prefix, xml_name.namespaceURI, xml_name.localName) == ("xml", "http://www.w3.org/XML/1998/namespace", "lang")

    def test_element_name_uses_existing_truthiness(self, element):
        assert qname(element, element) is None
        result = qname(element, element[0])
        assert (result.prefix, result.namespaceURI, result.localName) == ("p", "urn:p", "root")

    def test_default_namespace_can_be_disabled(self):
        result = qname("item", {None: "urn:default"}, noPrefixIsNoNamespace=True)
        assert (result.prefix, result.namespaceURI, result.localName) == (None, None, "item")
        assert qname("p:item", noPrefixIsNoNamespace=True) is None

    @pytest.mark.parametrize("flag, value", [("prefixException", "p:item"), ("castException", None)])
    def test_exception_class(self, flag, value):
        with pytest.raises(ValueError):
            qname(value, **{flag: ValueError})

    @pytest.mark.parametrize("flag, value", [("prefixException", "p:item"), ("castException", None)])
    def test_exception_instance_preserves_identity(self, flag, value):
        exception = ValueError("custom message")
        with pytest.raises(ValueError) as caught:
            qname(value, **{flag: exception})
        assert caught.value is exception

    @pytest.mark.parametrize("flag, value", [("prefixException", "p:item"), ("castException", None)])
    def test_falsey_exception_flags_preserve_none_result(self, flag, value):
        class FalseyException(Exception):
            def __bool__(self):
                return False

        class FalseyMeta(type):
            def __bool__(cls):
                return False

        class FalseyExceptionClass(Exception, metaclass=FalseyMeta):
            pass

        assert qname(value, **{flag: FalseyException()}) is None
        assert qname(value, **{flag: FalseyExceptionClass}) is None


class TestQnameFromNsmap:
    def test_unprefixed_name(self):
        result = qnameFromNsmap(NSMAP, "localName")
        assert result == QName(None, "http://default.ns", "localName")

    def test_prefixed_name(self):
        result = qnameFromNsmap(NSMAP, "pfx:localName")
        assert result == QName("pfx", "http://pfx.ns", "localName")

    def test_xml_prefix(self):
        result = qnameFromNsmap(NSMAP, "xml:lang")
        assert result == QName("xml", "http://www.w3.org/XML/1998/namespace", "lang")

    def test_href_style(self):
        result = qnameFromNsmap(NSMAP, "http://some.ns#localName")
        assert result == QName(None, "http://some.ns", "localName")

    def test_href_no_namespace(self):
        result = qnameFromNsmap(NSMAP, "#localName")
        assert result == QName(None, "", "localName")

    def test_undefined_prefix_returns_none(self):
        result = qnameFromNsmap(NSMAP, "bad:localName")
        assert result is None

    def test_undefined_prefix_raises_custom_exception(self):
        with pytest.raises(ValueError):
            qnameFromNsmap(NSMAP, "bad:localName", prefixException=ValueError)

    def test_undefined_prefix_raises_custom_exception_instance(self):
        with pytest.raises(ValueError, match="my message"):
            qnameFromNsmap(NSMAP, "bad:localName", prefixException=ValueError("my message"))

    def test_no_default_namespace(self):
        nsmap = {"pfx": "http://pfx.ns"}
        result = qnameFromNsmap(nsmap, "localName")
        assert result == QName(None, None, "localName")

    def test_empty_nsmap(self):
        result = qnameFromNsmap({}, "localName")
        assert result == QName(None, None, "localName")

    def test_empty_nsmap_with_prefix_returns_none(self):
        result = qnameFromNsmap({}, "pfx:localName")
        assert result is None

    def test_empty_nsmap_with_prefix_raises(self):
        with pytest.raises(ValueError):
            qnameFromNsmap({}, "pfx:localName", prefixException=ValueError)


class TestGDateCombinedTimezoneOffset:
    """gMonthDay/gDay are the only g* types whose field unit (a calendar day, 24h) is
    shorter than the 28h two opposite +-14:00 offsets can combine to (XSD Datatypes
    3.2.7.3), so unlike gYear/gYearMonth/gMonth, adjacent-day values with different,
    explicit timezones can denote the *same* instant despite differing numeral fields.
    """

    def test_gMonthDay_adjacent_days_opposite_offsets_are_equal_instant(self):
        # --06-14 at -10:00 is 2000-06-14T10:00:00Z; --06-15 at +14:00 is also
        # 2000-06-14T10:00:00Z (2000-06-15T00:00:00 minus the +14:00 offset).
        a = gMonthDay(6, 14, tzinfo=datetime.timezone(datetime.timedelta(hours=-10)))
        b = gMonthDay(6, 15, tzinfo=datetime.timezone(datetime.timedelta(hours=14)))
        assert a == b
        assert not (a < b)
        assert not (a > b)
        assert a <= b and a >= b
        assert hash(a) == hash(b)

    def test_gDay_adjacent_days_opposite_offsets_are_equal_instant(self):
        a = gDay(14, tzinfo=datetime.timezone(datetime.timedelta(hours=-10)))
        b = gDay(15, tzinfo=datetime.timezone(datetime.timedelta(hours=14)))
        assert a == b
        assert not (a < b)
        assert not (a > b)
        assert hash(a) == hash(b)

    def test_gMonthDay_naive_vs_aware_never_equal_and_order_raises(self):
        naive = gMonthDay(6, 14)
        aware = gMonthDay(6, 14, tzinfo=datetime.timezone.utc)
        assert naive != aware
        assert not (naive == aware)
        with pytest.raises(TypeError):
            naive < aware

    def test_gMonthDay_large_gap_still_determinate_despite_offsets(self):
        # A gap of many days can never be closed by a <=28h combined swing.
        early = gMonthDay(1, 1, tzinfo=datetime.timezone(datetime.timedelta(hours=-14)))
        late = gMonthDay(6, 15, tzinfo=datetime.timezone(datetime.timedelta(hours=14)))
        assert early < late
        assert not (early == late)
