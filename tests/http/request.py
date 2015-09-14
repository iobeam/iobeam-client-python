'''Provides dummy interfaces of http/request'''

from iobeam.http import request

_BASE_URL = "https://api-dev.iobeam.com/v1/"


'''
Basic dummy request factory.
'''
class DummyRequester(object):

    def __init__(self, request):
        self._request = request
        self.lastMethod = None
        self.lastUrl = None

    def makeEndpoint(self, endpoint):
        return _BASE_URL + endpoint

    def get(self, url):
        self.lastMethod = "GET"
        self.lastUrl = url
        self._request.method = "GET"
        self._request.url = url
        return self._request

    def post(self, url):
        self.lastMethod = "POST"
        self.lastUrl = url
        self._request.method = "POST"
        self._request.url = url
        return self._request


'''
Dummy request object that implements all of iobeam/http/request
except that it does not be default hit the network.
'''
class DummyRequest(request.Request):

    def __init__(self, method, url):
        request.Request.__init__(self, method, url)
        self.header("User-Agent", "iobeam python dummy")

    '''
    Subclasses should implement this method
    '''
    def dummyExecute(self, url, params=None, headers=None, json=None):
        raise Exception("Not implemented!")

    def execute(self):
        self.resp = None
        if self.method == "GET":
            self.resp = self.dummyExecute(self.url, params=self.params, headers=self.headers)
        elif self.method == "POST":
            self.resp = self.dummyExecute(self.url, params=self.params, headers=self.headers, json=self.body)
        else:
            print("unsupported method")
