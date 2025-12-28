import os
import time
import requests
import xmltodict
from dotenv import load_dotenv

load_dotenv()

# Global access token management
access_token = None
expires_at = 0

TEAM_KEYS = os.environ["YAHOO_TEAM_KEYS"].split(",")  # e.g., 390.l.279011.t.6,390.l.279011.t.8
CURRENT_WEEK = int(os.environ.get("YAHOO_CURRENT_WEEK", 1))  # default to week 1 if not set

def refresh_access_token():
    """Refresh Yahoo OAuth access token using the refresh token."""
    global access_token, expires_at
    res = requests.post(
        "https://api.login.yahoo.com/oauth2/get_token",
        auth=(os.environ["YAHOO_CLIENT_ID"], os.environ["YAHOO_CLIENT_SECRET"]),
        data={
            "grant_type": "refresh_token",
            "refresh_token": os.environ["YAHOO_REFRESH_TOKEN"]
        }
    )
    res.raise_for_status()
    data = res.json()
    access_token = data["access_token"]
    expires_at = time.time() + data["expires_in"] - 60  # 1 min buffer

def yahoo_get(url):
    """Generic GET request to Yahoo Fantasy API with automatic token refresh."""
    if not access_token or time.time() > expires_at:
        refresh_access_token()
    res = requests.get(url, headers={
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    })
    res.raise_for_status()
    return res

def get_player_points(player_key):
    """Fetch current and projected points for a player in the current week."""
    url = f"https://fantasysports.yahooapis.com/fantasy/v2/player/{player_key}/stats;type=week;week={CURRENT_WEEK}"
    res = yahoo_get(url)
    data = xmltodict.parse(res.text)
    player = data.get("fantasy_content", {}).get("player", {})

    # Current points
    current_points = float(player.get("player_points", {}).get("total") or 0)
    # Projected points
    projected_points = float(player.get("player_projected_points", {}).get("total") or 0)

    return current_points, projected_points

def get_team_scores():
    """Return current and projected points for the custom teams using player stats."""
    team_lines = ["🏈 *Custom Team Scores*\n"]

    for team_key in TEAM_KEYS:
        # Fetch roster
        url = f"https://fantasysports.yahooapis.com/fantasy/v2/team/{team_key}/roster/players"
        try:
            res = yahoo_get(url)
        except Exception as e:
            team_lines.append(f"*{team_key}*: Error fetching roster ({e})")
            continue

        data = xmltodict.parse(res.text)
        team = data.get("fantasy_content", {}).get("team", {})
        team_name = team.get("name") or team.get("nickname") or f"Team {team_key}"

        # Extract players
        players = team.get("roster", {}).get("players", {}).get("player", [])
        if not isinstance(players, list):
            players = [players]

        # Sum points for all players
        total_current = 0
        total_projected = 0
        for player in players:
            player_key = player.get("player_key")
            if not player_key:
                continue
            try:
                current, projected = get_player_points(player_key)
                total_current += current
                total_projected += projected
            except Exception as e:
                print(f"Error fetching player {player_key}: {e}")
                continue

        team_lines.append(f"*{team_name}*: Current = {total_current:.2f}, Projected = {total_projected:.2f}")

    return "\n".join(team_lines)
