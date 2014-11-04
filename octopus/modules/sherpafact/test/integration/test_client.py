from unittest import TestCase

from octopus.modules.sherpafact import client

class TestClientIntegration(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_01_raw_query(self):
        fc = client.FactClient()
        resp, url = fc.raw_query([698, 709], issn="0309-1325")

        assert resp.status_code == 200

    def test_02_query(self):
        fc = client.FactClient()
        f = fc.query([698, 709], issn="0309-1325")
        assert isinstance(f, client.FactJson)

