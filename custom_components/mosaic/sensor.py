"""Sensor entities for Mosaic."""

import logging

from homeassistant.components.sensor import SensorEntity
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
    """Set up sensor entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    
    entities = [
        MosaicCurrentAppSensor(coordinator, display_id)
        for display_id in coordinator.get_display_ids()
    ]
    async_add_entities(entities)


class MosaicCurrentAppSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing current app."""

    def __init__(self, coordinator: MosaicDataUpdateCoordinator, display_id: str) -> None:
        super().__init__(coordinator)
        self._display_id = display_id
        display = coordinator.get_display(display_id)
        self._attr_unique_id = f"mosaic_{display_id}_app"
        self._attr_name = f"{display.get('name', display_id)} Current App"
        self._attr_icon = "mdi:application"

    @property
    def _display(self) -> dict:
        return self.coordinator.get_display(self._display_id)

    @property
    def native_value(self) -> str:
        return self._display.get("current_app", "unknown")

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "display_id": self._display_id,
            "brightness": self._display.get("brightness"),
            "power": self._display.get("power"),
            "rotation_enabled": self._display.get("rotation_enabled"),
            "width": self._display.get("width"),
            "height": self._display.get("height"),
        }
