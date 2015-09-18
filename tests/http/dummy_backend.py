from tests.http import request
from time import time

class DummyBackend(request.DummyRequest):

    def __init__(self, timestampReturn=None, registerReturn=None):
        request.DummyRequest.__init__(self, None, None)
        self.reset()
        if timestampReturn is None:
            self._timestamp = int(time() * 1000)
        else:
            self._timestamp = int(timestampReturn)

        if registerReturn is None:
            self._register = ("break", "test")
        else:
            self._register = registerReturn

    def dummyExecute(self, url, params=None, headers=None, json=None):
        class Resp(dict):
            __getattr__, __setattr__ = dict.get, dict.__setitem__

            def json(self):
                return self

        self.lastUrl = url
        self.lastParams = params
        self.lastHeaders = headers
        self.lastJson = json
        self.calls += 1

        if url.endswith("/devices/timestamp"):
            return Resp(self.getTimestamp())
        elif url.endswith("/devices"):
            did = None
            dname = None
            if "device_id" in self.body:
                did = self.body["device_id"]
            if "device_name" in self.body:
                dname = self.body["device_name"]
            return Resp(self.registerDevice(deviceId=did, deviceName=dname))
        elif url.endswith("/imports"):
            return Resp(self.importData())
        elif "/exports" in url:
            return Resp(self.getData())
        else:
            return None

    def getTimestamp(self):
        return {"status_code": 200, "server_timestamp": self._timestamp}

    def registerDevice(self, deviceId=None, deviceName=None):
        did = deviceId or self._register[0]
        dname = deviceName or self._register[1]
        # For compatibility with both Python 2 and 3.
        try:
            unicode
        except NameError:
            unicode = str  # Python3
        return {
            "status_code": 201,
            "device_id": unicode(did),
            "device_name": unicode(dname)
        }

    def importData(self):
        return {"status_code": 200}

    def getData(self):
        return {"status_code": 200}

    def reset(self):
        self.lastUrl = None
        self.lastParams = None
        self.lastHeaders = None
        self.lastJson = None
        self.calls = 0
