from iobeam.http import request


'''
Communicates with the backend and exposes available Imports API methods.
'''
class ImportService(object):

    def __init__(self, token=None):
        self.token = token

    '''
    Wraps API call `POST /imports`

    Sends data to the iobeam backend to be stored.

    Params:
        projectId - Project ID the data belongs to
        deviceId - Device ID the data belongs to
        dataSeries - Dataset to send, as a dictionary where the keys are
            the name of the series, and the values are sets containing
            `iobeam.iobeam.DataPoint`s.

    Returns:
        True if the data is sent successfully; False and the response otherwise.

    Raises:
        Exception - If any of projectId, deviceId, or dataSeries is None.
    '''
    def importData(self, projectId, deviceId, dataSeries):
        if not self.token:
            raise request.UnauthorizedError.noTokenSet();
        if projectId is None:
            raise Exception("Project ID cannot be None")
        elif deviceId is None:
            raise Exception("Device ID cannot be None")
        elif dataSeries is None:
            raise Exception("Dataset cannot be None")
        elif len(dataSeries) == 0:
            return True
        endpoint = "imports/"

        r = request.post(request.makeEndpoint(endpoint)).token(self.token)
        sources = []
        reqBody = {
            "project_id": projectId, "device_id": deviceId, "sources": sources
        }
        for k in dataSeries:
            pts = []
            obj = {"name": k, "data": pts}
            for d in dataSeries[k]:
                pts.append(d.toDict())
            sources.append(obj)

        r.setBody(reqBody)
        r.execute()

        if (r.getResponseCode() == 200):
            return (True, None)
        else:
            return (False, r.getResponse())
