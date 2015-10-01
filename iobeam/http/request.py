"""Classes used when communicating via HTTP to the iobeam backend."""
import requests

class Requester(object):
    """Generates HTTP requests using `requests` library."""

    _BASE_URL = "https://api.iobeam.com/v1/"

    def __init__(self, baseUrl=_BASE_URL):
        self._baseUrl = baseUrl

    def makeEndpoint(self, endpoint):
        """Create a fully defined URL for an endpoint."""
        return self._baseUrl + endpoint

    def get(self, url):
        """Return a base GET request for a given URL."""
        return Request("GET", url)

    def post(self, url):
        """Return a base POST request for a given URL."""
        return Request("POST", url)


class UnauthorizedError(Exception):
    """Error for forbidden access."""

    def __init__(self, value):
        Exception.__init__(self, value)

    @staticmethod
    def noTokenSet():
        """Return an `UnauthorizedError` when a token is not set."""
        return UnauthorizedError("no token set.")

class Error(Exception):
    """Generic error for HTTP operations."""

    def __init__(self, value):
        Exception.__init__(self, value)

class Request(object):
    """Wrapper for an HTTP request object."""

    def __init__(self, method, url):
        self.method = method
        self.url = url
        self.headers = {}
        self.header("User-Agent", "iobeam python")
        self.resp = None
        self.body = None
        self.params = {}

    def header(self, key, value):
        """Add a header to the request (chainable)."""
        self.headers[key] = value
        return self

    def token(self, token):
        """Set a token for the request (chainable)."""
        return self.header("Authorization", "Bearer {}".format(token))

    def setBody(self, body):
        """Set the request body (chainable)."""
        self.body = body
        return self

    def setParam(self, key, value):
        """Set a query parameter for a request (chainable)."""
        self.params[key] = value
        return self

    def execute(self):
        """Execute an HTTP request using `requests` library."""
        self.resp = None
        if self.method == "GET":
            self.resp = requests.get(
                self.url, params=self.params, headers=self.headers)
        elif self.method == "POST":
            self.resp = requests.post(self.url, params=self.params,
                                      headers=self.headers, json=self.body)
        else:
            print("unsupported method")

    def getResponse(self):
        """Return response body for a given request."""
        if self.resp is None:
            return None
        try:
            return self.resp.json()
        except Exception:
            return None

    def getResponseCode(self):
        """Return HTTP status code for a given request."""
        return self.resp.status_code
