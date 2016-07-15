"""The iobeam client and related types/methods."""
from .endpoints import devices
from .endpoints import exports
from .endpoints import imports
from .endpoints import tokens
from .http import request
from .resources import data
from .resources import device
from .resources import query
from .utils import utils

import os.path

#  Aliases for resource types for convenience outside the package.
DataStore = data.DataStore
DataPoint = data.DataPoint
DataSeries = data.DataSeries
Timestamp = data.Timestamp
TimeUnit = data.TimeUnit
QueryReq = query.Query

_DEVICE_ID_FILE = "iobeam_device_id"

class ClientBuilder(object):
    """Used to build an iobeam client object."""

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
        """Client object should save deviceId to disk (chainble).

        Params:
            path - File system path to save deviceId

        Returns:
            This Builder object, for chaining.
        """
        self._diskPath = path
        return self

    def setDeviceId(self, deviceId):
        """Client object should set deviceId (chainable)."""
        utils.checkValidDeviceId(deviceId)
        self._deviceId = deviceId
        return self

    def _setRegArgs(self, deviceId, deviceName, setOnDupe):
        """Set registration args.

        Params:
            deviceId - Desired device id; if None, server generated.
            deviceName - Desired device name; if None, server generated.
            setOnDupe - Whether "already registered" errors should be ignored
        """
        if deviceId is not None or setOnDupe:
            utils.checkValidDeviceId(deviceId)
        self._regArgs = (deviceId, deviceName, setOnDupe)

    def registerOrSetId(self, deviceId, deviceName=None):
        """Client object should register itself, or set the id if it exists.

        Params:
            deviceId - Desired device id to register or set if it exists
            deviceName - Desired device name (optional)

        Returns:
            This Builder object, for chaining.
        """
        self._setRegArgs(deviceId, deviceName, True)
        return self


    def registerDevice(self, deviceId=None, deviceName=None):
        """Client object should register itself (chainable).

        Params:
            deviceId - Desired device id (optional)
            deviceName - Desired deviceName (optional)

        Returns:
            This Builder object, for chaining.
        """
        self._setRegArgs(deviceId, deviceName, False)
        return self

    def setBackend(self, baseUrl):
        """Client object should use this url as the backend (chainable).

        Params:
            baseUrl - Base part of the URL to use for making API requests.

        Returns:
            This Builder object, for chaining.
        """
        self._backend = request.getRequester(url=baseUrl)
        return self

    def build(self):
        """Actually construct the client object."""
        client = _Client(self._diskPath, self._projectId, self._projectToken,
                         self._backend, deviceId=self._deviceId)
        if self._regArgs is not None:
            did, dname, setOnDupe = self._regArgs
            client.registerDevice(deviceId=did, deviceName=dname,
                                  setOnDupe=setOnDupe)

        return client


class _Client(object):
    """Client object used to communicate with iobeam."""

    # pylint: disable=too-many-arguments
    def __init__(self, path, projectId, projectToken, backend, deviceId=None):
        """Constructor for iobeam client object.

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
        """
        utils.checkValidProjectId(projectId)
        utils.checkValidProjectToken(projectToken)

        self.projectId = projectId
        self.projectToken = projectToken
        self._path = path
        self._dataset = {}
        self._batches = []

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
        self._deviceService = devices.DeviceService(projectToken,
                                                    requester=backend)
        self._importService = imports.ImportService(projectToken,
                                                    requester=backend)
        self._tokenService = tokens.TokenService(requester=backend)

        self._checkToken()
    # pylint: enable=too-many-arguments

    def _checkToken(self):
        """Check if token is expired, and refresh if necessary."""
        if utils.isExpiredToken(self.projectToken):
            newToken = self._refreshToken()
            if newToken is not None:
                self.projectToken = newToken

    def _refreshToken(self):
        """Refresh expired project token."""
        return self._tokenService.refreshToken(self.projectToken)

    def registerDevice(self, deviceId=None, deviceName=None, setOnDupe=False):
        """Registers the device with iobeam.

        If a path was provided when the client was constructed, the device ID
        will be stored on disk.

        Params:
            deviceId - Desired device ID; otherwise randomly generated
            deviceName - Desired device name; otherwise randomly generated
            setOnDupe - If duplicate device id, use the id instead of raising an
                        error; default False (will throw an error if duplicate).

        Returns:
            This client object (allows for chaining)

        Raises:
            devices.DuplicateIdError - If id is a dupliecate and `setOnDupe` is
                                       False.
        """
        activeSet = self._activeDevice is not None
        didIsNone = deviceId is None
        if activeSet and (didIsNone or self._activeDevice.deviceId == deviceId):
            return self

        if deviceId is not None:
            utils.checkValidDeviceId(deviceId)

        self._checkToken()
        try:
            d = self._deviceService.registerDevice(self.projectId,
                                                   deviceId=deviceId,
                                                   deviceName=deviceName)
        except devices.DuplicateIdError:
            if setOnDupe:
                d = device.Device(self.projectId, deviceId,
                                  deviceName=deviceName)
            else:
                raise
        self._setActiveDevice(d)

        return self

    def setDeviceId(self, deviceId):
        """Set client's active device id."""
        d = device.Device(self.projectId, deviceId)
        self._setActiveDevice(d)

    def getDeviceId(self):
        """Get client's active device id."""
        if self._activeDevice is None:
            return None
        else:
            return self._activeDevice.deviceId

    def _setActiveDevice(self, dev):
        """Internally sets the client's device id, including saving to disk."""
        self._activeDevice = dev
        if self._path is not None:
            p = os.path.join(self._path, _DEVICE_ID_FILE)
            with open(p, "w") as f:
                f.write(self._activeDevice.deviceId)

    def isRegistered(self):
        """Tells whether this client has a registered device.

        Returns:
            True if there is a device ID associated with this client
        """
        return self._activeDevice is not None

    def addDataPoint(self, seriesName, datapoint):
        """Adds a single DataPoint to a series in the data store.

        If the series does not currently exist, it will be created.

        Params:
            seriesName - The series to add the datapoint to
            datapoint - DataPoint to be added

        Raises:
            ValueError - If series name is None, not a string, or length 0.
        """
        if seriesName is None or not isinstance(seriesName, str):
            raise ValueError("seriesName cannot be None or a non-string")
        elif len(seriesName) == 0:
            raise ValueError("seriesName cannot be a 0-length string")
        elif datapoint is None or not isinstance(datapoint, data.DataPoint):
            utils.getLogger().warning("tried to add an invalid or None datapoint")
            return

        if seriesName not in self._dataset:
            self._dataset[seriesName] = set()
        self._dataset[seriesName].add(datapoint)

    def addDataSeries(self, dataseries):
        """Adds a DataSeries to the data store.

        If the series exists, all the points will be added.

        Params:
            dataseries - The DataSeries to add to the data store.

        Raises:
            ValueError - If dataseries is None or not a DataSeries object
        """
        if dataseries is None or not isinstance(dataseries, data.DataSeries):
            raise ValueError("dataseries was None or not a DataSeries")
        elif len(dataseries) == 0:
            utils.getLogger().warning("tried to add empty dataseries")
            return

        key = dataseries.getName()
        if key not in self._dataset:
            self._dataset[key] = set()

        for p in dataseries.getPoints():
            self._dataset[key].add(p)

    def clearSeries(self, seriesName):
        """Removes any points associated with `seriesName`."""
        self._dataset.pop(seriesName, None)

    def createDataStore(self, columns):
        """Create a DataStore that is tracked by this client.

        Params:
            columns - List of stream names for the DataStore

        Returns:
            DataStore object with those columns and being tracked
            by this client for sending.
        """
        for store in self._batches:
            if store.hasSameColumns(columns):
                return store

        ds = data.DataStore(columns)
        self._batches.append(ds)

        return ds

    def addDataStore(self, store):
        """Add a DataStore to this client.

        Params:
            store - The DataStore to add to the data store.
        """
        if store is None:
            utils.getLogger().warning("adding store was None")
            return
        elif not isinstance(store, data.DataStore):
            raise ValueError("store must be a DataStore")

        self._batches.append(store)

    def _convertDataSetToBatches(self):
        """Convert legacy format into new table format."""
        dataset = self._dataset
        batches = []
        for name in dataset:
            batch = data.DataStore([name])
            for point in dataset[name]:
                asDict = point.toDict()
                ts = data.Timestamp(asDict["time"], unit=TimeUnit.MICROSECONDS)
                row = {}
                row[name] = asDict["value"]
                batch.add(ts, row)
            batches.append(batch)
        self._dataset = {}
        return batches

    def send(self):
        """Sends stored data to the iobeam backend.

        Raises:
            Exception - if sending the data fails.
        """
        self._checkToken()
        pid = self.projectId
        did = self._activeDevice.deviceId
        tempBatches = self._convertDataSetToBatches()

        for b in list(self._batches):
            success, extra = self._importService.importBatch(pid, did, b)
            if not success:
                raise Exception("send failed. server sent: {}".format(extra))
            else:
                b.clear()

        # temp batches are not saved between calls; re-made each time
        for b in tempBatches:
            success, extra = self._importService.importBatch(pid, did, b)
            if not success:
                raise Exception("send failed. server sent: {}".format(extra))


    @staticmethod
    def query(token, qry, backend=None):
        """Performs a query on the iobeam backend.

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
        """
        if token is None:
            raise ValueError("token cannot be None")
        elif qry is None:
            raise ValueError("qry cannot be None")
        elif not isinstance(qry, QueryReq):
            raise ValueError("qry must be a iobeam.QueryReq")
        requester = None
        if backend is not None:
            requester = request.getRequester(url=backend)

        service = exports.ExportService(token, requester=requester)
        return service.getData(qry)

    @staticmethod
    def fetchToken(userToken, projectId, duration=None, options=None,
                   backend=None):
        """Fetch a token for the given parameters."""
        if userToken is None:
            raise ValueError("userToken cannot be None")
        requester = None
        if backend is not None:
            requester = request.getRequester(url=backend)

        service = tokens.TokenService(requester=requester)
        return service.getProjectToken(userToken, projectId,
                                       duration=duration, options=options)

# Aliases
def makeQuery(token, qry, backend=None):
    """Perform iobeam query."""
    return _Client.query(token, qry, backend)

def fetchDeviceToken(userToken, projectId, deviceId, duration=None,
                     options=None, backend=None):
    """Fetch a token specifically for a device.

    Params:
        userToken - User token to authenticate to iobeam
        projectId - Project ID to which the device belongs
        deviceId - Device ID to make the token for
        duration - Specification of how long the token is valid for, in
                   form <num><unit> where unit is (w)eeks, (d)ays, (h)ours,
                   (m)inutes, or (s)econds. Example: 5w = 5 weeks.
                   Optional, with a default of None (standard token
                   validity period).
        options - Additional options for the token passed as a dict. Options
                  include permissions (booleans, named "read", "write",
                  "admin") or if refreshable (boolean, "refreshable").
    Returns:
        JSON web token string of the token.
    """
    if options is not None:
        paramOptions = options.copy()
    else:
        paramOptions = {}
    paramOptions["device_id"] = deviceId
    return _Client.fetchToken(userToken, projectId, duration=duration,
                              options=options, backend=backend)
