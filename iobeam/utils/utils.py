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
        raise ValueError("projectId must be an int");
    elif not projectId > 0:
        raise ValueError("projectId must be greater than 0")
