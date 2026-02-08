# Quick Start Guide

## 5-Minute Overview

The Mosaic Home Assistant integration lets you control LED mosaic displays from Home Assistant.

### Installation (HACS)

1. Open HACS → Integrations
2. Create custom repository: `https://github.com/johnfernkas/mosaic`
3. Install "Mosaic LED Display"
4. Restart Home Assistant

### Setup

1. Settings → Devices & Services → Create Integration
2. Search "Mosaic"
3. Choose auto-detect or enter add-on URL
4. Done! Entities appear automatically

### Basic Usage

#### Show Text

```yaml
service: mosaic.push_text
data:
  target: kitchen
  text: "Hello!"
  duration: 10
```

#### Control Brightness

```yaml
service: light.turn_on
target:
  entity_id: light.mosaic_kitchen
data:
  brightness: 100  # 0-255 scale
```

#### Toggle Rotation

```yaml
service: switch.turn_on
target:
  entity_id: switch.mosaic_kitchen_rotation
```

## Entities Created

For each display, you get:

- **light.mosaic_{name}** — Brightness slider (0-100%)
- **switch.mosaic_{name}_power** — Power on/off
- **switch.mosaic_{name}_rotation** — Enable/disable app rotation
- **sensor.mosaic_{name}_status** — Connection status

## Available Services

### push_text
Display text on a display
```yaml
target: "kitchen"      # Display ID or "all"
text: "Hello World"
duration: 10           # seconds
priority: normal       # low, normal, high, sticky
color: [255,255,255]   # RGB
font: default
```

### push_image
Display an image
```yaml
target: "kitchen"
image: "/config/www/image.png"  # Path or URL
duration: 10
priority: normal
```

### show_app
Show app temporarily
```yaml
target: "kitchen"
app: "fuzzyclock"
duration: 30  # Then return to rotation
```

### clear
Clear notifications
```yaml
target: "kitchen"  # or "all"
```

## Common Automations

### Morning Brightness

```yaml
automation:
  - alias: "Morning brightness"
    trigger:
      platform: time
      at: "07:00:00"
    action:
      service: light.turn_on
      target:
        entity_id: light.mosaic_kitchen
      data:
        brightness: 200  # 0-255
```

### Doorbell Alert

```yaml
automation:
  - alias: "Doorbell notification"
    trigger:
      webhook_id: doorbell_webhook
    action:
      - service: mosaic.push_text
        data:
          target: all
          text: "DOORBELL"
          duration: 15
          priority: high
          color: [255, 0, 0]  # Red
```

### Show Weather Periodically

```yaml
automation:
  - alias: "Show weather"
    trigger:
      platform: state
      entity_id: binary_sensor.someone_home
      to: "on"
    action:
      service: mosaic.show_app
      data:
        target: kitchen
        app: weather
        duration: 60
```

### Nighttime Dimming

```yaml
automation:
  - alias: "Dim at night"
    trigger:
      platform: time
      at: "23:00:00"
    action:
      service: light.turn_on
      target:
        entity_id: light.mosaic_kitchen
      data:
        brightness: 50
```

## Troubleshooting

### Can't connect?

1. Check add-on is running
2. Verify URL: `curl http://localhost:8176/api/status`
3. Check HA logs: Settings → System → Logs

### Entities missing?

1. Reload integration: Settings → Devices & Services → Mosaic → Reload
2. Check add-on returns displays: `curl http://localhost:8176/api/displays`

### Service failing?

1. Test endpoint: `curl -X POST http://localhost:8176/api/notify -H "Content-Type: application/json" -d '{"display":"default","type":"text","text":"test","duration":5,"priority":"normal"}'`
2. Check HA logs for errors

## Documentation

- **README.md** — Full feature documentation
- **DEVELOPMENT.md** — For developers
- **API_SPECIFICATION.md** — For add-on developers
- **STRUCTURE.md** — Code structure and design

## Need Help?

- Check [README.md](README.md) troubleshooting section
- Review service examples in [DEVELOPMENT.md](DEVELOPMENT.md)
- See [API_SPECIFICATION.md](API_SPECIFICATION.md) for technical details

---

**That's it!** You now have an integrated LED display in Home Assistant. 🎨
