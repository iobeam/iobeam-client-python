'''
Common utility functions.
'''

'''
Checks that a projectId is valid: a position int.

Raises:
    ValueError - If projectId is None, not an int, or <= 0.
'''
def checkValidProjectId(projectId):
    if projectId is None or not isinstance(projectId, int):
        raise ValueError("projectId must be an int")
    elif not projectId > 0:
        raise ValueError("projectId must be greater than 0")

def checkValidDeviceId(deviceId):
    if deviceId is None or not isinstance(deviceId, str):
        raise ValueError("deviceId must be a string")
    elif len(deviceId) == 0:
        raise ValueError("deviceId must be more than 0 characters")

def checkValidProjectToken(token):
    if token is None or not isinstance(token, str):
        raise ValueError("token must be a string")
    elif len(token) == 0:
        raise ValueError("token must be more than 0 characters")
