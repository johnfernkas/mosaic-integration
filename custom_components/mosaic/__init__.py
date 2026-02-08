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

    # Create API client
    api = MosaicAPIClient(
        base_url=entry.data[CONF_URL],
        api_key=entry.data.get(CONF_API_KEY),
        verify_ssl=entry.data.get(CONF_VERIFY_SSL, True),
    )

    # Create coordinator
    coordinator = MosaicDataUpdateCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    # Store references
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_API: api,
        DATA_COORDINATOR: coordinator,
    }

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    await async_setup_services(hass, entry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Mosaic config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Close API client
        api = hass.data[DOMAIN][entry.entry_id][DATA_API]
        await api.close()

        # Remove data
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_setup_services(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up services for Mosaic."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    async def handle_push_text(call) -> None:
        """Handle push_text service call."""
        target = call.data.get("target", "all")
        text = call.data.get("text", "")
        duration = call.data.get("duration", 10)
        priority = call.data.get("priority", "normal")
        color = call.data.get("color", "#FFFFFF")
        font = call.data.get("font", "default")

        _LOGGER.info(f"Pushing text to {target}: {text}")
        await coordinator.async_push_text(
            display_id=target,
            text=text,
            duration=duration,
            priority=priority,
            color=color,
            font=font,
        )

    async def handle_push_image(call) -> None:
        """Handle push_image service call."""
        target = call.data.get("target", "all")
        image = call.data.get("image", "")
        duration = call.data.get("duration", 10)
        priority = call.data.get("priority", "normal")

        _LOGGER.info(f"Pushing image to {target}")
        await coordinator.async_push_image(
            display_id=target,
            image=image,
            duration=duration,
            priority=priority,
        )

    async def handle_show_app(call) -> None:
        """Handle show_app service call."""
        target = call.data.get("target")
        app = call.data.get("app")
        duration = call.data.get("duration", 30)

        if not target or not app:
            _LOGGER.error("show_app requires target and app parameters")
            return

        _LOGGER.info(f"Showing app {app} on {target}")
        await coordinator.async_show_app(
            display_id=target,
            app_id=app,
            duration=duration,
        )

    async def handle_clear(call) -> None:
        """Handle clear service call."""
        target = call.data.get("target", "all")

        _LOGGER.info(f"Clearing notifications on {target}")
        await coordinator.async_clear(display_id=target)

    # Register services
    hass.services.async_register(
        DOMAIN,
        "push_text",
        handle_push_text,
        schema=None,  # Defined in services.yaml
    )

    hass.services.async_register(
        DOMAIN,
        "push_image",
        handle_push_image,
        schema=None,
    )

    hass.services.async_register(
        DOMAIN,
        "show_app",
        handle_show_app,
        schema=None,
    )

    hass.services.async_register(
        DOMAIN,
        "clear",
        handle_clear,
        schema=None,
    )

    _LOGGER.info("Mosaic services registered")
