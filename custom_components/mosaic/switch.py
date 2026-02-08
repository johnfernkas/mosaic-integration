"""Switch entities for Mosaic display control."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityFeature
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
    """Set up switch entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    # Get displays from coordinator data
    displays = coordinator.data.get("displays", [])
    entities = []

    for display in displays:
        display_id = display.get("id", "default")
        display_name = display.get("name", "Mosaic")

        # Power switch
        entities.append(MosaicPowerSwitch(coordinator, display))

        # Rotation switch
        entities.append(MosaicRotationSwitch(coordinator, display))

    async_add_entities(entities)


class MosaicPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Switch for display power control."""

    def __init__(self, coordinator: MosaicDataUpdateCoordinator, display: dict) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.display = display
        self._display_id = display.get("id", "default")
        self._display_name = display.get("name", "Mosaic")

        self._attr_unique_id = f"mosaic_power_{self._display_id}"
        self._attr_name = f"{self._display_name} Power"
        self._attr_device_name = self._display_name

    @property
    def is_on(self) -> bool:
        """Return True if display is powered on."""
        return self.display.get("power", True)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the display."""
        await self.coordinator.async_set_power(self._display_id, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the display."""
        await self.coordinator.async_set_power(self._display_id, False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            "display_id": self._display_id,
        }


class MosaicRotationSwitch(CoordinatorEntity, SwitchEntity):
    """Switch for app rotation control."""

    def __init__(self, coordinator: MosaicDataUpdateCoordinator, display: dict) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.display = display
        self._display_id = display.get("id", "default")
        self._display_name = display.get("name", "Mosaic")

        self._attr_unique_id = f"mosaic_rotation_{self._display_id}"
        self._attr_name = f"{self._display_name} Rotation"
        self._attr_device_name = self._display_name

    @property
    def is_on(self) -> bool:
        """Return True if rotation is enabled."""
        rotation_config = self.coordinator.data.get("rotation_configs", {}).get(
            self._display_id, {}
        )
        return rotation_config.get("enabled", True)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable rotation."""
        await self.coordinator.async_set_rotation_enabled(self._display_id, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable rotation."""
        await self.coordinator.async_set_rotation_enabled(self._display_id, False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        rotation_config = self.coordinator.data.get("rotation_configs", {}).get(
            self._display_id, {}
        )
        return {
            "display_id": self._display_id,
            "dwell_seconds": rotation_config.get("dwell_seconds", "unknown"),
            "app_count": len(rotation_config.get("apps", [])),
        }
