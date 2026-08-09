"""
Application Flask pour mpsolutionsia.fr
Route POST /chat avec système de métiers multiples.
"""

import os
import logging
import traceback
import sys
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from anthropic import Anthropic, APIConnectionError, APITimeoutError
import httpx
from mp_system_prompts import get_system_prompt, get_available_metiers

# Configuration
load_dotenv()
os.environ["PYTHONUTF8"] = "1"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Application Flask
app = Flask(__name__)

# Client Anthropic avec timeouts pour Render
api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
logger.info(f"[STARTUP] ANTHROPIC_API_KEY présente: {bool(api_key)}")
if api_key:
    logger.info(f"[STARTUP] Clé API format: {api_key[:20]}...{api_key[-10:]}")
else:
    logger.error("[STARTUP] ⚠️  ANTHROPIC_API_KEY NOT SET! L'app ne fonctionnera pas sans elle!")

client = Anthropic(
    api_key=api_key,
    timeout=httpx.Timeout(60.0),
    max_retries=3
)
logger.info("[STARTUP] Client Anthropic initialisé")

# Stockage des conversations par session
conversation_store = {}


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint with API key status."""
    api_key_present = bool(os.getenv("ANTHROPIC_API_KEY", "").strip())
    if api_key_present:
        api_key_status = "configured"
    else:
        api_key_status = "missing"

    return jsonify({
        "status": "alive",
        "app": "mpsolutionsia",
        "api_key_set": api_key_present,
        "api_key_status": api_key_status,
        "endpoints": ["/health", "/metiers", "/chat", "/reset", "/diagnose"]
    }), 200 if api_key_present else 503


@app.route("/metiers", methods=["GET"])
def metiers():
    """Liste tous les métiers disponibles."""
    try:
        available = get_available_metiers()
        logger.info(f"Métiers demandés: {available}")
        return jsonify({
            "metiers": available,
            "count": len(available)
        }), 200
    except Exception as e:
        logger.error(f"Erreur dans /metiers: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/chat", methods=["POST"])
def chat():
    """
    Route principale pour le chat.

    Requête:
    {
        "message": "Bonjour, j'aimerais...",
        "metier": "plombier",
        "session_id": "optional_session_id"
    }

    Réponse:
    {
        "response": "Bonjour! ...",
        "session_id": "session_id",
        "metier": "plombier"
    }
    """
    try:
        logger.info("=== Début requête /chat ===")
        data = request.get_json()
        logger.info(f"Données reçues: {data}")

        # Validation des champs requis
        if not data:
            logger.warning("Aucune donnée reçue")
            return jsonify({"error": "Corps de requête vide"}), 400

        if "message" not in data:
            logger.warning("Champ 'message' manquant")
            return jsonify({"error": "Champ 'message' requis"}), 400

        if "metier" not in data:
            logger.warning("Champ 'metier' manquant")
            return jsonify({"error": "Champ 'metier' requis"}), 400

        message = data["message"]
        metier = data["metier"]
        session_id = data.get("session_id", f"default_{metier}")

        logger.info(f"Session: {session_id}, Métier: {metier}, Message: {message[:50]}...")

        # Valider le métier
        try:
            system_prompt = get_system_prompt(metier)
            logger.info(f"System prompt chargé pour: {metier}")
        except ValueError as e:
            logger.error(f"Métier invalide: {str(e)}")
            return jsonify({
                "error": str(e),
                "available_metiers": get_available_metiers()
            }), 400

        # Initialiser la conversation si nouvelle session
        if session_id not in conversation_store:
            conversation_store[session_id] = []
            logger.info(f"Nouvelle session créée: {session_id}")

        # Ajouter le message de l'utilisateur
        conversation_store[session_id].append({
            "role": "user",
            "content": message
        })

        # Vérifier que le client est initialisé
        if not client:
            raise Exception("Client Anthropic non initialisé - clé API manquante?")

        # Appeler l'API Anthropic
        logger.info(f"Appel API Anthropic pour {metier}...")
        logger.debug(f"Messages: {conversation_store[session_id]}")

        try:
            response = client.messages.create(
                model="claude-sonnet-5",
                max_tokens=1000,
                thinking={"type": "disabled"},
                system=system_prompt,
                messages=conversation_store[session_id]
            )
        except Exception as api_error:
            logger.error(f"Erreur API: {type(api_error).__name__}: {str(api_error)}")
            raise

        assistant_reply = response.content[0].text
        logger.info(f"Réponse reçue: {assistant_reply[:100]}...")

        # Stocker la réponse
        conversation_store[session_id].append({
            "role": "assistant",
            "content": assistant_reply
        })

        logger.info("=== Fin requête /chat - Succès ===")
        return jsonify({
            "response": assistant_reply,
            "session_id": session_id,
            "metier": metier
        }), 200

    except (APIConnectionError, APITimeoutError) as e:
        logger.error(f"ERREUR CONNEXION API: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        return jsonify({
            "error": "Erreur de connexion à l'API Anthropic",
            "details": str(e),
            "retry": True
        }), 503

    except Exception as e:
        logger.error(f"ERREUR dans /chat: {str(e)}")
        logger.error(f"Traceback complet:\n{traceback.format_exc()}")
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route("/reset", methods=["POST"])
def reset():
    """Réinitialise une session de conversation."""
    try:
        data = request.get_json()
        session_id = data.get("session_id", "default")

        logger.info(f"Réinitialisation session: {session_id}")
        conversation_store.pop(session_id, None)

        logger.info(f"Session {session_id} réinitialisée")
        return jsonify({
            "status": "ok",
            "session_id": session_id,
            "message": "Session réinitialisée"
        }), 200

    except Exception as e:
        logger.error(f"ERREUR dans /reset: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/diagnose", methods=["GET"])
def diagnose():
    """Endpoint de diagnostic pour vérifier la configuration."""
    diagnostics = {
        "status": "unknown",
        "app": "mpsolutionsia",
        "api_key_present": bool(os.getenv("ANTHROPIC_API_KEY", "").strip()),
        "available_metiers": get_available_metiers(),
        "connectivity": {},
        "errors": []
    }

    try:
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()

        if api_key:
            diagnostics["api_key_format"] = f"{api_key[:20]}...{api_key[-10:]}"

        # Test 1: DNS resolution
        logger.info("Test 1: Résolution DNS...")
        import socket
        try:
            ip = socket.gethostbyname("api.anthropic.com")
            diagnostics["connectivity"]["dns"] = f"✓ Résolvé en {ip}"
            logger.info(f"DNS OK: {ip}")
        except Exception as e:
            diagnostics["connectivity"]["dns"] = f"✗ Erreur DNS: {str(e)}"
            diagnostics["errors"].append(f"DNS: {str(e)}")
            logger.error(f"DNS FAIL: {str(e)}")

        # Test 2: HTTP connectivity
        logger.info("Test 2: Test connectivité HTTP...")
        try:
            import requests
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
            response = client.messages.create(
                model="claude-sonnet-5",
                max_tokens=10,
                thinking={"type": "disabled"},
                messages=[{"role": "user", "content": "Hi"}]
            )
            diagnostics["connectivity"]["anthropic_api"] = "✓ API fonctionne"
            diagnostics["status"] = "ok"
            logger.info("API Anthropic OK")
        except Exception as e:
            diagnostics["connectivity"]["anthropic_api"] = f"✗ Erreur API: {type(e).__name__}: {str(e)}"
            diagnostics["errors"].append(f"Anthropic API: {type(e).__name__}: {str(e)}")
            diagnostics["status"] = "error"
            logger.error(f"API FAIL: {type(e).__name__}: {str(e)}")

        logger.info(f"Diagnostics: {diagnostics}")
        return jsonify(diagnostics), 200 if diagnostics["status"] == "ok" else 503

    except Exception as e:
        logger.error(f"Erreur dans /diagnose: {str(e)}")
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Gère les routes non trouvées."""
    return jsonify({
        "error": "Route non trouvée",
        "available_endpoints": [
            "GET /health",
            "GET /metiers",
            "GET /diagnose",
            "POST /chat",
            "POST /reset"
        ]
    }), 404


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logger.info(f"Démarrage application mpsolutionsia sur le port {port}")
    app.run(debug=True, port=port)
