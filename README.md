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

## Example Questions

Simple lookups:
- "What are the current NBA standings?"
- "Who leads the league in assists this season?"
- "What's the Lakers roster?"
- "What were today's NBA scores?"

Player deep dives:
- "Compare Steph Curry's home vs away splits this season"
- "Show me LeBron's month-by-month scoring averages this year"
- "How has Jokic's usage rate changed over his career?"
- "What are Luka's stats in clutch situations?"

Multi-tool analytical questions:
- "Which rookie is having the best season by PER?"
- "Who are the top 10 isolation scorers and how efficient are they?"
- "Find all international players averaging 20+ points this season"
- "How do the top 5 assist leaders compare in turnover rate?"
- "Which bench players from the Eastern Conference have the highest +/- this month?"
- "What's the best-performing Duke alumni in the league right now?"

Advanced / tracking data:
- "Who drives to the basket the most per game and what's their efficiency?"
- "Which players lead the league in hustle stats like deflections and loose balls?"
- "How do the top rim protectors compare in contested shots at the rim?"
- "Who are the best catch-and-shoot players by 3PT% with at least 4 attempts per game?"
- "Which players generate the most points as pick-and-roll ball handlers?"

Game-specific analysis:
- "Break down last night's Celtics-Lakers box score — who had the best plus/minus?"
- "Show me Giannis's game log for the last 2 weeks"
- "How have the Warriors performed on the road this season?"
