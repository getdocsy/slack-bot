from flask import Flask, request, jsonify
from docsy_server.api.state import GithubRepositoryState

app = Flask(__name__)

@app.route('/engine/suggestion', methods=['POST'])
def generate_suggestion():
    print("Generating suggestion")
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required inputs
        if not data or 'context' not in data:
            return jsonify({
                "error": "Missing required fields. Please provide 'context'"
            }), 400
            
        context = data['context']
        
        for state in context:
            state = GithubRepositoryState(**state)
            print(state)

        return jsonify({"suggestion": "Hello, world!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
