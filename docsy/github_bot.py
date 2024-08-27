import os
import hmac
import hashlib
from flask import Flask, request, jsonify
from github import GithubIntegration, Auth

flask_app = Flask(__name__)

GITHUB_WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET")
assert GITHUB_WEBHOOK_SECRET is not None, "GITHUB_WEBHOOK_SECRET is not set"

# GITHUB_APP_ID = os.environ.get("GITHUB_APP_ID")
# GITHUB_APP_PRIVATE_KEY = os.environ.get("GITHUB_APP_PRIVATE_KEY")
# assert GITHUB_APP_ID is not None, "GITHUB_APP_ID is not set"
# assert GITHUB_APP_PRIVATE_KEY is not None, "GITHUB_APP_PRIVATE_KEY is not set"

# app_installation_id = 51286673
# repo_name = "felixzieger/congenial-computing-machine"


@flask_app.route("/github/events", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Hub-Signature-256")
    if signature is None:
        print("missing signature")
        return jsonify({"status": "missing signature"}), 400

    secret = bytes(GITHUB_WEBHOOK_SECRET, "utf-8")

    mac = hmac.new(secret, msg=request.data, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + mac.hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        print("invalid signature")
        return jsonify({"status": "invalid signature"}), 400

    if request.method == "POST":
        payload = request.json

        if payload["action"] == "opened":
            # Handle pull request opened event
            pull_request = payload["pull_request"]
            pr_number = pull_request["number"]
            pr_title = pull_request["title"]
            pr_user = pull_request["user"]["login"]
            repo_name = payload["repository"]["full_name"]

            # Example: print details or take action
            print(
                f"Pull request #{pr_number} opened by {pr_user} in {repo_name}: {pr_title}"
            )

        return jsonify({"status": "processed"}), 200
    else:
        print("invalid request")
        return jsonify({"status": "invalid request"}), 400


if __name__ == "__main__":
    flask_app.run(port=3000, debug=True)
