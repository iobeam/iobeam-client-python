import unittest

from iobeam.endpoints import imports
from iobeam.resources import data
from tests.http import dummy_backend
from tests.http import request

_PROJECT_ID = 1
_DEVICE_ID = "test_id"
_TOKEN = dummy_backend.TOKEN

ImportService = imports.ImportService
DataPoint = data.DataPoint
DummyBackend = dummy_backend.DummyBackend


def makeLinearDataSeries(limit):
    ret = set()
    for x in range(0, int(limit)):
        ret.add(DataPoint(x))

    return ret


class TestImportService(unittest.TestCase):

    def _basicRequestChecks(self, req, numSeries):
        self.assertTrue(req is not None)
        self.assertEqual(_PROJECT_ID, req["project_id"])
        self.assertEqual(_DEVICE_ID, req["device_id"])
        self.assertTrue(req["sources"] is not None)
        self.assertEqual(numSeries, len(req["sources"]))

    def test_makeRequest(self):
        data = {}
        req = ImportService._makeRequest(_PROJECT_ID, _DEVICE_ID, data)
        self._basicRequestChecks(req, 0)

        data = {
            "t": [DataPoint(5.0)]
        }
        req = ImportService._makeRequest(_PROJECT_ID, _DEVICE_ID, data)
        self._basicRequestChecks(req, 1)

        data = {
            "t1": [DataPoint(5.0)],
            "t2": [DataPoint(10.0)]
        }
        req = ImportService._makeRequest(_PROJECT_ID, _DEVICE_ID, data)
        self._basicRequestChecks(req, 2)

        data = {
            "t1": [DataPoint(5.0)],
            "t2": [DataPoint(10.0), DataPoint(20.0)]
        }
        req = ImportService._makeRequest(_PROJECT_ID, _DEVICE_ID, data)
        self._basicRequestChecks(req, 2)

    def _basicRequestListChecks(self, reqList, size):
        self.assertTrue(reqList is not None)
        self.assertEqual(size, len(reqList))

    def test_makeListOfReqsSmall(self):
        d = {"t": makeLinearDataSeries(0)}
        reqList = ImportService._makeListOfReqs(_PROJECT_ID, _DEVICE_ID, d)
        self._basicRequestListChecks(reqList, 0)

        d = {"t": makeLinearDataSeries(1)}
        reqList = ImportService._makeListOfReqs(_PROJECT_ID, _DEVICE_ID, d)
        self._basicRequestListChecks(reqList, 1)

        # Just under the limit
        LIMIT = ImportService._BATCH_SIZE
        d = {"t": makeLinearDataSeries(LIMIT - 1)}
        reqList = ImportService._makeListOfReqs(_PROJECT_ID, _DEVICE_ID, d)
        self._basicRequestListChecks(reqList, 1)

    def test_makeListOfReqsBig(self):
        LIMIT = ImportService._BATCH_SIZE

        # At the limit
        d = {"t": makeLinearDataSeries(LIMIT)}
        reqList = ImportService._makeListOfReqs(_PROJECT_ID, _DEVICE_ID, d)
        self._basicRequestListChecks(reqList, 1)

        # Just over the limit
        d = {"t": makeLinearDataSeries(LIMIT + 1)}
        reqList = ImportService._makeListOfReqs(_PROJECT_ID, _DEVICE_ID, d)
        self._basicRequestListChecks(reqList, 2)

        # At the 2x limit
        d = {"t": makeLinearDataSeries(LIMIT * 2)}
        reqList = ImportService._makeListOfReqs(_PROJECT_ID, _DEVICE_ID, d)
        self._basicRequestListChecks(reqList, 2)

        # Just over the 2x limit
        d = {"t": makeLinearDataSeries(LIMIT * 2 + 1)}
        reqList = ImportService._makeListOfReqs(_PROJECT_ID, _DEVICE_ID, d)
        self._basicRequestListChecks(reqList, 3)

    def test_makeListsOfReqsSmallSeries(self):
        LIMIT = ImportService._BATCH_SIZE

        d = {
            "t": makeLinearDataSeries(LIMIT - 1),
            "t2": makeLinearDataSeries(LIMIT / 2)
        }
        reqList = ImportService._makeListOfReqs(_PROJECT_ID, _DEVICE_ID, d)
        self._basicRequestListChecks(reqList, 2)

    def test_makeListsOfReqsMixed(self):
        LIMIT = ImportService._BATCH_SIZE

        d = {
            "t": makeLinearDataSeries(LIMIT - 1),  # 1 req
            "t2": makeLinearDataSeries(LIMIT + 2)  # 2 reqs
        }
        reqList = ImportService._makeListOfReqs(_PROJECT_ID, _DEVICE_ID, d)
        self._basicRequestListChecks(reqList, 3)

    def test_importDataSimple(self):
        dummy = DummyBackend()
        service = ImportService(_TOKEN, requester=request.DummyRequester(dummy))
        self.assertEqual(_TOKEN, service.token)
        self.assertTrue(service._requester is not None)

        dataset = {
            "t": makeLinearDataSeries(10)
        }
        success, extra = service.importData(1, _DEVICE_ID, dataset)
        self.assertTrue(success)
        self.assertTrue(extra is None)
        self.assertEqual(1, dummy.calls)
        body = dummy.lastJson
        self.assertEqual(1, body["project_id"])
        self.assertEqual(_DEVICE_ID, body["device_id"])
        self.assertEqual(1, len(body["sources"]))
        series = body["sources"][0]
        self.assertEqual("t", series["name"])
        self.assertEqual(10, len(series["data"]))

    def test_importDataComplex(self):
        LIMIT = ImportService._BATCH_SIZE
        dummy = DummyBackend()
        service = ImportService(_TOKEN, requester=request.DummyRequester(dummy))
        self.assertEqual(_TOKEN, service.token)
        self.assertTrue(service._requester is not None)

        dataset = {
            "t": makeLinearDataSeries(LIMIT - 1),  # 1 req
            "t2": makeLinearDataSeries(LIMIT + 2)  # 2 reqs
        }
        success, extra = service.importData(1, _DEVICE_ID, dataset)
        self.assertTrue(success)
        self.assertTrue(extra is None)
        self.assertEqual(3, dummy.calls)

    def test_importBadToken(self):
        dummy = DummyBackend()
        service = ImportService("wrong",
                                requester=request.DummyRequester(dummy))
        dataset = {
            "t": makeLinearDataSeries(10)
        }

        success, extra = service.importData(1, _DEVICE_ID, dataset)
        self.assertFalse(success)
        self.assertTrue(extra is not None)
        self.assertEqual(403, extra.status_code)
        self.assertEqual(1, dummy.calls)

    def test_importBadRequest(self):
        dummy = DummyBackend()
        service = ImportService(_TOKEN, requester=request.DummyRequester(dummy))
        class BrokenDataPoint(object):

            def toDict(self):
                return {"ts": "bad", "val": "bad"}
        dataset = {
            "t": [BrokenDataPoint()]
        }

        success, extra = service.importData(1, _DEVICE_ID, dataset)
        self.assertFalse(success)
        self.assertTrue(extra is not None)
        self.assertEqual(400, extra.status_code)
        self.assertEqual(1, dummy.calls)
