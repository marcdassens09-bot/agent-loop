from memory_agent import MemoryAgent
agent = MemoryAgent()
from layout_agent import LayoutAgent
layout = LayoutAgent()
from debug_agent import DebugAgent
debug = DebugAgent()
from prospect_agent import ProspectAgent
prospect = ProspectAgent()
from deploy_agent import DeployAgent
deploy = DeployAgent()
from clients_agent import ClientsAgent
clients = ClientsAgent()
import os
import sys
import traceback
os.environ["PYTHONUTF8"] = "1"
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from agent import agent_camping
from search_agent import SearchAgent
search = SearchAgent()
load_dotenv()

app = Flask(__name__)
conversation_store = {}

# Configuration du logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        logger.info("=== Début requête /chat ===")
        data = request.get_json()
        logger.info(f"Données reçues: {data}")

        if not data or "message" not in data:
            logger.warning("Message manquant dans la requête")
            return jsonify({"error": "Champ message manquant"}), 400

        session_id = data.get("session_id", "default")
        user_message = data["message"]
        logger.info(f"Session: {session_id}, Message: {user_message[:50]}...")

        if session_id not in conversation_store:
            conversation_store[session_id] = []
        conversation_store[session_id].append({"role": "user", "content": user_message})

        logger.info("Vérification résumé...")
        if agent.doit_resumer():
            logger.info("Résumé en cours...")
            agent.resumer(conversation_store[session_id])

        logger.info("Appel agent_camping...")
        result = agent_camping(session_id, user_message)
        logger.info(f"Résultat agent_camping: {result}")

        assistant_reply = result.get("response", "")
        conversation_store[session_id].append({"role": "assistant", "content": assistant_reply})

        logger.info("=== Fin requête /chat - Succès ===")
        return jsonify({"session_id": session_id, "response": assistant_reply, "collected": result.get("collected", {}), "ready": result.get("ready", False)})

    except Exception as e:
        logger.error(f"ERREUR dans /chat: {str(e)}")
        logger.error(f"Traceback complet:\n{traceback.format_exc()}")
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route("/reset", methods=["POST"])
def reset():
    try:
        data = request.get_json()
        session_id = data.get("session_id", "default")
        logger.info(f"Réinitialisation session: {session_id}")
        conversation_store.pop(session_id, None)
        logger.info(f"Session {session_id} réinitialisée")
        return jsonify({"status": "ok", "session_id": session_id})
    except Exception as e:
        logger.error(f"ERREUR dans /reset: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "alive"})

if __name__ == "__main__":
    app.run(debug=True)
