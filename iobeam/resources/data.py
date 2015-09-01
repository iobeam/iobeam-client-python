from time import time


'''
Represents a time-series datapoint, using a timestamp and value.
'''
class DataPoint(object):

    '''
    Constructor of a DataPoint.

    Takes in a value, which must be a number type, and optionally a
    timestamp. If a timestamp is not supplied, the current time in
    milliseconds is used.

    Raises:
        ValueError - If value is not a number (int/float) or timestamp is not an
                     int.
    '''
    def __init__(self, value, timestamp=None):
        if not (isinstance(value, int) or isinstance(value, float)):
            raise ValueError("'value' must be a number.")
        if timestamp is None:
            self._timestamp = int(time() * 1000)
        elif not isinstance(timestamp, int):
            raise ValueError("timestamp must be an int (milliseconds)")
        else:
            self._timestamp = int(timestamp)
        self._value = value

    '''
    Prints out: DataPoint{timestamp: <timestamp>, value: <value>}
    '''
    def __str__(self):
        return "DataPoint{{timestamp: {}, value: {}}}".format(
            self._timestamp, self._value)

    def __eq__(self, other):
        if other is None or not isinstance(other, DataPoint):
            return False
        return (self._value == other._value) and (
            self._timestamp == other._timestamp)

    '''
    Converts to a dictionary that is usable for the imports API.

    Returns:
        Dictionary with keys 'time' and 'value'.
    '''
    def toDict(self):
        return {"time": self._timestamp, "value": self._value}

'''
A collection of DataPoints for a given named series.
'''
class DataSeries(object):

    '''
    Constructor for DataSeries with a name and its points.

    Params:
        name - Name of the data series
        points - DataPoints in the series

    Throws:
        ValueError - If `name` is None
    '''
    def __init__(self, name, points):
        if name is None:
            raise ValueError("Name cannot be None")
        self._name = name
        self._points = list(points) if points is not None else []

    '''
    Returns the number of points in the series
    '''
    def __len__(self):
        return len(self._points)

    '''
    Prints out: DataSeries{name: <name>, len: <size of points>}
    '''
    def __str__(self):
        return "DataSeries{{name: {}, len: {}}}".format(self._name, len(self))

    def getName(self):
        return self._name

    def getPoints(self):
        return self._points

'''
Creates a DataSeries from a list of values at uniform time intervals.

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
'''
def makeUniformDataSeries(seriesName, startTime, endTime, values):
    if (seriesName is None) or (startTime is None) or (endTime is None):
        return None
    elif endTime <= startTime:
        return None
    elif (values is None) or len(values) == 0:
        return DataSeries(seriesName, [])

    valLen = len(values)
    if valLen == 1:
        pt = DataPoint(values[0], startTime)
        return DataSeries(seriesName, [pt])
    elif valLen == 2:
        pt1 = DataPoint(values[0], startTime)
        pt2 = DataPoint(values[1], endTime)
        return DataSeries(seriesName, [pt1, p2])

    interval = (endTime - startTime) / (valLen - 1)
    pts = []
    # For compatibility with both Python 2 and 3.
    try:
        xrange
    except NameError:
        xrange = range  # Python3
    for i in xrange(0, valLen):
        d = DataPoint(values[i], startTime + (i * interval))
        pts.append(d)

    return DataSeries(seriesName, pts)
