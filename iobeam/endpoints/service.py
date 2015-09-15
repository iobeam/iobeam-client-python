from iobeam.http import request

class EndpointService(object):

    def __init__(self, token, requester=None):
        self.token = token
        if requester is None:
            self._requester = request.Requester()
        else:
            self._requester = requester

    def requester(self):
        return self._requester

    def makeEndpoint(self, endpoint):
        return self._requester.makeEndpoint(endpoint)
