import unittest

from iobeam import iobeam

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


    def test_buildBasic(self):
        builder = iobeam.ClientBuilder(1, "dummy")
        client = builder.build()

        self.assertTrue(client is not None)
        self.assertTrue(isinstance(client, iobeam._Client))
        self.assertEqual(1, client.projectId)
        self.assertEqual("dummy", client.projectToken)
        self.assertTrue(client.getDeviceId() is None)
        self.assertFalse(client.isRegistered())


class TestClient(unittest.TestCase):

    def _testClientState(self, client, pid, ptoken, path):
        self.assertEqual(pid, client.projectId)
        self.assertEqual(ptoken, client.projectToken)
        self.assertEqual(path, client._path)
        self.assertEqual(0, len(client._dataset))

    def _makeTempClient(self, deviceId=None):
        return iobeam._Client(None, 1, "dummy", None, deviceId=deviceId)

    def test_constructorBasic(self):
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
