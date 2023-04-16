from flask import Flask, jsonify, request, Response
import asyncio
from flask_cors import CORS
import uuid
from agent.action_planner import main
from agent.context_utils import add_context

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def helloWorld():
    return "<div> Hello there </div>"

@app.route("/", methods=["POST"])
async def pushConversation():
    data = request.get_json()
    user_input = data.get("user_input", None)
    session_id = data.get("session_id", None)
    if session_id is None or len(session_id) < 1:
        session_id = str(uuid.uuid4())
    data = await main(user_input, session_id)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8004)
