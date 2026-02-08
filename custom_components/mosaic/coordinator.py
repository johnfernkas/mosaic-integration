"""Data update coordinator for Mosaic."""

import logging
from datetime import timedelta
from typing import Any, Dict, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import MosaicAPIClient, MosaicAPIError
from .const import DOMAIN, DEFAULT_POLL_INTERVAL

_LOGGER = logging.getLogger(__name__)


class MosaicDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for Mosaic."""

    def __init__(self, hass: HomeAssistant, api: MosaicAPIClient):
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance
            api: Mosaic API client
        """
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_POLL_INTERVAL),
        )
        self.api = api
        self.last_status: Optional[Dict[str, Any]] = None

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data from Mosaic add-on."""
        try:
            data = {
                "status": await self.api.get_status(),
                "displays": await self.api.get_displays(),
            }

            # Get rotation config for each display
            if data["displays"]:
                data["rotation_configs"] = {}
                for display in data["displays"]:
                    try:
                        display_id = display.get("id", "default")
                        data["rotation_configs"][display_id] = (
                            await self.api.get_rotation_config(display_id)
                        )
                    except MosaicAPIError as e:
                        _LOGGER.warning(f"Failed to get rotation config for {display_id}: {e}")

            self.last_status = data
            return data

        except MosaicAPIError as err:
            raise UpdateFailed(f"Error communicating with Mosaic add-on: {err}")
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}")

    async def async_push_text(
        self,
        display_id: str,
        text: str,
        duration: int = 10,
        priority: str = "normal",
        color: str = "#FFFFFF",
        font: str = "default",
    ) -> Dict[str, Any]:
        """Push text to display."""
        try:
            result = await self.api.push_text(
                display_id=display_id,
                text=text,
                duration=duration,
                priority=priority,
                color=color,
                font=font,
            )
            # Refresh data after push
            await self.async_request_refresh()
            return result
        except MosaicAPIError as err:
            raise UpdateFailed(f"Failed to push text: {err}")

    async def async_push_image(
        self, display_id: str, image: str, duration: int = 10, priority: str = "normal"
    ) -> Dict[str, Any]:
        """Push image to display."""
        try:
            result = await self.api.push_image(
                display_id=display_id,
                image=image,
                duration=duration,
                priority=priority,
            )
            await self.async_request_refresh()
            return result
        except MosaicAPIError as err:
            raise UpdateFailed(f"Failed to push image: {err}")

    async def async_show_app(
        self, display_id: str, app_id: str, duration: int = 30
    ) -> Dict[str, Any]:
        """Show app temporarily."""
        try:
            result = await self.api.show_app(
                display_id=display_id,
                app_id=app_id,
                duration=duration,
            )
            await self.async_request_refresh()
            return result
        except MosaicAPIError as err:
            raise UpdateFailed(f"Failed to show app: {err}")

    async def async_clear(self, display_id: str) -> Dict[str, Any]:
        """Clear notifications."""
        try:
            result = await self.api.clear(display_id=display_id)
            await self.async_request_refresh()
            return result
        except MosaicAPIError as err:
            raise UpdateFailed(f"Failed to clear: {err}")

    async def async_set_brightness(self, display_id: str, brightness: int) -> None:
        """Set brightness."""
        try:
            await self.api.set_brightness(display_id, brightness)
            await self.async_request_refresh()
        except MosaicAPIError as err:
            raise UpdateFailed(f"Failed to set brightness: {err}")

    async def async_set_power(self, display_id: str, power: bool) -> None:
        """Set power state."""
        try:
            await self.api.set_power(display_id, power)
            await self.async_request_refresh()
        except MosaicAPIError as err:
            raise UpdateFailed(f"Failed to set power: {err}")

    async def async_set_rotation_enabled(self, display_id: str, enabled: bool) -> None:
        """Set rotation enabled state."""
        try:
            await self.api.set_rotation_enabled(display_id, enabled)
            await self.async_request_refresh()
        except MosaicAPIError as err:
            raise UpdateFailed(f"Failed to set rotation: {err}")
