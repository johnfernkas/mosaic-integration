"""Mosaic LED Display integration for Home Assistant."""

import logging
from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import MosaicAPIClient
from .const import CONF_API_KEY, CONF_URL, CONF_VERIFY_SSL, DATA_API, DATA_COORDINATOR, DOMAIN
from .coordinator import MosaicDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: Final = [Platform.LIGHT, Platform.SWITCH, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mosaic from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    api = MosaicAPIClient(
        base_url=entry.data[CONF_URL],
        api_key=entry.data.get(CONF_API_KEY),
        verify_ssl=entry.data.get(CONF_VERIFY_SSL, True),
    )

    coordinator = MosaicDataUpdateCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        DATA_API: api,
        DATA_COORDINATOR: coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_setup_services(hass, entry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Mosaic config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        api = hass.data[DOMAIN][entry.entry_id][DATA_API]
        await api.close()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_setup_services(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up services."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    async def handle_push_text(call) -> None:
        text = call.data.get("text", "")
        duration = call.data.get("duration", 10)
        color = call.data.get("color", "#FFFFFF")
        display_id = call.data.get("display_id")
        await coordinator.async_push_text(text, duration, color, display_id)

    async def handle_skip(call) -> None:
        display_id = call.data.get("display_id")
        await coordinator.async_skip(display_id)

    hass.services.async_register(DOMAIN, "push_text", handle_push_text)
    hass.services.async_register(DOMAIN, "skip", handle_skip)
    _LOGGER.info("Mosaic services registered")
