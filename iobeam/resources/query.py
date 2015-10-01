"""Data types related to doing queries."""
from iobeam.utils import utils
from iobeam.resources import data

# alias query.TimeUnit to data.TimeUnit
TimeUnit = data.TimeUnit

class Query(object):
    """Represents a data query."""

    @staticmethod
    def _validIntOrRaise(val, msg):
        """Check if value is an int type

        Params:
            val - Value to be checked
            msg - ValueError msg if it is not an int

        Returns:
            True if `val` is int, False if is None.

        Raises:
            ValueError - If val is a non-int.
        """
        if val is None:
            return False
        elif not isinstance(val, int):
            raise ValueError(msg)
        else:
            return True

    @staticmethod
    def _validPositiveIntOrRaise(val, msg):
        """Check if value is an int and > 0.

        Params:
            val - Value to be checked
            msg - ValueError msg if it is not an int

        Returns:
            True if `val` is int and > 0, False if it is None.

        Raises:
            ValueError - If val is a non-int
        """
        if not Query._validIntOrRaise(val, msg):
            return False
        elif val > 0:
            return True
        else:
            raise ValueError(msg)

    def __init__(self, projectId, deviceId=None, seriesName=None,
                 timeUnit=TimeUnit.MILLISECONDS):
        """Construct a new query object."""
        utils.checkValidProjectId(projectId)
        if timeUnit is None:
            timeUnit = TimeUnit.MILLISECONDS
        if not isinstance(timeUnit, TimeUnit):
            raise ValueError("timeUnit must be a query.TimeUnit")

        self._pid = projectId
        self._did = deviceId
        self._series = seriesName
        self._params = {}
        self._timeUnit = timeUnit
        if timeUnit != TimeUnit.MILLISECONDS:
            self._params["timefmt"] = str(timeUnit.value)

    def getUrl(self):
        """Gets the resource locator portion of the exports API call

        Returns:
            String of format <projectId>/<deviceId or 'all'>/<seriesName or 'all'>
        """
        did = self._did or "all"
        series = self._series or "all"
        return "{}/{}/{}".format(self._pid, did, series)

    def getParams(self):
        """Return parameter dictionary for this query."""
        return self._params

    def limit(self, limit):
        """Sets limit of this query, i.e., the max # of results per series."""
        msg = "limit must be a positive int"
        if Query._validPositiveIntOrRaise(limit, msg):
            self._params["limit"] = limit
        return self

    def fromTime(self, time):
        """Sets the from time limit for results."""
        msg = "time must be an int ({} from epoch)".format(self._timeUnit.value)
        if Query._validIntOrRaise(time, msg):
            self._params["from"] = time
        return self

    def toTime(self, time):
        """Sets the to time limit for results."""
        msg = "time must be an int ({} from epoch)".format(self._timeUnit.value)
        if Query._validIntOrRaise(time, msg):
            self._params["to"] = time
        return self

    def inTimeRange(self, start, end):
        """Sets the time limits for results.

        Params:
            start - Beginning of time range to get results from
            end - End of time range to get results from
        """
        if start is not None and end is not None:
            self.fromTime(start).toTime(end)
            if end < start:
                self._params.pop("from", None)
                self._params.pop("to", None)
                raise ValueError("end cannot be less than start")
        return self

    def lessThan(self, value):
        """Sets the max value for values in the results."""
        msg = "value must be an int"
        if Query._validIntOrRaise(value, msg):
            self._params["less_than"] = value
        return self

    def greaterThan(self, value):
        """Sets the min value for values in the results."""
        msg = "value must be an int"
        if Query._validIntOrRaise(value, msg):
            self._params["greater_than"] = value
        return self

    # pylint: disable=redefined-builtin
    def inValueRange(self, min, max):
        """Sets the value range for results.

        Params:
            min - Minimum value to have in results
            max - Maximum value to have in results
        """
        if min is not None and max is not None:
            self.lessThan(max).greaterThan(min)
            if max < min:
                self._params.pop("less_than", None)
                self._params.pop("greater_than", None)
                raise ValueError("max value cannot be larger than min value")
        return self
    # pylint: enable=redefined-builtin

    def equals(self, value):
        """Sets the value that all results must equal."""
        msg = "value must be an int"
        if Query._validIntOrRaise(value, msg):
            self._params["equals"] = value
        return self
