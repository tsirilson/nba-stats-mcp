"""Team-related tools: search, stats, game log, roster."""

from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations

from nba_stats_mcp.server import mcp
from nba_stats_mcp.helpers import resolve_team, get_team_id, rate_limit, df_to_records


@mcp.tool(
    annotations=ToolAnnotations(readOnlyHint=True),
    title="Search Teams",
)
def search_teams(query: str) -> list[dict]:
    """Search for NBA teams by name, abbreviation, or city.

    Use this to resolve a team name to their team_id before calling other team tools.

    Args:
        query: Team name, abbreviation, or city (e.g. "Lakers", "LAL", "Los Angeles")

    Returns:
        List of matching teams with id, full_name, and abbreviation.
    """
    results = resolve_team(query)
    if not results:
        raise ToolError(f"No teams found matching '{query}'")
    return results


@mcp.tool(
    annotations=ToolAnnotations(readOnlyHint=True),
    title="Get Team Stats",
)
def get_team_stats(
    team: str,
    per_mode: str = "PerGame",
    season_type: str = "Regular Season",
) -> list[dict]:
    """Get a team's year-by-year franchise statistics.

    Args:
        team: Team name, abbreviation, or city (e.g. "Lakers", "LAL")
        per_mode: "PerGame", "Totals", or "Per36"
        season_type: "Regular Season" or "Playoffs"

    Returns:
        Year-by-year stats for the franchise.
    """
    from nba_api.stats.endpoints import TeamYearByYearStats

    try:
        team_id = get_team_id(team)
        rate_limit()
        stats = TeamYearByYearStats(
            team_id=team_id,
            per_mode_simple=per_mode,
            season_type_all_star=season_type,
        )
        df = stats.get_data_frames()[0]
        return df_to_records(df, max_rows=100)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Failed to get team stats: {e}")


@mcp.tool(
    annotations=ToolAnnotations(readOnlyHint=True),
    title="Get Team Game Log",
)
def get_team_game_log(
    team: str,
    season: str = "2025-26",
    season_type: str = "Regular Season",
    date_from: str = "",
    date_to: str = "",
) -> list[dict]:
    """Get a team's game-by-game results for a season.

    Args:
        team: Team name, abbreviation, or city
        season: Season string (e.g. "2025-26")
        season_type: "Regular Season" or "Playoffs"
        date_from: Filter start date (MM/DD/YYYY format, optional)
        date_to: Filter end date (MM/DD/YYYY format, optional)

    Returns:
        List of game-by-game results.
    """
    from nba_api.stats.endpoints import TeamGameLog

    try:
        team_id = get_team_id(team)
        rate_limit()
        log = TeamGameLog(
            team_id=team_id,
            season=season,
            season_type_all_star=season_type,
            date_from_nullable=date_from,
            date_to_nullable=date_to,
        )
        df = log.get_data_frames()[0]
        return df_to_records(df)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Failed to get team game log: {e}")


@mcp.tool(
    annotations=ToolAnnotations(readOnlyHint=True),
    title="Get Team Roster",
)
def get_team_roster(
    team: str,
    season: str = "2025-26",
) -> dict:
    """Get a team's roster for a given season.

    Args:
        team: Team name, abbreviation, or city
        season: Season string (e.g. "2025-26")

    Returns:
        Roster with player IDs, positions, heights, weights, and coaching staff.
    """
    from nba_api.stats.endpoints import CommonTeamRoster

    try:
        team_id = get_team_id(team)
        rate_limit()
        roster = CommonTeamRoster(team_id=team_id, season=season)
        dfs = roster.get_data_frames()

        result = {}
        if len(dfs) > 0 and not dfs[0].empty:
            result["players"] = df_to_records(dfs[0])
        if len(dfs) > 1 and not dfs[1].empty:
            result["coaches"] = df_to_records(dfs[1])
        return result
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Failed to get team roster: {e}")
