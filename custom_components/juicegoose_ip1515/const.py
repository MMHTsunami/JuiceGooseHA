"""Constants for the Juice Goose IP 15-15 integration."""

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "juicegoose_ip1515"
DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)
PLATFORMS = (Platform.SWITCH, Platform.BINARY_SENSOR, Platform.BUTTON)

POD_NAMES: dict[int, str] = {pod: f"POD {pod}" for pod in range(1, 4)}

STATUS_PATH = "/status.xml"
POD_CONTROL_PATHS: dict[int, str] = {
    pod: f"/pod{pod}.cgi" for pod in POD_NAMES
}
SEQUENCE_PATH = "/sequence.cgi"

QUERY_STATUS = "status"
QUERY_DELAY = "delay"
STATUS_OFF = 0
STATUS_ON = 1
SEQUENCE_DOWN = 0
SEQUENCE_UP = 1
MIN_SEQUENCE_DELAY_SECONDS = 3
DEFAULT_SEQUENCE_DELAY_SECONDS = 10

POD_STATUS_TAGS: dict[int, str] = {
    pod: f"pod{pod}" for pod in POD_NAMES
}
SEQUENCE_STATUS_TAG = "seq"
MANUAL_OVERRIDE_STATUS_TAG = "mosws"
