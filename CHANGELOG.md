# Changelog

All notable changes to the Mosaic integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-08

### Added

- Initial release of Mosaic Home Assistant integration
- Config flow with auto-detection of add-on
- Light entity for brightness control
- Switch entities for display power and rotation toggle
- Sensor entity for display connection status
- Data coordinator polling add-on every 30 seconds
- Services:
  - `mosaic.push_text` - Display text on displays
  - `mosaic.push_image` - Display images on displays
  - `mosaic.show_app` - Temporarily show specific apps
  - `mosaic.clear` - Clear notifications and return to rotation
- Complete API client for Mosaic add-on
- HACS-compatible metadata
- Comprehensive documentation
- Type hints and py.typed marker

### Features

- Auto-detect Mosaic add-on on common URLs
- Manual configuration with custom URLs
- Optional API key authentication
- Multi-display support
- Priority-based notifications
- Entity grouping by display
- Extra attributes for advanced use cases

### Documentation

- README.md with usage examples
- DEVELOPMENT.md for developers
- API_SPECIFICATION.md for add-on developers
- Inline code documentation and type hints

## Future Releases

### Planned for v0.2.0

- [ ] Number entity for dwell time control
- [ ] Select entity for current app selection
- [ ] Image display optimization
- [ ] Brightness schedule automations
- [ ] WebSocket support for real-time updates
- [ ] Display discovery via mDNS

### Planned for v0.3.0

- [ ] Schema-based app configuration UI
- [ ] Community apps browser integration
- [ ] Tidbyt WebP format support
- [ ] Notification history logging
- [ ] Advanced rotation scheduling

### Backlog

- [ ] Media player integration (album art)
- [ ] Camera integration (display feeds)
- [ ] Weather-aware brightness adjustment
- [ ] Gesture recognition (future hardware)
- [ ] Plugin system for custom entities
