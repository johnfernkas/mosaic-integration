"""Sensor entities for Mosaic display status."""

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DOMAIN, STATUS_CONNECTED, STATUS_DISCONNECTED
from .coordinator import MosaicDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    # Get displays from coordinator data
    displays = coordinator.data.get("displays", [])
    entities = [MosaicStatusSensor(coordinator, display) for display in displays]

    async_add_entities(entities)


class MosaicStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor for display connection status."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: MosaicDataUpdateCoordinator, display: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.display = display
        self._display_id = display.get("id", "default")
        self._display_name = display.get("name", "Mosaic")

        self._attr_unique_id = f"mosaic_status_{self._display_id}"
        self._attr_name = f"{self._display_name} Status"
        self._attr_device_name = self._display_name

    @property
    def native_value(self) -> str:
        """Return the current status."""
        # Check if display is connected by checking if it exists in latest data
        displays = self.coordinator.data.get("displays", [])
        for d in displays:
            if d.get("id") == self._display_id:
                return STATUS_CONNECTED

        return STATUS_DISCONNECTED

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        displays = self.coordinator.data.get("displays", [])
        for d in displays:
            if d.get("id") == self._display_id:
                return {
                    "display_id": self._display_id,
                    "width": d.get("width", "unknown"),
                    "height": d.get("height", "unknown"),
                    "brightness": d.get("brightness", "unknown"),
                    "power": d.get("power", "unknown"),
                }

        return {
            "display_id": self._display_id,
        }
