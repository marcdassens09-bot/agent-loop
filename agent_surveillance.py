# -*- coding: utf-8 -*-
"""
agent_surveillance.py — Agent de surveillance du parc MP Solutions IA.

Deuxième agent loop du dépôt : il réutilise la boucle générique de
agent_loop.py, mais avec ses propres outils, construits sur
verifier_services.py (le script qu'on lance avant/après les rotations
de clés).

Ce que l'agent sait faire :
    - vérifier UN service (rapide) ou TOUT le parc (long : les
      instances gratuites Render dorment, ~50 s de réveil chacune) ;
    - consulter le mémo des pannes connues pour diagnostiquer ;
    - proposer le correctif — il ne modifie RIEN lui-même.

Usage :
    python agent_surveillance.py                          -> bilan complet du parc
    python agent_surveillance.py "ta question"            -> question libre
    Exemples :
        python agent_surveillance.py "mpsolutionsia repond-il ?"
        python agent_surveillance.py "le bot camping renvoie des erreurs, diagnostique"
"""

import sys
import json
import time

# On réutilise la boucle générique et le client déjà configurés
from agent_loop import boucle_agent

# ... et les fonctions de vérification déjà écrites et éprouvées
from verifier_services import SERVICES, verifier_diagnose, verifier_chat


# ---------------------------------------------------------------------------
# 1. LES OUTILS
# ---------------------------------------------------------------------------

def verifier_un_service(nom_service: str) -> str:
    for nom, url, methode in SERVICES:
        if nom == nom_service:
            debut = time.time()
            if methode == "diagnose":
                ok, detail = verifier_diagnose(url)
            else:
                ok, detail = verifier_chat(url)
            return json.dumps({
                "service": nom, "operationnel": ok, "detail": detail,
                "duree_secondes": round(time.time() - debut),
                "methode_de_test": methode,
            }, ensure_ascii=False)
    raise ValueError(
        f"Service inconnu. Choisir parmi : {', '.join(n for n, _, _ in SERVICES)}"
    )


def verifier_tout_le_parc() -> str:
    resultats = []
    for nom, url, methode in SERVICES:
        debut = time.time()
        if methode == "diagnose":
            ok, detail = verifier_diagnose(url)
        else:
            ok, detail = verifier_chat(url)
        resultats.append({"service": nom, "operationnel": ok, "detail": detail,
                          "duree_secondes": round(time.time() - debut)})
    return json.dumps(resultats, ensure_ascii=False)


def consulter_memo_pannes() -> str:
    """Les leçons apprises sur ce parc — vérifiées en conditions réelles."""
    return """MEMO DES PANNES CONNUES (parc MP Solutions, vérifié août 2026)

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
   Le site vitrine et sa bulle sont dans C:\\Users\\marcd\\ (site-mpsolutions
   + assistant-mpsolutions)."""


OUTILS = [
    {
        "name": "verifier_un_service",
        "description": "Teste UN service Render du parc (vraie réponse vs "
                       "message de repli). Rapide : un seul appel, mais "
                       "compter ~50 s si l'instance dort.",
        "input_schema": {
            "type": "object",
            "properties": {
                "nom_service": {"type": "string",
                                "enum": [n for n, _, _ in SERVICES]},
            },
            "required": ["nom_service"],
        },
    },
    {
        "name": "verifier_tout_le_parc",
        "description": "Teste les 7 services Render d'un coup. LONG (jusqu'à "
                       "plusieurs minutes si des instances dorment) : ne "
                       "l'utiliser que pour un bilan complet demandé.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "consulter_memo_pannes",
        "description": "Retourne le mémo des pannes connues du parc (piège "
                       "Start Command, clés par service, réponses de repli...). "
                       "À consulter AVANT de conclure sur la cause d'une panne.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

IMPLEMENTATIONS = {
    "verifier_un_service": verifier_un_service,
    "verifier_tout_le_parc": verifier_tout_le_parc,
    "consulter_memo_pannes": consulter_memo_pannes,
}

SYSTEM_PROMPT = (
    "Tu es l'agent de surveillance interne du parc de chatbots MP Solutions IA "
    "(7 services Render). Tu vérifies, tu diagnostiques, tu proposes le "
    "correctif — mais tu ne modifies jamais rien toi-même. "
    "Avant de conclure sur la cause d'une panne, consulte le mémo des pannes "
    "connues. Termine toujours par : le constat, la cause probable, et les "
    "étapes concrètes du correctif (où cliquer, quoi vérifier). "
    "Réponds en français, de façon claire pour un non-informaticien."
)


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or (
        "Fais un bilan complet du parc et signale ce qui doit être corrigé."
    )
    print(f"Question : {question}\n")
    boucle_agent(question, max_tours=10, outils=OUTILS,
                 implementations=IMPLEMENTATIONS, system=SYSTEM_PROMPT)
