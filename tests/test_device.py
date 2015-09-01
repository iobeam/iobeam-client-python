import unittest

from iobeam.resources import device

_PROJECT_ID = 1
_DEVICE_ID = "py_test_id"
_DEVICE_NAME = "py_test_device"


class TestDevice(unittest.TestCase):

    def test_validConstructor(self):
        d = device.Device(_PROJECT_ID, _DEVICE_ID, deviceName=_DEVICE_NAME)
        self.assertEqual(_PROJECT_ID, d.projectId)
        self.assertEqual(_DEVICE_ID, d.deviceId)
        self.assertEqual(_DEVICE_NAME, d.deviceName)

    def test_validConstructorNoName(self):
        d = device.Device(_PROJECT_ID, _DEVICE_ID)
        self.assertEqual(_PROJECT_ID, d.projectId)
        self.assertEqual(_DEVICE_ID, d.deviceId)
        self.assertTrue(d.deviceName is None)

    def test_invalidProjectId(self):
        # None is not a valid project id
        badId = None
        try:
            d = device.Device(badId, _DEVICE_ID)
            self.assertTrue(False)
        except ValueError as e:
            self.assertEqual("projectId must be an int", str(e))

        # No non-int project ids
        badId = "50"
        try:
            d = device.Device(badId, _DEVICE_ID)
            self.assertTrue(False)
        except ValueError as e:
            self.assertEqual("projectId must be an int", str(e))

        # No negative project ids
        badId = -1
        try:
            d = device.Device(badId, _DEVICE_ID)
            self.assertTrue(False)
        except ValueError as e:
            self.assertEqual("projectId must be greater than 0", str(e))

        # 0 is not a valid project id
        badId = 0
        try:
            d = device.Device(badId, _DEVICE_ID)
            self.assertTrue(False)
        except ValueError as e:
            self.assertEqual("projectId must be greater than 0", str(e))

    def test_invalidDeviceId(self):
        # None is not a valid device id
        badId = None
        try:
            d = device.Device(_PROJECT_ID, badId)
            self.assertTrue(False)
        except ValueError as e:
            self.assertEqual("deviceId cannot be None", str(e))
