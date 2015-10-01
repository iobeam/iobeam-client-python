import unittest

from iobeam.utils import utils

_PROJECT_ID = 1
_DEVICE_ID = "py_test_id"
_DEVICE_NAME = "py_test_device"


class TestUtilsFuncs(unittest.TestCase):

    def test_checkValidProjectId(self):
        def verify(pid, msg):
            try:
                utils.checkValidProjectId(pid)
            except ValueError as e:
                self.assertEqual(msg, str(e))

        verify(None, "projectId must be an int")
        verify("50", "projectId must be an int")
        verify(-1, "projectId must be greater than 0")
        verify(0, "projectId must be greater than 0")

        # Should be valid
        utils.checkValidProjectId(1)
        utils.checkValidProjectId(14436643675940)
        self.assertTrue(True)

    def test_checkValidDeviceId(self):
        def verify(did, msg):
            try:
                utils.checkValidDeviceId(did)
            except ValueError as e:
                self.assertEqual(msg, str(e))

        verify(None, "deviceId must be a string")
        verify(1, "deviceId must be a string")
        verify("", "deviceId must be more than 0 characters")

        # Should be valid
        utils.checkValidDeviceId("valid")
        self.assertTrue(True)

    def test_checkValidProjectToken(self):
        def verify(token, msg):
            try:
                utils.checkValidProjectToken(token)
            except ValueError as e:
                self.assertEqual(msg, str(e))

        verify(None, "token must be a string")
        verify(1, "token must be a string")
        verify("", "token must be more than 0 characters")

        # Should be valid
        utils.checkValidProjectToken("valid")
        self.assertTrue(True)
