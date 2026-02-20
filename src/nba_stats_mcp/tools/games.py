"""Game-related tools: scores, box scores."""

from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations

from nba_stats_mcp.server import mcp
from nba_stats_mcp.helpers import rate_limit, df_to_records


@mcp.tool(
    annotations=ToolAnnotations(readOnlyHint=True),
    title="Get Game Scores",
)
def get_game_scores(date: str = "") -> dict:
    """Get NBA game scores for a specific date (or today's live scores).

    Args:
        date: Date in YYYY-MM-DD format. Leave empty for today's games/live scores.

    Returns:
        Game scores with status, teams, and game IDs.
    """
    from nba_api.stats.endpoints import ScoreboardV2
    from datetime import datetime

    try:
        if not date:
            game_date = datetime.today().strftime("%Y-%m-%d")
        else:
            game_date = date

        rate_limit()
        scoreboard = ScoreboardV2(game_date=game_date)
        dfs = scoreboard.get_data_frames()

        result = {}
        dataset_names = [
            "game_header", "line_score", "series_standings",
            "last_meeting", "east_conf_standings_by_day",
            "west_conf_standings_by_day", "available",
        ]
        for i, name in enumerate(dataset_names):
            if i < len(dfs) and not dfs[i].empty:
                result[name] = df_to_records(dfs[i], max_rows=50)

        return result
    except Exception as e:
        raise ToolError(f"Failed to get game scores: {e}")


@mcp.tool(
    annotations=ToolAnnotations(readOnlyHint=True),
    title="Get Box Score",
)
def get_box_score(
    game_id: str,
    include_advanced: bool = False,
) -> dict:
    """Get detailed box score for a specific game.

    Args:
        game_id: NBA game ID (get from get_game_scores or game logs, e.g. "0022500001")
        include_advanced: Also include advanced stats (offensive/defensive rating, usage, etc.)

    Returns:
        Player stats and team stats for the game.
    """
    from nba_api.stats.endpoints import BoxScoreTraditionalV3

    try:
        rate_limit()
        box = BoxScoreTraditionalV3(game_id=game_id)
        dfs = box.get_data_frames()

        result = {}
        if len(dfs) > 0 and not dfs[0].empty:
            result["player_stats"] = df_to_records(dfs[0], max_rows=50)
        if len(dfs) > 1 and not dfs[1].empty:
            result["team_stats"] = df_to_records(dfs[1])

        if include_advanced:
            from nba_api.stats.endpoints import BoxScoreAdvancedV3

            rate_limit()
            adv = BoxScoreAdvancedV3(game_id=game_id)
            adv_dfs = adv.get_data_frames()
            if len(adv_dfs) > 0 and not adv_dfs[0].empty:
                result["player_advanced"] = df_to_records(adv_dfs[0], max_rows=50)
            if len(adv_dfs) > 1 and not adv_dfs[1].empty:
                result["team_advanced"] = df_to_records(adv_dfs[1])

        return result
    except Exception as e:
        raise ToolError(f"Failed to get box score: {e}")
