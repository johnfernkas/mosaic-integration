"""Light entities for Mosaic brightness control."""

import logging
from typing import Any

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import MosaicDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up light entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    
    entities = [
        MosaicLight(coordinator, display_id)
        for display_id in coordinator.get_display_ids()
    ]
    async_add_entities(entities)


class MosaicLight(CoordinatorEntity, LightEntity):
    """Mosaic brightness light entity."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(self, coordinator: MosaicDataUpdateCoordinator, display_id: str) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self._display_id = display_id
        display = coordinator.get_display(display_id)
        self._attr_unique_id = f"mosaic_{display_id}"
        self._attr_name = display.get("name", f"Mosaic {display_id}")

    @property
    def _display(self) -> dict:
        return self.coordinator.get_display(self._display_id)

    @property
    def brightness(self) -> int | None:
        """Return the brightness (0-255 for HA)."""
        brightness = self._display.get("brightness", 80)
        return int(brightness * 255 / 100)

    @property
    def is_on(self) -> bool:
        """Return True if on."""
        return self._display.get("power", True)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on."""
        if "brightness" in kwargs:
            brightness = int(kwargs["brightness"] * 100 / 255)
            await self.coordinator.async_set_brightness(self._display_id, brightness)
        if not self.is_on:
            await self.coordinator.async_set_power(self._display_id, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""
        await self.coordinator.async_set_power(self._display_id, False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            "display_id": self._display_id,
            "current_app": self._display.get("current_app", ""),
            "rotation_enabled": self._display.get("rotation_enabled", True),
            "width": self._display.get("width"),
            "height": self._display.get("height"),
        }
