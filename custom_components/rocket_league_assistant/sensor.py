"""Sensor platform for Rocket League Assistant."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PLAYLISTS, RANK_TIERS
from .coordinator import RocketLeagueCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Rocket League Assistant sensors."""
    _LOGGER.debug("Setting up sensors for entry: %s", config_entry.title)
    
    coordinator: RocketLeagueCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    _LOGGER.debug("Retrieved coordinator for user: %s (%s UUID: %s)", 
                 coordinator.username, coordinator.platform, coordinator.uuid)
    
    entities = []
    
    # Create rank sensors for each playlist
    for playlist_key in PLAYLISTS:
        entities.extend([
            RocketLeagueRankSensor(
                coordinator,
                config_entry,
                playlist_key,
                "mmr",
                "MMR",
                SensorDeviceClass.VOLTAGE,  # Using voltage as a numeric device class
                SensorStateClass.MEASUREMENT
            ),
            RocketLeagueRankSensor(
                coordinator,
                config_entry,
                playlist_key,
                "tier",
                "Tier",
                None,
                None
            ),
            RocketLeagueRankSensor(
                coordinator,
                config_entry,
                playlist_key,
                "division",
                "Division",
                None,
                None
            ),
            RocketLeagueRankSensor(
                coordinator,
                config_entry,
                playlist_key,
                "matches_played",
                "Matches Played",
                None,
                SensorStateClass.TOTAL_INCREASING
            ),
            RocketLeagueRankSensor(
                coordinator,
                config_entry,
                playlist_key,
                "rank_name",
                "Rank",
                None,
                None
            ),
        ])
    
    # Add current match sensors
    entities.extend([
        CurrentPlaylistSensor(coordinator, config_entry),
        LastMatchResultSensor(coordinator, config_entry),
        PlayerTeamScoreSensor(coordinator, config_entry),
        OpponentTeamScoreSensor(coordinator, config_entry),
    ])
    
    _LOGGER.debug("Created %d entities for user %s", len(entities), coordinator.username)
    
    async_add_entities(entities)
    _LOGGER.info("Successfully set up %d sensors for %s (%s)", 
                len(entities), coordinator.username, coordinator.platform)


class RocketLeagueBaseSensor(CoordinatorEntity[RocketLeagueCoordinator], SensorEntity):
    """Base class for Rocket League sensors."""

    def __init__(
        self,
        coordinator: RocketLeagueCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=f"Rocket League Assistant - {coordinator.username} ({coordinator.platform.title()})",
            manufacturer="Rocket League Assistant",
            model=f"Player Stats - {coordinator.platform.title()}",
        )


class RocketLeagueRankSensor(RocketLeagueBaseSensor):
    """Sensor for individual rank attributes."""

    def __init__(
        self,
        coordinator: RocketLeagueCoordinator,
        config_entry: ConfigEntry,
        playlist: str,
        attribute: str,
        attribute_name: str,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
    ) -> None:
        """Initialize the rank sensor."""
        super().__init__(coordinator, config_entry)
        self.playlist = playlist
        self.attribute = attribute
        self._attr_name = f"{coordinator.username} {PLAYLISTS.get(playlist, playlist)} {attribute_name}"
        self._attr_unique_id = f"{config_entry.entry_id}_{playlist}_{attribute}"
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        
        # Set icon based on attribute type
        if attribute == "mmr":
            self._attr_icon = "mdi:trophy"
        elif attribute == "tier":
            self._attr_icon = "mdi:medal"
        elif attribute == "division":
            self._attr_icon = "mdi:numeric"
        elif attribute == "matches_played":
            self._attr_icon = "mdi:counter"
        elif attribute == "rank_name":
            self._attr_icon = "mdi:crown"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        super()._handle_coordinator_update()

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        ranks = self.coordinator.ranks
        if self.playlist not in ranks:
            return None
            
        playlist_data = ranks[self.playlist]
        value = playlist_data.get(self.attribute)
        
        # Return raw value without conversion
        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        ranks = self.coordinator.ranks
        if self.playlist not in ranks:
            return {}
            
        playlist_data = ranks[self.playlist]
        return {
            "playlist": self.playlist,
            "playlist_display_name": PLAYLISTS.get(self.playlist, self.playlist),
            "is_synced": playlist_data.get("is_synced", False),
            "platform": self.coordinator.platform,
            "uuid": self.coordinator.uuid,
        }


class CurrentPlaylistSensor(RocketLeagueBaseSensor):
    """Sensor for the current playlist being played."""

    def __init__(
        self,
        coordinator: RocketLeagueCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the current playlist sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_name = f"{coordinator.username} Current Playlist"
        self._attr_unique_id = f"{config_entry.entry_id}_current_playlist"
        self._attr_icon = "mdi:gamepad-variant"

    @property
    def native_value(self) -> str | None:
        """Return the current playlist name."""
        current = self.coordinator.current_playlist
        playlist_name = current.get("name")
        return PLAYLISTS.get(playlist_name, playlist_name) if playlist_name else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        current = self.coordinator.current_playlist
        return {
            "playlist_id": current.get("id"),
            "mmr": current.get("mmr"),
            "tier": current.get("tier"),
            "division": current.get("division"),
            "rank_name": current.get("rank_name"),
            "matches_played": current.get("matches_played"),
            "is_synced": current.get("is_synced"),
            "platform": self.coordinator.platform,
            "uuid": self.coordinator.uuid,
        }


class LastMatchResultSensor(RocketLeagueBaseSensor):
    """Sensor for the last match result."""

    def __init__(
        self,
        coordinator: RocketLeagueCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the match result sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_name = f"{coordinator.username} Last Match Result"
        self._attr_unique_id = f"{config_entry.entry_id}_match_result"
        self._attr_icon = "mdi:soccer"

    @property
    def native_value(self) -> str | None:
        """Return the match result."""
        team_data = self.coordinator.team_data
        if not team_data:
            return None
            
        player_score = team_data.get("PlayersTeam", {}).get("score", 0)
        other_score = team_data.get("OtherTeam", {}).get("score", 0)
        
        if player_score > other_score:
            return "Win"
        elif player_score < other_score:
            return "Loss"
        else:
            return "Tie"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        team_data = self.coordinator.team_data
        if not team_data:
            return {}
            
        return {
            "player_team_score": team_data.get("PlayersTeam", {}).get("score"),
            "other_team_score": team_data.get("OtherTeam", {}).get("score"),
            "player_team_color": team_data.get("PlayersTeam", {}).get("color"),
            "other_team_color": team_data.get("OtherTeam", {}).get("color"),
            "platform": self.coordinator.platform,
            "uuid": self.coordinator.uuid,
        }


class PlayerTeamScoreSensor(RocketLeagueBaseSensor):
    """Sensor for player team score."""

    def __init__(
        self,
        coordinator: RocketLeagueCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the player team score sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_name = f"{coordinator.username} Team Score"
        self._attr_unique_id = f"{config_entry.entry_id}_team_score"
        self._attr_icon = "mdi:counter"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return the player team score."""
        team_data = self.coordinator.team_data
        return team_data.get("PlayersTeam", {}).get("score") if team_data else None


class OpponentTeamScoreSensor(RocketLeagueBaseSensor):
    """Sensor for opponent team score."""

    def __init__(
        self,
        coordinator: RocketLeagueCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the opponent team score sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_name = f"{coordinator.username} Opponent Score"
        self._attr_unique_id = f"{config_entry.entry_id}_opponent_score"
        self._attr_icon = "mdi:counter"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return the opponent team score."""
        team_data = self.coordinator.team_data
        return team_data.get("OtherTeam", {}).get("score") if team_data else None