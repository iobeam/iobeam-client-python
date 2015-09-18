import unittest

from iobeam.http import request as req
from iobeam.endpoints import devices
from iobeam.resources import device
from tests.http import dummy_backend
from tests.http import request

_PROJECT_ID = 0
_DEVICE_ID = "test_id"
_TOKEN = dummy_backend.TOKEN

_TIMESTAMP = 5

_NONE_DEVICE_ID = "dummy_id"
_NONE_DEVICE_NAME = "dummy_name"

DeviceService = devices.DeviceService
Device = device.Device
DummyBackend = dummy_backend.DummyBackend


class TestDeviceService(unittest.TestCase):

    def test_createService(self):
        registerReturn = (_NONE_DEVICE_ID, _NONE_DEVICE_NAME)
        dummy = DummyBackend(registerReturn=registerReturn)
        service = DeviceService(_TOKEN, requester=request.DummyRequester(dummy))
        self.assertEqual(_TOKEN, service.token)
        self.assertTrue(service.requester() is not None)
        self.assertTrue(isinstance(service.requester(), request.DummyRequester))

    def test_getTimestamp(self):
        dummy = DummyBackend(timestampReturn=_TIMESTAMP)
        service = DeviceService(_TOKEN, requester=request.DummyRequester(dummy))

        ret = service.getTimestamp()
        self.assertEqual(_TIMESTAMP, ret)
        self.assertEqual(1, dummy.calls)

    def test_getTimestampBadToken(self):
        dummy = DummyBackend(timestampReturn=_TIMESTAMP)
        service = DeviceService("wrong", requester=request.DummyRequester(dummy))

        ret = service.getTimestamp()
        self.assertEqual(-1, ret)
        self.assertEqual(1, dummy.calls)

    def _checkDevice(self, ret, pid, did, dname):
        self.assertTrue(isinstance(ret, Device))
        self.assertEqual(pid, ret.projectId)
        self.assertEqual(did, ret.deviceId)
        self.assertEqual(dname, ret.deviceName)

    def test_registerDeviceNone(self):
        registerReturn = (_NONE_DEVICE_ID, _NONE_DEVICE_NAME)
        dummy = DummyBackend(registerReturn=registerReturn)
        service = DeviceService(_TOKEN, requester=request.DummyRequester(dummy))

        ret = service.registerDevice(1)
        self._checkDevice(ret, 1, _NONE_DEVICE_ID, _NONE_DEVICE_NAME)
        self.assertEqual(1, dummy.calls)

    def test_registerDevice(self):
        registerReturn = (_NONE_DEVICE_ID, _NONE_DEVICE_NAME)
        dummy = DummyBackend(registerReturn=registerReturn)
        service = DeviceService(_TOKEN, requester=request.DummyRequester(dummy))

        ret = service.registerDevice(1, deviceId="a_given_id")
        self._checkDevice(ret, 1, "a_given_id", _NONE_DEVICE_NAME)
        self.assertEqual(1, dummy.calls)
        body = dummy.lastJson
        self.assertEqual("a_given_id", body["device_id"])

        ret = service.registerDevice(
            1, deviceId="a_given_id2", deviceName="a_given_name")
        self._checkDevice(ret, 1, "a_given_id2", "a_given_name")
        self.assertEqual(2, dummy.calls)
        body = dummy.lastJson
        self.assertEqual("a_given_id2", body["device_id"])
        self.assertEqual("a_given_name", body["device_name"])

        ret = service.registerDevice(1, deviceName="a_given_name2")
        self._checkDevice(ret, 1, _NONE_DEVICE_ID, "a_given_name2")
        self.assertEqual(3, dummy.calls)
        body = dummy.lastJson
        self.assertEqual("a_given_name2", body["device_name"])

    def test_registerDeviceDupeId(self):
        registerReturn = (_NONE_DEVICE_ID, _NONE_DEVICE_NAME)
        dummy = DummyBackend(registerReturn=registerReturn)
        service = DeviceService(_TOKEN, requester=request.DummyRequester(dummy))

        regId = "a_given_id"
        ret = service.registerDevice(1, deviceId=regId)
        self._checkDevice(ret, 1, regId, _NONE_DEVICE_NAME)
        self.assertEqual(1, dummy.calls)
        body = dummy.lastJson
        self.assertEqual(regId, body["device_id"])

        try:
            ret = service.registerDevice(1, deviceId=regId)
            self.assertTrue(False)
        except req.Error as e:
            self.assertEqual(2, dummy.calls)
            self.assertEqual("Received unexpected code: 422", str(e))

    def test_registerDeviceDupeName(self):
        registerReturn = (_NONE_DEVICE_ID, _NONE_DEVICE_NAME)
        dummy = DummyBackend(registerReturn=registerReturn)
        service = DeviceService(_TOKEN, requester=request.DummyRequester(dummy))

        regName = "a_given_name"
        ret = service.registerDevice(1, deviceName=regName)
        self._checkDevice(ret, 1, _NONE_DEVICE_ID, regName)
        self.assertEqual(1, dummy.calls)
        body = dummy.lastJson
        self.assertEqual(regName, body["device_name"])

        try:
            ret = service.registerDevice(1, deviceName=regName)
            self.assertTrue(False)
        except req.Error as e:
            self.assertEqual(2, dummy.calls)
            self.assertEqual("Received unexpected code: 422", str(e))

    def test_registerBadToken(self):
        registerReturn = (_NONE_DEVICE_ID, _NONE_DEVICE_NAME)
        dummy = DummyBackend(registerReturn=registerReturn)
        service = DeviceService("wrong", requester=request.DummyRequester(dummy))

        regId = "a_given_id"
        try:
            ret = service.registerDevice(1, deviceId=regId)
            self.assertTrue(False)
        except req.UnauthorizedError:
            self.assertEqual(1, dummy.calls)
