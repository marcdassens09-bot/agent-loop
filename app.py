from memory_agent import MemoryAgent
agent = MemoryAgent()
from layout_agent import LayoutAgent
layout = LayoutAgent()
from debug_agent import DebugAgent
debug = DebugAgent()
from prospect_agent import ProspectAgent
prospect = ProspectAgent()
import os
os.environ["PYTHONUTF8"] = "1"
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from agent import agent_camping
from search_agent import SearchAgent
search = SearchAgent()
load_dotenv()

app = Flask(__name__)
conversation_store = {}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Champ message manquant"}), 400
    session_id = data.get("session_id", "default")
    user_message = data["message"]
    if session_id not in conversation_store:
        conversation_store[session_id] = []
    conversation_store[session_id].append({"role": "user", "content": user_message})
    if agent.doit_resumer():
        agent.resumer(conversation_store[session_id])
    result = agent_camping(session_id, user_message)
    assistant_reply = result.get("response", "")
    conversation_store[session_id].append({"role": "assistant", "content": assistant_reply})
    return jsonify({"session_id": session_id, "response": assistant_reply, "collected": result.get("collected", {}), "ready": result.get("ready", False)})

@app.route("/reset", methods=["POST"])
def reset():
    data = request.get_json()
    session_id = data.get("session_id", "default")
    conversation_store.pop(session_id, None)
    return jsonify({"status": "ok", "session_id": session_id})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "alive"})

if __name__ == "__main__":
    app.run(debug=True)
