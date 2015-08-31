from iobeam.http import request


'''
Communicates with the backend and exposes available Exports API methods.
'''
class ExportService(object):

    def __init__(self, token=None):
        self.token = token

    '''
    Wraps API call `POST /exports`

    Queries data from the iobeam backend.

    Params:
        query - A iobeam.resources.Query object that contains the parameters
                for the query.

    Returns:
        A dictionary representing the query results.

    Raises:
        Exception - If `query` is None
    '''
    def getData(self, query):
        if not self.token:
            raise request.UnauthorizedError.noTokenSet();
        if query is None:
            raise Exception("query cannot be None")

        endpoint = "exports/{}".format(query.getUrl())

        r = request.get(request.makeEndpoint(endpoint)).token(self.token)
        params = query.getParams()
        for p in params:
            r.setParam(p, params[p])
        r.execute()

        return r.getResponse()
