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
        # None is not a valid project id
        badId = None
        try:
            q = query.Query(badId)
            self.assertTrue(False)
        except ValueError as e:
            self.assertEqual("projectId must be an int", str(e))

        # No non-int project ids
        badId = "50"
        try:
            q = query.Query(badId)
            self.assertTrue(False)
        except ValueError as e:
            self.assertEqual("projectId must be an int", str(e))

        # No negative project ids
        badId = -1
        try:
            q = query.Query(badId)
            self.assertTrue(False)
        except ValueError as e:
            self.assertEqual("projectId must be greater than 0", str(e))

        # 0 is not a valid project id
        badId = 0
        try:
            q = query.Query(badId)
            self.assertTrue(False)
        except ValueError as e:
            self.assertEqual("projectId must be greater than 0", str(e))

    def test_constructorInvalidTimeUnit(self):
        tu = "fake"
        try:
            q = query.Query(_PROJECT_ID, timeUnit=tu)
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

    def test_getUrl(self):
        ALL = "all"
        q = query.Query(_PROJECT_ID)
        self.assertEqual("{}/{}/{}".format(_PROJECT_ID, ALL, ALL), q.getUrl())

        q = query.Query(_PROJECT_ID, deviceId=_DEVICE_ID)
        self.assertEqual("{}/{}/{}".format(_PROJECT_ID, _DEVICE_ID, ALL),
                         q.getUrl())

        q = query.Query(_PROJECT_ID, seriesName=_SERIES)
        self.assertEqual("{}/{}/{}".format(_PROJECT_ID, ALL, _SERIES),
                         q.getUrl())

        q = query.Query(_PROJECT_ID, deviceId=_DEVICE_ID, seriesName=_SERIES)
        self.assertEqual("{}/{}/{}".format(_PROJECT_ID, _DEVICE_ID, _SERIES),
                         q.getUrl())

    # None should be essentially a no-op
    def paramNoneTest(self, q, func):
        ret = func(None)
        self.assertEqual(0, len(q.getParams()))
        self.assertEqual(q, ret)

    def test_limit(self):
        q = query.Query(_PROJECT_ID)

        self.paramNoneTest(q, q.limit)

        ret = q.limit(5)
        self.assertEqual(5, q.getParams()["limit"])
        self.assertEqual(q, ret)

        # Failure case: non-int
        try:
            q.limit("junk")
            self.assertTrue(False)
        except ValueError as e:
            pass

        # Failure cases: non-positive int
        try:
            q.limit(0)
            self.assertTrue(False)
        except ValueError as e:
            pass

        try:
            q.limit(-1)
            self.assertTrue(False)
        except ValueError as e:
            pass

    def test_fromTime(self):
        q = query.Query(_PROJECT_ID)

        self.paramNoneTest(q, q.fromTime)

        ret = q.fromTime(5000)
        self.assertEqual(5000, q.getParams()["from"])
        self.assertEqual(q, ret)

        # Failure case: non-int
        try:
            q.fromTime("junk")
            self.assertTrue(False)
        except ValueError as e:
            pass

    def test_toTime(self):
        q = query.Query(_PROJECT_ID)

        self.paramNoneTest(q, q.toTime)

        ret = q.toTime(15000)
        self.assertEqual(15000, q.getParams()["to"])
        self.assertEqual(q, ret)

        # Failure case: non-int
        try:
            q.toTime("junk")
            self.assertTrue(False)
        except ValueError as e:
            pass

    def test_greaterThan(self):
        q = query.Query(_PROJECT_ID)

        self.paramNoneTest(q, q.greaterThan)

        ret = q.greaterThan(0)
        self.assertEqual(0, q.getParams()["greater_than"])
        self.assertEqual(q, ret)

        # Failure case: non-int
        try:
            q.greaterThan("junk")
            self.assertTrue(False)
        except ValueError as e:
            pass

    def test_lessThan(self):
        q = query.Query(_PROJECT_ID)

        self.paramNoneTest(q, q.lessThan)

        ret = q.lessThan(1000)
        self.assertEqual(1000, q.getParams()["less_than"])
        self.assertEqual(q, ret)

        # Failure case: non-int
        try:
            q.greaterThan("junk")
            self.assertTrue(False)
        except ValueError as e:
            pass

    def test_equals(self):
        q = query.Query(_PROJECT_ID)

        self.paramNoneTest(q, q.equals)

        ret = q.equals(10)
        self.assertEqual(10, q.getParams()["equals"])
        self.assertEqual(q, ret)

        # Failure case: non-int
        try:
            q.greaterThan("junk")
            self.assertTrue(False)
        except ValueError as e:
            pass
