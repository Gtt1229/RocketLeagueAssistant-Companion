"""Data coordinator for Rocket League Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.event import async_track_time_interval

from .const import CONF_USERNAME, CONF_PLATFORM, CONF_UUID, DOMAIN, PLATFORM_STEAM, PLATFORM_EPIC

_LOGGER = logging.getLogger(__name__)


class RocketLeagueCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Rocket League data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.username = entry.data[CONF_USERNAME]
        self.platform = entry.data[CONF_PLATFORM]
        self.uuid = entry.data[CONF_UUID]
        self.entry = entry
        self.hass = hass
        
        # Try to restore last match data from entry data
        self._last_match_data: dict[str, Any] = entry.data.get("last_match_data", {})
        
        _LOGGER.debug("Initializing RocketLeagueCoordinator for user: %s, platform: %s, UUID: %s", 
                     self.username, self.platform, self.uuid)
        
        if self._last_match_data:
            _LOGGER.debug("Restored previous match data from config entry")
        else:
            _LOGGER.debug("No previous match data found, starting with empty state")
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the webhook."""
        _LOGGER.debug("Updating data for coordinator %s (%s UUID: %s)", 
                     self.username, self.platform, self.uuid)
        # Return the last received data
        return self._last_match_data

    @staticmethod
    def extract_uuid_from_uid(uid: str, platform: str) -> str | None:
        """Extract UUID from platform-specific UID format."""
        _LOGGER.debug("Extracting UUID from UID: %s for platform: %s", uid, platform)
        
        if not uid:
            _LOGGER.debug("UID is empty or None")
            return None
            
        # Format: "PLATFORM|UUID|0"
        # Steam example: "Steam|12345678901234567|0"
        # Epic example: "EPIC|12345678901234567|0"
        
        parts = uid.split("|")
        if len(parts) != 3:
            _LOGGER.debug("UID format invalid, expected 3 parts separated by '|', got %d parts: %s", 
                         len(parts), parts)
            return None
            
        platform_part = parts[0].lower()
        uuid_part = parts[1]
        
        _LOGGER.debug("Parsed UID - Platform: %s, UUID: %s, Suffix: %s", 
                     platform_part, uuid_part, parts[2])
        
        # Check if the platform matches
        if platform == PLATFORM_STEAM and platform_part == "steam":
            _LOGGER.debug("Steam platform match, extracted UUID: %s", uuid_part)
            return uuid_part
        elif platform == PLATFORM_EPIC and platform_part == "epic":
            _LOGGER.debug("Epic platform match, extracted UUID: %s", uuid_part)
            return uuid_part
        else:
            _LOGGER.debug("Platform mismatch - Expected: %s, Got: %s", platform, platform_part)
            
        return None

    @callback
    def update_match_data(self, webhook_data: dict[str, Any]) -> None:
        """Update match data from webhook."""
        _LOGGER.debug("Received webhook data for coordinator %s (%s UUID: %s)", 
                     self.username, self.platform, self.uuid)
        _LOGGER.debug("Webhook data keys: %s", list(webhook_data.keys()) if webhook_data else "None")
        
        player_data = webhook_data.get("MMRData", {}).get("player_data", {})
        received_uid = player_data.get("uid", "")
        
        _LOGGER.debug("Player data from webhook: %s", player_data)
        _LOGGER.debug("Received UID: %s", received_uid)
        
        # Extract UUID from the received UID
        received_uuid = self.extract_uuid_from_uid(received_uid, self.platform)
        _LOGGER.debug("Extracted UUID from webhook: %s", received_uuid)
        _LOGGER.debug("Expected UUID: %s", self.uuid)
        
        if received_uuid == self.uuid:
            self._last_match_data = webhook_data
            
            # Save the data to config entry for persistence across reloads
            self._save_match_data_to_entry(webhook_data)
            
            self.async_set_updated_data(webhook_data)
            _LOGGER.info(
                "✅ Updated match data for %s user %s (UUID: %s)", 
                self.platform.title(), 
                self.username, 
                self.uuid
            )
            _LOGGER.debug("Match data updated with: %s", webhook_data)
        else:
            _LOGGER.debug(
                "❌ Webhook data UUID mismatch for %s user %s. Expected UUID: %s, received UID: %s (extracted UUID: %s)",
                self.platform.title(),
                self.username,
                self.uuid,
                received_uid,
                received_uuid
            )

    def _save_match_data_to_entry(self, webhook_data: dict[str, Any]) -> None:
        """Save match data to config entry for persistence."""
        try:
            # Create new data dict with the last match data
            new_data = dict(self.entry.data)
            new_data["last_match_data"] = webhook_data
            
            # Update the config entry
            self.hass.config_entries.async_update_entry(
                self.entry, 
                data=new_data
            )
            _LOGGER.debug("Saved match data to config entry for persistence")
        except Exception as e:
            _LOGGER.warning("Failed to save match data to config entry: %s", e)

    @property
    def player_data(self) -> dict[str, Any]:
        """Get player data."""
        return self._last_match_data.get("MMRData", {}).get("player_data", {})

    @property
    def current_playlist(self) -> dict[str, Any]:
        """Get current playlist data."""
        return self._last_match_data.get("MMRData", {}).get("current_playlist", {})

    @property
    def ranks(self) -> dict[str, Any]:
        """Get all ranks data."""
        return self._last_match_data.get("MMRData", {}).get("ranks", {})

    @property
    def team_data(self) -> dict[str, Any]:
        """Get team data."""
        return self._last_match_data.get("TeamData", {})