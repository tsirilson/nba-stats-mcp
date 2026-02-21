"""League-wide tools: standings, leaders, league player stats."""

from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations

from nba_stats_mcp.server import mcp
from nba_stats_mcp.helpers import rate_limit, df_to_records, API_TIMEOUT


@mcp.tool(
    annotations=ToolAnnotations(readOnlyHint=True),
    title="Get Standings",
)
def get_standings(
    season: str = "2025-26",
    season_type: str = "Regular Season",
) -> list[dict]:
    """Get NBA standings with records, streaks, and conference/division ranks.

    Args:
        season: Season string (e.g. "2025-26")
        season_type: "Regular Season" or "Playoffs"

    Returns:
        Full standings for all teams.
    """
    from nba_api.stats.endpoints import LeagueStandingsV3

    try:
        rate_limit()
        standings = LeagueStandingsV3(
            season=season,
            season_type=season_type,
            timeout=API_TIMEOUT,
        )
        df = standings.get_data_frames()[0]
        return df_to_records(df, max_rows=30)
    except Exception as e:
        raise ToolError(f"Failed to get standings: {e}")


@mcp.tool(
    annotations=ToolAnnotations(readOnlyHint=True),
    title="Get League Leaders",
)
def get_league_leaders(
    stat: str = "PTS",
    season: str = "2025-26",
    per_mode: str = "PerGame",
    season_type: str = "Regular Season",
    top_n: int = 25,
) -> list[dict]:
    """Get the league's top players ranked by a specific stat.

    Args:
        stat: Stat category to rank by (e.g. "PTS", "AST", "REB", "STL", "BLK", "FG_PCT", "FT_PCT", "FG3M", "EFF")
        season: Season string (e.g. "2025-26")
        per_mode: "PerGame", "Totals", or "Per48"
        season_type: "Regular Season" or "Playoffs"
        top_n: Number of leaders to return (default 25, max 100)

    Returns:
        Top N players ranked by the chosen stat.
    """
    from nba_api.stats.endpoints import LeagueLeaders

    try:
        rate_limit()
        leaders = LeagueLeaders(
            stat_category_abbreviation=stat,
            season=season,
            per_mode48=per_mode,
            season_type_all_star=season_type,
            timeout=API_TIMEOUT,
        )
        df = leaders.get_data_frames()[0]
        top_n = min(top_n, 100)
        return df_to_records(df, max_rows=top_n)
    except Exception as e:
        raise ToolError(f"Failed to get league leaders: {e}")


@mcp.tool(
    annotations=ToolAnnotations(readOnlyHint=True),
    title="Get League Player Stats",
)
def get_league_player_stats(
    season: str = "2025-26",
    measure_type: str = "Base",
    per_mode: str = "PerGame",
    season_type: str = "Regular Season",
    player_position: str = "",
    conference: str = "",
    division: str = "",
    starter_bench: str = "",
    player_experience: str = "",
    college: str = "",
    country: str = "",
    draft_year: str = "",
    draft_pick: str = "",
    height: str = "",
    weight: str = "",
    last_n_games: int = 0,
    month: int = 0,
    opponent_team_id: int = 0,
    outcome: str = "",
    location: str = "",
    shot_clock_range: str = "",
    top_n: int = 75,
) -> list[dict]:
    """Get stats for all players in the league with powerful filtering options.

    This is the most flexible stat tool — use it to answer questions like:
    "Best scoring forwards from Duke", "International players averaging 20+",
    "Bench players with most assists in January", etc.

    Args:
        season: Season string (e.g. "2025-26")
        measure_type: "Base", "Advanced", "Misc", "Scoring", "Usage", "Defense", "Four Factors", or "Opponent"
        per_mode: "PerGame", "Totals", "Per36", "Per48"
        season_type: "Regular Season" or "Playoffs"
        player_position: Filter by position — "F", "C", "G", or "" for all
        conference: "East", "West", or "" for all
        division: "Atlantic", "Central", "Southeast", "Northwest", "Pacific", "Southwest", or "" for all
        starter_bench: "Starters", "Bench", or "" for all
        player_experience: "Rookie", "Sophomore", "Veteran", or "" for all
        college: College name filter (e.g. "Duke", "Kentucky")
        country: Country filter (e.g. "USA", "France", "Serbia")
        draft_year: Draft year filter (e.g. "2020")
        draft_pick: Draft pick range — "1st Round", "2nd Round", "1st Pick", "Lottery", "Undrafted", or ""
        height: Height filter (e.g. "GT 6-10", "LT 6-2")
        weight: Weight filter (e.g. "GT 250", "LT 200")
        last_n_games: Only consider last N games (0 = full season)
        month: Month number (1-12, 0 = all months)
        opponent_team_id: Filter by opponent team ID (0 = all opponents)
        outcome: "W" for wins only, "L" for losses only, "" for all
        location: "Home", "Road", or "" for all
        shot_clock_range: e.g. "24-22", "22-18 Very Early", "18-15 Early", "15-7 Average", "7-4 Late", "4-0 Very Late"
        top_n: Number of players to return (default 75, max 100)

    Returns:
        Stats for top players matching the filters.
    """
    from nba_api.stats.endpoints import LeagueDashPlayerStats

    try:
        rate_limit()
        top_n = min(max(top_n, 1), 100)

        kwargs = dict(
            season=season,
            measure_type_detailed_defense=measure_type,
            per_mode_detailed=per_mode,
            season_type_all_star=season_type,
            last_n_games=str(last_n_games),
            month=str(month),
            opponent_team_id=opponent_team_id,
        )

        if player_position:
            kwargs["player_position_abbreviation_nullable"] = player_position
        if conference:
            kwargs["conference_nullable"] = conference
        if division:
            kwargs["division_simple_nullable"] = division
        if starter_bench:
            kwargs["starter_bench_nullable"] = starter_bench
        if player_experience:
            kwargs["player_experience_nullable"] = player_experience
        if college:
            kwargs["college_nullable"] = college
        if country:
            kwargs["country_nullable"] = country
        if draft_year:
            kwargs["draft_year_nullable"] = draft_year
        if draft_pick:
            kwargs["draft_pick_nullable"] = draft_pick
        if height:
            kwargs["height_nullable"] = height
        if weight:
            kwargs["weight_nullable"] = weight
        if outcome:
            kwargs["outcome_nullable"] = outcome
        if location:
            kwargs["location_nullable"] = location
        if shot_clock_range:
            kwargs["shot_clock_range_nullable"] = shot_clock_range

        kwargs["timeout"] = API_TIMEOUT
        stats = LeagueDashPlayerStats(**kwargs)
        df = stats.get_data_frames()[0]

        # Keep only core columns to stay within MCP output limits (~25K char max)
        core_cols = [
            "PLAYER_NAME", "TEAM_ABBREVIATION", "AGE", "GP", "MIN",
            "PTS", "REB", "AST", "STL", "BLK", "TOV",
            "FG_PCT", "FG3_PCT", "FT_PCT", "PLUS_MINUS",
        ]
        keep = [c for c in core_cols if c in df.columns]
        # For non-Base measure types, also keep any columns not in the drop list
        if measure_type != "Base":
            drop_always = {"PLAYER_ID", "TEAM_ID", "NICKNAME", "W", "L", "W_PCT",
                           "BLKA", "PF", "PFD", "NBA_FANTASY_PTS", "DD2", "TD3",
                           "WNBA_FANTASY_PTS", "TEAM_COUNT", "FTM", "FTA"}
            for c in df.columns:
                if c not in keep and c not in drop_always and not c.endswith("_RANK"):
                    keep.append(c)
        df = df[[c for c in keep if c in df.columns]]

        return df_to_records(df, max_rows=top_n)
    except Exception as e:
        raise ToolError(f"Failed to get league player stats: {e}")
