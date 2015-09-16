from .endpoints import devices
from .endpoints import exports
from .endpoints import imports
from .http import request
from .resources import data
from .resources import device
from .resources import query
from .utils import utils
import os.path

'''
Aliases for resource types for convenience outside the package.
'''
DataPoint = data.DataPoint
DataSeries = data.DataSeries
Timestamp = data.Timestamp
TimeUnit = data.TimeUnit
QueryReq = query.Query

_DEVICE_ID_FILE = "iobeam_device_id"

class ClientBuilder(object):

    def __init__(self, projectId, projectToken):
        utils.checkValidProjectId(projectId)
        utils.checkValidProjectToken(projectToken)

        self._projectId = projectId
        self._projectToken = projectToken
        self._diskPath = None
        self._deviceId = None
        self._regArgs = None
        self._backend = None

    def saveToDisk(self, path="."):
        self._diskPath = path
        return self

    def setDeviceId(self, deviceId):
        utils.checkValidDeviceId(deviceId)
        self._deviceId = deviceId
        return self

    def registerDevice(self, deviceId=None, deviceName=None):
        self._regArgs = (deviceId, deviceName)
        return self

    def setBackend(self, baseUrl):
        self._backend = request.Requester(baseUrl=baseUrl)
        return self

    def build(self):
        client = _Client(self._diskPath, self._projectId, self._projectToken,
                         self._backend, deviceId=self._deviceId)
        if (self._regArgs is not None):
            did, dname = self._regArgs
            client.registerDevice(deviceId=did, deviceName=dname)

        return client


class _Client(object):

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
        backend - Base url of the backend to use; if None, requests go to
                  https://api.iobeam.com/v1/
        deviceId - Device id if previously registered
    '''
    def __init__(self, path, projectId, projectToken, backend, deviceId=None):
        utils.checkValidProjectId(projectId)
        utils.checkValidProjectToken(projectToken)

        self.projectId = projectId
        self.projectToken = projectToken
        self._path = path
        self._dataset = {}

        self._activeDevice = None
        if deviceId is not None:
            self._setActiveDevice(device.Device(projectId, deviceId))
        elif self._path is not None:
            p = os.path.join(self._path, _DEVICE_ID_FILE)
            if os.path.isfile(p):
                with open(p, "r") as f:
                    did = f.read()
                    if len(did) > 0:
                        self._activeDevice = device.Device(projectId, did)


        # Setup services
        requester = backend
        self._deviceService = devices.DeviceService(projectToken,
                                                    requester=backend)
        self._importService = imports.ImportService(projectToken,
                                                    requester=backend)

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
        if self._activeDevice is not None and (deviceId is None or
            self._activeDevice.deviceId == deviceId):
            return self

        d = self._deviceService.registerDevice(self.projectId,
            deviceId=deviceId, deviceName=deviceName)
        self._setActiveDevice(d)

        return self

    def setDeviceId(self, deviceId):
        d = device.Device(self.projectId, deviceId)
        self._setActiveDevice(d)

    def getDeviceId(self):
        if self._activeDevice is None:
            return None
        else:
            return self._activeDevice.deviceId

    def _setActiveDevice(self, device):
        self._activeDevice = device
        if self._path is not None:
            p = os.path.join(self._path, _DEVICE_ID_FILE)
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
        if seriesName is None or not isinstance(seriesName, str):
            return
        elif len(seriesName) == 0:
            return
        elif datapoint is None or not isinstance(datapoint, data.DataPoint):
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
        if dataseries is None or not isinstance(dataseries, data.DataSeries):
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

    Raises:
        Will throw an Exception if sending the data fails.
    '''
    def send(self):
        pid = self.projectId
        did = self._activeDevice.deviceId
        dataset = self._dataset
        success, extra = self._importService.importData(pid, did, dataset)
        if not success:
            raise Exception("Send failed, server sent: {}".format(extra))

    '''
    Performs a query on the iobeam backend.

    The Query specifies the project, device, and series to look up, as well
    as any parameters to use.

    Params:
        token - A token with read access for the given project.
        query - Specifies a data query to perform.

    Returns:
        A dictionary representing the results of the query.

    Raises:
        ValueError - If `token` or `query` is None, or `query` is the wrong
                     type.
    '''
    @staticmethod
    def query(token, query, backend=None):
        if token is None:
            raise ValueError("token cannot be None")
        elif query is None:
            raise ValueError("query cannot be None")
        elif not isinstance(query, QueryReq):
            raise ValueError("query must be a iobeam.QueryReq")
        requester = None
        if backend is not None:
            requester = request.Requester(baseUrl=backend)

        print(requester)
        service = exports.ExportService(token, requester=requester)
        return service.getData(query)

MakeQuery = _Client.query
