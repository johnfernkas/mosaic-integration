"""Constants for the Mosaic integration."""

DOMAIN = "mosaic"
DEFAULT_PORT = 8176
DEFAULT_NAME = "Mosaic"
DEFAULT_POLL_INTERVAL = 30

# Config keys
CONF_URL = "url"
CONF_VERIFY_SSL = "verify_ssl"
CONF_API_KEY = "api_key"
CONF_AUTO_DETECT = "auto_detect"

# Entity naming
ENTITY_LIGHT = "light"
ENTITY_SWITCH_POWER = "switch_power"
ENTITY_SWITCH_ROTATION = "switch_rotation"
ENTITY_SELECT_APP = "select_app"
ENTITY_SENSOR_STATUS = "sensor_status"
ENTITY_NUMBER_DWELL = "number_dwell"

# Service names
SERVICE_PUSH_TEXT = "push_text"
SERVICE_PUSH_IMAGE = "push_image"
SERVICE_SHOW_APP = "show_app"
SERVICE_CLEAR = "clear"

# Service field names
FIELD_TARGET = "target"
FIELD_TEXT = "text"
FIELD_DURATION = "duration"
FIELD_PRIORITY = "priority"
FIELD_COLOR = "color"
FIELD_FONT = "font"
FIELD_IMAGE = "image"
FIELD_APP = "app"

# Priority levels
PRIORITY_LOW = "low"
PRIORITY_NORMAL = "normal"
PRIORITY_HIGH = "high"
PRIORITY_STICKY = "sticky"
PRIORITY_OPTIONS = [PRIORITY_LOW, PRIORITY_NORMAL, PRIORITY_HIGH, PRIORITY_STICKY]

# Status values
STATUS_CONNECTED = "connected"
STATUS_DISCONNECTED = "disconnected"
STATUS_UNKNOWN = "unknown"

# Data keys
DATA_COORDINATOR = "coordinator"
DATA_DISPLAYS = "displays"
DATA_API = "api"

# Attributes
ATTR_BRIGHTNESS = "brightness"
ATTR_POWER = "power"
ATTR_ROTATION = "rotation"
ATTR_STATUS = "status"
ATTR_DWELL = "dwell"
ATTR_CURRENT_APP = "current_app"
ATTR_WIDTH = "width"
ATTR_HEIGHT = "height"
ATTR_POSITION = "position"
