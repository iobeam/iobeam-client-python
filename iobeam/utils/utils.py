"""Common utility functions."""
import jwt
import logging
import sys
import time

IS_PY3 = sys.version_info >= (3, 0)

# For compatibility with both Python 2 and 3.
# pylint: disable=redefined-builtin,invalid-name
if IS_PY3:
    unicode = str
    long = int
# pylint: enable=redefined-builtin,invalid-name

EXPIRY_FUDGE = 1000 * 60 * 60 * 24  # one day in milliseconds

def isExpiredToken(projectToken):
    """Check if token's expiry date (minus a bit) has passed.

    Token is expired if the current time is after the expiry date less EXPIRY_FUDGE.

    Params:
        projectToken - JWT token to decode

    Returns:
        True if expired; False otherwise.

    Raises:
        ValueError - projectToken is not a valid JWT token
    """
    checkValidProjectToken(projectToken)
    opts = {"verify_signature": False, "verify_exp": False}
    try:
        decoded = jwt.decode(projectToken, '', options=opts)
    except jwt.DecodeError:
        raise ValueError("invalid jwt token")
    exp = int(decoded["exp"]) * 1000
    now = int(time.time() * 1000)

    return now >= (exp - EXPIRY_FUDGE)


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

__LOGGER = None

def getLogger():
    global __LOGGER
    if __LOGGER is not None:
        logger = __LOGGER
    else:
        logger = logging.getLogger("iobeam")
        logger.setLevel(logging.WARNING)
        __LOGGER = logger

    if len(logger.handlers) == 0:
        logger.addHandler(logging.NullHandler())
    return logger
