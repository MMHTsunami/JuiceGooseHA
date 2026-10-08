"""Constants for the Juice Goose IP 15-15 integration."""

from datetime import timedelta

DOMAIN = "juicegoose_ip1515"
DEFAULT_PORT = 23
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)

# The unit exposes fifteen controlled outputs; labels can be refined from device data.
POD_NAMES: dict[int, str] = {pod: f"POD {pod}" for pod in range(1, 16)}

# Provisional ASCII command templates. Confirm the device's exact command syntax
# against its protocol documentation before sending commands to hardware.
COMMAND_STATUS = "STATUS"
COMMAND_POD_ON = "POD {pod} ON"
COMMAND_POD_OFF = "POD {pod} OFF"
