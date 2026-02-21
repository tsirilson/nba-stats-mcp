"""Advanced stats tool: tracking, hustle, defense, play types."""

from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations

from nba_stats_mcp.server import mcp
from nba_stats_mcp.helpers import rate_limit, df_to_records, API_TIMEOUT


# Key columns to keep per stat type — trim noise to stay under MCP output limits
_HUSTLE_COLS = [
    "PLAYER_NAME", "TEAM_ABBREVIATION", "AGE", "G", "MIN",
    "CONTESTED_SHOTS", "DEFLECTIONS", "CHARGES_DRAWN",
    "SCREEN_ASSISTS", "SCREEN_AST_PTS",
    "LOOSE_BALLS_RECOVERED", "BOX_OUTS",
]

# Columns to always drop from tracking stats (keep the sport-specific ones)
_TRACKING_DROP = {"PLAYER_ID", "TEAM_ID", "W", "L"}


def _trim_df(df, keep_cols=None, top_n=50, sort_by=None, ascending=False):
    """Trim a dataframe: select columns, sort, and limit rows."""
    if keep_cols:
        # Only keep specified columns
        df = df[[c for c in keep_cols if c in df.columns]]
    else:
        # Drop ID columns
        drop_ids = {"PLAYER_ID", "TEAM_ID", "CLOSE_DEF_PERSON_ID"}
        df = df.drop(columns=[c for c in drop_ids if c in df.columns], errors="ignore")

    if sort_by and sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=ascending)

    return df.head(top_n)


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
    top_n: int = 50,
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
        top_n: Number of players to return (default 50, max 150). Results are sorted by the most relevant stat.

    Returns:
        Advanced stat data for top players.
    """
    top_n = min(max(top_n, 1), 150)
    try:
        if stat_type == "tracking":
            return _get_tracking_stats(season, per_mode, season_type, pt_measure_type, top_n)
        elif stat_type == "hustle":
            return _get_hustle_stats(season, per_mode, season_type, top_n)
        elif stat_type == "defense":
            return _get_defense_stats(season, per_mode, season_type, defense_category, top_n)
        elif stat_type == "playtype":
            return _get_playtype_stats(season, season_type, play_type, top_n)
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
    season: str, per_mode: str, season_type: str, pt_measure_type: str, top_n: int
) -> list[dict]:
    from nba_api.stats.endpoints import LeagueDashPtStats

    rate_limit()
    stats = LeagueDashPtStats(
        season=season,
        per_mode_simple=per_mode,
        season_type_all_star=season_type,
        pt_measure_type=pt_measure_type,
        player_or_team="Player",
        timeout=API_TIMEOUT,
    )
    df = stats.get_data_frames()[0]
    df = df.drop(columns=[c for c in _TRACKING_DROP if c in df.columns], errors="ignore")
    df = _trim_df(df, top_n=top_n)
    return df_to_records(df, max_rows=top_n)


def _get_hustle_stats(season: str, per_mode: str, season_type: str, top_n: int) -> list[dict]:
    from nba_api.stats.endpoints import LeagueHustleStatsPlayer

    rate_limit()
    stats = LeagueHustleStatsPlayer(
        season=season,
        per_mode_time=per_mode,
        season_type_all_star=season_type,
        timeout=API_TIMEOUT,
    )
    df = stats.get_data_frames()[0]
    df = _trim_df(df, keep_cols=_HUSTLE_COLS, top_n=top_n, sort_by="DEFLECTIONS")
    return df_to_records(df, max_rows=top_n)


def _get_defense_stats(
    season: str, per_mode: str, season_type: str, defense_category: str, top_n: int
) -> list[dict]:
    from nba_api.stats.endpoints import LeagueDashPtDefend

    rate_limit()
    stats = LeagueDashPtDefend(
        season=season,
        per_mode_simple=per_mode,
        season_type_all_star=season_type,
        defense_category=defense_category,
        timeout=API_TIMEOUT,
    )
    df = stats.get_data_frames()[0]
    df = _trim_df(df, top_n=top_n)
    return df_to_records(df, max_rows=top_n)


def _get_playtype_stats(
    season: str, season_type: str, play_type: str, top_n: int
) -> list[dict]:
    from nba_api.stats.endpoints import SynergyPlayTypes

    rate_limit()
    stats = SynergyPlayTypes(
        season=season,
        season_type_all_star=season_type,
        play_type_nullable=play_type,
        player_or_team_abbreviation="P",
        type_grouping_nullable="offensive",
        timeout=API_TIMEOUT,
    )
    df = stats.get_data_frames()[0]
    df = _trim_df(df, top_n=top_n)
    return df_to_records(df, max_rows=top_n)
