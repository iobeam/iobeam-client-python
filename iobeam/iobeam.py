from .endpoints import devices
from .endpoints import imports
from .resources import device
from .resources import data

DataPoint = data.DataPoint
DataSeries = data.DataSeries

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
        self._dataset[seriesName].add(d)

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
