# -*- coding: utf-8 -*-
"""
mcp_serveur_surveillance.py — Serveur MCP pour la surveillance du parc
MP Solutions IA.

Différence avec agent_surveillance.py : ce fichier n'appelle PAS Claude
lui-même. Il expose les outils de verifier_services.py au format MCP
(Model Context Protocol), pour que N'IMPORTE QUEL client MCP — Claude Code
dans cette session, Claude Desktop, un autre agent — puisse les appeler
directement, sans repasser par boucle_agent.

Trois outils exposés :
    - verifier_un_service(nom_service)  : teste un service, rapide
    - verifier_tout_le_parc()           : teste les 6 services, long
    - consulter_memo_pannes()           : le mémo des pannes connues

Aucun secret n'est manipulé : comme verifier_services.py, ce serveur
n'interroge que des URLs publiques.

Pour le brancher sur Claude Code : voir .mcp.json à la racine du dépôt.

Test manuel (mode debug, ouvre un inspecteur web) :
    mcp dev mcp_serveur_surveillance.py
"""

import time

from mcp.server.fastmcp import FastMCP

from verifier_services import SERVICES, verifier_diagnose, verifier_chat

mcp = FastMCP("surveillance-mp-solutions")

MEMO_PANNES = """MEMO DES PANNES CONNUES (parc MP Solutions, vérifié août 2026)

1. START COMMAND RENDER : le dashboard écrase le Procfile. Render auto-détecte
   app.py et préremplit "gunicorn app:app" — on modifie alors un fichier jamais
   chargé et aucun correctif n'a d'effet. Sur mpsolutionsia, GET /health doit
   renvoyer "api_key_set" ; s'il ne renvoie que {"status":"alive"}, c'est
   app.py qui tourne au lieu de mpsolutionsia_app.py.

2. CLES API PAR SERVICE : chaque service Render a ses propres variables
   d'environnement. Une rotation de clé doit être répercutée sur CHAQUE
   service (onglet Environment), sinon 401. Le .env du PC local est un
   endroit de plus, souvent oublié.

3. REPONSES DE REPLI : un service sans clé valide répond souvent HTTP 200
   avec un message générique ("erreur technique", "désolé, j'ai rencontré un
   problème") au lieu d'une vraie réponse. Un 200 ne prouve rien : il faut
   lire le contenu.

4. INSTANCES GRATUITES : elles s'endorment. Premier appel ~50 s. Un timeout
   sur un seul appel n'est pas une panne ; deux échecs de suite, si.

5. CONSOLE ANTHROPIC : la colonne "Dernière utilisation" des clés a un retard
   énorme (elle affichait "—" pour des clés servant 7 services). Ne jamais
   s'en servir pour décider qu'une clé est libre.

6. DEPOTS : agent-loop alimente 2 services (mpsolutionsia + agent-loop).
   Le bot camping vit dans un dépôt séparé (chatbot-camping-eychecadous).
   Le site vitrine et sa bulle sont dans C:\\Projets\\ (site-mpsolutions
   + assistant-mpsolutions)."""


def _tester(nom, url, methode):
    debut = time.time()
    if methode == "diagnose":
        ok, detail = verifier_diagnose(url)
    else:
        ok, detail = verifier_chat(url)
    return {
        "service": nom,
        "operationnel": ok,
        "detail": detail,
        "duree_secondes": round(time.time() - debut),
        "methode_de_test": methode,
    }


@mcp.tool()
def verifier_un_service(nom_service: str) -> dict:
    """Teste UN service Render du parc MP Solutions (vraie réponse vs message
    de repli). Rapide : un seul appel, mais compter ~50 s si l'instance
    gratuite dort.

    nom_service doit être l'un de : mpsolutionsia, chatbot-camping-eychecadous,
    assistant-mpsolutions, demo-chatbot-ia, chatbot-ia-cleanpro-1,
    chatbot-ia-camping.
    """
    for nom, url, methode in SERVICES:
        if nom == nom_service:
            return _tester(nom, url, methode)
    connus = ", ".join(n for n, _, _ in SERVICES)
    raise ValueError(f"Service inconnu : '{nom_service}'. Choisir parmi : {connus}")


@mcp.tool()
def verifier_tout_le_parc() -> list[dict]:
    """Teste les 6 services Render du parc d'un coup. LONG (jusqu'à plusieurs
    minutes si des instances dorment) : ne l'utiliser que pour un bilan
    complet demandé explicitement."""
    return [_tester(nom, url, methode) for nom, url, methode in SERVICES]


@mcp.tool()
def consulter_memo_pannes() -> str:
    """Retourne le mémo des pannes connues du parc MP Solutions (piège Start
    Command Render, clés API par service, réponses de repli...). À consulter
    AVANT de conclure sur la cause d'une panne."""
    return MEMO_PANNES


if __name__ == "__main__":
    mcp.run()
