"""Data types related to making data points and series."""
# pylint: disable=too-few-public-methods
from time import time
from enum import Enum

# For compatibility with both Python 2 and 3.
# pylint: disable=redefined-builtin,invalid-name
try:
    xrange
except NameError as e:
    long = int
    xrange = range
# pylint: enable=redefined-builtin,invalid-name


class TimeUnit(Enum):
    """Enum of different time units."""
    MILLISECONDS = "msec"
    MICROSECONDS = "usec"
    SECONDS = "sec"

class Timestamp(object):
    """Represents a timestamp, using a value and TimeUnit."""

    # TODO change type to unit
    def __init__(self, value, type=TimeUnit.MILLISECONDS):
        """Constructor of a Timestamp.

        Params:
            value - Numeric value of the timestamp. Must be an integer.
                    Precision is supported by using a different TimeUnit,
                    i.e., 5.5 seconds should be created as 5500 milliseconds
                    or 5500000 microseconds.
            type - TimeUnit to use for the given value
        """
        if value is None or not isinstance(value, (int, long)):
            raise ValueError("timestamp value must be an int")
        self._value = value
        self._type = type

    def __eq__(self, other):
        if other is None or not isinstance(other, Timestamp):
            return False

        return self.asMicroseconds() == other.asMicroseconds()

    def asMicroseconds(self):
        """This timestamp value represented in microseconds.

        Returns:
            Timestamp converted to an integral number of microseconds.
            For timestamps with TimeUnit.MICROSECONDS, this is just the initial
            value; for TimeUnit.MILLISECONDS, value * 1000; and for
            TimeUnit.SECONDS, value * 1000000.
        """
        if self._type == TimeUnit.MICROSECONDS:
            return self._value
        elif self._type == TimeUnit.MILLISECONDS:
            return int(self._value * 1000)
        elif self._type == TimeUnit.SECONDS:
            return int(self._value * 1000000)
        else:
            raise ValueError("unknown type")


class DataPoint(object):
    """Represents a time-series datapoint, using a timestamp and value."""

    def __init__(self, value, timestamp=None):
        """Constructor of a DataPoint.

        Takes in a value, which must be a number type, and optionally a
        timestamp. If a timestamp is not supplied, the current time in
        milliseconds is used.

        Raises:
            ValueError - If value is not a number (int/float) or timestamp is not an
                         int.
        """
        if not isinstance(value, (int, long, float)):
            raise ValueError("'value' must be a number.")
        if timestamp is None:
            self._timestamp = Timestamp(int(time() * 1000),
                                        TimeUnit.MILLISECONDS)
        elif isinstance(timestamp, (int, long)):
            self._timestamp = Timestamp(timestamp, TimeUnit.MILLISECONDS)
        elif isinstance(timestamp, Timestamp):
            self._timestamp = timestamp
        else:
            raise ValueError(
                "invalid type for timestamp: {}".format(type(timestamp)))

        self._value = value

    def __str__(self):
        """Prints out: DataPoint{timestamp: <timestamp>, value: <value>}"""
        return "DataPoint{{timestamp: {}, value: {}}}".format(
            self._timestamp.asMicroseconds(), self._value)

    # pylint:disable=protected-access
    def __eq__(self, other):
        if other is None or not isinstance(other, DataPoint):
            return False
        return (self._value == other._value) and (
            self._timestamp == other._timestamp)
    # pylint:enable=protected-access

    def __hash__(self):
        return self._timestamp.asMicroseconds() + self._value

    def toDict(self):
        """Converts to a dictionary that is usable for the imports API.

        Returns:
            Dictionary with keys 'time' and 'value'.
        """
        return {
            "time": self._timestamp.asMicroseconds(),
            "value": self._value
        }

class DataSeries(object):
    """A collection of DataPoints for a given named series."""

    def __init__(self, name, points):
        """Constructor for DataSeries with a name and its points.

        Params:
            name - Name of the data series
            points - DataPoints in the series

        Throws:
            ValueError - If `name` is None
        """
        if name is None:
            raise ValueError("Name cannot be None")
        self._name = name
        self._points = list(points) if points is not None else []

    def __len__(self):
        """Returns the number of points in the series"""
        return len(self._points)

    def __str__(self):
        """Prints out: DataSeries{name: <name>, len: <size of points>}"""
        return "DataSeries{{name: {}, len: {}}}".format(self._name, len(self))

    def getName(self):
        """Return name of the series."""
        return self._name

    def getPoints(self):
        """Return the `DataPoint`s in the series."""
        return self._points

def makeUniformDataSeries(seriesName, startTime, endTime, values):
    """Creates a DataSeries from a list of values at uniform time intervals.

    Given a `startTime` and `endTime`, this function creates a DataSeries where
    each DataPoint is separated by a uniform time interval, with the first point
    at `startTime` and the last one at `endTime`. For example, if
    `startTime` is 0 and `endTime is 100, and there are 5 values, the resulting
    DataPoints would be at times 0, 25, 50, 75, 100.

    Params:
        seriesName - Name of the resulting DataSeries
        startTime - Time in milliseconds when the series should start
        endTime - Time in milliseconds when the series should end
        values - Numerical values to be made into DataPoints.

    Returns:
        A uniformly distributed DataSeries with DataPoints corresponding to
        `values`. None if the parameters are invalid, i.e., None or
        endTime <= startTime.
    """
    if (seriesName is None) or (startTime is None) or (endTime is None):
        return None
    elif not isinstance(startTime, (int, long)) or not isinstance(endTime, (int, long)):
        return None  # TODO: should raise ValueError?
    elif endTime <= startTime:
        return None  # TODO: should raise ValueError?
    elif (values is None) or len(values) == 0:
        return DataSeries(seriesName, [])

    valLen = len(values)
    if valLen == 1:
        pt = DataPoint(values[0], startTime)
        return DataSeries(seriesName, [pt])
    elif valLen == 2:
        pt1 = DataPoint(values[0], startTime)
        pt2 = DataPoint(values[1], endTime)
        return DataSeries(seriesName, [pt1, pt2])

    interval = (endTime - startTime) / (valLen - 1)
    pts = []

    for i in xrange(0, valLen - 1):
        t = int(startTime + (i * interval))
        d = DataPoint(values[i], timestamp=t)
        pts.append(d)
    pts.append(DataPoint(values[valLen - 1], timestamp=endTime))

    return DataSeries(seriesName, pts)
