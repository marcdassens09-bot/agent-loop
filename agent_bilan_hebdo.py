# -*- coding: utf-8 -*-
"""
agent_bilan_hebdo.py — Agent de bilan hebdomadaire MP Solutions IA.

Réutilise la boucle générique de agent_loop.py pour croiser deux sources
déjà existantes dans le dépôt, jusqu'ici consultées séparément :
    - clients_agent.py (ClientsAgent)      -> clients actifs, prospects,
                                               revenu mensuel, actions à faire
    - verifier_services.py (agent_surveillance) -> état du parc Render

Ce que l'agent NE fait PAS : il ne modifie rien dans ClientsAgent, ne
relance personne, ne consulte aucune donnée hors de ce dépôt (pas de
trésorerie Qonto, pas de dossiers Drive) — uniquement une synthèse de ce
que le code sait déjà. Pour que le bilan reste utile, le dict PROSPECTS de
clients_agent.py doit rester à jour (c'est déjà la règle d'usage de ce
fichier, pas une nouveauté de cet agent).

Usage :
    python agent_bilan_hebdo.py                  -> bilan complet de la semaine
    python agent_bilan_hebdo.py "ta question"    -> question ciblée
"""

import sys
import json

from agent_loop import boucle_agent
from clients_agent import ClientsAgent
from verifier_services import SERVICES, verifier_diagnose, verifier_chat

_agent_clients = ClientsAgent()


# ---------------------------------------------------------------------------
# 1. LES OUTILS
# ---------------------------------------------------------------------------

def tableau_de_bord_clients() -> str:
    """Clients actifs, revenu mensuel, prospects et actions à faire."""
    return json.dumps({
        "revenu_mensuel": _agent_clients.revenu_mensuel(),
        "nb_clients_actifs": len(_agent_clients.clients),
        "nb_prospects": len(_agent_clients.prospects),
        "actions_a_faire": _agent_clients.actions_a_faire(),
        "detail_clients": _agent_clients.clients,
        "detail_prospects": _agent_clients.prospects,
    }, ensure_ascii=False)


def verifier_tout_le_parc() -> str:
    """Teste les 7 services Render d'un coup (peut prendre plusieurs minutes
    si des instances gratuites dorment)."""
    resultats = []
    for nom, url, methode in SERVICES:
        if methode == "diagnose":
            ok, detail = verifier_diagnose(url)
        else:
            ok, detail = verifier_chat(url)
        resultats.append({"service": nom, "operationnel": ok, "detail": detail})
    return json.dumps(resultats, ensure_ascii=False)


OUTILS = [
    {
        "name": "tableau_de_bord_clients",
        "description": "Retourne l'état des clients actifs, des prospects et "
                       "des actions à faire, avec le revenu mensuel récurrent. "
                       "Toujours l'utiliser en premier pour un bilan.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "verifier_tout_le_parc",
        "description": "Teste les 7 services Render du parc. LONG (jusqu'à "
                       "plusieurs minutes) : ne l'utiliser que pour un bilan "
                       "complet, pas pour une question ciblée sur les clients.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

IMPLEMENTATIONS = {
    "tableau_de_bord_clients": tableau_de_bord_clients,
    "verifier_tout_le_parc": verifier_tout_le_parc,
}

SYSTEM_PROMPT = (
    "Tu es l'agent de bilan hebdomadaire interne de MP Solutions IA (outil "
    "de pilotage, pas un bot public). Ton rôle : croiser l'état des "
    "clients/prospects et l'état du parc de services pour produire une "
    "synthèse courte et actionnable, comme un point du lundi matin. "
    "Structure toujours la réponse en 3 parties : "
    "1) Revenu et clients actifs (le chiffre d'abord). "
    "2) Prospects — classe les actions par priorité, la plus urgente en tête. "
    "3) Parc technique — ne signale que ce qui ne fonctionne pas ; si tout va "
    "bien, dis-le en une ligne, ne détaille pas les 7 services un par un. "
    "N'invente aucune donnée absente des outils (pas de chiffre de "
    "trésorerie, pas de dossier en cours) : si une information manque, dis "
    "qu'elle n'est pas suivie ici plutôt que de la deviner. "
    "Réponds en français, de façon concise."
)


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or (
        "Fais le bilan hebdomadaire : clients, prospects à relancer en "
        "priorité, et état du parc technique."
    )
    print(f"Question : {question}\n")
    boucle_agent(question, max_tours=6, outils=OUTILS,
                 implementations=IMPLEMENTATIONS, system=SYSTEM_PROMPT)
