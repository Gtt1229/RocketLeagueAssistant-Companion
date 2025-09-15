"""Constants for the Rocket League Assistant integration."""

DOMAIN = "rocket_league_assistant"

# Configuration constants
CONF_USERNAME = "username"
CONF_WEBHOOK_ID = "webhook_id"
CONF_PLATFORM = "platform"
CONF_UUID = "uuid"

# Platform constants
PLATFORM_STEAM = "steam"
PLATFORM_EPIC = "epic"
PLATFORMS_LIST = [PLATFORM_STEAM, PLATFORM_EPIC]

# Default values
DEFAULT_NAME = "Rocket League Assistant"

# Rocket League playlists
PLAYLISTS = {
    "Solo_Duel": "1v1",
    "Doubles": "2v2", 
    "Standard": "3v3",
    "Hoops": "Hoops",
    "Rumble": "Rumble",
    "Dropshot": "Dropshot",
    "Snow_Day": "Snow Day",
    "Tournaments": "Tournaments"
}

# Rank tiers mapping
RANK_TIERS = {
    0: "Unranked",
    1: "Bronze I",
    2: "Bronze II", 
    3: "Bronze III",
    4: "Silver I",
    5: "Silver II",
    6: "Silver III",
    7: "Gold I",
    8: "Gold II",
    9: "Gold III", 
    10: "Platinum I",
    11: "Platinum II",
    12: "Platinum III",
    13: "Diamond I",
    14: "Diamond II",
    15: "Diamond III",
    16: "Champion I",
    17: "Champion II",
    18: "Champion III",
    19: "Grand Champion I",
    20: "Grand Champion II",
    21: "Grand Champion III",
    22: "Supersonic Legend"
}