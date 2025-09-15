"""Config flow for Rocket League Assistant integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_USERNAME, CONF_PLATFORM, CONF_UUID, DEFAULT_NAME, DOMAIN, PLATFORMS_LIST

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PLATFORM): vol.In(PLATFORMS_LIST),
        vol.Required(CONF_UUID): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rocket League Assistant."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        _LOGGER.debug("Config flow started with user_input: %s", user_input)
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                _LOGGER.debug("Processing config flow input for user: %s, platform: %s, UUID: %s", 
                             user_input.get(CONF_USERNAME), 
                             user_input.get(CONF_PLATFORM), 
                             user_input.get(CONF_UUID))
                
                # Use platform and UUID for unique identification
                unique_id = f"{user_input[CONF_PLATFORM]}_{user_input[CONF_UUID]}"
                _LOGGER.debug("Generated unique_id: %s", unique_id)
                
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                
                _LOGGER.info("Creating config entry for %s (%s) with UUID: %s", 
                            user_input[CONF_USERNAME], 
                            user_input[CONF_PLATFORM], 
                            user_input[CONF_UUID])
                
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during config flow setup")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""