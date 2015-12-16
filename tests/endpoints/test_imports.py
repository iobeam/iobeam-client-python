import unittest

from iobeam.endpoints import imports
from iobeam.resources import data
from tests.http import dummy_backend
from tests.http import request

_PROJECT_ID = 1
_DEVICE_ID = "test_id"
_TOKEN = dummy_backend.TOKEN

ImportService = imports.ImportService
DataStore = data.DataStore
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

    def _basicBatchRequestChecks(self, req, fieldsLen, dataRows):
        self.assertTrue(req is not None)
        self.assertEqual(_PROJECT_ID, req["project_id"])
        self.assertEqual(_DEVICE_ID, req["device_id"])
        self.assertTrue(req["sources"] is not None)
        self.assertEqual(fieldsLen, len(req["sources"]["fields"]))
        self.assertEqual(dataRows, len(req["sources"]["data"]))

    def test_makeBatchRequest(self):
        batch = DataStore(["series1", "series2"])
        FIELDS_LEN = 1 + len(batch.columns())
        req = ImportService._makeBatchRequest(_PROJECT_ID, _DEVICE_ID, batch)
        self._basicBatchRequestChecks(req, FIELDS_LEN, 0)

        batch.add(0, {"series1": 1, "series2": 2})
        req = ImportService._makeBatchRequest(_PROJECT_ID, _DEVICE_ID, batch)
        self._basicBatchRequestChecks(req, FIELDS_LEN, 1)

    def test_makeListOfBatchReqs(self):
        LIMIT = ImportService._BATCH_SIZE
        batch = DataStore(["series1", "series2"])
        reqs = ImportService._makeListOfBatchReqs(_PROJECT_ID, _DEVICE_ID, batch)
        self.assertEqual(0, len(reqs))

        batch.add(0, {"series1": 1, "series2": 2})
        reqs = ImportService._makeListOfBatchReqs(_PROJECT_ID, _DEVICE_ID, batch)
        self.assertEqual(1, len(reqs))

        limitRows = LIMIT // len(batch.columns()) - 1
        # just under limit
        for i in range(0, limitRows - 1):
            batch.add(i + 1, {"series1": i + 2, "series2": i + 3})
        reqs = ImportService._makeListOfBatchReqs(_PROJECT_ID, _DEVICE_ID, batch)
        self.assertEqual(1, len(reqs))

        # at limit
        batch.add(5000, {"series1": 5001, "series2": 5002})
        reqs = ImportService._makeListOfBatchReqs(_PROJECT_ID, _DEVICE_ID, batch)
        self.assertEqual(1, len(reqs))

        # over limit
        batch.add(10000, {"series1": 10001, "series2": 10002})
        reqs = ImportService._makeListOfBatchReqs(_PROJECT_ID, _DEVICE_ID, batch)
        self.assertEqual(2, len(reqs))

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

    def test_importBatchBadArgs(self):
        dummy = DummyBackend()
        # bad project id
        service = ImportService(_TOKEN, requester=request.DummyRequester(dummy))
        try:
            _ = service.importBatch(0, _DEVICE_ID, None)
            self.assertTrue(False)
        except ValueError:
            pass

        # bad token
        service = ImportService("", requester=request.DummyRequester(dummy))
        try:
            _ = service.importBatch(_PROJECT_ID, _DEVICE_ID, None)
            self.assertTrue(False)
        except ValueError:
            pass

        # bad device id
        service = ImportService(_TOKEN, requester=request.DummyRequester(dummy))
        try:
            _ = service.importBatch(_PROJECT_ID, "", None)
            self.assertTrue(False)
        except ValueError:
            pass

    def test_importBatch(self):
        dummy = DummyBackend()
        service = ImportService(_TOKEN, requester=request.DummyRequester(dummy))
        self.assertEqual(_TOKEN, service.token)
        self.assertTrue(service.requester() is not None)

        batch = DataStore(["t"])
        for i in range(0, 10):
            batch.add(i, {"t": i})
        success, extra = service.importBatch(_PROJECT_ID, _DEVICE_ID, batch)
        self.assertTrue(success)
        self.assertTrue(extra is None)
        self.assertEqual(1, dummy.calls)

        body = dummy.lastJson
        self.assertEqual(_PROJECT_ID, body["project_id"])
        self.assertEqual(_DEVICE_ID, body["device_id"])

        sources = body["sources"]
        self.assertEqual(2, len(sources))
        self.assertEqual(2, len(sources["fields"]))
        self.assertEqual("time", sources["fields"][0])
        self.assertEqual("t", sources["fields"][1])
        self.assertEqual(10, len(sources["data"]))
