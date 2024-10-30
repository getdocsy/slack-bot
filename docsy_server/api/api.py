import json
from loguru import logger
from flask import Flask, request, jsonify
from docsy_server.api.context import GithubRepositoryContext
from docsy_server.engine.github_manager import get_github_manager_for_repo
from docsy_server.engine.ai import Prompt
from docsy_server.engine import ai

app = Flask(__name__)

@app.route('/engine/suggestion', methods=['POST'])
def generate_suggestion():
    logger.info("Generating suggestion")
    context = []
    try:
        data = request.get_json()
        context = data['context']
        target = data['target']
        target = GithubRepositoryContext(**target)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
       
    ghm = get_github_manager_for_repo(51286673,target.github_repo_full_name) # TODO: choose installation id from auth
    file_paths = ghm.list_md_files()
    prompts = [
        Prompt(role="system", content="The following changes are made to the code:"),
    ] + [Prompt(role="user", content=str(c)) for c in context] + [
        Prompt(role="system", content="The following is the current structure of the documentation:"),
        Prompt(role="system", content= "\n".join(file_paths)),
        Prompt(role="system", content= ( "Which files in the documentation needs to be updated to reflect the changes? "
                                        "Answer with a JSON object with the following format: "
                                        "{\"files\": [{\"path\": \"path/to/file\", \"action\": \"+\", \"explanation\": \"explanation of why this file needs to be updated\"}]}"
                                        "Where 'path' is the path to the file that needs to be updated, and 'action' is '+' if the file should be created, '-' if the file should be deleted, or '~' if the file should be modified."
                                        "Explanation is optional, but if provided, it should be a short explanation of which of the code changes require a change to this file. Keep it short."
                                        "Do not format your answer as markdown, just return the JSON object."))
    ]

    suggestion_str = ai.get_suggestion(prompts)
    suggestion = json.loads(suggestion_str)

    return jsonify({"suggestion": suggestion}), 200


@app.route('/engine/whoami', methods=['POST'])
def whoami():
    return jsonify({"email": "dev@felixzieger.de"}), 200 #TODO: check for AUTH! get user from auth

if __name__ == '__main__':
    app.run(debug=True)
