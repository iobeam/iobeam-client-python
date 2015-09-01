from iobeam.utils import utils

'''
Represents a data query.
'''
class Query(object):

    def __init__(self, projectId, deviceId=None, seriesName=None):
        utils.checkValidProjectId(projectId)

        self._pid = projectId
        self._did = deviceId
        self._series = seriesName
        self._params = {}

    '''
    Gets the resource locator portion of the exports API call

    Returns:
        String of format <projectId>/<deviceId or 'all'>/<seriesName or 'all'>
    '''
    def getUrl(self):
        did = self._did if self._did is not None else "all"
        series = self._series if self._series is not None else "all"
        return "{}/{}/{}".format(self._pid, did, series)

    def getParams(self):
        return self._params

    '''
    Sets the limit of this query, i.e., the max number of results series.
    '''
    def limit(self, limit):
        if limit is None:
            return self
        if not isinstance(limit, int) or not limit > 0:
            raise ValueError("limit must be a positive int")

        self._params["limit"] = limit
        return self

    '''
    Sets the from time limit for results.
    '''
    def fromTime(self, time):
        if time is None:
            return self
        elif not isinstance(time, int):
            raise ValueError("time must be an int (milliseconds from epoch)")

        self._params["from"] = time
        return self

    '''
    Sets the to time limit for results.
    '''
    def toTime(self, time):
        if time is None:
            return self
        elif not isinstance(time, int):
            raise ValueError("time must be an int (milliseconds from epoch)")

        self._params["to"] = time
        return self

    '''
    Sets the max value for values in the results.
    '''
    def lessThan(self, value):
        if value is None:
            return self
        elif not isinstance(value, int):
            raise ValueError("value must be an int")

        self._params["less_than"] = value
        return self

    '''
    Sets the min value for values in the results.
    '''
    def greaterThan(self, value):
        if value is None:
            return self
        elif not isinstance(value, int):
            raise ValueError("value must be an int")

        self._params["greater_than"] = value
        return self

    '''
    Sets the value that all results must equal.
    '''
    def equals(self, value):
        if value is None:
            return self
        elif not isinstance(value, int):
            raise ValueError("value must be an int")

        self._params["equals"] = value
        return self
