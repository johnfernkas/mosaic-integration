"""Light entity for Mosaic brightness control."""

import logging
from typing import Any

from homeassistant.components.light import ColorMode, LightEntity, LightEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_BRIGHTNESS, DATA_COORDINATOR, DOMAIN
from .coordinator import MosaicDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up light entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    # Get displays from coordinator data
    displays = coordinator.data.get("displays", [])
    entities = [
        MosaicLight(coordinator, display) for display in displays
    ]

    async_add_entities(entities)


class MosaicLight(CoordinatorEntity, LightEntity):
    """Mosaic brightness light entity."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_supported_features = LightEntityFeature.BRIGHTNESS

    def __init__(self, coordinator: MosaicDataUpdateCoordinator, display: dict) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self.display = display
        self._display_id = display.get("id", "default")
        self._display_name = display.get("name", "Mosaic")

        self._attr_unique_id = f"mosaic_light_{self._display_id}"
        self._attr_name = f"{self._display_name}"
        self._attr_device_name = self._display_name

    @property
    def brightness(self) -> int | None:
        """Return the brightness."""
        return self.display.get("brightness", 100)

    @property
    def is_on(self) -> bool:
        """Return True if light is on."""
        return self.display.get("power", True)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        brightness = kwargs.get("brightness", 100)
        await self.coordinator.async_set_brightness(self._display_id, brightness)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        # Turn off by setting brightness to 0 or power to false
        await self.coordinator.async_set_power(self._display_id, False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            "display_id": self._display_id,
            "width": self.display.get("width", "unknown"),
            "height": self.display.get("height", "unknown"),
        }
