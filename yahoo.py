import os
import time
import requests
import xmltodict
from dotenv import load_dotenv

load_dotenv()

# Global access token management
access_token = None
expires_at = 0

# Load team keys from environment variable
TEAM_KEYS = os.environ["YAHOO_TEAM_KEYS"].split(",")  # e.g., 390.l.12345.t.1,390.l.12345.t.2

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

def get_team_scores():
    """
    Return current and projected points for the teams listed in TEAM_KEYS.
    """
    team_lines = ["🏈 *Custom Team Scores*\n"]

    for key in TEAM_KEYS:
        url = f"https://fantasysports.yahooapis.com/fantasy/v2/team/{key}/stats"
        try:
            res = yahoo_get(url)
        except Exception as e:
            team_lines.append(f"*{key}*: Error fetching data ({e})")
            continue

        data = xmltodict.parse(res.text)
        team = data.get("fantasy_content", {}).get("team", {})

        # Extract name
        name = team.get("name") or team.get("nickname") or f"Team {key}"

        # Extract points safely
        current_points = float(team.get("team_points", {}).get("total") or 0)
        projected_points = float(team.get("team_projected_points", {}).get("total") or 0)

        team_lines.append(f"*{name}*: Current = {current_points}, Projected = {projected_points}")

    return "\n".join(team_lines)
