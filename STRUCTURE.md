# Integration Structure

## Directory Layout

```
mosaic-integration/
├── custom_components/
│   └── mosaic/
│       ├── __init__.py              # Main integration setup & service registration
│       ├── manifest.json            # HA integration metadata
│       ├── config_flow.py           # Configuration UI (config flow)
│       ├── const.py                 # Constants and enums
│       ├── coordinator.py           # Data update coordinator (30s polling)
│       ├── api.py                   # HTTP client for add-on API
│       ├── light.py                 # Light entity (brightness)
│       ├── switch.py                # Switch entities (power, rotation)
│       ├── sensor.py                # Sensor entity (status)
│       ├── services.yaml            # Service definitions
│       ├── py.typed                 # Type hints marker
│       └── translations/
│           └── en.json              # English translations
├── hacs.json                        # HACS metadata
├── README.md                        # User documentation
├── DEVELOPMENT.md                   # Developer guide
├── CHANGELOG.md                     # Version history
├── API_SPECIFICATION.md             # Complete API spec for add-on
├── ADD_ON_INTEGRATION_GUIDE.md      # Implementation guide for add-on devs
├── STRUCTURE.md                     # This file
├── LICENSE                          # MIT License
├── .gitignore                       # Git ignore rules
├── .flake8                          # Linting configuration
├── requirements.txt                 # Runtime dependencies
└── requirements-dev.txt             # Development dependencies
```

## File Descriptions

### Core Integration Files

#### `custom_components/mosaic/__init__.py` (155 lines)
- Integration entry point (`async_setup_entry`)
- Setup platforms (light, switch, sensor)
- Service registration (push_text, push_image, show_app, clear)
- Cleanup on unload

#### `custom_components/mosaic/config_flow.py` (165 lines)
- User step: choose auto-detect or manual
- Auto-detect step: try common URLs
- Manual step: enter custom URL + API key
- Error handling and validation

#### `custom_components/mosaic/coordinator.py` (155 lines)
- `MosaicDataUpdateCoordinator` class
- 30-second polling interval
- Fetches status, displays, and rotation configs
- Wrapper methods for service calls (push_text, show_app, clear, etc)
- Error handling with `UpdateFailed`

#### `custom_components/mosaic/api.py` (335 lines)
- `MosaicAPIClient` class
- HTTP communication with add-on
- Methods for all endpoints (status, displays, notifications, rotation, etc)
- Error handling and timeouts
- Async/await pattern with aiohttp

### Entity Platforms

#### `custom_components/mosaic/light.py` (75 lines)
- `MosaicLight` entity for brightness control
- Brightness 0-100
- Turn on/off
- Extra attributes (display_id, dimensions)

#### `custom_components/mosaic/switch.py` (140 lines)
- `MosaicPowerSwitch` for power on/off
- `MosaicRotationSwitch` for rotation enable/disable
- Extra attributes with rotation config details

#### `custom_components/mosaic/sensor.py` (75 lines)
- `MosaicStatusSensor` for connection status
- Shows "connected" or "disconnected"
- Extra attributes with display details

### Configuration & Constants

#### `custom_components/mosaic/const.py` (60 lines)
- `DOMAIN` = "mosaic"
- Default values (port, poll interval)
- Config keys
- Entity types
- Service names and fields
- Status values
- Priority levels

#### `custom_components/mosaic/manifest.json`
- Integration name and version
- Home Assistant version requirement
- Dependencies (aiohttp)
- Documentation and issue tracker links

#### `custom_components/mosaic/services.yaml`
- Service definitions with field schemas
- Used by HA UI to show service call forms
- Defines: push_text, push_image, show_app, clear

#### `custom_components/mosaic/translations/en.json`
- English UI strings
- Service descriptions
- Entity names
- Error messages

### Documentation

#### `README.md` (320 lines)
- Feature overview
- Installation instructions (HACS, manual)
- Setup walkthrough
- Entity and service usage examples
- Troubleshooting guide
- Architecture diagram

#### `DEVELOPMENT.md` (320 lines)
- Project structure explanation
- Setup and testing instructions
- How to add new entities
- How to add new services
- API client usage patterns
- Data coordinator patterns
- Config flow modification
- Testing checklist
- Common issues

#### `API_SPECIFICATION.md` (400 lines)
- Complete HTTP API specification
- All endpoints documented
- Request/response examples
- Field descriptions
- Authentication details
- Error handling conventions
- Implementation checklist

#### `ADD_ON_INTEGRATION_GUIDE.md` (350 lines)
- For add-on developers
- Requirements overview
- Implementation path (Phase 1-4)
- Data types (Go structs)
- Error handling patterns
- Example Go implementation
- Performance considerations
- Debugging tips
- Testing guide

#### `CHANGELOG.md` (70 lines)
- Version history
- Features in v0.1.0
- Planned features for v0.2.0+

### Dependencies

#### `requirements.txt`
```
aiohttp>=3.8.0
```

#### `requirements-dev.txt`
```
homeassistant>=2023.11.0
pytest>=7.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0
mypy>=1.0
ruff>=0.1.0
aiohttp>=3.8.0
```

## Entity Model

Per display, the integration creates:

```
light.mosaic_{display_id}
├── Brightness: 0-100
├── State: on/off
└── Attributes:
    ├── display_id
    ├── width
    └── height

switch.mosaic_{display_id}_power
├── State: on/off
└── Attributes:
    └── display_id

switch.mosaic_{display_id}_rotation
├── State: on/off
├── Dwell time (attribute)
├── App count (attribute)
└── display_id (attribute)

sensor.mosaic_{display_id}_status
├── State: connected/disconnected
├── Width (attribute)
├── Height (attribute)
├── Brightness (attribute)
├── Power (attribute)
└── display_id (attribute)
```

## Service Model

### `mosaic.push_text`
- Target display
- Text message
- Duration (0 = sticky)
- Priority (low/normal/high/sticky)
- Color (RGB hex)
- Font name

### `mosaic.push_image`
- Target display
- Image path/URL
- Duration
- Priority

### `mosaic.show_app`
- Target display (required)
- App ID (required)
- Duration

### `mosaic.clear`
- Target display (optional, default "all")

## Data Flow

```
Home Assistant UI / Automation
         ↓
   Config Flow Entry
         ↓
   __init__.py (async_setup_entry)
         ↓
   ├─→ Coordinator (creates, 30s polling)
   ├─→ Light Platform (creates entities)
   ├─→ Switch Platform (creates entities)
   ├─→ Sensor Platform (creates entities)
   └─→ Services (registers handlers)
         ↓
   API Client (aiohttp)
         ↓
   Mosaic Add-on (HTTP endpoints)
         ↓
   LED Displays
```

## Key Design Decisions

1. **Data Coordinator Pattern** — Single coordinator polls all data, multiple entities consume it
2. **Per-Display Entities** — Each display gets separate light, switches, and sensor
3. **Async/Await** — All I/O operations are async for HA integration
4. **Type Hints** — Full type hints for IDE support and mypy checking
5. **Configuration Flow** — UI-based setup with auto-detection fallback
6. **Services Over Entities** — Complex actions (push_text, show_app) are services, not entities
7. **Graceful Degradation** — Missing endpoints don't break the integration

## Extensibility Points

### Adding New Entities

1. Create new file in `custom_components/mosaic/`
2. Implement async_setup_entry and entity class
3. Add platform to PLATFORMS in `__init__.py`
4. Add entity names to const.py

### Adding New Services

1. Define in `services.yaml`
2. Add handler in `__init__.py`
3. Use `hass.services.async_register()`
4. Call coordinator methods if needed

### Adding New API Methods

1. Add method to `MosaicAPIClient` in `api.py`
2. Use coordinator helper methods if entity-related
3. Document in `API_SPECIFICATION.md`

## Testing

The structure supports:
- **Unit tests** via pytest
- **Type checking** via mypy
- **Linting** via ruff
- **Manual testing** with real Home Assistant

## Code Quality

- **Type hints** on all public methods
- **Docstrings** on classes and key methods
- **Constants** defined in const.py
- **Error handling** with UpdateFailed and custom exceptions
- **Async patterns** throughout
- **HA integration conventions** followed

## Version Compatibility

- **Home Assistant**: 2023.11.0+
- **Python**: 3.9+
- **aiohttp**: 3.8.0+

---

**Last Updated:** 2026-02-08
