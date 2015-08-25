import requests

def get(url):
    return Request("GET", url)

def post(url):
    return Request("POST", url)

BASE_URL = "https://api-dev.iobeam.com/v1/"

def makeEndpoint(endpoint):
    return BASE_URL + endpoint


class UnauthorizedError(Exception):
    def __init__(self):
        self.value = "Unauthorized - no token set."

    def __str__(self):
        return repr(self.value)


class Request(object):

    def __init__(self, method, url):
        self.method = method
        self.url = url
        self.headers = dict()
        self.header("User-Agent", "iobeam python")
        self.resp = None
        self.body = None

    def header(self, key, value):
        self.headers[key] = value
        return self

    def token(self, token):
        return self.header("Authorization", "Bearer {}".format(token))

    def setBody(self, body):
        self.body = body
        return self

    def execute(self):
        self.resp = None
        if self.method == "GET":
            self.resp = requests.get(self.url, headers=self.headers)
        elif self.method == "POST":
            self.resp = requests.post(self.url, json=self.body, headers=self.headers)
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
