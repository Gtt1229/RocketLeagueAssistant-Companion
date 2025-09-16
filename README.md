# Rocket League Assistant - Home Assistant Integration

This custom Home Assistant integration allows you to track Rocket League rank data and match results from the [Rocket League Assistant BakkesMod Plugin](https://github.com/Gtt1229/RocketLeagueAssistant/).

![RLABanner](https://github.com/user-attachments/assets/0e1a93d5-99fe-4958-8c1e-f7e671fe2d62)

## Features

- Track MMR, tier, division, and matches played for all competitive playlists
- Monitor current playlist and last match results
- Support for multiple usernames
- Real-time updates via webhook automation
- Individual entities for each rank and playlist

## Installation

### Manual Installation

1. Copy the `custom_components/rocket_league_assistant` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Configuration > Integrations
4. Click the "+" button and search for "Rocket League Assistant"
5. Follow the configuration steps

### HACS Installation

1. Open HACS in Home Assistant
2. Go to Integrations
3. Search for "Rocket League Assistant"
4. Install the integration
5. Restart Home Assistant

## Configuration

When setting up the integration, you'll need to provide:

- **Name**: A friendly name for this instance (default: "Rocket League Assistant")
- **Username**: Your Rocket League username as it appears in the JSON data
- **Platform**: Your gaming platform (Steam or Epic)
- **UUID**: Your platform-specific UUID (You can locate your UUID in the URL when reviewing your stats at https://rocketleague.tracker.network/)

### Finding Your UUID

**Tracker**
You can locate your UUID in the URL when reviewing your stats at https://rocketleague.tracker.network/

**Via JSON Data**
You can find your UID in the JSON data sent by your Rocket League Assistant under `MMRData.player_data.uid`.

## Setting Up with Existing Webhook Automation

If you already have a webhook automation receiving Rocket League data, you can simply add a service call to forward the data to this integration:

### Action YAML

Add this action to your existing webhook automation:

```yaml
- service: rocket_league_assistant.update_match_data
  data:
    json_data: "{{ trigger.json }}"
```

## Entities Created

For each configured username, the integration creates the following entities:

### Rank Entities (per playlist)
- `sensor.{username}_{playlist}_mmr` - Current MMR
- `sensor.{username}_{playlist}_tier` - Current tier (as rank name)
- `sensor.{username}_{playlist}_division` - Current division
- `sensor.{username}_{playlist}_matches_played` - Total matches played
- `sensor.{username}_{playlist}_rank` - Full rank name (e.g., "Diamond II Div 2")

### Match Information
- `sensor.{username}_current_playlist` - Currently active playlist
- `sensor.{username}_last_match_result` - Win/Loss/Tie
- `sensor.{username}_team_score` - Your team's score
- `sensor.{username}_opponent_score` - Opponent team's score

### Supported Playlists
- Solo Duel (1v1)
- Doubles (2v2)
- Standard (3v3)
- Hoops
- Rumble
- Dropshot
- Snow Day
- Tournaments

## Example JSON Data Structure

The integration expects JSON data in this format:

```json
{
  "data": "matchEnded",
  "TeamData": {
    "PlayersTeam": {
      "color": {"r": 24, "g": 115, "b": 255},
      "score": 7
    },
    "OtherTeam": {
      "color": {"r": 194, "g": 100, "b": 24},
      "score": 3
    }
  },
  "MMRData": {
    "player_data": {
      "name": "YourUsername",
      "uid": "Steam|1234567890123456|0"
    },
    "current_playlist": {
      "id": 10,
      "name": "Solo_Duel",
      "mmr": 894,
      "tier": 14,
      "division": 1,
      "matches_played": 2,
      "rank_name": "Diamond II Div 2",
      "is_synced": true
    },
    "ranks": {
      "Solo_Duel": {
        "mmr": 894,
        "tier": 14,
        "division": 1,
        "matches_played": 2,
        "rank_name": "Diamond II Div 2"
      }
      // ... other playlists
    }
  }
}
```

## Dashboard Examples

### (WORK IN PROGRESS) Rank Tracking Card

```yaml
type: entities
title: Rocket League Ranks
entities:
  - sensor.user_doubles_rank
  - sensor.user_doubles_mmr
  - sensor.user_standard_rank
  - sensor.user_standard_mmr
  - sensor.user_solo_duel_rank
  - sensor.user_solo_duel_mmr
```

### Match Results Card
```yaml
type: glance
title: Last Match
entities:
  - sensor.user_current_playlist
  - sensor.user_last_match_result
  - sensor.user_team_score
  - sensor.user_opponent_score
```

## Troubleshooting

### No Data Showing
1. Verify your platform and UUID in the integration configuration matches your UID in the JSON
2. Check that webhook automation is properly configured
3. Ensure the Rocket League Assistant is sending data to the correct webhook URL

### Multiple Users
- Create separate integration instances for each platform/UUID combination
- Each user will have their own set of entities

### Webhook Not Working
1. Check Home Assistant logs for webhook errors
2. Verify the webhook URL is accessible from your Rocket League Assistant
3. Test the webhook manually using curl or Postman

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/gtt1229/RocketLeagueAssistant-Companion).
