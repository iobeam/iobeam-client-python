"""Used to communicate with iobeam's Tokens API"""
from iobeam.endpoints import service
from iobeam.http import request
from iobeam.utils import utils

def _checkValidDuration(duration):
    """Check that a duration string is of valid form: <num><unit>

    Raises:
        ValueError - If unit is not one of w, d, h, m, or s;
                     OR if first part is not a number.
    """
    if duration[-1:] not in ["w", "d", "h", "m", "s"]:
        raise ValueError("duration unit must be one of w, d, h, m, or s" \
                         + "(week, day, hour, minute, second)")
    int(duration[:-1])  #  throws a ValueError if not an int

class TokenService(service.EndpointService):
    """Communicates with the backend and exposes available Tokens API methods."""

    def __init__(self, requester=None):
        service.EndpointService.__init__(self, None, requester=requester)

    def getProjectToken(self, userToken, projectId, duration=None, options=None):
        """Wraps API call `GET /tokens/project`

        Gets a new project token with the supplied parameters.

        Params:
            userToken - User token to authenticate to the iobeam backend
            projectId - ID of the project to get a token for
            duration - Specification of how long the token is valid for, in
                       form <num><unit> where unit is (w)eeks, (d)ays, (h)ours,
                       (m)inutes, or (s)econds. Example: 5w = 5 weeks.
                       Optional, with a default of None (standard token
                       validity period).
            options - Additional options for the token passed as a dict. Options
                      include permissions (booleans, named "read", "write", "admin"),
                      refreshable (boolean, "refreshable"), and device ID (string,
                      "device_id").

        Returns:
            The JSON web token (JWT) string
        Raises:
            UnknownCodeError if an error response is returned by server.
        """
        utils.checkValidProjectId(projectId)

        endpoint = self.makeEndpoint("tokens/project")
        r = self.requester().get(endpoint).token(userToken) \
            .setParam("project_id", projectId)
        if duration is not None:
            _checkValidDuration(duration)
            r.setParam("duration", duration)

        if options is not None:
            if not isinstance(options, dict):
                raise ValueError("options must be a dict")
            for p in options:
                r.setParam(p, options[p])
        r.execute()

        if r.getResponseCode() == 200:
            return r.getResponse()["token"]
        else:
            raise request.UnknownCodeError(r)


    def refreshToken(self, oldToken):
        """Wraps API call `POST /tokens/project`

        Refreshes project token using an old token.

        Params:
            oldToken - Previous project token to refresh

        Returns:
            Refreshed project token (string).

        Raises:
            UnknownCodeError if an error response is returned by server.
        """
        utils.checkValidProjectToken(oldToken)
        endpoint = self.makeEndpoint("tokens/project")
        req = {"refresh_token": oldToken}

        r = self.requester().post(endpoint).setBody(req)
        r.execute()

        if r.getResponseCode() == 200:
            return r.getResponse()["token"]
        else:
            raise request.UnknownCodeError(r)
