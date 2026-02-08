# Mosaic Add-on API Specification

This document specifies the HTTP API endpoints required by the Home Assistant integration.

## Overview

The Mosaic add-on must provide HTTP endpoints for status monitoring, display control, notifications, and app management.

## Base URL

- **Default:** `http://localhost:8176`
- **HA Add-on (Ingress):** `http://a0d7b954-mosaic:8176`
- **Custom:** User-specified via config flow

## Status Endpoint

### GET /api/status

Get add-on health and version information.

**Response (200):**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "currentApp": "weather",
  "display": {
    "width": 64,
    "height": 32
  }
}
```

**Fields:**
- `status` (string): "ok", "error", etc.
- `version` (string): Semantic version
- `currentApp` (string): Currently displaying app ID
- `display` (object): Default display dimensions

---

## Display Management

### GET /api/displays

Get list of registered displays.

**Response (200):**
```json
[
  {
    "id": "kitchen",
    "name": "Kitchen Mosaic",
    "width": 64,
    "height": 32,
    "brightness": 85,
    "power": true,
    "rotation_enabled": true,
    "client_type": "interstate75w"
  }
]
```

**Fields per display:**
- `id` (string): Unique display ID
- `name` (string): Human-readable name
- `width` (int): Display width in pixels
- `height` (int): Display height in pixels
- `brightness` (int): 0-100
- `power` (bool): Power state
- `rotation_enabled` (bool): App rotation enabled
- `client_type` (string): Client type (interstate75w, tidbyt, etc)

---

### POST /api/displays

Register a new display.

**Request:**
```json
{
  "id": "kitchen",
  "name": "Kitchen Mosaic",
  "width": 64,
  "height": 32,
  "client_type": "interstate75w"
}
```

**Response (201):**
```json
{
  "id": "kitchen",
  "name": "Kitchen Mosaic",
  "width": 64,
  "height": 32,
  "brightness": 100,
  "power": true,
  "rotation_enabled": true,
  "client_type": "interstate75w"
}
```

---

### GET /api/displays/{id}

Get display configuration.

**Response (200):**
```json
{
  "id": "kitchen",
  "name": "Kitchen Mosaic",
  "width": 64,
  "height": 32,
  "brightness": 85,
  "power": true,
  "rotation_enabled": true,
  "client_type": "interstate75w"
}
```

---

### PUT /api/displays/{id}

Update display configuration.

**Request (partial update):**
```json
{
  "brightness": 75,
  "power": true,
  "rotation_enabled": false
}
```

**Response (200):**
```json
{
  "id": "kitchen",
  "name": "Kitchen Mosaic",
  "width": 64,
  "height": 32,
  "brightness": 75,
  "power": true,
  "rotation_enabled": false,
  "client_type": "interstate75w"
}
```

**Updateable fields:**
- `brightness` (int): 0-100
- `power` (bool): Power state
- `rotation_enabled` (bool): Enable/disable rotation

---

## Frame Endpoint

### GET /frame

Get raw frame data for display.

**Query Parameters:**
- `display` (string): Display ID (default: "default")
- `format` (string): "raw" (default), "webp", "gif"

**Response Headers:**
```
X-Frame-Width: 64
X-Frame-Height: 32
X-Frame-Count: 8
X-Frame-Delay-Ms: 100
X-Dwell-Secs: 10
X-Brightness: 85
X-App-Name: weather
Content-Type: application/octet-stream
```

**Response Body:**
Raw RGB bytes: `width × height × 3 × frame_count` bytes

**Frame Format (raw):**
- RGB888: 3 bytes per pixel
- Row-major order (left-to-right, top-to-bottom)
- No padding between rows

**Example:**
- Display: 64x32
- Frames: 1 (static image)
- Total bytes: 64 × 32 × 3 × 1 = 6,144 bytes

---

## Rotation Management

### GET /api/displays/{id}/rotation

Get rotation configuration.

**Response (200):**
```json
{
  "enabled": true,
  "dwell_seconds": 10,
  "apps": [
    {
      "id": "weather",
      "name": "Weather",
      "config": {}
    },
    {
      "id": "fuzzyclock",
      "name": "Fuzzy Clock",
      "config": {}
    }
  ],
  "current_app_index": 0
}
```

**Fields:**
- `enabled` (bool): Rotation enabled
- `dwell_seconds` (int): Seconds per app
- `apps` (array): Apps in rotation
- `current_app_index` (int): Current app index

---

### PUT /api/displays/{id}/rotation

Update rotation configuration.

**Request:**
```json
{
  "enabled": true,
  "dwell_seconds": 15
}
```

**Response (200):**
```json
{
  "enabled": true,
  "dwell_seconds": 15,
  "apps": [...],
  "current_app_index": 0
}
```

---

### POST /api/displays/{id}/rotation/show-app

Show a specific app temporarily.

**Request:**
```json
{
  "app": "fuzzyclock",
  "duration": 30
}
```

**Response (200):**
```json
{
  "status": "showing",
  "app": "fuzzyclock",
  "duration_seconds": 30
}
```

---

### POST /api/displays/{id}/rotation/skip

Skip to next app in rotation.

**Response (200):**
```json
{
  "current_app": "fuzzyclock",
  "current_app_index": 1
}
```

---

## Notifications

### POST /api/notify

Push notification to display.

**Request:**
```json
{
  "display": "kitchen",
  "type": "text",
  "text": "Hello World",
  "duration": 10,
  "priority": "normal",
  "color": "#FFFFFF",
  "font": "default"
}
```

**Type: text**
- `text` (string): Text to display
- `color` (string): Hex color code
- `font` (string): Font name
- `duration` (int): Seconds to show (0 = sticky)

**Type: image**
```json
{
  "display": "kitchen",
  "type": "image",
  "image": "/path/to/image.png",
  "duration": 10,
  "priority": "normal"
}
```
- `image` (string): Path or URL to image
- `duration` (int): Seconds to show

**Priority Levels:**
- `low` (default) — Queued after current app
- `normal` — Interrupts rotation, returns after duration
- `high` — Immediate, preempts queue
- `sticky` — Stays until cleared (duration ignored)

**Response (201):**
```json
{
  "id": "notif-12345",
  "display": "kitchen",
  "type": "text",
  "text": "Hello World",
  "duration": 10,
  "priority": "normal",
  "created_at": "2026-02-08T20:30:00Z"
}
```

---

### GET /api/notify/queue

Get notification queue.

**Query Parameters:**
- `display` (string): Filter by display (optional)

**Response (200):**
```json
{
  "queue": [
    {
      "id": "notif-12345",
      "display": "kitchen",
      "type": "text",
      "text": "Hello World",
      "priority": "normal",
      "position": 1
    }
  ]
}
```

---

### DELETE /api/notify

Clear notifications.

**Query Parameters:**
- `display` (string): Display ID or "all"

**Response (200):**
```json
{
  "cleared": 3,
  "display": "kitchen"
}
```

---

### DELETE /api/notify/{id}

Remove notification from queue.

**Response (200):**
```json
{
  "id": "notif-12345",
  "removed": true
}
```

---

## App Management

### GET /api/apps

List installed apps.

**Response (200):**
```json
{
  "apps": [
    {
      "id": "weather",
      "name": "Weather",
      "author": "Tidbyt",
      "version": "1.0.0"
    },
    {
      "id": "fuzzyclock",
      "name": "Fuzzy Clock",
      "author": "Max Timkovich",
      "version": "1.2.0"
    }
  ]
}
```

---

### GET /api/apps/community

Browse community apps (from bundled index).

**Query Parameters:**
- `search` (string): Search term
- `category` (string): Filter by category
- `limit` (int): Max results (default: 50)

**Response (200):**
```json
{
  "apps": [
    {
      "id": "fuzzyclock",
      "name": "Fuzzy Clock",
      "summary": "Human readable time",
      "author": "Max Timkovich",
      "category": "time"
    }
  ],
  "count": 487,
  "updated": "2026-02-08T00:00:00Z"
}
```

---

### POST /api/apps/install

Install community app.

**Request:**
```json
{
  "id": "fuzzyclock"
}
```

**Response (201):**
```json
{
  "id": "fuzzyclock",
  "name": "Fuzzy Clock",
  "status": "installed",
  "version": "1.2.0"
}
```

---

### GET /api/apps/{id}/schema

Get app configuration schema.

**Response (200):**
```json
{
  "id": "fuzzyclock",
  "schema": {
    "version": "1",
    "fields": [
      {
        "id": "use_24h",
        "name": "24-Hour Format",
        "type": "toggle",
        "default": false
      }
    ]
  }
}
```

---

### POST /api/apps/{id}/config

Save app configuration.

**Request:**
```json
{
  "use_24h": true
}
```

**Response (200):**
```json
{
  "id": "fuzzyclock",
  "config": {
    "use_24h": true
  }
}
```

---

## Error Handling

All endpoints return standard error responses:

**400 — Bad Request**
```json
{
  "error": "invalid_request",
  "message": "Missing required field: text"
}
```

**401 — Unauthorized**
```json
{
  "error": "unauthorized",
  "message": "Invalid API key"
}
```

**404 — Not Found**
```json
{
  "error": "not_found",
  "message": "Display 'kitchen' not found"
}
```

**500 — Internal Server Error**
```json
{
  "error": "server_error",
  "message": "Failed to render app"
}
```

---

## Authentication

Optional API key authentication:

```http
GET /api/status
Authorization: Bearer <api_key>
```

If configured, add-on must validate API key on all requests.

---

## Implementation Checklist

- [ ] GET /api/status
- [ ] GET /api/displays
- [ ] POST /api/displays
- [ ] GET /api/displays/{id}
- [ ] PUT /api/displays/{id}
- [ ] GET /frame
- [ ] GET /api/displays/{id}/rotation
- [ ] PUT /api/displays/{id}/rotation
- [ ] POST /api/displays/{id}/rotation/show-app
- [ ] POST /api/displays/{id}/rotation/skip
- [ ] POST /api/notify
- [ ] GET /api/notify/queue
- [ ] DELETE /api/notify
- [ ] DELETE /api/notify/{id}
- [ ] GET /api/apps
- [ ] GET /api/apps/community
- [ ] POST /api/apps/install
- [ ] GET /api/apps/{id}/schema
- [ ] POST /api/apps/{id}/config

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-08 | Initial specification |

---

## References

- [Mosaic Design Document](../DESIGN.md)
- [Home Assistant Integration Docs](https://developers.home-assistant.io/)
