from .endpoints import devices
from .endpoints import exports
from .endpoints import imports
from .resources import data
from .resources import device
from .resources import query

DataPoint = data.DataPoint
DataSeries = data.DataSeries
Query = query.Query

class Iobeam(object):

    def __init__(self, path, projectId, projectToken, deviceId=None):
        self._path = path
        self.projectId = projectId
        self.projectToken = projectToken
        self._dataset = dict()
        if deviceId is not None:
            self._activeDevice = device.Device(projectId, deviceId, None)
        else:
            self._activeDevice = None

        # Setup services
        self._deviceService = devices.DeviceService(token=projectToken)
        self._importService = imports.ImportService(token=projectToken)

    def registerDevice(self, deviceId=None, deviceName=None):
        self._activeDevice = self._deviceService.registerDevice(self.projectId,
            deviceId=deviceId, deviceName=deviceName)

        return self

    '''
    Tells whether this client has a registered device.

    Returns:
        True if there is a device ID associated with this client
    '''
    def isRegistered(self):
        return self._activeDevice is not None


    def addDataPoint(self, seriesName, datapoint):
        if (seriesName is None) or (datapoint is None):
            return
        elif not isinstance(datapoint, data.DataPoint):
            return

        if seriesName not in self._dataset:
            self._dataset[seriesName] = set()
        self._dataset[seriesName].add(datapoint)

    def addDataSeries(self, dataseries):
        if dataseries is None:
            return
        elif not isinstance(dataseries, data.DataSeries):
            return
        elif len(dataseries) == 0:
            return

        key = dataseries.getName()
        if key not in self._dataset:
            self._dataset[key] = set()

        for p in dataseries.getPoints():
            self._dataset[key].add(p)

    def clearSeries(self, seriesName):
        self._dataset.pop(seriesName, None)

    def send(self):
        pid = self.projectId
        did = self._activeDevice.deviceId
        dataset = self._dataset
        return self._importService.importData(pid, did, dataset)

    '''
    Performs a query on the iobeam backend.

    The Query specifies the project, device, and series to look up, as well
    as any parameters to use.

    Params:
        token - A token with read access for the given project.
        query - Specifies a data query to perform.

    Returns:
        A dictionary representing the results of the query.
    '''
    @staticmethod
    def query(token, query):
        if token is None:
            raise ValueError("token cannot be None")
        elif query is None:
            raise ValueError("query cannot be None")
        elif not isinstance(query, Query):
            raise ValueError("query must be a iobeam.resources.query.Query")

        service = exports.ExportService(token)
        return service.getData(query)
