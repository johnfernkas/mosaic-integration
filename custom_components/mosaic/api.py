"""API client for Mosaic add-on."""

import aiohttp
import asyncio
import logging
from typing import Any, Dict, Optional
from urllib.parse import urljoin

_LOGGER = logging.getLogger(__name__)


class MosaicAPIError(Exception):
    """Mosaic API error."""

    pass


class MosaicAPIClient:
    """Client for Mosaic add-on API."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, verify_ssl: bool = True):
        """Initialize the API client.

        Args:
            base_url: Base URL of the Mosaic add-on (e.g., http://localhost:8176)
            api_key: Optional API key for authentication
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the session."""
        if self._session:
            await self._session.close()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def _request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an API request."""
        url = urljoin(self.base_url, endpoint)
        session = await self._get_session()

        try:
            async with session.request(
                method,
                url,
                json=data,
                headers=self._get_headers(),
                verify_ssl=self.verify_ssl,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    text = await resp.text()
                    raise MosaicAPIError(f"API error {resp.status}: {text}")
        except asyncio.TimeoutError as e:
            raise MosaicAPIError(f"Request timeout: {e}")
        except aiohttp.ClientError as e:
            raise MosaicAPIError(f"Connection error: {e}")

    async def get_status(self) -> Dict[str, Any]:
        """Get Mosaic status.

        Returns:
            {
                "status": "ok",
                "version": "0.1.0",
                "currentApp": "clock",
                "display": {
                    "width": 64,
                    "height": 32
                }
            }
        """
        return await self._request("GET", "/api/status")

    async def get_displays(self) -> list:
        """Get list of registered displays."""
        result = await self._request("GET", "/api/displays")
        return result.get("displays", []) if isinstance(result, dict) else result

    async def register_display(
        self, display_id: str, name: str, width: int, height: int, client_type: str = "interstate75w"
    ) -> Dict[str, Any]:
        """Register a new display."""
        return await self._request(
            "POST",
            "/api/displays",
            {
                "id": display_id,
                "name": name,
                "width": width,
                "height": height,
                "client_type": client_type,
            },
        )

    async def get_display(self, display_id: str) -> Dict[str, Any]:
        """Get display configuration."""
        return await self._request("GET", f"/api/displays/{display_id}")

    async def update_display(self, display_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update display configuration."""
        return await self._request("PUT", f"/api/displays/{display_id}", data)

    async def get_frame(
        self, display_id: str = "default", format: str = "raw"
    ) -> bytes:
        """Get raw frame data.

        Args:
            display_id: Display ID
            format: Format (raw, webp, gif)

        Returns:
            Raw frame bytes
        """
        url = urljoin(self.base_url, f"/frame?display={display_id}&format={format}")
        session = await self._get_session()

        try:
            async with session.get(
                url,
                headers=self._get_headers(),
                verify_ssl=self.verify_ssl,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    return await resp.read()
                else:
                    raise MosaicAPIError(f"Frame API error {resp.status}")
        except asyncio.TimeoutError as e:
            raise MosaicAPIError(f"Request timeout: {e}")
        except aiohttp.ClientError as e:
            raise MosaicAPIError(f"Connection error: {e}")

    async def push_text(
        self,
        display_id: str,
        text: str,
        duration: int = 10,
        priority: str = "normal",
        color: str = "#FFFFFF",
        font: str = "default",
    ) -> Dict[str, Any]:
        """Push text to display.

        Args:
            display_id: Display ID or "all"
            text: Text to display
            duration: Duration in seconds (0 = sticky)
            priority: Priority level
            color: Text color in hex
            font: Font name
        """
        return await self._request(
            "POST",
            "/api/notify",
            {
                "display": display_id,
                "type": "text",
                "text": text,
                "duration": duration,
                "priority": priority,
                "color": color,
                "font": font,
            },
        )

    async def push_image(
        self, display_id: str, image: str, duration: int = 10, priority: str = "normal"
    ) -> Dict[str, Any]:
        """Push image to display.

        Args:
            display_id: Display ID or "all"
            image: Path or URL to image
            duration: Duration in seconds
            priority: Priority level
        """
        return await self._request(
            "POST",
            "/api/notify",
            {
                "display": display_id,
                "type": "image",
                "image": image,
                "duration": duration,
                "priority": priority,
            },
        )

    async def show_app(
        self, display_id: str, app_id: str, duration: int = 30
    ) -> Dict[str, Any]:
        """Show app temporarily.

        Args:
            display_id: Display ID
            app_id: App ID
            duration: Duration in seconds
        """
        return await self._request(
            "POST",
            f"/api/displays/{display_id}/rotation/show-app",
            {
                "app": app_id,
                "duration": duration,
            },
        )

    async def clear(self, display_id: str) -> Dict[str, Any]:
        """Clear notifications and return to rotation.

        Args:
            display_id: Display ID or "all"
        """
        return await self._request("DELETE", f"/api/notify?display={display_id}")

    async def get_rotation_config(self, display_id: str) -> Dict[str, Any]:
        """Get rotation configuration."""
        return await self._request("GET", f"/api/displays/{display_id}/rotation")

    async def set_brightness(self, display_id: str, brightness: int) -> Dict[str, Any]:
        """Set display brightness.

        Args:
            display_id: Display ID
            brightness: Brightness 0-100
        """
        return await self._request(
            "PUT",
            f"/api/displays/{display_id}",
            {"brightness": brightness},
        )

    async def set_power(self, display_id: str, power: bool) -> Dict[str, Any]:
        """Set display power state.

        Args:
            display_id: Display ID
            power: True to power on, False to power off
        """
        return await self._request(
            "PUT",
            f"/api/displays/{display_id}",
            {"power": power},
        )

    async def set_rotation_enabled(self, display_id: str, enabled: bool) -> Dict[str, Any]:
        """Enable or disable app rotation.

        Args:
            display_id: Display ID
            enabled: True to enable rotation
        """
        return await self._request(
            "PUT",
            f"/api/displays/{display_id}/rotation",
            {"enabled": enabled},
        )

    async def skip_app(self, display_id: str) -> Dict[str, Any]:
        """Skip to next app in rotation."""
        return await self._request("POST", f"/api/displays/{display_id}/rotation/skip")
