"""Used to implement an iobeam API endpoint."""
from iobeam.http import request

class EndpointService(object):
    """Base class for implementing an iobeam endpoint."""

    def __init__(self, token, requester=None):
        self.token = token
        if requester is None:
            self._requester = request.Requester()
        else:
            self._requester = requester

    def requester(self):
        """Return this service's HTTP requester object"""
        return self._requester

    def makeEndpoint(self, endpoint):
        """Create a string of the full API endpoint"""
        return self._requester.makeEndpoint(endpoint)
