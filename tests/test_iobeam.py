import unittest
import sys
if sys.version_info > (3, 2):
    from unittest.mock import patch
else:
    from mock import patch

from iobeam import iobeam
from iobeam.endpoints import devices
from iobeam.resources import data
from tests.http import dummy_backend
from tests.http import request

def checkTokenNone():
    pass

DummyBackend = dummy_backend.DummyBackend

class TestClientBuilder(unittest.TestCase):

    def test_constructor(self):
        builder = iobeam.ClientBuilder(1, "dummy")
        self.assertEqual(1, builder._projectId)
        self.assertEqual("dummy", builder._projectToken)

    def test_constructorFails(self):
        def verify(pid, token):
            try:
                builder = iobeam.ClientBuilder(pid, token)
                self.assertTrue(False)
            except ValueError:
                pass

        # Bad project ids
        bads = [None, "1", 0]
        for p in bads:
            verify(p, "dummy")

        # Bad tokens
        bads = [None, 1, ""]
        for t in bads:
            verify(1, t)

    def test_chainable(self):
        builder = iobeam.ClientBuilder(1, "dummy")
        self.assertEqual(builder, builder.saveToDisk())
        self.assertEqual(builder, builder.setDeviceId("dummy"))
        self.assertEqual(builder, builder.registerOrSetId("dummy"))
        self.assertEqual(builder, builder.registerDevice("dummy"))
        self.assertEqual(builder, builder.setBackend("test.com"))

    def test_buildBasic(self):
        builder = iobeam.ClientBuilder(1, "dummy")
        with patch.object(iobeam._Client, "_checkToken"):
            client = builder.build()

        self.assertTrue(client is not None)
        self.assertTrue(isinstance(client, iobeam._Client))
        self.assertEqual(1, client.projectId)
        self.assertEqual("dummy", client.projectToken)
        self.assertTrue(client.getDeviceId() is None)
        self.assertFalse(client.isRegistered())

    def test_registerOrSet(self):
        builder = iobeam.ClientBuilder(1, "dummy").registerOrSetId("test")
        dummy = DummyBackend()
        backend = request.DummyRequester(dummy)
        builder._backend = backend
        with patch.object(iobeam._Client, "_checkToken"):
            client = builder.build()

        self.assertEqual("test", client.getDeviceId())
        self.assertEqual(1, dummy.calls)

        builder = iobeam.ClientBuilder(1, "dummy").registerOrSetId("test")
        builder._backend = backend
        with patch.object(iobeam._Client, "_checkToken"):
            client2 = builder.build()
        self.assertEqual("test", client2.getDeviceId())
        self.assertEqual(2, dummy.calls)

    def test_registerOrSetInvalid(self):
        def check(deviceId):
            try:
                builder = iobeam.ClientBuilder(1, "dummy").registerOrSetId(deviceId)
                self.assertTrue(False)
            except ValueError:
                pass

        badIds = [None, 5, ""]
        for i in badIds:
            check(i)

    def test_registerInvalid(self):
        def check(deviceId):
            try:
                builder = iobeam.ClientBuilder(1, "dummy")
                builder.registerDevice(deviceId=deviceId)
                self.assertTrue(False)
            except ValueError:
                pass

        # Note: None not included because that signals server to randomly generate
        # an id, rather than being an error.
        badIds = [5, ""]
        for i in badIds:
            check(i)


class TestClient(unittest.TestCase):

    def _testClientState(self, client, pid, ptoken, path):
        self.assertEqual(pid, client.projectId)
        self.assertEqual(ptoken, client.projectToken)
        self.assertEqual(path, client._path)
        self.assertEqual(0, len(client._dataset))

    def _makeTempClient(self, backend=None, deviceId=None):
        with patch.object(iobeam._Client, "_checkToken"):
            return iobeam._Client(None, 1, "dummy", backend, deviceId=deviceId)

    def test_constructorBasic(self):
        with patch.object(iobeam._Client, "_checkToken", return_value=None):
            client = iobeam._Client(None, 1, "dummy", None)
            self._testClientState(client, 1, "dummy", None)
            self.assertTrue(client._activeDevice is None)

    def test_isRegistered(self):
        client = self._makeTempClient()
        self.assertFalse(client.isRegistered())
        client.setDeviceId("fake")
        self.assertTrue(client.isRegistered())

        client = self._makeTempClient(deviceId="fake")
        self.assertTrue(client.isRegistered())

    def test_getAndSetDeviceId(self):
        client = self._makeTempClient()
        self.assertTrue(client.getDeviceId() is None)
        client.setDeviceId("fake")
        self.assertTrue(client.getDeviceId() is "fake")

        client = self._makeTempClient(deviceId="fake")
        self.assertTrue(client.getDeviceId() is "fake")
        client.setDeviceId("fake2")
        self.assertTrue(client.getDeviceId() is "fake2")
        try:
            client.setDeviceId(None)
            self.assertTrue(False)
        except ValueError:
            pass

    def test_addDataPointInvalidNames(self):
        client = self._makeTempClient()
        dp = iobeam.DataPoint(0)
        def verify(series, point):
            try:
                client.addDataPoint(series, point)
                self.assertTrue(False)
            except ValueError:
                pass

        vals = [
            (None, dp),
            (1, dp),
            ("", dp)
        ]
        for (series, point) in vals:
            verify(series, point)

    def test_addDataPointInvalidVals(self):
        client = self._makeTempClient()
        series = "test"
        def verify0(series, point):
            client.addDataPoint(series, point)
            self.assertEqual(0, len(client._dataset))

        vals = [
            (series, None),
            (series, "not a point")
        ]
        for (series, point) in vals:
            verify0(series, point)

    def test_addDataPoint(self):
        client = self._makeTempClient()
        series = "test"
        vals = [0, 11, 28]

        dp = iobeam.DataPoint(vals[0])
        client.addDataPoint(series, dp)
        self.assertEqual(1, len(client._dataset))
        self.assertEqual(1, len(client._dataset[series]))
        self.assertTrue(dp in client._dataset[series])

        dp = iobeam.DataPoint(vals[1])
        client.addDataPoint(series, dp)
        self.assertEqual(1, len(client._dataset))
        self.assertEqual(2, len(client._dataset[series]))
        self.assertTrue(dp in client._dataset[series])

        dp = iobeam.DataPoint(vals[2])
        client.addDataPoint(series, dp)
        self.assertEqual(1, len(client._dataset))
        self.assertEqual(3, len(client._dataset[series]))
        self.assertTrue(dp in client._dataset[series])

    def test_addDataSeriesInvalid(self):
        client = self._makeTempClient()
        def verify0(val):
            try:
                client.addDataSeries(val)
                self.assertTrue(False)
            except ValueError:
                pass

        vals = [None, "not a series"]
        for v in vals:
            verify0(v)

    def test_addDataSeriesInvalidNoError(self):
        client = self._makeTempClient()
        client.addDataSeries(iobeam.DataSeries("test", None))
        self.assertEqual(0, len(client._dataset))


    def test_addDataSeries(self):
        client = self._makeTempClient()
        series = "test"

        ds = data.makeUniformDataSeries(series, 0, 100, [0, 1, 2])
        client.addDataSeries(ds)
        self.assertEqual(1, len(client._dataset))
        self.assertEqual(3, len(client._dataset[series]))
        for p in ds.getPoints():
            self.assertTrue(p in client._dataset[series])

        ds = data.makeUniformDataSeries(series, 101, 200, [3, 4, 5])
        client.addDataSeries(ds)
        self.assertEqual(1, len(client._dataset))
        self.assertEqual(6, len(client._dataset[series]))
        for p in ds.getPoints():
            self.assertTrue(p in client._dataset[series])

    def test_clearSeries(self):
        client = self._makeTempClient()
        series = "test"

        dp = iobeam.DataPoint(45)
        client.addDataPoint(series, dp)
        self.assertEqual(1, len(client._dataset))
        self.assertEqual(1, len(client._dataset[series]))
        client.clearSeries(series)
        self.assertEqual(0, len(client._dataset))

    def test_registerDevice(self):
        dummy = DummyBackend()
        backend = request.DummyRequester(dummy)
        client = self._makeTempClient(backend=backend)
        client._checkToken = checkTokenNone

        self.assertTrue(client._activeDevice is None)
        client.registerDevice()
        self.assertTrue(client._activeDevice is not None)
        self.assertEqual(1, dummy.calls)

    def test_registerDeviceSameAsSet(self):
        dummy = DummyBackend()
        backend = request.DummyRequester(dummy)
        client = self._makeTempClient(backend=backend, deviceId="fake")
        self.assertEqual("fake", client.getDeviceId())
        client.registerDevice()
        self.assertEqual("fake", client.getDeviceId())
        self.assertEqual(0, dummy.calls)
        client.registerDevice("fake")
        self.assertEqual("fake", client.getDeviceId())
        self.assertEqual(0, dummy.calls)

    def test_registerDupe(self):
        dummy = DummyBackend()
        backend = request.DummyRequester(dummy)
        client = self._makeTempClient(backend=backend)
        client._checkToken = checkTokenNone

        self.assertTrue(client._activeDevice is None)
        client.registerDevice(deviceId="dummy")
        self.assertTrue("dummy", client.getDeviceId())
        self.assertEqual(1, dummy.calls)

        backend = request.DummyRequester(dummy)
        client = self._makeTempClient(backend=backend)
        client._checkToken = checkTokenNone
        try:
            client.registerDevice(deviceId="dummy")
            self.assertTrue(False)
        except devices.DuplicateIdError:
            self.assertEqual(2, dummy.calls)
        client.registerDevice(deviceId="dummy", setOnDupe=True)
        self.assertTrue("dummy", client.getDeviceId())

    def test_registerBadIds(self):
        def check(client, deviceId):
            try:
                self.assertTrue(client._activeDevice is None)
                client.registerDevice(deviceId=deviceId)
                self.assertTrue(False)
            except ValueError:
                self.assertTrue(client._activeDevice is None)
                self.assertEqual(0, dummy.calls)

        dummy = DummyBackend()
        backend = request.DummyRequester(dummy)
        client = self._makeTempClient(backend=backend)
        badIds = [5, ""]
        for i in badIds:
            check(client, i)

    def test_convertDataSetToBatches(self):
        dummy = DummyBackend()
        backend = request.DummyRequester(dummy)
        client = self._makeTempClient(backend=backend, deviceId="fake")

        series = "test"
        vals = [0, 11, 28]
        ts = data.Timestamp(1)
        dp = iobeam.DataPoint(vals[0], timestamp=ts)
        client.addDataPoint(series, dp)
        ts = data.Timestamp(2)
        dp = iobeam.DataPoint(vals[1], timestamp=ts)
        client.addDataPoint(series, dp)
        self.assertEqual(1, len(client._dataset))
        self.assertEqual(0, len(client._batches))

        client._convertDataSetToBatches()
        self.assertEqual(0, len(client._dataset))
        self.assertEqual(1, len(client._batches))
        for b in client._batches:
            self.assertEqual(1, len(b.columns()))
            self.assertEqual(series, b.columns()[0])
            self.assertEqual(2, len(b))

    def test_send(self):
        dummy = DummyBackend()
        backend = request.DummyRequester(dummy)
        client = self._makeTempClient(backend=backend, deviceId="fake")
        client._checkToken = checkTokenNone

        series = "test"
        vals = [0, 11, 28]
        dp = iobeam.DataPoint(vals[0])
        client.addDataPoint(series, dp)

        client.send()
        self.assertEqual(0, len(client._dataset))
        self.assertEqual(1, dummy.calls)
        self.assertTrue(dummy.lastUrl.endswith("/imports"))
        self.assertEqual(1, dummy.lastJson["project_id"])
        self.assertEqual("fake", dummy.lastJson["device_id"])
        # 2: 'fields' and 'data', batch format
        self.assertEqual(2, len(dummy.lastJson["sources"]))

    def test_queryInvalid(self):
        def verify(token, qry):
            try:
                iobeam._Client.query(token, qry)
                self.assertTrue(False)
            except ValueError:
                pass
        qry = iobeam.QueryReq(1)
        bad = [
            (None, qry),
            ("dummy", None),
            ("dummy", "wrong type")
        ]
        for (t, q) in bad:
            verify(t, q)

    def test_query(self):
        want = {"test": "complete"}
        qry = iobeam.QueryReq(1)
        with patch.object(iobeam.exports.ExportService, "getData",
                          return_value=want) as mm:
            ret = iobeam._Client.query("dummy", qry)
            self.assertEqual(want, ret)
            mm.assert_called_once_with(qry)


    def test_makeQuery(self):
        want = {"test": "complete"}
        with patch.object(iobeam._Client, "query", return_value=want) as mm:
            ret = iobeam.makeQuery("dummy", None)
            self.assertEqual(want, ret)
            mm.assert_called_once_with("dummy", None, None)
