"""Advanced stats tool: tracking, hustle, defense, play types."""

from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations

from nba_stats_mcp.server import mcp
from nba_stats_mcp.helpers import rate_limit, df_to_records


@mcp.tool(
    annotations=ToolAnnotations(readOnlyHint=True),
    title="Get Advanced Stats",
)
def get_advanced_stats(
    stat_type: str,
    season: str = "2025-26",
    per_mode: str = "PerGame",
    season_type: str = "Regular Season",
    pt_measure_type: str = "SpeedDistance",
    defense_category: str = "Overall",
    play_type: str = "Isolation",
) -> list[dict]:
    """Get advanced NBA stats: player tracking, hustle, defense, or play type data.

    Args:
        stat_type: Type of advanced stats — "tracking", "hustle", "defense", or "playtype"
        season: Season string (e.g. "2025-26")
        per_mode: "PerGame" or "Totals" (not used for playtype)
        season_type: "Regular Season" or "Playoffs"
        pt_measure_type: For tracking only — "SpeedDistance", "Drives", "Passing",
            "Possessions", "CatchShoot", "PullUpShoot", "Rebounding", "Defense",
            "Efficiency", "ElbowTouch", "PostTouch", "PaintTouch"
        defense_category: For defense only — "Overall", "3 Pointers", "2 Pointers",
            "Less Than 6Ft", "Greater Than 15Ft"
        play_type: For playtype only — "Isolation", "Transition", "PRBallHandler",
            "PRRollman", "Postup", "Spotup", "Handoff", "Cut", "OffScreen", "OffRebound"

    Returns:
        Advanced stat data for all qualifying players.
    """
    try:
        if stat_type == "tracking":
            return _get_tracking_stats(season, per_mode, season_type, pt_measure_type)
        elif stat_type == "hustle":
            return _get_hustle_stats(season, per_mode, season_type)
        elif stat_type == "defense":
            return _get_defense_stats(season, per_mode, season_type, defense_category)
        elif stat_type == "playtype":
            return _get_playtype_stats(season, season_type, play_type)
        else:
            raise ToolError(
                f"Unknown stat_type '{stat_type}'. "
                "Must be one of: tracking, hustle, defense, playtype"
            )
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Failed to get advanced stats: {e}")


def _get_tracking_stats(
    season: str, per_mode: str, season_type: str, pt_measure_type: str
) -> list[dict]:
    from nba_api.stats.endpoints import LeagueDashPtStats

    rate_limit()
    stats = LeagueDashPtStats(
        season=season,
        per_mode_simple=per_mode,
        season_type_all_star=season_type,
        pt_measure_type=pt_measure_type,
        player_or_team="Player",
    )
    df = stats.get_data_frames()[0]
    return df_to_records(df)


def _get_hustle_stats(season: str, per_mode: str, season_type: str) -> list[dict]:
    from nba_api.stats.endpoints import LeagueHustleStatsPlayer

    rate_limit()
    stats = LeagueHustleStatsPlayer(
        season=season,
        per_mode_time=per_mode,
        season_type_all_star=season_type,
    )
    df = stats.get_data_frames()[0]
    return df_to_records(df)


def _get_defense_stats(
    season: str, per_mode: str, season_type: str, defense_category: str
) -> list[dict]:
    from nba_api.stats.endpoints import LeagueDashPtDefend

    rate_limit()
    stats = LeagueDashPtDefend(
        season=season,
        per_mode_simple=per_mode,
        season_type_all_star=season_type,
        defense_category=defense_category,
    )
    df = stats.get_data_frames()[0]
    return df_to_records(df)


def _get_playtype_stats(
    season: str, season_type: str, play_type: str
) -> list[dict]:
    from nba_api.stats.endpoints import SynergyPlayTypes

    rate_limit()
    stats = SynergyPlayTypes(
        season=season,
        season_type_all_star=season_type,
        play_type_nullable=play_type,
        player_or_team_abbreviation="P",
        type_grouping_nullable="offensive",
    )
    df = stats.get_data_frames()[0]
    return df_to_records(df)
