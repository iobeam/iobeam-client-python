import unittest

from iobeam.resources import query

_PROJECT_ID = 1
_DEVICE_ID = "py_test_id"
_SERIES = "temp"


class TestQuery(unittest.TestCase):

    def test_constructorOnlyProject(self):
        q = query.Query(_PROJECT_ID)
        self.assertEqual(_PROJECT_ID, q._pid)
        self.assertTrue(q._did is None)
        self.assertTrue(q._series is None)
        self.assertEqual(0, len(q._params))

    def test_constructorWithTimeUnit(self):
        tu = query.TimeUnit.SECONDS
        q = query.Query(_PROJECT_ID, timeUnit=tu)
        self.assertEqual(_PROJECT_ID, q._pid)
        self.assertTrue(q._did is None)
        self.assertTrue(q._series is None)
        self.assertEqual(1, len(q.getParams()))
        self.assertTrue("timefmt" in q.getParams())
        self.assertEqual(tu.value, q.getParams()["timefmt"])

    def test_invalidProjectId(self):
        def verify(badId, msg):
            try:
                q = query.Query(badId)
                self.assertTrue(False)
            except ValueError as e:
                self.assertEqual(msg, str(e))

        # None is not valid
        verify(None, "projectId must be an int")
        # No non-int project ids
        verify("50", "projectId must be an int")
        # No negative project ids
        verify(-1, "projectId must be greater than 0")
        # 0 is not a valid project id
        verify(0, "projectId must be greater than 0")

    def test_constructorInvalidTimeUnit(self):
        tu = "fake"
        try:
            q = query.Query(_PROJECT_ID, timeUnit=tu)
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

    def test_getUrl(self):
        def shouldFmt(pid, did, series):
            return "{}/{}/{}".format(pid, did, series)

        ALL = "all"
        q = query.Query(_PROJECT_ID)
        self.assertEqual(shouldFmt(_PROJECT_ID, ALL, ALL),
                         q.getUrl())

        q = query.Query(_PROJECT_ID, deviceId=_DEVICE_ID)
        self.assertEqual(shouldFmt(_PROJECT_ID, _DEVICE_ID, ALL),
                         q.getUrl())

        q = query.Query(_PROJECT_ID, seriesName=_SERIES)
        self.assertEqual(shouldFmt(_PROJECT_ID, ALL, _SERIES),
                         q.getUrl())

        q = query.Query(_PROJECT_ID, deviceId=_DEVICE_ID, seriesName=_SERIES)
        self.assertEqual(shouldFmt(_PROJECT_ID, _DEVICE_ID, _SERIES),
                         q.getUrl())

    # None should be essentially a no-op
    def paramNoneTest(self, q, func):
        ret = func(None)
        self.assertEqual(0, len(q.getParams()))
        self.assertEqual(q, ret)

    def _checkInvalid(self, func, value):
        try:
            func(value)
            self.assertTrue(False)
        except ValueError as e:
            pass

    def test_limit(self):
        q = query.Query(_PROJECT_ID)
        self.paramNoneTest(q, q.limit)

        ret = q.limit(5)
        self.assertEqual(5, q.getParams()["limit"])
        self.assertEqual(q, ret)

        # Failure case: non-int
        self._checkInvalid(q.limit, "junk")
        # Failure cases: non-positive int
        self._checkInvalid(q.limit, 0)
        self._checkInvalid(q.limit, -1)

    def test_fromTime(self):
        q = query.Query(_PROJECT_ID)
        self.paramNoneTest(q, q.fromTime)

        ret = q.fromTime(5000)
        self.assertEqual(5000, q.getParams()["from"])
        self.assertEqual(q, ret)

        # Failure case: non-int
        self._checkInvalid(q.fromTime, "junk")

    def test_toTime(self):
        q = query.Query(_PROJECT_ID)
        self.paramNoneTest(q, q.toTime)

        ret = q.toTime(15000)
        self.assertEqual(15000, q.getParams()["to"])
        self.assertEqual(q, ret)

        # Failure case: non-int
        self._checkInvalid(q.toTime, "junk")

    def test_greaterThan(self):
        q = query.Query(_PROJECT_ID)
        self.paramNoneTest(q, q.greaterThan)

        ret = q.greaterThan(0)
        self.assertEqual(0, q.getParams()["greater_than"])
        self.assertEqual(q, ret)

        # Failure case: non-int
        self._checkInvalid(q.greaterThan, "junk")

    def test_lessThan(self):
        q = query.Query(_PROJECT_ID)
        self.paramNoneTest(q, q.lessThan)

        ret = q.lessThan(1000)
        self.assertEqual(1000, q.getParams()["less_than"])
        self.assertEqual(q, ret)

        # Failure case: non-int
        self._checkInvalid(q.lessThan, "junk")

    def test_equals(self):
        q = query.Query(_PROJECT_ID)
        self.paramNoneTest(q, q.equals)

        ret = q.equals(10)
        self.assertEqual(10, q.getParams()["equals"])
        self.assertEqual(q, ret)

        # Failure case: non-int
        self._checkInvalid(q.equals, "junk")
