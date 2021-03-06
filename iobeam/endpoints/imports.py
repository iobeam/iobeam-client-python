"""Used to communicate with iobeam's Imports API"""
from iobeam.endpoints import service
from iobeam.http import request
from iobeam.utils import utils


class ImportService(service.EndpointService):
    """Communicates with the backend and exposes available Imports API methods."""

    _BATCH_SIZE = 1000  # max # of pts in a single request

    def __init__(self, token, requester=None):
        service.EndpointService.__init__(self, token, requester=requester)

    @staticmethod
    def _makeRequest(projectId, deviceId, dataset):
        """Creates the body of a import request.

        Params:
            projectId - Project ID of the request
            deviceId - Device ID of the request
            dataset - The data series of the request, a map with names to lists
                of data.DataPoints.

        Returns:
            A dictionary that is the body of an import request.
        """
        sources = []
        req = {
            "project_id": projectId,
            "device_id": deviceId,
            "sources": sources,
            "timefmt": "usec"
        }
        for series in dataset:
            pts = []
            obj = {"name": series, "data": pts}
            for d in dataset[series]:
                pts.append(d.toDict())
            sources.append(obj)

        return req

    @staticmethod
    def _makeBatchRequest(projectId, deviceId, dataStore):
        """Creates the body of a table import request.

        Params:
            projectId - Project ID of the request
            deviceId - Device ID of the request
            dataStore - The DataStore that makes the body of the request.

        Returns:
            A dictionary that is the body of an import request.
        """
        sources = {}
        req = {
            "project_id": projectId,
            "device_id": deviceId,
            "sources": sources,
            "timefmt": "usec"
        }

        sources["fields"] = ["time"]
        for f in dataStore.columns():
            sources["fields"].append(f)
        sources["data"] = []
        for r in dataStore.rows():
            row = []
            for f in sources["fields"]:
                row.append(r[f])
            sources["data"].append(row)

        return req

    @staticmethod
    def _makeListOfReqs(projectId, deviceId, dataset):
        """Creates a list of import requests from a data set.

        If the data set is under _BATCH_SIZE, it will be one request. Otherwise
        it will be split into multiple requests as follows:
        (1) if a single series has less than ImportService._BATCH_SIZE points,
            it will be a request.
        (2) if a single series has more, it will be broken into multiple requests of
            ImportService._BATCH_SIZE size.

        Params:
            projectId - Project ID of the requests
            deviceId - Device ID of the requests
            dataset - The data set that will be broken into requests.

        Returns:
            A list of import request bodies.
        """
        totalLen = sum(len(dataset[k]) for k in dataset)

        reqs = []
        # No series, no requests
        if totalLen == 0:
            pass
        # Everything can fit in one request
        elif totalLen <= ImportService._BATCH_SIZE:
            reqs.append(
                ImportService._makeRequest(projectId, deviceId, dataset))
        # Need to create multiple requests
        else:
            for series in dataset:
                seriesLen = len(dataset[series])
                # If the series itself is small enough, send it
                if seriesLen <= ImportService._BATCH_SIZE:
                    temp = {}
                    temp[series] = dataset[series]
                    reqs.append(
                        ImportService._makeRequest(projectId, deviceId, temp))
                # Split series into chunks of up to _BATCH_SIZE
                else:
                    idx = 0
                    valsList = list(dataset[series])
                    while idx < seriesLen:
                        end = idx + ImportService._BATCH_SIZE
                        vals = valsList[idx:end]
                        temp = {}
                        temp[series] = vals
                        reqs.append(ImportService._makeRequest(
                            projectId, deviceId, temp))
                        idx += ImportService._BATCH_SIZE

        return reqs

    @staticmethod
    def _makeListOfBatchReqs(projectId, deviceId, dataBatch):
        """Creates a list of import requests from a DataStore.

        If the data set is under _BATCH_SIZE, it will be one request. Otherwise
        it will be split into multiple requests of at most _BACH_SIZE data
        points.

        Params:
            projectId - Project ID of the requests
            deviceId - Device ID of the requests
            dataset - The data batch to create requests from

        Returns:
            A list of batch import request bodies.
        """
        totalLen = len(dataBatch)

        reqs = []
        # No series, no requests
        if totalLen == 0:
            pass
        # Everything can fit in one request
        elif totalLen <= ImportService._BATCH_SIZE:
            reqs.append(ImportService._makeBatchRequest(projectId, deviceId, dataBatch))
        # Need to create multiple requests
        else:
            maxRowsPerBatch = ImportService._BATCH_SIZE // len(dataBatch.columns())
            batches = dataBatch.split(maxRowsPerBatch)
            for b in batches:
                reqs.append(ImportService._makeBatchRequest(projectId, deviceId, b))

        return reqs

    def importData(self, projectId, deviceId, dataSeries):
        """Wraps API call `POST /imports`

        Sends data to the iobeam backend to be stored.

        Params:
            projectId - Project ID the data belongs to
            deviceId - Device ID the data belongs to
            dataSeries - Dataset to send, as a dictionary where the keys are
            the name of the series, and the values are sets containing
            `iobeam.iobeam.DataPoint`s.

        Returns:
            A tuple where the first item is the success of all of the requests (True if
            all succeed, False otherwise); the second item is any error message or None
            if successful.

        Raises:
            Exception - If any of projectId, deviceId, or dataSeries is None.
        """
        if not self.token:
            raise request.UnauthorizedError.noTokenSet()
        if projectId is None:
            raise Exception("Project ID cannot be None")
        elif deviceId is None:
            raise Exception("Device ID cannot be None")
        elif dataSeries is None:
            raise Exception("Dataset cannot be None")
        elif len(dataSeries) == 0:
            return (True, None)
        endpoint = self.makeEndpoint("imports")

        reqs = ImportService._makeListOfReqs(projectId, deviceId, dataSeries)
        success = True
        extra = None
        for req in reqs:
            r = self.requester().post(endpoint).token(self.token)
            r.setBody(req)
            r.execute()
            success = success and (r.getResponseCode() == 200)
            if r.getResponseCode() != 200:
                extra = r.getResponse()

        return (success, extra)

    def importBatch(self, projectId, deviceId, dataStore):
        """Wraps API call `POST /imports?fmt=table`

        Sends data to the iobeam backend to be stored.

        Params:
            projectId - Project ID the data belongs to
            deviceId - Device ID the data belongs to
            dataStore - A `DataStore` object containing the the data to be imported

        Returns:
            A tuple where the first item is the success of all of the requests (True if
            all succeed, False otherwise); the second item is any error message or None
            if successful.

        Raises:
            ValueError - If validity checks fail for the token, project id, or device id.
        """
        utils.checkValidProjectId(projectId)
        utils.checkValidProjectToken(self.token)
        utils.checkValidDeviceId(deviceId)
        if dataStore is None or len(dataStore) == 0:
            utils.getLogger().warning("Attempted to send with no data")
            return (True, None)
        endpoint = self.makeEndpoint("imports")

        reqs = ImportService._makeListOfBatchReqs(projectId, deviceId, dataStore)
        success = True
        extra = None
        for req in reqs:
            r = self.requester().post(endpoint).token(self.token) \
                .setParam("fmt", "table") \
                .setBody(req)
            r.execute()
            success = success and (r.getResponseCode() == 200)
            if r.getResponseCode() != 200:
                extra = r.getResponse()

        return (success, extra)
