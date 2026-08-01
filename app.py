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
from anthropic import APIConnectionError, APITimeoutError
import requests
import socket
import httpx
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

    except (APIConnectionError, APITimeoutError) as e:
        logger.error(f"ERREUR CONNEXION API: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        return jsonify({
            "error": "Erreur de connexion à l'API (free tier Render ?)",
            "details": str(e),
            "retry": True
        }), 503
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

@app.route("/diagnose", methods=["GET"])
def diagnose():
    """Endpoint de diagnostic pour vérifier la connexion API Anthropic."""
    diagnostics = {
        "status": "unknown",
        "api_key_present": bool(os.getenv("ANTHROPIC_API_KEY", "").strip()),
        "api_key_format": "",
        "connectivity": {},
        "errors": []
    }

    try:
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if api_key:
            diagnostics["api_key_format"] = f"{api_key[:20]}...{api_key[-10:]}"

        # Test 1: DNS resolution
        logger.info("Test 1: Résolution DNS pour api.anthropic.com...")
        import socket
        try:
            ip = socket.gethostbyname("api.anthropic.com")
            diagnostics["connectivity"]["dns"] = f"✓ Résolvé en {ip}"
            logger.info(f"DNS OK: api.anthropic.com → {ip}")
        except Exception as e:
            diagnostics["connectivity"]["dns"] = f"✗ Erreur DNS: {str(e)}"
            diagnostics["errors"].append(f"DNS: {str(e)}")
            logger.error(f"DNS FAIL: {str(e)}")

        # Test 2: HTTP connectivity
        logger.info("Test 2: Test de connectivité HTTP...")
        try:
            response = requests.head("https://api.anthropic.com", timeout=10)
            diagnostics["connectivity"]["http"] = f"✓ Status {response.status_code}"
            logger.info(f"HTTP OK: Status {response.status_code}")
        except Exception as e:
            diagnostics["connectivity"]["http"] = f"✗ Erreur HTTP: {str(e)}"
            diagnostics["errors"].append(f"HTTP: {str(e)}")
            logger.error(f"HTTP FAIL: {str(e)}")

        # Test 3: Appel API Anthropic
        logger.info("Test 3: Test appel API Anthropic...")
        try:
            from anthropic import Anthropic
            test_api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
            test_client = Anthropic(api_key=test_api_key, timeout=httpx.Timeout(30.0))
            response = test_client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            diagnostics["connectivity"]["anthropic_api"] = "✓ API fonctionne"
            diagnostics["status"] = "ok"
            logger.info("API Anthropic OK")
        except Exception as e:
            diagnostics["connectivity"]["anthropic_api"] = f"✗ Erreur API: {type(e).__name__}: {str(e)}"
            diagnostics["errors"].append(f"Anthropic API: {type(e).__name__}: {str(e)}")
            logger.error(f"API FAIL: {type(e).__name__}: {str(e)}")
            diagnostics["status"] = "error"

        logger.info(f"Diagnostics: {diagnostics}")
        return jsonify(diagnostics), 200 if diagnostics["status"] == "ok" else 503

    except Exception as e:
        logger.error(f"Erreur dans /diagnose: {str(e)}")
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

if __name__ == "__main__":
    app.run(debug=True)
