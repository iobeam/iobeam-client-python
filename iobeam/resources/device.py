'''
Represents a device that is associated with a project.
'''
class Device(object):

    def __init__(self, projectId, deviceId, deviceName):
        self.projectId = projectId
        self.deviceId = deviceId
        self.deviceName = deviceName

    '''
    Prints a string representation of this device in the form:
    <deviceName> [<projectId>: <deviceId>]
    '''
    def __str__(self):
        return "{} [{}: {}]".format(self.deviceName, self.projectId,
                                    self.deviceId)
