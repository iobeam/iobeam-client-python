"""Used to communicate with iobeam's Tokens API"""
from iobeam.endpoints import service
from iobeam.http import request
from iobeam.utils import utils


class TokenService(service.EndpointService):
    """Communicates with the backend and exposes available Tokens API methods."""

    def __init__(self, requester=None):
        service.EndpointService.__init__(self, None, requester=requester)

    def refreshToken(self, oldToken):
        """Wraps API call `POST /tokens/project`

        Refreshes project token using an old token.

        Params:
            oldToken - Previous project token to refresh

        Returns:
            Refreshed project token (string), or None if an error occurs.
        """
        utils.checkValidProjectToken(oldToken)
        endpoint = self.makeEndpoint("tokens/project")
        req = {"refresh_token": oldToken}

        r = self.requester().post(endpoint).setBody(req)
        r.execute()

        if r.getResponseCode() == 200:
            return r.getResponse()["token"]
        else:
            return None
