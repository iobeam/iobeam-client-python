from iobeam.utils import utils
from tests.http import request
from time import time

# For compatibility with both Python 2 and 3.
# pylint: disable=redefined-builtin,invalid-name
if utils.IS_PY3:
    unicode = str
# pylint: enable=redefined-builtin,invalid-name


AUTH = "Authorization"
USER_TOKEN = "userdummy"
TOKEN = "dummy"
NEW_TOKEN = "newdummy"
_STATUS_CODE = "status_code"

class DummyBackend(request.DummyRequest):

    def __init__(self, timestampReturn=None, registerReturn=None):
        request.DummyRequest.__init__(self, None, None)
        self.reset()
        self._registeredIds = set()
        self._registeredNames = set()

        self._timestamp = int(timestampReturn or time() * 1000)
        self._register = registerReturn or ("break", "test")

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

        if url.endswith("/tokens/project") and self.method == "POST":
            return Resp(self.refreshToken(self.body["refresh_token"]))
        elif url.endswith("/tokens/project"):
            return Resp(self.newProjectToken(params))

        if AUTH not in headers or (headers[AUTH] != "Bearer {}".format(TOKEN)):
            return Resp({
                _STATUS_CODE: 403,
                "message": "bad token"
            })

        if url.endswith("/devices/timestamp"):
            return Resp(self.getTimestamp())
        elif url.endswith("/devices"):
            body = self.body
            did = body["device_id"] if "device_id" in body else None
            dname = body["device_name"] if "device_name" in body else None
            return Resp(self.registerDevice(deviceId=did, deviceName=dname))
        elif url.endswith("/imports"):
            fmt = params.get("fmt") if params is not None else None
            batch = fmt is "table"
            return Resp(self.importData(self.body, batch))
        elif "/exports" in url:
            return Resp(self.getData())
        else:
            return None

    def refreshToken(self, oldToken):
        if oldToken == TOKEN:
            return {_STATUS_CODE: 200, "token": NEW_TOKEN}
        else:
            return {_STATUS_CODE: 401, "message": "bad token"}

    def newProjectToken(self, params):
        read = params.get("read", True)
        write = params.get("write", True)
        admin = params.get("admin", True)

        # Instead of the string, we pass a JSON object to confirm
        # params are being passed correctly
        token = {"read": read, "write": write, "admin": admin}
        ret = {
            _STATUS_CODE: 200,
            "token": token,
            "read": read,
            "write": write,
            "admin": admin
        }
        if "duration" in params:
            token["duration"] = params.get("duration")
        if "refreshable" in params:
            token["refreshable"] = params.get("refreshable")
        if "device_id" in params:
            token["device_id"] = params.get("device_id")

        return ret

    def getTimestamp(self):
        return {
            _STATUS_CODE: 200,
            "server_timestamp": self._timestamp
        }

    # TODO - Change so subsequent calls without providing deviceId don't fail
    def registerDevice(self, deviceId=None, deviceName=None):
        did = deviceId or self._register[0]
        dname = deviceName or self._register[1]

        if did in self._registeredIds or dname in self._registeredNames:
            errors = []
            if did in self._registeredIds:
                errors.append(
                    {"code": 150, "message": "Device ID already in use"})
            elif dname in self._registeredNames:
                errors.append(
                    {"code": 151, "message": "Device name already in use"})
            return {
                _STATUS_CODE: 422,
                "errors": errors
            }
        self._registeredIds.add(did)
        self._registeredNames.add(dname)

        return {
            _STATUS_CODE: 201,
            "device_id": unicode(did),
            "device_name": unicode(dname)
        }

    def importData(self, body, isBatch):
        if ("project_id" not in body or
            "device_id" not in body or
            "sources" not in body):
            return {_STATUS_CODE: 400}
        elif isBatch:
            return {_STATUS_CODE: 200}
        else:
            for p in body["sources"]:
                if "name" not in p or "data" not in p:
                    return {_STATUS_CODE: 400}
                else:
                    for d in p["data"]:
                        if "time" not in d or "value" not in d:
                            return {_STATUS_CODE: 400}
        return {_STATUS_CODE: 200}

    def getData(self):
        return {_STATUS_CODE: 200}

    def reset(self):
        self.lastUrl = None
        self.lastParams = None
        self.lastHeaders = None
        self.lastJson = None
        self.calls = 0
