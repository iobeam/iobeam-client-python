"""Data types related to making data points and series."""
# pylint: disable=too-few-public-methods
from time import time
from enum import Enum
from iobeam.utils import utils

# For compatibility with both Python 2 and 3.
# pylint: disable=redefined-builtin,invalid-name
if utils.IS_PY3:
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

    def __init__(self, value, unit=TimeUnit.MILLISECONDS):
        """Constructor of a Timestamp.

        Params:
            value - Numeric value of the timestamp. Must be an integer.
                    Precision is supported by using a different TimeUnit,
                    i.e., 5.5 seconds should be created as 5500 milliseconds
                    or 5500000 microseconds.
            unit - TimeUnit to use for the given value
        """
        if value is None or not isinstance(value, (int, long)):
            raise ValueError("timestamp value must be an int")
        self._value = value
        self._type = unit

    def __eq__(self, other):
        if other is None or not isinstance(other, Timestamp):
            return False

        return self.asMicroseconds() == other.asMicroseconds()

    def asMilliseconds(self):
        """This timestamp value represented in milliseconds.

        Returns:
            Timestamp coverted to an integral number of milliseconds.
            For timestamps with TimeUnit.MICROSECONDS, this is the value / 1000;
            for TimeUnit.MILLISECONDS this is just the value; and for
            TimeUnit.SECONDS, this is value * 1000.
        """
        if self._type == TimeUnit.MICROSECONDS:
            return int(self._value // 1000)
        elif self._type == TimeUnit.MILLISECONDS:
            return self._value
        elif self._type == TimeUnit.SECONDS:
            return self._value * 1000

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


class DataStore(object):
    """A collection of data streams with rows batched by time."""

    def __init__(self, columns):
        """Construct a new DataStore object with given columns.

        Params:
            fields - Column or series names for data in this batch.

        Raises:
            ValueError - If `columns` is None, empty, or not a list. Also, if
            it contains reserved names: time, time_offset.
        """
        if columns is None or len(columns) == 0:
            raise ValueError("columns cannot be None or empty")
        if not isinstance(columns, list):
            raise ValueError("columns must be a list of strings")
        for c in columns:
            utils.checkValidSeriesName(c)

        self._columns = list(columns)  # defensive copy
        self._rows = []

    def clear(self):
        """Remove all data rows."""
        del self._rows[:]

    def add(self, timestamp, dataDict):
        """Add row of data at a given timestamp.

        Params:
            timestamp - Timestamp for all points to share
            dataDict - Data values keyed by which series they belong to.

        Raises:
            ValueError - For multiple cases:
                (a) timestamp is neither an int or a Timestamp type
                (b) dataDict is empty or None
                (b) dataDict contains keys not in this store
        """
        ts = None
        # validate timestamp
        if isinstance(timestamp, (int, long)):
            ts = Timestamp(timestamp)
        elif isinstance(timestamp, Timestamp):
            ts = timestamp
        else:
            raise ValueError("timestamp must be an int or Timestamp type")

        # validate data
        if dataDict is None or len(dataDict) == 0:
            raise ValueError("dataDict cannot be None or empty")
        for k in dataDict:
            if k not in self._columns:
                raise ValueError("dataDict can only contain keys in this store's columns")

        # everything ok, make row
        row = {"time": ts.asMicroseconds()}
        for f in self._columns:
            if f in dataDict:
                row[f] = dataDict[f]
            else:
                row[f] = None
        self._rows.append(row)

    def columns(self):
        """Return a copy of the columns in this store."""
        return list(self._columns)

    def rows(self):
        """Return a copy of the rows in this store."""
        ret = []
        for r in self._rows:
            ret.append(r.copy())
        return ret

    def hasSameColumns(self, cols):
        """Check if this datastore has exactly a list of columns."""
        if cols is None or not isinstance(cols, list):
            return False
        elif len(cols) != len(self._columns):
            return False
        else:
            return set(cols) == set(self._columns)


    def split(self, chunkSize):
        """Split a store into multiple batches with `chunkSize` rows.

        Params:
            chunkSize - Max number of rows to include in a split

        Returns:
            List of DataStores containing at most chunkSize rows from this store.
        """
        ret = []
        for i in range(0, len(self._rows), chunkSize):
            temp = DataStore(self._columns)
            temp._rows = self._rows[i:i+chunkSize]
            ret.append(temp)

        return ret

    def __len__(self):
        """Return the size of this store in terms of data points."""
        return len(self._rows) * len(self._columns)


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
        timestamp = int(startTime + (i * interval))
        d = DataPoint(values[i], timestamp=timestamp)
        pts.append(d)
    pts.append(DataPoint(values[valLen - 1], timestamp=endTime))

    return DataSeries(seriesName, pts)
