### https://example.com/yahoo/callback?code=cb2z7zbeyp4r79g7gernst7zmf78dke3

import os
import time
import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from yahoo import get_team_scores

app = Flask(__name__)

SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

@app.route("/slack/commands", methods=["POST"])
def slack_commands():
    command_text = request.form.get("command")
    if command_text != "/scoreboard":
        return jsonify({"text": "Unknown command"}), 200

    # Fetch scores from Yahoo
    try:
        scoreboard = get_team_scores()
    except Exception as e:
        scoreboard = f"Error fetching team scores: {e}"

    return jsonify({
        "response_type": "in_channel",
        "text": scoreboard
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)




