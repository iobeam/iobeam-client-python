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

        ret = service.refreshToken(_OLD_TOKEN[:2])
        self.assertTrue(ret is None)
        self.assertEqual(1, dummy.calls)
