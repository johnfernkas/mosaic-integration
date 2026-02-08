# Mosaic LED Display Integration

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)

Home Assistant integration for the **Mosaic LED Display** add-on. Control and interact with your LED mosaic displays directly from Home Assistant automations, scripts, and dashboards.

## Features

- **Brightness Control** — Adjust display brightness from 0-100% via the `light.mosaic_*` entity
- **Power Management** — Turn displays on/off via `switch.mosaic_*_power`
- **App Rotation** — Enable/disable rotating through apps via `switch.mosaic_*_rotation`
- **Display Status** — Monitor connection status via `sensor.mosaic_*_status`
- **Push Notifications** — Send text/images to displays with priority levels
- **Show Apps** — Temporarily show specific apps then return to rotation
- **Data Coordinator** — Polls add-on every 30 seconds for updates

## Installation

### Via HACS

1. Open HACS → Integrations
2. Click the **+ Create my own repository** button
3. Enter repository URL: `https://github.com/johnfernkas/mosaic-integration`
4. Select category: **Integration**
5. Click **CREATE**
6. Install the Mosaic integration
7. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/mosaic` directory to `~/.homeassistant/custom_components/`
2. Restart Home Assistant

## Setup

1. Go to Settings → Devices & Services → Integrations
2. Click **Create Integration**
3. Search for "Mosaic"
4. Choose auto-detect or manual configuration:
   - **Auto-detect**: Searches common URLs (assumes standard HA add-on DNS)
   - **Manual**: Enter add-on URL (e.g., `http://localhost:8176`)

## Usage

### Entities

After setup, the integration creates the following entities for each display:

| Entity | Type | Purpose |
|--------|------|---------|
| `light.mosaic_{name}` | Light | Brightness control (0-100) |
| `switch.mosaic_{name}_power` | Switch | Display power on/off |
| `switch.mosaic_{name}_rotation` | Switch | Enable/disable app rotation |
| `sensor.mosaic_{name}_status` | Sensor | Connection status (connected/disconnected) |

### Services

#### `mosaic.push_text`

Display text on one or more displays.

```yaml
service: mosaic.push_text
data:
  target: kitchen  # Display ID or "all"
  text: "Hello World"
  duration: 10  # seconds, 0 = sticky
  priority: normal  # low, normal, high, sticky
  color: [255, 255, 255]  # RGB
  font: default
```

#### `mosaic.push_image`

Display an image on a display.

```yaml
service: mosaic.push_image
data:
  target: kitchen
  image: "/config/www/myimage.png"  # Path or URL
  duration: 10
  priority: normal
```

#### `mosaic.show_app`

Show a specific app temporarily.

```yaml
service: mosaic.show_app
data:
  target: kitchen
  app: fuzzyclock  # App ID
  duration: 30  # seconds before returning to rotation
```

#### `mosaic.clear`

Clear all notifications and return to app rotation.

```yaml
service: mosaic.clear
data:
  target: kitchen  # or "all"
```

## Examples

### Simple Automation

```yaml
automation:
  - alias: "Show time when motion detected"
    trigger:
      platform: state
      entity_id: binary_sensor.kitchen_motion
      to: "on"
    action:
      service: mosaic.show_app
      data:
        target: kitchen
        app: fuzzyclock
        duration: 30
```

### Send Notifications

```yaml
automation:
  - alias: "Doorbell notification"
    trigger:
      webhook_id: doorbell_webhook
    action:
      service: mosaic.push_text
      data:
        target: all
        text: "Someone at the door!"
        duration: 15
        priority: high
        color: [255, 0, 0]  # Red
```

### Control Brightness on Schedule

```yaml
automation:
  - alias: "Dim display at night"
    trigger:
      platform: time
      at: "22:00:00"
    action:
      service: light.turn_on
      target:
        entity_id: light.mosaic_kitchen
      data:
        brightness: 50
```

## Configuration

The integration stores the following configuration:

- **URL** — Base URL of the Mosaic add-on
- **API Key** — Optional API key for authentication
- **Verify SSL** — Whether to verify SSL certificates

These can be updated in Settings → Devices & Services → Mosaic → Configure.

## Troubleshooting

### Cannot connect to add-on

1. Check that the Mosaic add-on is running
2. Verify the URL is correct (default: `http://a0d7b954-mosaic:8176` for HA add-ons)
3. If using a custom URL, ensure it's accessible from your HA instance
4. Check HA logs for errors: Settings → System → Logs

### Entities not showing up

1. Ensure the add-on API is returning displays correctly
2. Check that displays are registered in the add-on
3. Reload the integration: Settings → Devices & Services → Mosaic → Reload

### Services failing

1. Check that the add-on is responding: `curl http://localhost:8176/api/status`
2. Verify service parameters are correct
3. Check HA logs for API errors

## Development

### Requirements

- Python 3.9+
- Home Assistant 2023.11+
- aiohttp

### Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Type checking
mypy custom_components/mosaic

# Linting
ruff check custom_components/mosaic
```

## Architecture

The integration consists of:

- **API Client** (`api.py`) — Communicates with the add-on HTTP API
- **Data Coordinator** (`coordinator.py`) — Polls add-on every 30s, manages service calls
- **Config Flow** (`config_flow.py`) — UI-based setup with auto-detection
- **Entity Platforms** — Light, Switch, and Sensor entities per display
- **Services** — Event-driven actions for push notifications and app control

### Data Flow

```
┌─────────────────────────────────────────┐
│  Home Assistant UI                      │
│  - Config Flow Setup                    │
│  - Entities Dashboard                   │
│  - Service Calls                        │
└────────────────┬────────────────────────┘
                 │
        ┌────────▼────────┐
        │   Coordinator   │
        │  (poll every    │
        │      30s)       │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │   API Client    │
        │  (aiohttp)      │
        └────────┬────────┘
                 │ HTTP
        ┌────────▼────────────────┐
        │  Mosaic Add-on (Go)     │
        │  - Pixlet Renderer      │
        │  - App Rotation         │
        │  - Notification Queue   │
        │  - HTTP API             │
        └────────┬────────────────┘
                 │
        ┌────────▼──────────┐
        │  LED Displays     │
        │  (Interstate 75W, │
        │   Tidbyt, etc)    │
        └───────────────────┘
```

## API Specification

The integration expects the Mosaic add-on to provide the following HTTP endpoints:

### Status
```
GET /api/status
Response: {status, version, currentApp, display: {width, height}}
```

### Displays
```
GET /api/displays
Response: [{id, name, width, height, brightness, power, ...}]
```

### Notifications
```
POST /api/notify
Body: {display, type, text/image, duration, priority, color, font}
```

### Rotation
```
GET /api/displays/{id}/rotation
PUT /api/displays/{id}/rotation
POST /api/displays/{id}/rotation/show-app
POST /api/displays/{id}/rotation/skip
```

### Control
```
PUT /api/displays/{id}
Body: {brightness, power, rotation}
```

See [DESIGN.md](https://github.com/johnfernkas/mosaic-integration/blob/main/DESIGN.md) for complete API spec.

## License

MIT — See LICENSE file

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues, feature requests, or questions:
- Open an issue on [GitHub](https://github.com/johnfernkas/mosaic-integration/issues)
- Check the [Mosaic design doc](https://github.com/johnfernkas/mosaic-integration/blob/main/DESIGN.md)

---

**Mosaic** — LED display server for Home Assistant | [GitHub](https://github.com/johnfernkas/mosaic-integration)
