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

    def __init__(self, method, url):
        request.DummyRequest.__init__(self, method, url)
        self.lastUrl = None
        self.lastParams = None
        self.lastHeaders = None
        self.lastJson = None

    def dummyExecute(self, url, params=None, headers=None, json=None):
        class Resp(dict):
            __getattr__, __setattr__ = dict.get, dict.__setitem__

            def json(self):
                return self

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

class TestDeviceService(unittest.TestCase):

    def test_getTimestamp(self):
        service = DeviceService(
            _TOKEN, requester=request.DummyRequester(DummyDeviceService))
        self.assertEqual(_TOKEN, service.token)
        self.assertTrue(service._requester is not None)

        ret = service.getTimestamp()
        self.assertEqual(_TIMESTAMP, ret)

    def _checkDevice(self, ret, pid, did, dname):
        self.assertTrue(isinstance(ret, Device))
        self.assertEqual(pid, ret.projectId)
        self.assertEqual(did, ret.deviceId)
        self.assertEqual(dname, ret.deviceName)

    def test_registerDeviceNone(self):
        service = DeviceService(
            _TOKEN, requester=request.DummyRequester(DummyDeviceService))
        self.assertEqual(_TOKEN, service.token)
        self.assertTrue(service._requester is not None)

        ret = service.registerDevice(1)
        self._checkDevice(ret, 1, _NONE_DEVICE_ID, _NONE_DEVICE_NAME)

    def test_registerDevice(self):
        service = DeviceService(
            _TOKEN, requester=request.DummyRequester(DummyDeviceService))
        self.assertEqual(_TOKEN, service.token)
        self.assertTrue(service._requester is not None)

        ret = service.registerDevice(1, deviceId="a_given_id")
        self._checkDevice(ret, 1, "a_given_id", _NONE_DEVICE_NAME)

        ret = service.registerDevice(
            1, deviceId="a_given_id2", deviceName="a_given_name")
        self._checkDevice(ret, 1, "a_given_id2", "a_given_name")

        ret = service.registerDevice(1, deviceName="a_given_name2")
        self._checkDevice(ret, 1, _NONE_DEVICE_ID, "a_given_name2")
