import unittest

from iobeam.endpoints import devices
from iobeam.resources import device
from tests.http import request

_PROJECT_ID = 0
_DEVICE_ID = "test_id"
_TOKEN = "dummy"

_TIMESTAMP = 5

_NONE_DEVICE_ID = "dummy_id"
_NONE_DEVICE_NAME = "dummy_name"

DeviceService = devices.DeviceService
Device = device.Device

class DummyDeviceService(request.DummyRequest):

    def __init__(self):
        request.DummyRequest.__init__(self, None, None)
        self.reset()

    def dummyExecute(self, url, params=None, headers=None, json=None):
        class Resp(dict):
            __getattr__, __setattr__ = dict.get, dict.__setitem__

            def json(self):
                return self

        self.lastParams = params
        self.lastHeaders = headers
        self.lastJson = json
        self.calls += 1

        if "devices/timestamp" in url:
            return Resp(self.getTimestamp())
        elif "devices" in url:
            did = None
            dname = None
            if "device_id" in self.body:
                did = self.body["device_id"]
            if "device_name" in self.body:
                dname = self.body["device_name"]
            return Resp(self.registerDevice(deviceId=did, deviceName=dname))
        else:
            return None

    def getTimestamp(self):
        return {"status_code": 200, "server_timestamp": _TIMESTAMP}

    def registerDevice(self, deviceId=None, deviceName=None):
        did = deviceId or _NONE_DEVICE_ID
        dname = deviceName or _NONE_DEVICE_NAME
        return {"status_code": 201, "device_id": did, "device_name": dname}

    def reset(self):
        self.lastParams = None
        self.lastHeaders = None
        self.lastJson = None
        self.calls = 0

class TestDeviceService(unittest.TestCase):

    def test_getTimestamp(self):
        dummy = DummyDeviceService()
        service = DeviceService(_TOKEN, requester=request.DummyRequester(dummy))
        self.assertEqual(_TOKEN, service.token)
        self.assertTrue(service._requester is not None)

        ret = service.getTimestamp()
        self.assertEqual(_TIMESTAMP, ret)
        self.assertEqual(1, dummy.calls)

    def _checkDevice(self, ret, pid, did, dname):
        self.assertTrue(isinstance(ret, Device))
        self.assertEqual(pid, ret.projectId)
        self.assertEqual(did, ret.deviceId)
        self.assertEqual(dname, ret.deviceName)

    def test_registerDeviceNone(self):
        dummy = DummyDeviceService()
        service = DeviceService(_TOKEN, requester=request.DummyRequester(dummy))
        self.assertEqual(_TOKEN, service.token)
        self.assertTrue(service._requester is not None)

        ret = service.registerDevice(1)
        self._checkDevice(ret, 1, _NONE_DEVICE_ID, _NONE_DEVICE_NAME)
        self.assertEqual(1, dummy.calls)

    def test_registerDevice(self):
        dummy = DummyDeviceService()
        service = DeviceService(_TOKEN, requester=request.DummyRequester(dummy))
        self.assertEqual(_TOKEN, service.token)
        self.assertTrue(service._requester is not None)

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

    # TODO test error conditions
