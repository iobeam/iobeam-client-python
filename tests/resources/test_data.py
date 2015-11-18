import unittest

from iobeam.resources import data


class TestTimestamp(unittest.TestCase):

    def test_invalidValues(self):
        def verify(val):
            try:
                ts = data.Timestamp(val)
                self.assertTrue(False)
            except ValueError:
                pass

        verify(None)
        verify("not an int")
        verify("5")
        verify(5.5)

    def test_explicitConstructor(self):
        ts = data.Timestamp(5, unit=data.TimeUnit.SECONDS)
        self.assertEqual(ts._type, data.TimeUnit.SECONDS)
        self.assertEqual(5000000, ts.asMicroseconds())

    def test_impliedConstructor(self):
        ts = data.Timestamp(5)
        self.assertEqual(ts._type, data.TimeUnit.MILLISECONDS)
        self.assertEqual(ts.asMicroseconds(), 5000)

    def test_constructorRealTime(self):
        ts = data.Timestamp(1443664367594)  # should be a long in 2.7
        self.assertEqual(ts._type, data.TimeUnit.MILLISECONDS)
        self.assertEqual(ts.asMicroseconds(), 1443664367594000)

    def test_asMilliseconds(self):
        secTs = data.Timestamp(5500, data.TimeUnit.SECONDS)
        msecTs = data.Timestamp(5500, data.TimeUnit.MILLISECONDS)
        usecTs = data.Timestamp(5500, data.TimeUnit.MICROSECONDS)
        usecTs2 = data.Timestamp(6000, data.TimeUnit.MICROSECONDS)

        self.assertEqual(5500000, secTs.asMilliseconds())
        self.assertEqual(5500, msecTs.asMilliseconds())
        self.assertEqual(5, usecTs.asMilliseconds())
        self.assertEqual(6, usecTs2.asMilliseconds())

    def test_asMicroseconds(self):
        secTs = data.Timestamp(5, data.TimeUnit.SECONDS)
        msecTs = data.Timestamp(5, data.TimeUnit.MILLISECONDS)
        usecTs = data.Timestamp(5, data.TimeUnit.MICROSECONDS)

        self.assertEqual(5000000, secTs.asMicroseconds())
        self.assertEqual(5000, msecTs.asMicroseconds())
        self.assertEqual(5, usecTs.asMicroseconds())


class TestDataPoint(unittest.TestCase):

    def test_fullConstructorWithAllTypes(self):
        dp = data.DataPoint(5, timestamp=10)
        self.assertEqual(5, dp._value)
        self.assertEqual(data.Timestamp(10, data.TimeUnit.MILLISECONDS),
                         dp._timestamp)
        self.assertEqual("DataPoint{timestamp: 10000, value: 5}", str(dp))

        dp = data.DataPoint(1443664367594000, timestamp=10)
        self.assertEqual(1443664367594000, dp._value)
        self.assertEqual(data.Timestamp(10, data.TimeUnit.MILLISECONDS),
                         dp._timestamp)

        dp = data.DataPoint(5.0, timestamp=11)
        self.assertEqual(5.0, dp._value)
        self.assertEqual(data.Timestamp(11, data.TimeUnit.MILLISECONDS),
                         dp._timestamp)

    def test_fullConstructorWithTimestamps(self):
        ts = data.Timestamp(5, data.TimeUnit.MICROSECONDS)
        dp = data.DataPoint(5, timestamp=ts)
        self.assertEqual(5, dp._value)
        self.assertEqual(data.Timestamp(5, data.TimeUnit.MICROSECONDS),
                         dp._timestamp)
        self.assertEqual("DataPoint{timestamp: 5, value: 5}", str(dp))

        dp = data.DataPoint(5, timestamp=1443664367594000)
        self.assertEqual(5, dp._value)
        self.assertEqual(
            data.Timestamp(1443664367594000, data.TimeUnit.MILLISECONDS),
            dp._timestamp)

    def test_impliedConstructor(self):
        dp = data.DataPoint(50)
        self.assertEqual(50, dp._value)
        self.assertTrue(dp._timestamp is not None)

    def test_constructorError(self):
        try:
            dp = data.DataPoint(5, timestamp="now")
            self.assertTrue(False)
        except ValueError as e:
            self.assertEqual("invalid type for timestamp: {}".format(
                type("now")), str(e))

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
        self.assertEqual(10000, ret["time"])
        self.assertEqual(5, ret["value"])


class TestDataBatch(unittest.TestCase):

    def test_constructor(self):
        fields = ["a", "boo", "cola"]
        db = data.DataBatch(fields)
        self.assertEqual(3, len(db.fields()))
        for i in range(0, len(fields)):
            self.assertEqual(fields[i], db.fields()[i])
        # check defensive constructor
        fields.append("done")
        self.assertEqual(3, len(db.fields()))
        # check defensive getter
        db.fields().append("done")
        self.assertEqual(3, len(db.fields()))

    def test_constructorBad(self):
        def verify(fields):
            try:
                _ = data.DataBatch(fields)
                self.assertTrue(False)
            except ValueError:
                pass

        cases = [None, []]
        for c in cases:
            verify(c)

    def test_add(self):
        fields = ["a", "b", "c"]
        db = data.DataBatch(fields)
        self.assertEqual(0, len(db.rows()))
        self.assertEqual(0, len(db))
        db.add(0, {"a": 1, "b": 2, "c": 3})
        self.assertEqual(1, len(db.rows()))
        self.assertEqual(3, len(db))
        r1 = db.rows()[0]
        self.assertEqual(0, r1["time"])
        self.assertEqual(1, r1["a"])
        self.assertEqual(2, r1["b"])
        self.assertEqual(3, r1["c"])

        db.add(1, {"a": 4, "c": 6})
        self.assertEqual(2, len(db.rows()))
        self.assertEqual(6, len(db))
        r2 = db.rows()[1]
        self.assertEqual(1000, r2["time"])
        self.assertEqual(4, r2["a"])
        self.assertEqual(None, r2["b"])
        self.assertEqual(6, r2["c"])

    def test_addBad(self):
        fields = ["a", "b", "c"]
        db = data.DataBatch(fields)
        def verify(time, data):
            try:
                db.add(time, data)
                self.assertTrue(False)
            except ValueError:
                pass

        cases = [
            ("0", {"a": 1}),
            (0, None),
            (0, {}),
            (0, {"a": 1, "d": 0})
        ]

        for (t, d) in cases:
            verify(t, d)


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
