"""Player-related tools: search, info, stats, game log, splits."""

from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations

from nba_stats_mcp.server import mcp
from nba_stats_mcp.helpers import resolve_player, rate_limit, df_to_records, API_TIMEOUT


@mcp.tool(
    annotations=ToolAnnotations(readOnlyHint=True),
    title="Search Players",
)
def search_players(query: str) -> list[dict]:
    """Search for NBA players by name (supports partial/fuzzy matching).

    Use this to resolve a player name to their player_id before calling other player tools.

    Args:
        query: Player name to search for (e.g. "Curry", "LeBron", "Giannis")

    Returns:
        List of matching players with id, full_name, and is_active status.
    """
    results = resolve_player(query)
    if not results:
        raise ToolError(f"No players found matching '{query}'")
    return results[:25]


@mcp.tool(
    annotations=ToolAnnotations(readOnlyHint=True),
    title="Get Player Info",
)
def get_player_info(player_id: str) -> dict:
    """Get biographical and career info for a player.

    Args:
        player_id: NBA player ID (use search_players to find this)

    Returns:
        Player bio, draft info, current team, and headline stats.
    """
    from nba_api.stats.endpoints import CommonPlayerInfo

    try:
        rate_limit()
        info = CommonPlayerInfo(player_id=player_id, timeout=API_TIMEOUT)
        dfs = info.get_data_frames()

        result = {}
        if len(dfs) > 0 and not dfs[0].empty:
            result["player_info"] = dfs[0].to_dict(orient="records")[0]
        if len(dfs) > 1 and not dfs[1].empty:
            result["headline_stats"] = dfs[1].to_dict(orient="records")[0]
        return result
    except Exception as e:
        raise ToolError(f"Failed to get player info: {e}")


@mcp.tool(
    annotations=ToolAnnotations(readOnlyHint=True),
    title="Get Player Stats",
)
def get_player_stats(
    player_id: str,
    per_mode: str = "PerGame",
) -> dict:
    """Get a player's career statistics (season-by-season and career totals).

    Args:
        player_id: NBA player ID
        per_mode: Stat mode — "PerGame", "Totals", or "Per36"

    Returns:
        Season-by-season regular season stats, playoff stats, and career totals.
    """
    from nba_api.stats.endpoints import PlayerCareerStats

    try:
        rate_limit()
        career = PlayerCareerStats(player_id=player_id, per_mode36=per_mode, timeout=API_TIMEOUT)
        dfs = career.get_data_frames()

        result = {}
        dataset_names = [
            "regular_season", "career_regular_season",
            "post_season", "career_post_season",
            "all_star", "career_all_star",
            "college", "career_college",
        ]
        for i, name in enumerate(dataset_names):
            if i < len(dfs) and not dfs[i].empty:
                result[name] = df_to_records(dfs[i])
        return result
    except Exception as e:
        raise ToolError(f"Failed to get player stats: {e}")


@mcp.tool(
    annotations=ToolAnnotations(readOnlyHint=True),
    title="Get Player Game Log",
)
def get_player_game_log(
    player_id: str,
    season: str = "2025-26",
    season_type: str = "Regular Season",
    date_from: str = "",
    date_to: str = "",
) -> list[dict]:
    """Get a player's game-by-game stats for a season.

    Args:
        player_id: NBA player ID
        season: Season string (e.g. "2025-26", "2024-25")
        season_type: "Regular Season" or "Playoffs"
        date_from: Filter start date (MM/DD/YYYY format, optional)
        date_to: Filter end date (MM/DD/YYYY format, optional)

    Returns:
        List of game-by-game stat lines.
    """
    from nba_api.stats.endpoints import PlayerGameLog

    try:
        rate_limit()
        log = PlayerGameLog(
            player_id=player_id,
            season=season,
            season_type_all_star=season_type,
            date_from_nullable=date_from,
            date_to_nullable=date_to,
            timeout=API_TIMEOUT,
        )
        df = log.get_data_frames()[0]
        return df_to_records(df)
    except Exception as e:
        raise ToolError(f"Failed to get player game log: {e}")


@mcp.tool(
    annotations=ToolAnnotations(readOnlyHint=True),
    title="Get Player Splits",
)
def get_player_splits(
    player_id: str,
    season: str = "2025-26",
    measure_type: str = "Base",
    per_mode: str = "PerGame",
    season_type: str = "Regular Season",
) -> dict:
    """Get a player's stat splits (home/away, win/loss, by month, etc.).

    Args:
        player_id: NBA player ID
        season: Season string (e.g. "2025-26")
        measure_type: "Base", "Advanced", "Misc", "Scoring", or "Usage"
        per_mode: "PerGame", "Totals", or "Per36"
        season_type: "Regular Season" or "Playoffs"

    Returns:
        Dict with split categories: overall, location (home/away), win_loss,
        monthly, pre_post_allstar, days_rest, starter_bench.
    """
    from nba_api.stats.endpoints import PlayerDashboardByGeneralSplits

    try:
        rate_limit()
        splits = PlayerDashboardByGeneralSplits(
            player_id=player_id,
            season=season,
            measure_type_detailed=measure_type,
            per_mode_detailed=per_mode,
            season_type_playoffs=season_type,
            timeout=API_TIMEOUT,
        )
        dfs = splits.get_data_frames()

        split_names = [
            "overall", "location", "win_loss", "monthly",
            "pre_post_allstar", "days_rest", "starter_bench",
        ]
        result = {}
        for i, name in enumerate(split_names):
            if i < len(dfs) and not dfs[i].empty:
                result[name] = df_to_records(dfs[i])
        return result
    except Exception as e:
        raise ToolError(f"Failed to get player splits: {e}")
