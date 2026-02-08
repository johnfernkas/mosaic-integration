"""API client for Mosaic add-on."""

import aiohttp
import asyncio
import logging
from typing import Any, Dict, List, Optional

_LOGGER = logging.getLogger(__name__)


class MosaicAPIError(Exception):
    """Mosaic API error."""
    pass


class MosaicAPIClient:
    """Client for Mosaic add-on API."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, verify_ssl: bool = True):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self._session: Optional[aiohttp.ClientSession] = None

    async def close(self):
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Make an API request."""
        url = f"{self.base_url}{endpoint}"
        session = await self._get_session()
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with session.request(
                method, url, json=data, headers=headers,
                ssl=self.verify_ssl if self.verify_ssl else False,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    text = await resp.text()
                    raise MosaicAPIError(f"API error {resp.status}: {text}")
        except asyncio.TimeoutError:
            raise MosaicAPIError("Request timeout")
        except aiohttp.ClientError as e:
            raise MosaicAPIError(f"Connection error: {e}")

    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    async def get_status(self) -> Dict[str, Any]:
        """Get server status."""
        return await self._request("GET", "/api/status")

    # -------------------------------------------------------------------------
    # Multi-display API
    # -------------------------------------------------------------------------

    async def get_displays(self) -> List[Dict[str, Any]]:
        """Get list of all displays."""
        return await self._request("GET", "/api/displays")

    async def register_display(self, display_id: str, name: str, width: int = 64, height: int = 32) -> Dict[str, Any]:
        """Register a new display."""
        return await self._request("POST", "/api/displays", {
            "id": display_id,
            "name": name,
            "width": width,
            "height": height,
        })

    async def get_display(self, display_id: str) -> Dict[str, Any]:
        """Get display info."""
        return await self._request("GET", f"/api/displays/{display_id}")

    async def set_brightness(self, display_id: str, brightness: int) -> Dict[str, Any]:
        """Set brightness (0-100)."""
        return await self._request("PUT", f"/api/displays/{display_id}/brightness", {"brightness": brightness})

    async def set_power(self, display_id: str, power: bool) -> Dict[str, Any]:
        """Set power state."""
        return await self._request("PUT", f"/api/displays/{display_id}/power", {"power": power})

    async def skip(self, display_id: str) -> Dict[str, Any]:
        """Skip to next app."""
        return await self._request("POST", f"/api/displays/{display_id}/skip")

    async def get_rotation(self, display_id: str) -> Dict[str, Any]:
        """Get rotation config."""
        return await self._request("GET", f"/api/displays/{display_id}/rotation")

    async def set_rotation_enabled(self, display_id: str, enabled: bool) -> Dict[str, Any]:
        """Enable/disable rotation."""
        return await self._request("PUT", f"/api/displays/{display_id}/rotation", {"enabled": enabled})

    # -------------------------------------------------------------------------
    # Notifications
    # -------------------------------------------------------------------------

    async def push_text(self, text: str, duration: int = 10, color: str = "#FFFFFF") -> Dict[str, Any]:
        """Push text notification."""
        return await self._request("POST", "/api/notify", {
            "text": text,
            "duration": duration,
            "color": color,
        })

    async def show_app(self, app_id: str, duration: int = 30) -> Dict[str, Any]:
        """Show app temporarily."""
        return await self._request("POST", "/api/show", {
            "app_id": app_id,
            "duration": duration,
        })
