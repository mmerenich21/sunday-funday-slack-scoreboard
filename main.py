### https://example.com/yahoo/callback?code=cb2z7zbeyp4r79g7gernst7zmf78dke3

import os
import time
import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from yahoo import get_team_scores

load_dotenv()
app = FastAPI()

def verify_slack(request: Request, body: bytes):
    """Verify that incoming requests really come from Slack."""
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    signature = request.headers.get("X-Slack-Signature")

    # Reject old requests
    if abs(time.time() - int(timestamp)) > 300:
        raise HTTPException(status_code=403, detail="Stale request")

    base = f"v0:{timestamp}:{body.decode()}"
    my_sig = "v0=" + hmac.new(
        os.environ["SLACK_SIGNING_SECRET"].encode(),
        base.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(my_sig, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

@app.post("/slack/commands")
async def slack_commands(request: Request):
    body = await request.body()
    verify_slack(request, body)  # Comment this out for local testing if needed

    scoreboard = get_team_scores()  # Uses the two-team function

    return {
        "response_type": "in_channel",  # visible to everyone in channel
        "text": scoreboard
    }



