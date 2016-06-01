"""Classes used when communicating via HTTP to the iobeam backend."""
import requests
from iobeam.utils import utils

ERROR_CODE_DUPLICATE_DEVICE_ID = 150

_BASE_URL = "https://api.iobeam.com/v1/"


class Requester(object):
    """Generates HTTP requests using `requests` library."""

    def __init__(self, baseUrl=_BASE_URL):
        self._baseUrl = baseUrl
        self._session = requests.Session()

    def makeEndpoint(self, endpoint):
        """Create a fully defined URL for an endpoint."""
        return self._baseUrl + endpoint

    def get(self, url):
        """Return a base GET request for a given URL."""
        return Request("GET", url, self._session)

    def post(self, url):
        """Return a base POST request for a given URL."""
        return Request("POST", url, self._session)


_REQUESTERS = {_BASE_URL: Requester()}

def getRequester(url=None):
    if url is None:
        return _REQUESTERS[_BASE_URL]
    if url not in _REQUESTERS:
        _REQUESTERS[url] = Requester(baseUrl=url)
    return _REQUESTERS[url]


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

class UnknownCodeError(Error):

    def __init__(self, req):
        Error.__init__(self, "Received unexpected code: {}\nDetails: {}".format(
            req.getResponseCode(), str(req.getApiError())))

class Request(object):
    """Wrapper for an HTTP request object."""

    def __init__(self, method, url, session):
        self.method = method
        self.url = url
        self.headers = {}
        self.header("User-Agent", "iobeam python")
        self.header("Connection", "keep-alive")
        self.resp = None
        self.body = None
        self.params = {}
        self._session = session

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
            self.resp = self._session.get(
                self.url, params=self.params, headers=self.headers)
        elif self.method == "POST":
            self.resp = self._session.post(self.url, params=self.params,
                                           headers=self.headers, json=self.body)
        else:
            utils.getLogger().warning("UNSUPPORTED METHOD: {}", self.method)

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

    def getApiError(self):
        """Return iobeam API error.

        Returns:
            The JSON error or None otherwise.
        """
        if self.resp is None:
            return None
        try:
            msg = self.resp.json()
            return msg["errors"][0]
        except Exception:
            return None

    def getApiErrorCode(self):
        """Return iobeam API error code.

        Returns:
            The error code or None otherwise.
        """
        if self.resp is None:
            return None
        try:
            msg = self.resp.json()
            return msg["errors"][0]["code"]
        except Exception:
            return None
