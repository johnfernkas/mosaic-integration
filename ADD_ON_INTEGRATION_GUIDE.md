# Add-on Integration Guide

This guide is for Mosaic add-on developers implementing the required API endpoints.

## Quick Start

The Home Assistant integration communicates with the Mosaic add-on via HTTP endpoints. This document specifies what endpoints are required, what data they should return, and how to implement them.

## Core Requirements

### 1. Health Check Endpoint

**Endpoint:** `GET /api/status`

Must always return a 200 status with health information:

```json
{
  "status": "ok",
  "version": "0.1.0",
  "currentApp": "clock",
  "display": {
    "width": 64,
    "height": 32
  }
}
```

**Implementation tip:** Keep this lightweight and fast. It's checked every 30 seconds by the integration.

### 2. Display Registration

**Endpoints:**
- `GET /api/displays` — List displays
- `POST /api/displays` — Register new display
- `GET /api/displays/{id}` — Get display config
- `PUT /api/displays/{id}` — Update display config

Displays can be registered dynamically when clients connect (e.g., Interstate 75W boards) or statically via configuration.

**Implementation tip:** Store display state in memory and persist to `/data/displays.yaml` for recovery on restart.

### 3. Frame Serving

**Endpoint:** `GET /frame?display={id}&format=raw`

Return raw RGB pixels as bytes. This is the most performance-critical endpoint.

**Implementation tip:**
- For raw format, return uncompressed RGB888 (width × height × 3 bytes)
- Cache frames while rotation is paused
- Return frame metadata in headers (dimensions, frame count, timing)

### 4. App Rotation

**Endpoints:**
- `GET /api/displays/{id}/rotation` — Get rotation config
- `PUT /api/displays/{id}/rotation` — Update rotation
- `POST /api/displays/{id}/rotation/show-app` — Show app temporarily
- `POST /api/displays/{id}/rotation/skip` — Next app

**Implementation tip:** 
- Manage rotation state per-display (don't share)
- Use a timer to advance apps after dwell_seconds
- Queue notifications between apps in rotation

### 5. Notifications

**Endpoints:**
- `POST /api/notify` — Push notification
- `GET /api/notify/queue` — View queue
- `DELETE /api/notify` — Clear notifications

Implement priority levels:
- `low` — Queued for later
- `normal` — Interrupt rotation, return after duration
- `high` — Immediate, skip queue
- `sticky` — Stay until cleared

**Implementation tip:** Use FIFO queue per priority level. Sticky notifications don't timeout.

## Implementation Path

### Phase 1: Minimal (MVP)

Implement these endpoints first:

```
✓ GET /api/status
✓ GET /api/displays
✓ GET /frame
✓ POST /api/notify (text only)
✓ PUT /api/displays/{id}  (brightness, power only)
```

This enables:
- Integration connection and entity creation
- Display brightness control
- Basic text notifications

### Phase 2: Full Rotation

Add rotation support:

```
✓ GET /api/displays/{id}/rotation
✓ PUT /api/displays/{id}/rotation
✓ POST /api/displays/{id}/rotation/show-app
✓ POST /api/displays/{id}/rotation/skip
```

Enables:
- App rotation enable/disable
- Rotating through configured apps
- Dwell time adjustment

### Phase 3: Queue Management

Implement notification priority:

```
✓ GET /api/notify/queue
✓ DELETE /api/notify/{id}
Priority levels in POST /api/notify
```

### Phase 4: App Management (Future)

When community apps are integrated:

```
- GET /api/apps
- GET /api/apps/community
- POST /api/apps/install
- GET /api/apps/{id}/schema
- POST /api/apps/{id}/config
```

## Data Types

### Display Object

```go
type Display struct {
    ID              string `json:"id"`
    Name            string `json:"name"`
    Width           int    `json:"width"`
    Height          int    `json:"height"`
    Brightness      int    `json:"brightness"`        // 0-100
    Power           bool   `json:"power"`
    RotationEnabled bool   `json:"rotation_enabled"`
    ClientType      string `json:"client_type"`       // interstate75w, tidbyt, etc
}
```

### Rotation Config

```go
type RotationConfig struct {
    Enabled          bool   `json:"enabled"`
    DwellSeconds     int    `json:"dwell_seconds"`
    Apps             []App  `json:"apps"`
    CurrentAppIndex  int    `json:"current_app_index"`
}

type App struct {
    ID     string                 `json:"id"`
    Name   string                 `json:"name"`
    Config map[string]interface{} `json:"config"`
}
```

### Notification

```go
type Notification struct {
    Display  string `json:"display"`
    Type     string `json:"type"`           // text, image
    Text     string `json:"text,omitempty"`
    Image    string `json:"image,omitempty"`
    Duration int    `json:"duration"`       // seconds, 0 = sticky
    Priority string `json:"priority"`       // low, normal, high, sticky
    Color    string `json:"color,omitempty"` // hex, for text
    Font     string `json:"font,omitempty"` // font name
}
```

## Error Handling

Always return proper HTTP status codes:

| Status | Meaning |
|--------|---------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 500 | Server Error |

**Error Response Format:**

```json
{
  "error": "error_code",
  "message": "Human readable message"
}
```

## Testing Against Integration

### Test Setup

1. Start the integration with your add-on
2. Check HA logs for connection errors
3. Verify entities appear in HA UI

### Manual API Tests

```bash
# Check status
curl http://localhost:8176/api/status

# Get displays
curl http://localhost:8176/api/displays

# Push text
curl -X POST http://localhost:8176/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "display": "default",
    "type": "text",
    "text": "Hello",
    "duration": 10,
    "priority": "normal"
  }'

# Get frame
curl http://localhost:8176/frame?display=default&format=raw > frame.bin
```

### Integration Debug

In Home Assistant, check Settings → System → Logs for Mosaic errors.

Enable debug logging:

```yaml
logger:
  logs:
    custom_components.mosaic: debug
```

## Performance Considerations

### Frame Serving

The `/frame` endpoint is called by display clients (e.g., Interstate 75W) multiple times per second:

- **Keep responses < 100ms** (ideally < 50ms)
- Cache frame data between requests
- Use buffered I/O for large responses
- Consider compression for WebP format

### Status Polling

Integration polls `/api/status` every 30 seconds:

- Keep response < 10ms
- No expensive I/O
- Use in-memory state

### Notification Queue

Notifications can accumulate during long-running apps:

- Limit queue size (suggested: 100 items max)
- Implement TTL for old notifications
- Log dropped notifications

## Example Implementation (Go)

Here's a minimal example showing the core pattern:

```go
package main

import (
    "encoding/json"
    "net/http"
    "sync"
)

type Display struct {
    ID       string `json:"id"`
    Width    int    `json:"width"`
    Height   int    `json:"height"`
    Power    bool   `json:"power"`
    Brightness int  `json:"brightness"`
}

type Server struct {
    displays map[string]*Display
    mu       sync.RWMutex
}

// GET /api/status
func (s *Server) handleStatus(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]interface{}{
        "status":     "ok",
        "version":    "0.1.0",
        "currentApp": "clock",
        "display": map[string]int{
            "width":  64,
            "height": 32,
        },
    })
}

// GET /api/displays
func (s *Server) handleListDisplays(w http.ResponseWriter, r *http.Request) {
    s.mu.RLock()
    defer s.mu.RUnlock()
    
    displays := make([]*Display, 0, len(s.displays))
    for _, d := range s.displays {
        displays = append(displays, d)
    }
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(displays)
}

// PUT /api/displays/{id}
func (s *Server) handleUpdateDisplay(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")
    
    var req map[string]interface{}
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "Bad request", 400)
        return
    }
    
    s.mu.Lock()
    defer s.mu.Unlock()
    
    display, ok := s.displays[id]
    if !ok {
        http.Error(w, "Not found", 404)
        return
    }
    
    // Update fields
    if brightness, ok := req["brightness"].(float64); ok {
        display.Brightness = int(brightness)
    }
    if power, ok := req["power"].(bool); ok {
        display.Power = power
    }
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(display)
}

func main() {
    s := &Server{
        displays: map[string]*Display{
            "default": {
                ID:        "default",
                Width:     64,
                Height:    32,
                Power:     true,
                Brightness: 100,
            },
        },
    }
    
    http.HandleFunc("GET /api/status", s.handleStatus)
    http.HandleFunc("GET /api/displays", s.handleListDisplays)
    http.HandleFunc("PUT /api/displays/{id}", s.handleUpdateDisplay)
    
    http.ListenAndServe(":8176", nil)
}
```

## Debugging Tips

### Integration won't connect

1. Check `/api/status` responds with 200
2. Verify Content-Type is `application/json`
3. Check for JSON parsing errors in HA logs
4. Ensure all required fields are present

### Entities don't update

1. Verify `/api/displays` returns correct structure
2. Check display IDs match entity names
3. Verify coordinator refresh succeeds
4. Check for errors in update coordinator logs

### Services fail

1. Test endpoint with curl first
2. Check request body format matches spec
3. Verify HTTP status codes are correct
4. Log all requests for debugging

## Documentation

Keep your add-on documentation updated with:
- Implemented endpoints and versions
- Configuration examples
- Known limitations
- Performance characteristics

## Support

If you're implementing the add-on:

1. Reference this integration guide
2. Check [API_SPECIFICATION.md](API_SPECIFICATION.md) for endpoint details
3. Review [DESIGN.md](../DESIGN.md) for architecture context
4. Test against the integration in a real HA instance
5. Report any API changes needed back to the integration team

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-08
