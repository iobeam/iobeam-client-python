import unittest

from iobeam.resources import data

_PROJECT_ID = 1
_DEVICE_ID = "py_test_id"
_DEVICE_NAME = "py_test_device"


class TestDataPoint(unittest.TestCase):

    def test_fullConstructor(self):
        dp = data.DataPoint(5, timestamp=10)
        self.assertEqual(5, dp._value)
        self.assertEqual(10, dp._timestamp)
        self.assertEqual("DataPoint{timestamp: 10, value: 5}", str(dp))

        dp = data.DataPoint(5.0, timestamp=11)
        self.assertEqual(5.0, dp._value)
        self.assertEqual(11, dp._timestamp)

    def test_impliedConstructor(self):
        dp = data.DataPoint(50)
        self.assertEqual(50, dp._value)
        self.assertTrue(dp._timestamp is not None)

    def test_invalidTimestamp(self):
        try:
            dp = data.DataPoint(500, timestamp="now")
            self.assertTrue(False)
        except ValueError:
            pass

    def test_invalidValues(self):
        try:
            dp = data.DataPoint("500")
            self.assertTrue(False)
        except ValueError:
            pass

    def test_toDict(self):
        dp = data.DataPoint(5, timestamp=10)
        ret = dp.toDict()
        self.assertEqual(2, len(ret))
        self.assertEqual(10, ret["time"])
        self.assertEqual(5, ret["value"])
