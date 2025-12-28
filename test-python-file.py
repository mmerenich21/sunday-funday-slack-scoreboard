## Test python file

from yahoo import get_team_scores
from yahoo import yahoo_get
import json
import os

print(get_team_scores())


# league_key = os.environ["YAHOO_LEAGUE_KEY"]
# url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/teams"
# res = yahoo_get(url)
# import xmltodict
# data = xmltodict.parse(res.text)

# print(json.dumps(data, indent=2))
