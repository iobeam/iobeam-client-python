from .endpoints import devices
from .endpoints import exports
from .endpoints import imports
from .resources import data
from .resources import device
from .resources import query
import os.path

DataPoint = data.DataPoint
DataSeries = data.DataSeries
Query = query.Query

DEVICE_ID_FILE = "iobeam_device_id"

class Iobeam(object):

    '''
    Constructor for iobeam client object.

    Creates a client instance associated with a project and (potentially) a
    device. If `path` is provided, this device's ID will be stored at
    <path>/iobeam_device_id. This on-disk ID will be used if one is not
    provided as `deviceId`.

    Params:
        path - Path where device ID should be persisted
        projectId - iobeam project ID
        projectToken - iobeam project token with write access for sending data
        deviceName - Device name if previously registered
    '''
    def __init__(self, path, projectId, projectToken, deviceId=None):
        if projectId is None or not isinstance(projectId, int):
            raise ValueError("projectId must be an int")
        if projectToken is None:
            raise ValueError("projectToken cannot be None")

        self.projectId = projectId
        self.projectToken = projectToken
        self._path = path
        self._dataset = {}

        if deviceId is not None:
            self._setActiveDevice(device.Device(projectId, deviceId, None))
        else:
            if self._path is not None:
                p = os.path.join(self._path, DEVICE_ID_FILE)
                with open(p, "r") as f:
                    did = f.read()
                    self._activeDevice = device.Device(projectId, did, None)
            else:
                self._activeDevice = None

        # Setup services
        self._deviceService = devices.DeviceService(token=projectToken)
        self._importService = imports.ImportService(token=projectToken)

    '''
    Registers the device with iobeam.

    If a path was provided when the client was constructed, the device ID
    will be stored on disk.

    Params:
        deviceId - Desired device ID; otherwise randomly generated
        deviceName - Desired device name; otherwise randomly generated

    Returns:
        This client object (allows for chaining)
    '''
    def registerDevice(self, deviceId=None, deviceName=None):
        if self._activeDevice is None:
            return self
        if self._activeDevice.deviceId == deviceId:
            return self

        device = self._deviceService.registerDevice(self.projectId,
            deviceId=deviceId, deviceName=deviceName)
        self._setActiveDevice(device)

        return self

    def _setActiveDevice(self, device):
        self._activeDevice = device
        if self._path is not None:
            p = os.path.join(self._path, DEVICE_ID_FILE)
            with open(p, "w") as f:
                f.write(self._activeDevice.deviceId)

    '''
    Tells whether this client has a registered device.

    Returns:
        True if there is a device ID associated with this client
    '''
    def isRegistered(self):
        return self._activeDevice is not None

    '''
    Adds a single DataPoint to a series in the data store.

    If the series does not currently exist, it will be created.

    Params:
        seriesName - The series to add the datapoint to
        datapoint - DataPoint to be added
    '''
    def addDataPoint(self, seriesName, datapoint):
        if (seriesName is None) or (datapoint is None):
            return
        elif not isinstance(datapoint, data.DataPoint):
            return

        if seriesName not in self._dataset:
            self._dataset[seriesName] = set()
        self._dataset[seriesName].add(datapoint)

    '''
    Adds a DataSeries to the data store.

    If the series exists, all the points will be added.

    Params:
        dataseries - The DataSeries to add to the data store.
    '''
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

    '''
    Removes any points associated with `seriesName`.

    Params:
        seriesName - Name of the data series to be cleared.
    '''
    def clearSeries(self, seriesName):
        self._dataset.pop(seriesName, None)

    '''
    Sends stored data to the iobeam backend.

    Returns:
        Whether the data was successfully sent.
    '''
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
