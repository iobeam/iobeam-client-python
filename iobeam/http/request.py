import requests

class Requester(object):

    _BASE_URL = "https://api.iobeam.com/v1/"

    def __init__(self, baseUrl=_BASE_URL):
        self._baseUrl = baseUrl

    def makeEndpoint(self, endpoint):
        return self._baseUrl + endpoint

    def get(self, url):
        return Request("GET", url)

    def post(self, url):
        return Request("POST", url)


class UnauthorizedError(Exception):
    def __init__(self, value):
        Exception.__init__(self, value)

    @staticmethod
    def noTokenSet():
        return UnauthorizedError("no token set.")

class Error(Exception):
    def __init__(self, value):
        Exception.__init__(self, value)

class Request(object):

    def __init__(self, method, url):
        self.method = method
        self.url = url
        self.headers = {}
        self.header("User-Agent", "iobeam python")
        self.resp = None
        self.body = None
        self.params = {}

    def header(self, key, value):
        self.headers[key] = value
        return self

    def token(self, token):
        return self.header("Authorization", "Bearer {}".format(token))

    def setBody(self, body):
        self.body = body
        return self

    def setParam(self, key, value):
        self.params[key] = value
        return self

    def execute(self):
        self.resp = None
        if self.method == "GET":
            self.resp = requests.get(self.url, params=self.params, headers=self.headers)
        elif self.method == "POST":
            self.resp = requests.post(self.url, params=self.params, headers=self.headers, json=self.body)
        else:
            print("unsupported method")

    def getResponse(self):
        if self.resp is None:
            return None
        try:
            return self.resp.json()
        except:
            return None

    def getResponseCode(self):
        return self.resp.status_code
