import unittest

from iobeam.endpoints import tokens
from tests.http import dummy_backend
from tests.http import request

_OLD_TOKEN = dummy_backend.TOKEN
_NEW_TOKEN = dummy_backend.NEW_TOKEN

TokenService = tokens.TokenService
DummyBackend = dummy_backend.DummyBackend


class TestDeviceService(unittest.TestCase):

    def test_createService(self):
        dummy = DummyBackend()
        service = TokenService(requester=request.DummyRequester(dummy))
        self.assertEqual(None, service.token)
        self.assertTrue(service.requester() is not None)
        self.assertTrue(isinstance(service.requester(), request.DummyRequester))

    def test_getProjectToken(self):
        dummy = DummyBackend()
        service = TokenService(requester=request.DummyRequester(dummy))
        opts = {"device_id": "python-test", "refreshable": False}
        ret = service.getProjectToken("token", 1, duration="1d", options=opts)
        self.assertTrue(ret is not None)
        for o in opts:
            self.assertEqual(opts[o], ret[o])
        self.assertEqual("1d", ret["duration"])
        self.assertEqual(1, dummy.calls)

    def test_getProjectTokenWrong(self):
        def check(duration, opts):
            try:
                ret = service.getProjectToken("token", 1, duration=duration,
                    options=opts)
                self.assertTrue(False)
            except ValueError:
                pass
        dummy = DummyBackend()
        service = TokenService(requester=request.DummyRequester(dummy))

        check("5q", None)  # not a valid unit
        check("aw", None)  # not a valid number
        check(None, "not a dict")

    def test_refreshToken(self):
        dummy = DummyBackend()
        service = TokenService(requester=request.DummyRequester(dummy))

        ret = service.refreshToken(_OLD_TOKEN)
        self.assertTrue(ret is not None)
        self.assertEqual(_NEW_TOKEN, ret)
        self.assertEqual(1, dummy.calls)

    def test_refreshTokenWrong(self):
        dummy = DummyBackend()
        service = TokenService(requester=request.DummyRequester(dummy))

        try:
            ret = service.refreshToken(_OLD_TOKEN[:2])
        except request.UnknownCodeError:
            self.assertEqual(1, dummy.calls)
