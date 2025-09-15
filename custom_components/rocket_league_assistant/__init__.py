"""The Rocket League Assistant integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .coordinator import RocketLeagueCoordinator
from .services import async_setup_services, async_unload_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Rocket League Assistant component."""
    _LOGGER.debug("Setting up Rocket League Assistant integration")
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Rocket League Assistant from a config entry."""
    _LOGGER.info("Setting up Rocket League Assistant entry: %s", entry.title)
    _LOGGER.debug("Entry data: %s", {k: v for k, v in entry.data.items() if k != "uuid"})  # Don't log UUID
    
    coordinator = RocketLeagueCoordinator(hass, entry)
    
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    _LOGGER.debug("Added coordinator to hass.data with entry_id: %s", entry.entry_id)
    
    # Set up services if this is the first entry
    if len(hass.data[DOMAIN]) == 1:
        _LOGGER.debug("First entry, setting up services")
        await async_setup_services(hass)
    else:
        _LOGGER.debug("Additional entry, services already set up. Total entries: %d", len(hass.data[DOMAIN]))
    
    _LOGGER.debug("Setting up platforms: %s", PLATFORMS)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    _LOGGER.info("Successfully set up Rocket League Assistant entry: %s", entry.title)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading Rocket League Assistant entry: %s", entry.title)
    
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.debug("Removed coordinator for entry_id: %s", entry.entry_id)
        
        # Remove services if this was the last entry
        if not hass.data[DOMAIN]:
            _LOGGER.debug("Last entry removed, unloading services")
            await async_unload_services(hass)
        else:
            _LOGGER.debug("Other entries remain, keeping services. Remaining entries: %d", len(hass.data[DOMAIN]))
    else:
        _LOGGER.error("Failed to unload platforms for entry: %s", entry.title)
    
    return unload_ok