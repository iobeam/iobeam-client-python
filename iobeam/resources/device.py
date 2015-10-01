"""Data types related to iobeam devices."""
from iobeam.utils import utils


# pylint: disable=too-few-public-methods
class Device(object):
    """Represents a device that is associated with a project."""

    def __init__(self, projectId, deviceId, deviceName=None):
        """Constructor for a Device object.

        A valid Device object has at least a `projectId` and a `deviceId`, and
        optionally a `deviceName`.

        Params:
            projectId - Project id (int) that this device belongs to
            deviceId - Id of this device
            deviceName - Optional secondary identifier for the device

        Raises:
            ValueError - If projectId is None, not an int, or not >0. Also if
                         deviceId is None.
        """
        utils.checkValidProjectId(projectId)
        utils.checkValidDeviceId(deviceId)

        self.projectId = projectId
        self.deviceId = deviceId
        self.deviceName = deviceName

    def __str__(self):
        """Prints a string representation of this device.

        Format:
        <deviceName> [<projectId>: <deviceId>]
        """
        return "{} [{}: {}]".format(self.deviceName, self.projectId,
                                    self.deviceId)
# pylint: enable=too-few-public-methods
