"""Shared utilities for NBA Stats MCP server."""

import time
import threading

from nba_api.stats.static import players as static_players
from nba_api.stats.static import teams as static_teams


# --- Rate Limiter ---

_rate_lock = threading.Lock()
_last_call_time = 0.0
RATE_LIMIT_SECONDS = 0.6
API_TIMEOUT = 15  # seconds — fail fast instead of hanging


def rate_limit():
    """Enforce minimum delay between nba_api calls to avoid being blocked."""
    global _last_call_time
    with _rate_lock:
        now = time.time()
        elapsed = now - _last_call_time
        if elapsed < RATE_LIMIT_SECONDS:
            time.sleep(RATE_LIMIT_SECONDS - elapsed)
        _last_call_time = time.time()


# --- Player Resolution ---

def resolve_player(query: str) -> list[dict]:
    """Fuzzy-match a player name query against the static player list.

    Returns list of matching players sorted by active status then name,
    each with keys: id, full_name, is_active.
    """
    query_lower = query.lower().strip()
    all_players = static_players.get_players()

    exact = []
    starts_with = []
    contains = []

    for p in all_players:
        full = p["full_name"].lower()
        first = p["first_name"].lower()
        last = p["last_name"].lower()

        if full == query_lower or last == query_lower:
            exact.append(p)
        elif full.startswith(query_lower) or last.startswith(query_lower) or first.startswith(query_lower):
            starts_with.append(p)
        elif query_lower in full:
            contains.append(p)

    # Combine with priority: exact > starts_with > contains
    results = exact + starts_with + contains

    # Sort: active players first, then alphabetically
    results.sort(key=lambda p: (not p["is_active"], p["full_name"]))

    return [
        {"id": str(p["id"]), "full_name": p["full_name"], "is_active": p["is_active"]}
        for p in results
    ]


# --- Team Resolution ---

_TEAM_ABBREVIATION_MAP: dict[str, int] | None = None


def _get_team_map() -> dict[str, int]:
    """Build a lookup map from various team identifiers to team ID."""
    global _TEAM_ABBREVIATION_MAP
    if _TEAM_ABBREVIATION_MAP is not None:
        return _TEAM_ABBREVIATION_MAP

    mapping = {}
    for t in static_teams.get_teams():
        tid = t["id"]
        mapping[t["full_name"].lower()] = tid
        mapping[t["abbreviation"].lower()] = tid
        mapping[t["nickname"].lower()] = tid
        mapping[t["city"].lower()] = tid
        # Also add "city nickname" variations
        mapping[f"{t['city'].lower()} {t['nickname'].lower()}"] = tid

    _TEAM_ABBREVIATION_MAP = mapping
    return mapping


def resolve_team(query: str) -> list[dict]:
    """Resolve a team name, abbreviation, or city to team info.

    Returns list of matching teams, each with keys: id, full_name, abbreviation.
    """
    query_lower = query.lower().strip()
    team_map = _get_team_map()
    all_teams = static_teams.get_teams()

    # Try exact match first
    if query_lower in team_map:
        tid = team_map[query_lower]
        for t in all_teams:
            if t["id"] == tid:
                return [{"id": str(t["id"]), "full_name": t["full_name"], "abbreviation": t["abbreviation"]}]

    # Fuzzy: contains match
    results = []
    seen = set()
    for t in all_teams:
        if t["id"] in seen:
            continue
        searchable = f"{t['full_name']} {t['abbreviation']} {t['city']} {t['nickname']}".lower()
        if query_lower in searchable:
            results.append({"id": str(t["id"]), "full_name": t["full_name"], "abbreviation": t["abbreviation"]})
            seen.add(t["id"])

    return results


def get_team_id(query: str) -> str:
    """Convenience: resolve a team query to a single team ID, or raise."""
    from mcp.server.fastmcp.exceptions import ToolError

    matches = resolve_team(query)
    if not matches:
        raise ToolError(f"No team found matching '{query}'")
    return matches[0]["id"]


# --- DataFrame Helpers ---

def df_to_records(df, max_rows: int = 200) -> list[dict]:
    """Convert a pandas DataFrame to a list of dicts, capped at max_rows."""
    if df is None or df.empty:
        return []
    return df.head(max_rows).to_dict(orient="records")
