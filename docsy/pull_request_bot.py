import os
from flask import Flask, request, jsonify
from github import GithubIntegration, Auth

app = Flask(__name__)

# GITHUB_APP_ID = os.environ.get("GITHUB_APP_ID")
# GITHUB_APP_PRIVATE_KEY = os.environ.get("GITHUB_APP_PRIVATE_KEY")
# assert GITHUB_APP_ID is not None, "GITHUB_APP_ID is not set"
# assert GITHUB_APP_PRIVATE_KEY is not None, "GITHUB_APP_PRIVATE_KEY is not set"

# app_installation_id = 51286673
# repo_name = "felixzieger/congenial-computing-machine"


@app.route("/webhook", methods=["POST"])
def webhook():
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
        return jsonify({"status": "invalid request"}), 400


if __name__ == "__main__":
    app.run(port=3000, debug=True)
