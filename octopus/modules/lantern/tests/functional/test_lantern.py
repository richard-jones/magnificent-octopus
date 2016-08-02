from unittest import TestCase

from octopus.lib import paths
from octopus.modules.lantern import client

import json

class TestLantern(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_01_check(self):
        lc = client.Lantern()
        assert lc.check()

    def test_02_create(self):
        lc = client.Lantern()
        with open(paths.rel2abs(__file__, "../resources/test.json")) as f:
            j = json.load(f)
        res = lc.create_job("lantern@oneoverzero.com", "test.csv", j)
        assert res is not None

    def test_03_job_info_user_info(self):
        lc = client.Lantern()
        with open(paths.rel2abs(__file__, "../resources/test.json")) as f:
            j = json.load(f)
        res = lc.create_job("lantern@oneoverzero.com", "test.csv", j)

        job_id = res["data"]["job"]
        info = lc.get_job_info(job_id)
        orig = lc.get_original_data(job_id)
        prog = lc.get_progress(job_id)
        todo = lc.get_todo(job_id)
        results = lc.get_results(job_id)
        csv = lc.get_results_csv(job_id)

        assert info is not None
        assert orig is not None
        assert prog is not None
        assert todo is not None
        assert results is not None
        assert csv is not None

        jobs = lc.list_jobs("lantern@oneoverzero.com")
        quota = lc.get_quota("lantern@oneoverzero.com")

        assert jobs is not None
        assert quota is not None


