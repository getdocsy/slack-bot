import json
from loguru import logger
from flask import Flask, request, jsonify
from docsy_server.api.model import GithubRepository, Suggestion, GithubRepositoryContext
from docsy_server.engine.github_manager import get_github_manager_for_repo
from docsy_server.engine.ai import Prompt
from docsy_server.engine import ai
from docsy_server.engine.coder import DocsyCoder

app = Flask(__name__)

@app.route('/engine/suggestion/structure', methods=['POST'])
def generate_structure_suggestion():
    logger.info("Generating structure suggestion")
    try:
        data = request.get_json()
        context: GithubRepositoryContext = data['context']
        target = GithubRepository(**data['target'])
        ghm = get_github_manager_for_repo(51286673, target.github_repo_full_name)
        file_paths = ghm.list_md_files()
        file_suggestions = ai.get_structure_suggestions(context, file_paths)
        suggestion = Suggestion(target=target, file_suggestions=file_suggestions)
        result = jsonify(suggestion.export_to_cli_format())
        return result, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/engine/suggestion', methods=['POST'])
def generate_suggestion():
    logger.info("Generating suggestion")
    try:
        data = request.get_json()
        context: GithubRepositoryContext = data['context']
        target = GithubRepository(**data['target'])
        ghm = get_github_manager_for_repo(51286673, target.github_repo_full_name)
        coder = DocsyCoder(ghm)
        file_suggestions = coder.suggest(context, ghm.list_md_files())
        suggestion = Suggestion(target=target, file_suggestions=file_suggestions)
        result = jsonify(suggestion.export_to_cli_format())
        return result, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/engine/apply', methods=['POST'])
def apply_suggestion():
    # try:
        # Load
    data = request.get_json()
    target = GithubRepository(**data['target'])
    context: GithubRepositoryContext = data['context']
    suggestion = Suggestion(**data['suggestion'])

    logger.info(f"Preparing to apply suggestion for {target.github_repo_full_name}")
    # Prepare
    ghm = get_github_manager_for_repo(51286673, target.github_repo_full_name)
    coder = DocsyCoder(ghm)

    logger.info(f"Applying suggestion for {target.github_repo_full_name}")
    # Apply
    apply_response = coder.apply(suggestion, context)
    return jsonify(apply_response), 200
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

@app.route('/engine/whoami', methods=['POST'])
def whoami():
    return jsonify({"email": "dev@felixzieger.de"}), 200 #TODO: check for AUTH! get user from auth

@app.route('/engine/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(debug=True)
