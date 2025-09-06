import asyncio
from flask import Flask, render_template,jsonify, request
from client import research_then_translate

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')

@app.route("/send-message", methods=["POST"])
def send_message():
    data = request.get_json(silent=True) or {}
    question = data.get("question")
    language = data.get("language")
    if not question:
        return jsonify({"error": "Missing 'question' in JSON body"}), 400
    try:
        answer =  asyncio.run(research_then_translate(question, language))
        return  jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)