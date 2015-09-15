import unittest

from iobeam.resources import data


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


class TestDataSeries(unittest.TestCase):

    def test_constructorNonePoints(self):
        name = "test"
        pts = None

        ds = data.DataSeries(name, pts)
        self.assertEqual("test", ds.getName())
        self.assertEqual(0, len(ds.getPoints()))
        self.assertEqual(0, len(ds))

    def test_constructorEmptyPoints(self):
        name = "test"
        pts = []

        ds = data.DataSeries(name, pts)
        self.assertEqual("test", ds.getName())
        self.assertEqual(0, len(ds.getPoints()))
        self.assertEqual(0, len(ds))

    def test_constructor(self):
        name = "test"
        pts = [data.DataPoint(1), data.DataPoint(2), data.DataPoint(3)]

        ds = data.DataSeries(name, pts)
        self.assertEqual("test", ds.getName())
        self.assertEqual(3, len(ds.getPoints()))
        self.assertEqual(3, len(ds))
        for i in range(0, len(pts)):
            self.assertEqual(pts[i], ds.getPoints()[i])

    # TODO: Add checks/tests for whether lists are of right type?


class TestStaticFuncs(unittest.TestCase):

    _SERIES_NAME = "test"

    def test_makeUniformDataSeriesInvalid(self):
        _SERIES_NAME = TestStaticFuncs._SERIES_NAME

        # No name == None
        ret = data.makeUniformDataSeries(None, 0, 10, [0])
        self.assertTrue(ret is None)

        # Non-int start time == None
        ret = data.makeUniformDataSeries(_SERIES_NAME, None, 10, [0])
        self.assertTrue(ret is None)

        ret = data.makeUniformDataSeries(_SERIES_NAME, "0", 10, [0])
        self.assertTrue(ret is None)

        # Non-int end time == None
        ret = data.makeUniformDataSeries(_SERIES_NAME, 0, None, [0])
        self.assertTrue(ret is None)

        ret = data.makeUniformDataSeries(_SERIES_NAME, 0, "10", [0])
        self.assertTrue(ret is None)

        # Invalid time range == None
        ret = data.makeUniformDataSeries(_SERIES_NAME, 0, 0, [0])
        self.assertTrue(ret is None)

        ret = data.makeUniformDataSeries(_SERIES_NAME, 10, 0, [0])
        self.assertTrue(ret is None)

        # No points == empty list
        ret = data.makeUniformDataSeries(_SERIES_NAME, 0, 10, None)
        self.assertTrue(ret is not None)
        self.assertTrue(isinstance(ret, data.DataSeries))
        self.assertEqual(0, len(ret))
        self.assertEqual(_SERIES_NAME, ret.getName())

        ret = data.makeUniformDataSeries(_SERIES_NAME, 0, 10, [])
        self.assertTrue(ret is not None)
        self.assertTrue(isinstance(ret, data.DataSeries))
        self.assertEqual(0, len(ret))
        self.assertEqual(_SERIES_NAME, ret.getName())

    def test_makeUniformDataSeries(self):
        _SERIES_NAME = TestStaticFuncs._SERIES_NAME

        start = 10
        end = 110

        values = [0]
        ret = data.makeUniformDataSeries(_SERIES_NAME, start, end, values)
        self.assertTrue(isinstance(ret, data.DataSeries))
        self.assertEqual(1, len(ret))
        self.assertEqual(data.DataPoint(0, timestamp=start), ret.getPoints()[0])

        values = [0, 1]
        ret = data.makeUniformDataSeries(_SERIES_NAME, start, end, values)
        self.assertTrue(isinstance(ret, data.DataSeries))
        self.assertEqual(2, len(ret))
        self.assertEqual(data.DataPoint(0, timestamp=start), ret.getPoints()[0])
        self.assertEqual(data.DataPoint(1, timestamp=end), ret.getPoints()[1])

        values = [0, 1, 2]
        ret = data.makeUniformDataSeries(_SERIES_NAME, start, end, values)
        self.assertTrue(isinstance(ret, data.DataSeries))
        self.assertEqual(3, len(ret))
        pts = ret.getPoints()
        self.assertEqual(data.DataPoint(0, timestamp=start), pts[0])
        mid = int(start + ((end - start) / 2))
        self.assertEqual(data.DataPoint(1, timestamp=mid), pts[1])
        self.assertEqual(data.DataPoint(2, timestamp=end), pts[2])

        values = [0, 1, 2, 3]
        ret = data.makeUniformDataSeries(_SERIES_NAME, start, end, values)
        self.assertTrue(isinstance(ret, data.DataSeries))
        self.assertEqual(4, len(ret))
        pts = ret.getPoints()
        self.assertEqual(data.DataPoint(0, timestamp=start), pts[0])
        first_mid = int(start + ((end - start) / 3))
        second_mid = int(start + 2 * ((end - start) / 3))
        self.assertEqual(data.DataPoint(1, timestamp=first_mid), pts[1])
        self.assertEqual(data.DataPoint(2, timestamp=second_mid), pts[2])
        self.assertEqual(data.DataPoint(3, timestamp=end), pts[3])
