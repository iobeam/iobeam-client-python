"""Common utility functions."""

# For compatibility with both Python 2 and 3.
# pylint: disable=redefined-builtin,invalid-name
try:
    unicode
except NameError:
    unicode = str
    long = int
# pylint: enable=redefined-builtin,invalid-name

def checkValidProjectId(projectId):
    """Check that a projectId is valid: a position int.

    Raises:
        ValueError - If projectId is None, not an int, or <= 0.
    """
    if projectId is None or not isinstance(projectId, (int, long)):
        raise ValueError("projectId must be an int")
    elif not projectId > 0:
        raise ValueError("projectId must be greater than 0")

def __checkNon0LengthString(value, valueName):
    """Check that a value is a non-0 length string.

    Raises:
        ValueError - If `token` is (a) None, (b) not a string/unicode, or
                     (c) is of length 0.
    """
    if value is None:
        raise ValueError("{} must be a string".format(valueName))
    elif not isinstance(value, (str, unicode)):
        raise ValueError("{} must be a string".format(valueName))
    elif len(value) == 0:
        raise ValueError("{} must be more than 0 characters".format(valueName))

def checkValidDeviceId(deviceId):
    """Check that a deviceId is valid: string of len > 0

    Raises:
        ValueError - If `deviceId` is (a) None, (b) not a string/unicode, or
                     (c) is of length 0.
    """
    __checkNon0LengthString(deviceId, "deviceId")

def checkValidProjectToken(token):
    """Check that a token is valid: string of len > 0

    Raises:
        ValueError - If `token` is (a) None, (b) not a string/unicode, or
                     (c) is of length 0.
    """
    __checkNon0LengthString(token, "token")
