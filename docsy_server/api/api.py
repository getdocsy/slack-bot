from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/engine/suggestion', methods=['POST'])
def generate_suggestion():
    print("Generating suggestion")
    try:
        return jsonify({"suggestion": "Hello, world!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
