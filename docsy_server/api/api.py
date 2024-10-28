from flask import Flask, request, jsonify
from docsy_server.api.context import GithubRepositoryContext
from docsy_server.engine.github_manager import get_github_manager_for_repo

app = Flask(__name__)

@app.route('/engine/suggestion', methods=['POST'])
def generate_suggestion():
    print("Generating suggestion")
    context = []
    try:
        data = request.get_json()
        
        if not data or 'context' not in data:
            return jsonify({
                "error": "Missing required fields. Please provide 'context'"
            }), 400
            
        context = data['context']
    except Exception as e:
        return jsonify({"error": str(e)}), 500
       
    states:list[str] = []
    events:list[str] = []
    for c in context:
        c = GithubRepositoryContext(**c)
        ghm = get_github_manager_for_repo(51286673,c.github_repository_name) # TODO: choose installation id from auth
        # states.append(ghm.list_md_files())
        for commit in ghm.get_commits(c.pull_request_number):
            events.append(ghm.get_diff(commit.parents[0].sha, commit.sha))
    
    return jsonify({"suggestion": "Hello, world!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
