"""Switch entities for Mosaic."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    
    entities = []
    for display_id in coordinator.get_display_ids():
        entities.append(MosaicPowerSwitch(coordinator, display_id))
        entities.append(MosaicRotationSwitch(coordinator, display_id))
    
    async_add_entities(entities)


class MosaicPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Mosaic power switch."""

    def __init__(self, coordinator: MosaicDataUpdateCoordinator, display_id: str) -> None:
        super().__init__(coordinator)
        self._display_id = display_id
        display = coordinator.get_display(display_id)
        self._attr_unique_id = f"mosaic_{display_id}_power"
        self._attr_name = f"{display.get('name', display_id)} Power"
        self._attr_icon = "mdi:power"

    @property
    def _display(self) -> dict:
        return self.coordinator.get_display(self._display_id)

    @property
    def is_on(self) -> bool:
        return self._display.get("power", True)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_power(self._display_id, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_power(self._display_id, False)


class MosaicRotationSwitch(CoordinatorEntity, SwitchEntity):
    """Mosaic rotation switch."""

    def __init__(self, coordinator: MosaicDataUpdateCoordinator, display_id: str) -> None:
        super().__init__(coordinator)
        self._display_id = display_id
        display = coordinator.get_display(display_id)
        self._attr_unique_id = f"mosaic_{display_id}_rotation"
        self._attr_name = f"{display.get('name', display_id)} Rotation"
        self._attr_icon = "mdi:rotate-3d-variant"

    @property
    def _display(self) -> dict:
        return self.coordinator.get_display(self._display_id)

    @property
    def is_on(self) -> bool:
        return self._display.get("rotation_enabled", True)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_rotation_enabled(self._display_id, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_rotation_enabled(self._display_id, False)
