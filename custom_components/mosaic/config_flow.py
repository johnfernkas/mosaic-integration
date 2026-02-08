"""Config flow for Mosaic integration."""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_URL
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MosaicAPIClient, MosaicAPIError
from .const import CONF_API_KEY, CONF_AUTO_DETECT, CONF_VERIFY_SSL, DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_AUTO_DETECT, default=True): bool,
    }
)

STEP_MANUAL_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): str,
        vol.Optional(CONF_API_KEY): str,
        vol.Optional(CONF_VERIFY_SSL, default=True): bool,
    }
)


class MosaicConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Mosaic."""

    VERSION = 1

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)

        # Check if already configured
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input.get(CONF_AUTO_DETECT, True):
            return await self.async_step_auto_detect()
        else:
            return await self.async_step_manual()

    async def async_step_auto_detect(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Try to auto-detect the add-on."""
        if user_input is None:
            # Try common URLs
            for url in [
                "http://a0d7b954-mosaic:8176",  # Standard HA add-on DNS
                "http://localhost:8176",
                "http://127.0.0.1:8176",
            ]:
                try:
                    api = MosaicAPIClient(url)
                    status = await api.get_status()
                    await api.close()

                    _LOGGER.info(f"Auto-detected Mosaic at {url}")
                    return self.async_create_entry(
                        title=DEFAULT_NAME,
                        data={
                            CONF_URL: url,
                            CONF_API_KEY: None,
                            CONF_VERIFY_SSL: True,
                        },
                    )
                except MosaicAPIError:
                    continue

            _LOGGER.warning("Could not auto-detect Mosaic add-on")
            return await self.async_step_manual()

    async def async_step_manual(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle manual configuration."""
        errors = {}

        if user_input is not None:
            # Validate the connection
            try:
                api = MosaicAPIClient(
                    base_url=user_input[CONF_URL],
                    api_key=user_input.get(CONF_API_KEY),
                    verify_ssl=user_input.get(CONF_VERIFY_SSL, True),
                )
                status = await api.get_status()
                await api.close()

                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, DEFAULT_NAME),
                    data=user_input,
                )
            except MosaicAPIError as e:
                errors["base"] = "cannot_connect"
                _LOGGER.error(f"Failed to connect to Mosaic: {e}")
            except Exception as e:
                errors["base"] = "unknown"
                _LOGGER.error(f"Unexpected error: {e}")

        return self.async_show_form(
            step_id="manual",
            data_schema=STEP_MANUAL_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return options flow."""
        return MosaicOptionsFlowHandler(config_entry)


class MosaicOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for Mosaic."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle options."""
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_URL,
                        default=self.config_entry.data.get(CONF_URL),
                    ): str,
                    vol.Optional(
                        CONF_API_KEY,
                        default=self.config_entry.data.get(CONF_API_KEY, ""),
                    ): str,
                    vol.Optional(
                        CONF_VERIFY_SSL,
                        default=self.config_entry.data.get(CONF_VERIFY_SSL, True),
                    ): bool,
                }
            ),
        )

    async def async_step_init_submit(self, user_input: Dict[str, Any]) -> FlowResult:
        """Handle options submission."""
        return self.async_abort(reason="reconfigure_successful")
