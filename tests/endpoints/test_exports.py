import unittest

from iobeam.endpoints import exports
from iobeam.resources import query
from tests.http import dummy_backend
from tests.http import request

_PROJECT_ID = 1
_DEVICE_ID = "testdevice"
_TOKEN = "dummy"

_TIMESTAMP = 5

_NONE_DEVICE_ID = "dummy_id"
_NONE_DEVICE_NAME = "dummy_name"

ExportService = exports.ExportService
Query = query.Query
DummyBackend = dummy_backend.DummyBackend


class TestExportService(unittest.TestCase):

    def _getProperUrl(self, pid, did=None, series=None):
        urlDid = did or "all"
        urlSeries = series or "all"

        return "/exports/{}/{}/{}".format(str(pid), urlDid, urlSeries)

    def test_constructor(self):
        dummy = DummyBackend()
        service = ExportService(_TOKEN, requester=request.DummyRequester(dummy))
        self.assertEqual(_TOKEN, service.token)
        self.assertTrue(service.requester() is not None)
        self.assertTrue(isinstance(service.requester(), request.DummyRequester))

    def test_getDataBasic(self):
        dummy = DummyBackend()
        service = ExportService(_TOKEN, requester=request.DummyRequester(dummy))

        q = Query(_PROJECT_ID)
        service.getData(q)
        shouldUrl = self._getProperUrl(_PROJECT_ID)
        self.assertTrue(dummy.lastUrl.endswith(shouldUrl))
        self.assertEqual(0, len(dummy.lastParams))

        q = Query(_PROJECT_ID, deviceId=_DEVICE_ID)
        service.getData(q)
        shouldUrl = self._getProperUrl(_PROJECT_ID, did=_DEVICE_ID)
        self.assertTrue(dummy.lastUrl.endswith(shouldUrl))
        self.assertEqual(0, len(dummy.lastParams))

        q = Query(_PROJECT_ID, seriesName="test")
        service.getData(q)
        shouldUrl = self._getProperUrl(_PROJECT_ID, series="test")
        self.assertTrue(dummy.lastUrl.endswith(shouldUrl))
        self.assertEqual(0, len(dummy.lastParams))

        q = Query(_PROJECT_ID, deviceId=_DEVICE_ID, seriesName="test")
        service.getData(q)
        shouldUrl = self._getProperUrl(_PROJECT_ID, did=_DEVICE_ID,
                                       series="test")
        self.assertTrue(dummy.lastUrl.endswith(shouldUrl))
        self.assertEqual(0, len(dummy.lastParams))

    def test_getDataWithParams(self):
        dummy = DummyBackend()
        service = ExportService(_TOKEN, requester=request.DummyRequester(dummy))

        q = Query(_PROJECT_ID).limit(5)
        service.getData(q)
        shouldUrl = self._getProperUrl(_PROJECT_ID)
        self.assertTrue(dummy.lastUrl.endswith(shouldUrl))
        self.assertEqual(1, len(dummy.lastParams))
        self.assertTrue("limit" in dummy.lastParams)

        q = q.fromTime(0).toTime(1000)
        service.getData(q)
        self.assertTrue(dummy.lastUrl.endswith(shouldUrl))
        self.assertEqual(3, len(dummy.lastParams))
        self.assertTrue("limit" in dummy.lastParams)
        self.assertTrue("from" in dummy.lastParams)
        self.assertTrue("to" in dummy.lastParams)
        self.assertEqual(2, dummy.calls)

    # TODO test error conditions
