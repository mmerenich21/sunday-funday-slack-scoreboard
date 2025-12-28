import os
import requests
from dotenv import load_dotenv

load_dotenv()

res = requests.post(
    "https://api.login.yahoo.com/oauth2/get_token",
    auth=(os.environ["YAHOO_CLIENT_ID"], os.environ["YAHOO_CLIENT_SECRET"]),
    data={
        "grant_type": "refresh_token",
        "refresh_token": os.environ["YAHOO_REFRESH_TOKEN"]
    }
)

print(res.status_code)
print(res.json())