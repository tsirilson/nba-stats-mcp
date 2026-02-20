"""NBA Stats MCP Server — comprehensive NBA statistics via nba_api."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="nba-stats-mcp",
    instructions=(
        "NBA statistics server powered by nba_api. Provides 15 tools covering "
        "player search/stats/splits, team stats/rosters, league standings/leaders, "
        "game scores/box scores, and advanced stats (tracking, hustle, defense, play types). "
        "Use search_players/search_teams first to resolve names to IDs, then call "
        "stat tools with those IDs. All data is read-only from NBA.com."
    ),
)

# Register all tools by importing the modules (each uses @mcp.tool())
from nba_stats_mcp.tools import players  # noqa: F401, E402
from nba_stats_mcp.tools import teams  # noqa: F401, E402
from nba_stats_mcp.tools import league  # noqa: F401, E402
from nba_stats_mcp.tools import games  # noqa: F401, E402
from nba_stats_mcp.tools import advanced  # noqa: F401, E402


def main():
    mcp.run()


if __name__ == "__main__":
    main()
