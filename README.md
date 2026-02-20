# nba-stats-mcp

> MCP server that gives Claude deep access to NBA statistics — powered by [nba_api](https://github.com/swar/nba_api).

15 tools covering player stats, team data, league standings, game scores, and advanced analytics. Ask Claude anything about the NBA and it will pull live data from NBA.com to answer.

---

## What You Can Ask

### Quick Lookups
> *"What are the current NBA standings?"*
> *"Who leads the league in assists this season?"*
> *"What's the Lakers roster?"*
> *"What were today's NBA scores?"*

### Player Deep Dives
> *"Compare Steph Curry's home vs away splits this season"*
> *"Show me LeBron's month-by-month scoring averages this year"*
> *"How has Jokic's usage rate changed over his career?"*
> *"What are Luka's stats in clutch situations?"*

### Multi-Tool Analytical Questions
> *"Which rookie is having the best season by PER?"*
> *"Who are the top 10 isolation scorers and how efficient are they?"*
> *"Find all international players averaging 20+ points this season"*
> *"How do the top 5 assist leaders compare in turnover rate?"*
> *"Which bench players from the Eastern Conference have the highest +/- this month?"*
> *"What's the best-performing Duke alumni in the league right now?"*

### Advanced & Tracking Data
> *"Who drives to the basket the most per game and what's their efficiency?"*
> *"Which players lead the league in hustle stats like deflections and loose balls?"*
> *"How do the top rim protectors compare in contested shots at the rim?"*
> *"Who are the best catch-and-shoot players by 3PT% with at least 4 attempts per game?"*
> *"Which players generate the most points as pick-and-roll ball handlers?"*

### Game Analysis
> *"Break down last night's Celtics-Lakers box score — who had the best plus/minus?"*
> *"Show me Giannis's game log for the last 2 weeks"*
> *"How have the Warriors performed on the road this season?"*

---

## Installation

```bash
pip install nba-stats-mcp
```

## Usage with Claude Code

```bash
claude mcp add nba-stats -- nba-stats-mcp
```

---

## Available Tools

| Tool | Description |
|------|-------------|
| `search_players` | Find players by name (fuzzy matching) |
| `search_teams` | Find teams by name, abbreviation, or city |
| `get_player_info` | Player bio, draft info, current team |
| `get_player_stats` | Career stats — season-by-season + totals |
| `get_player_game_log` | Game-by-game stats for a season |
| `get_player_splits` | Home/away, win/loss, monthly, starter/bench splits |
| `get_team_stats` | Year-by-year franchise stats |
| `get_team_game_log` | Team game-by-game results |
| `get_team_roster` | Roster with positions, heights, weights |
| `get_standings` | League standings with records and streaks |
| `get_league_leaders` | Top N players ranked by any stat |
| `get_league_player_stats` | All players with 20+ filters (position, college, country, draft, clutch, etc.) |
| `get_game_scores` | Live scores or any date's results |
| `get_box_score` | Full box score with optional advanced stats |
| `get_advanced_stats` | Player tracking, hustle, defense, and play type data |

---

## License

MIT
