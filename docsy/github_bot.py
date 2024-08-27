import logging
import os
import hmac
import hashlib
from flask import Flask, request, jsonify

from docsy.github_manager import get_github_manager_for_repo
import docsy.shared

flask_app = Flask(__name__)

GITHUB_WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET")
assert GITHUB_WEBHOOK_SECRET is not None, "GITHUB_WEBHOOK_SECRET is not set"

ai = docsy.shared.ai
db = docsy.shared.db


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

        if payload["action"] == "opened" or payload["action"] == "reopened":
            # Handle pull request opened event
            # pull_request = payload["pull_request"]
            # pr_number = pull_request["number"]
            # pr_title = pull_request["title"]
            # pr_user = pull_request["user"]["login"]
            repo_name = payload["repository"]["full_name"]

            github_app_installation_id = payload["installation"]["id"]

            try:
                gitHubManager = get_github_manager_for_repo(
                    github_app_installation_id, repo_name
                )

                file_paths = gitHubManager.list_md_files()
            except Exception:
                return jsonify({"status": "internal server error"}), 500

        return jsonify({"status": "processed"}), 200
    else:
        print("invalid request")
        return jsonify({"status": "invalid request"}), 400


if __name__ == "__main__":
    flask_app.run(port=3000, debug=True)
