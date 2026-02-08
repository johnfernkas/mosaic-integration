"""Data update coordinator for Mosaic."""

import logging
from datetime import timedelta
from typing import Any, Dict, List

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MosaicAPIClient, MosaicAPIError
from .const import DOMAIN, DEFAULT_POLL_INTERVAL

_LOGGER = logging.getLogger(__name__)


class MosaicDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for Mosaic."""

    def __init__(self, hass: HomeAssistant, api: MosaicAPIClient):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_POLL_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data from Mosaic."""
        try:
            displays = await self.api.get_displays()
            
            # Build display data with rotation info
            display_data = {}
            for disp in displays:
                display_id = disp.get("id", "default")
                try:
                    rotation = await self.api.get_rotation(display_id)
                    disp["rotation"] = rotation
                except MosaicAPIError:
                    disp["rotation"] = {"enabled": True, "apps": []}
                display_data[display_id] = disp
            
            return {"displays": display_data}
        except MosaicAPIError as err:
            raise UpdateFailed(f"Error communicating with Mosaic: {err}")

    def get_display(self, display_id: str) -> Dict[str, Any]:
        """Get display data by ID."""
        displays = self.data.get("displays", {})
        return displays.get(display_id, {})

    def get_display_ids(self) -> List[str]:
        """Get list of display IDs."""
        return list(self.data.get("displays", {}).keys())

    async def async_set_brightness(self, display_id: str, brightness: int) -> None:
        """Set brightness."""
        try:
            await self.api.set_brightness(display_id, brightness)
            await self.async_request_refresh()
        except MosaicAPIError as err:
            _LOGGER.error(f"Failed to set brightness: {err}")

    async def async_set_power(self, display_id: str, power: bool) -> None:
        """Set power state."""
        try:
            await self.api.set_power(display_id, power)
            await self.async_request_refresh()
        except MosaicAPIError as err:
            _LOGGER.error(f"Failed to set power: {err}")

    async def async_set_rotation_enabled(self, display_id: str, enabled: bool) -> None:
        """Set rotation enabled."""
        try:
            await self.api.set_rotation_enabled(display_id, enabled)
            await self.async_request_refresh()
        except MosaicAPIError as err:
            _LOGGER.error(f"Failed to set rotation: {err}")

    async def async_push_text(self, text: str, duration: int = 10, color: str = "#FFFFFF") -> None:
        """Push text notification."""
        try:
            await self.api.push_text(text, duration, color)
        except MosaicAPIError as err:
            _LOGGER.error(f"Failed to push text: {err}")

    async def async_skip(self, display_id: str) -> None:
        """Skip to next app."""
        try:
            await self.api.skip(display_id)
            await self.async_request_refresh()
        except MosaicAPIError as err:
            _LOGGER.error(f"Failed to skip: {err}")
