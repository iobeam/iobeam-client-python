"""Used to communicate with iobeam's Exports API"""
from iobeam.endpoints import service
from iobeam.http import request


class ExportService(service.EndpointService):
    """Communicates with the backend and exposes available Exports API methods."""

    def __init__(self, token, requester=None):
        service.EndpointService.__init__(self, token, requester=requester)

    def getData(self, query):
        """Wraps API call `POST /exports`

        Queries data from the iobeam backend.

        Params:
            query - A iobeam.resources.Query object that contains the parameters
                    for the query.

        Returns:
            A dictionary representing the query results.

        Raises:
            Exception - If `query` is None
        """
        if not self.token:
            raise request.UnauthorizedError.noTokenSet()
        if query is None:
            raise Exception("query cannot be None")

        endpoint = self.makeEndpoint("exports/{}".format(query.getUrl()))

        r = self.requester().get(endpoint).token(self.token)
        params = query.getParams()
        for p in params:
            r.setParam(p, params[p])
        r.execute()

        return r.getResponse()
