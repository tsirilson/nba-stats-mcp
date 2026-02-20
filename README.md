# nba-stats-mcp

MCP server providing comprehensive NBA statistics via nba_api. Exposes 15 tools covering player stats, team data, league standings, game scores, and advanced analytics.

## Installation

```bash
pip install nba-stats-mcp
```

## Usage with Claude Code

```bash
claude mcp add nba-stats -- nba-stats-mcp
```

## Available Tools

- **search_players** — Find players by name
- **search_teams** — Find teams by name/abbreviation/city
- **get_player_info** — Player bio, draft info, current team
- **get_player_stats** — Career stats (season-by-season)
- **get_player_game_log** — Game-by-game stats
- **get_player_splits** — Home/away, win/loss, monthly splits
- **get_team_stats** — Year-by-year franchise stats
- **get_team_game_log** — Team game-by-game results
- **get_team_roster** — Current roster with player details
- **get_standings** — League standings
- **get_league_leaders** — Top N players by stat
- **get_league_player_stats** — All players with powerful filters
- **get_game_scores** — Today's/historical game scores
- **get_box_score** — Detailed box score for a game
- **get_advanced_stats** — Tracking, hustle, defense, play type data
