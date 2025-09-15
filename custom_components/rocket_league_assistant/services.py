"""Services for Rocket League Assistant integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SERVICE_UPDATE_MATCH_DATA = "update_match_data"

UPDATE_MATCH_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional("data"): str,
        vol.Optional("TeamData"): dict,
        vol.Optional("MMRData"): dict,
        vol.Optional("json_data"): dict,  # Accept full JSON payload
    }
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the Rocket League Assistant integration."""
    _LOGGER.debug("Setting up Rocket League Assistant services")

    async def handle_update_match_data(call: ServiceCall) -> None:
        """Handle the update_match_data service call."""
        _LOGGER.debug("Service call received with data keys: %s", list(call.data.keys()))
        
        # Support both individual fields and full JSON payload
        if "json_data" in call.data:
            # Full JSON payload provided
            webhook_data = call.data["json_data"]
            _LOGGER.debug("Using full JSON payload from service call")
        else:
            # Individual fields provided (backward compatibility)
            webhook_data = {
                "data": call.data.get("data"),
                "TeamData": call.data.get("TeamData", {}),
                "MMRData": call.data.get("MMRData", {}),
            }
            _LOGGER.debug("Using individual fields from service call")
        
        _LOGGER.debug("Webhook data to process: %s", webhook_data)
        _LOGGER.debug("Available coordinators: %s", list(hass.data[DOMAIN].keys()) if DOMAIN in hass.data else "None")
        
        # Update all coordinators with the new data
        updated_count = 0
        for entry_id, coordinator in hass.data[DOMAIN].items():
            _LOGGER.debug("Processing coordinator %s: %s", entry_id, type(coordinator).__name__)
            if hasattr(coordinator, 'update_match_data'):
                coordinator.update_match_data(webhook_data)
                updated_count += 1
                _LOGGER.debug("Updated coordinator %s with webhook data", entry_id)
            else:
                _LOGGER.warning("Coordinator %s does not have update_match_data method", entry_id)
        
        _LOGGER.info("Updated %d Rocket League coordinators with match data", updated_count)
        if updated_count == 0:
            _LOGGER.warning("No coordinators were updated - check your platform/UUID configuration")

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_MATCH_DATA,
        handle_update_match_data,
        schema=UPDATE_MATCH_DATA_SCHEMA,
    )
    _LOGGER.info("Rocket League Assistant service registered: %s.%s", DOMAIN, SERVICE_UPDATE_MATCH_DATA)


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services for the Rocket League Assistant integration."""
    _LOGGER.debug("Unloading Rocket League Assistant services")
    hass.services.async_remove(DOMAIN, SERVICE_UPDATE_MATCH_DATA)
    _LOGGER.info("Rocket League Assistant service unregistered: %s.%s", DOMAIN, SERVICE_UPDATE_MATCH_DATA)