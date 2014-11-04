from unittest import TestCase

from octopus.modules.sherpafact import client

class TestClient(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_01_url(self):
        fc = client.FactClient()

        url = fc.get_query_url("123", journal_title="My Journal", output="xml", trail=True)
        expected = fc.base_url + "?ak=" + fc.access_key + "&juliet_id=123&journaltitle=My+Journal&querytype=exact&markup=xml&trail=show"
        assert url == expected, (url, expected)

        url = fc.get_query_url(["123", 456], journal_title="My Journal", query_type="contains", trail=False)
        expected = fc.base_url + "?ak=" + fc.access_key + "&juliet_id=123%2C456&journaltitle=My+Journal&querytype=contains&markup=json&trail=hide"
        assert url == expected, (url, expected)

        url = fc.get_query_url(444, issn="1234-5678", output="php", trail=True)
        expected = fc.base_url + "?ak=" + fc.access_key + "&juliet_id=444&issn=1234-5678&markup=php&trail=show"
        assert url == expected, (url, expected)


