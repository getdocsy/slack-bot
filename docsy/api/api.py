import json
from loguru import logger
from flask import Flask, request, jsonify
from docsy.api.model import GithubRepository, Suggestion, GithubRepositoryContext
from docsy.engine.github_manager import get_github_manager_for_repo
from docsy.engine.ai import Prompt
from docsy.engine import ai
from docsy.engine.coder import DocsyCoder
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/engine/suggestion/structure", methods=["POST"])
def generate_structure_suggestion():
    logger.info("Generating structure suggestion")
    try:
        data = request.get_json()
        context: GithubRepositoryContext = data["context"]
        target = GithubRepository(**data["target"])
        ghm = get_github_manager_for_repo(51286673, target.github_repo_full_name)
        file_paths = ghm.list_md_files()
        file_suggestions = ai.get_structure_suggestions(context, file_paths)
        suggestion = Suggestion(target=target, file_suggestions=file_suggestions)
        result = jsonify(suggestion.export_to_cli_format())
        return result, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/engine/suggestion", methods=["POST"])
def generate_suggestion():
    logger.info("Generating suggestion")
    try:
        data = request.get_json()
        context: GithubRepositoryContext = data["context"]
        target = GithubRepository(**data["target"])
        ghm = get_github_manager_for_repo(51286673, target.github_repo_full_name)
        coder = DocsyCoder(ghm)
        file_suggestions = coder.suggest(context, ghm.list_md_files())
        suggestion = Suggestion(target=target, file_suggestions=file_suggestions)
        result = jsonify(suggestion.export_to_cli_format())
        return result, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/engine/apply", methods=["POST"])
def apply_suggestion():
    # try:
    # Load
    data = request.get_json()
    target = GithubRepository(**data["target"])
    context: GithubRepositoryContext = data["context"]
    suggestion = Suggestion(**data["suggestion"])

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


@app.route("/engine/whoami", methods=["POST"])
def whoami():
    return (
        jsonify({"email": "dev@felixzieger.de"}),
        200,
    )  # TODO: check for AUTH! get user from auth


@app.route("/engine/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/engine/analyze", methods=["POST"])
def analyze_docs():
    logger.info("Starting documentation analysis")
    try:
        data = request.get_json()
        docs_url = data.get("url")
        
        if not docs_url:
            return jsonify({"error": "Missing 'url' parameter in request body"}), 400
            
        # TODO: Implement async analysis task
        # For now, return a mock response
        analysis_id = "mock-analysis-123"  # This should be a unique identifier
        results_url = f"/api/engine/analysis/{analysis_id}"
        
        return jsonify({
            "status": "processing",
            "results_url": results_url
        }), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/engine/analyze", methods=["GET"])
def get_analysis_results():
    logger.info("Fetching analysis results")
    try:
        analysis_id = request.args.get('url')
        if not analysis_id:
            return jsonify({"error": "Missing 'url' parameter"}), 400

        # TODO: Implement actual result retrieval from database/storage
        # Mock response for now
        mock_results = {
            "analysis_id": analysis_id,
            "status": "completed", 
            "results": {
                "readability_score": 8.5,
                "coverage_score": 0.85,
                "suggestions": [
                    "Consider adding more code examples",
                    "API reference section needs more detail"
                ]
            }
        }
        
        return jsonify(mock_results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
