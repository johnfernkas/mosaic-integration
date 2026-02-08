# Development Guide

## Project Structure

```
mosaic-integration/
├── custom_components/mosaic/
│   ├── __init__.py           # Integration setup
│   ├── manifest.json         # HA integration manifest
│   ├── config_flow.py        # UI configuration
│   ├── const.py              # Constants
│   ├── coordinator.py        # Data update coordinator
│   ├── api.py                # API client
│   ├── light.py              # Brightness entity
│   ├── switch.py             # Power/rotation switches
│   ├── sensor.py             # Status sensor
│   ├── services.yaml         # Service definitions
│   ├── py.typed              # Type hints marker
│   └── translations/
│       └── en.json           # English translations
├── hacs.json                 # HACS metadata
├── README.md                 # User documentation
├── DEVELOPMENT.md            # This file
└── LICENSE
```

## Development Setup

### Prerequisites

- Python 3.9+
- Home Assistant 2023.11+ (for testing)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/johnfernkas/mosaic.git
cd mosaic/mosaic-integration

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt
```

## Local Testing

### Manual Testing in Home Assistant

1. Copy the integration to your HA `custom_components` directory:
   ```bash
   cp -r custom_components/mosaic ~/.homeassistant/custom_components/
   ```

2. Restart Home Assistant

3. Go to Settings → Devices & Services → Create Integration

### Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=custom_components/mosaic

# Run specific test
pytest tests/test_api.py
```

### Type Checking

```bash
mypy custom_components/mosaic
```

### Linting

```bash
ruff check custom_components/mosaic
ruff format custom_components/mosaic
```

## Adding New Entities

### 1. Create Entity File

Create a new file in `custom_components/mosaic/`, e.g., `number.py`:

```python
"""Number entity for Mosaic."""

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import MosaicDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    displays = coordinator.data.get("displays", [])
    entities = [
        MosaicDwellNumber(coordinator, display) for display in displays
    ]
    async_add_entities(entities)


class MosaicDwellNumber(CoordinatorEntity, NumberEntity):
    """Number entity for app dwell time."""

    def __init__(self, coordinator: MosaicDataUpdateCoordinator, display: dict):
        super().__init__(coordinator)
        self.display = display
        self._display_id = display.get("id", "default")
        
        self._attr_unique_id = f"mosaic_dwell_{self._display_id}"
        self._attr_name = f"{display.get('name')} Dwell"
        self._attr_min_value = 1
        self._attr_max_value = 300
        
    @property
    def native_value(self) -> float | None:
        rotation_config = self.coordinator.data.get("rotation_configs", {}).get(
            self._display_id, {}
        )
        return float(rotation_config.get("dwell_seconds", 10))
    
    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.api.set_dwell_seconds(self._display_id, int(value))
        await self.coordinator.async_request_refresh()
```

### 2. Add to Platform List

Update `__init__.py`:

```python
PLATFORMS: Final = [Platform.LIGHT, Platform.SWITCH, Platform.SENSOR, Platform.NUMBER]
```

### 3. Add Entity Names to Constants

Update `const.py`:

```python
ENTITY_NUMBER_DWELL = "number_dwell"
```

## Adding New Services

### 1. Define Service in services.yaml

```yaml
my_service:
  description: My service description
  fields:
    target:
      selector:
        text:
      description: Target display
      required: true
```

### 2. Register in __init__.py

```python
async def handle_my_service(call) -> None:
    """Handle service call."""
    target = call.data.get("target")
    # ... implementation

hass.services.async_register(DOMAIN, "my_service", handle_my_service)
```

## API Client Methods

The `api.py` client provides methods for all endpoints. When adding new features to the add-on, add corresponding client methods:

```python
async def set_dwell_seconds(self, display_id: str, seconds: int) -> Dict[str, Any]:
    """Set dwell time for app rotation."""
    return await self._request(
        "PUT",
        f"/api/displays/{display_id}/rotation",
        {"dwell_seconds": seconds},
    )
```

## Data Coordinator

The `MosaicDataUpdateCoordinator` handles:
- Polling the add-on every 30 seconds
- Managing state updates for all entities
- Providing helper methods for service calls
- Error handling and retry logic

To add new coordinator methods:

```python
async def async_my_action(self, param: str) -> None:
    """Perform action."""
    try:
        await self.api.my_method(param)
        await self.async_request_refresh()
    except MosaicAPIError as err:
        raise UpdateFailed(f"Error: {err}")
```

## Config Flow

The config flow handles:
1. **User step** — Initial setup (auto-detect or manual)
2. **Auto-detect step** — Tries common URLs
3. **Manual step** — User enters URL and API key

To modify config flow:

1. Update `STEP_USER_DATA_SCHEMA` or `STEP_MANUAL_DATA_SCHEMA` for new fields
2. Add new steps if needed
3. Update translations in `translations/en.json`

## Testing Checklist

Before submitting a PR:

- [ ] Entity creates successfully
- [ ] Entity updates from coordinator
- [ ] Service calls work
- [ ] Error handling works
- [ ] Type checking passes (`mypy`)
- [ ] Linting passes (`ruff`)
- [ ] Tests pass (`pytest`)
- [ ] No console errors in HA logs

## Stubbed API Endpoints

The following add-on endpoints are used but should be confirmed:

### Current Stubs

```
PUT /api/displays/{id}
- brightness: int (0-100)
- power: bool
- rotation: bool

PUT /api/displays/{id}/rotation
- enabled: bool
- dwell_seconds: int

POST /api/displays/{id}/rotation/show-app
- app: str
- duration: int
```

**To Do:** Confirm these match the actual add-on API implementation.

## Documentation

- **README.md** — User-facing documentation
- **DEVELOPMENT.md** — Developer guide (this file)
- **services.yaml** — Service definitions visible in HA UI
- **const.py** — Configuration constants
- **API docstrings** — Method documentation

Keep all documentation up-to-date with changes.

## Common Issues

### "Cannot connect to add-on"

Check:
1. Add-on is running (`docker ps | grep mosaic`)
2. URL is correct (default for HA: `http://a0d7b954-mosaic:8176`)
3. Network access between HA and add-on

### "Entities not updating"

Check:
1. Coordinator is fetching data (`hass.data[DOMAIN]`)
2. Display IDs match between API and entities
3. Refresh interval in coordinator (default 30s)

### "Type checking fails"

Use explicit type hints:
```python
from typing import Optional, Dict, Any

def my_method(self, arg: str) -> Optional[Dict[str, Any]]:
    pass
```

## Release Process

1. Update version in `manifest.json`
2. Update `CHANGELOG.md` (create if needed)
3. Tag release: `git tag v0.1.0`
4. Push to GitHub: `git push origin main --tags`
5. HACS will pick it up automatically

## References

- [HA Integration Development](https://developers.home-assistant.io/)
- [HA Entity Development](https://developers.home-assistant.io/docs/core/entity/)
- [Config Flow](https://developers.home-assistant.io/docs/data_entry_flow_index/)
- [Data Coordinator](https://developers.home-assistant.io/docs/integration_fetching_data/#coordinating-updates-across-multiple-entities)
