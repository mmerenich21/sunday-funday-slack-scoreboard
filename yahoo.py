import os
import time
import requests
import xmltodict
from dotenv import load_dotenv

load_dotenv()

# Global token management
access_token = None
expires_at = 0

# Replace with your two Yahoo Fantasy team IDs
TEAM_IDS = [6, 8]  # Example: [1, 5]

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
    expires_at = time.time() + data["expires_in"] - 60  # buffer for safety

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

def get_team_scores():
    """
    Returns current and projected points for the two specified teams.
    Works even if teams are not in official matchups.
    """
    league_key = os.environ["YAHOO_LEAGUE_KEY"]
    url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/teams"
    res = yahoo_get(url)
    data = xmltodict.parse(res.text)

    # Handle league node: list or dict
    league = data["fantasy_content"]["league"]
    league_node = league[1] if isinstance(league, list) else league

    # Extract teams; always as a list
    all_teams = league_node["teams"]["team"]
    if not isinstance(all_teams, list):
        all_teams = [all_teams]

    lines = ["🏈  *Boner Bowl Scoreboard* 🏈\n"]

    for team in all_teams:
        # Safely get team_id
        team_id = int(team.get("team_id") or team.get("@team_id", 0))
        if team_id not in TEAM_IDS:
            continue

        name = team.get("name") or team.get("nickname") or f"Team {team_id}"

        # Safely get current and projected points
        current_points = float(team.get("team_points", {}).get("total", 0))
        projected_points = float(team.get("team_projected_points", {}).get("total", 0))

        lines.append(f"*{name}*: Current = {current_points}, Projected = {projected_points}")

    return "\n".join(lines)

