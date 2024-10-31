import json
from loguru import logger
from flask import Flask, request, jsonify
from docsy_server.api.context import GithubRepositoryContext, Context
from docsy_server.engine.github_manager import get_github_manager_for_repo
from docsy_server.engine.ai import Prompt
from docsy_server.engine import ai

app = Flask(__name__)

@app.route('/engine/suggestion', methods=['POST'])
def generate_suggestion():
    logger.info("Generating suggestion")
    try:
        data = request.get_json()
        context: Context = data['context']
        target = GithubRepositoryContext(**data['target'])
        ghm = get_github_manager_for_repo(51286673, target.github_repo_full_name)
        file_paths = ghm.list_md_files()
        suggestion = ai.get_suggestion_from_context(context, file_paths)
        return jsonify({"suggestion": suggestion}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/engine/whoami', methods=['POST'])
def whoami():
    return jsonify({"email": "dev@felixzieger.de"}), 200 #TODO: check for AUTH! get user from auth

if __name__ == '__main__':
    app.run(debug=True)
