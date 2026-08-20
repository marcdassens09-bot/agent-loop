# -*- coding: utf-8 -*-
"""
agent_relances.py — Agent de relance automatique des prospects MP Solutions IA.

Réutilise boucle_agent (même principe que agent_bilan_hebdo.py). Différence :
ne se contente pas de lire le texte statique de prochaine_action, il calcule
lui-même qui relancer à partir des dates déjà présentes dans les notes
(clients_agent.ClientsAgent.relances_prioritaires) — un prospect "en attente
de réponse" depuis plus de SEUIL_RELANCE_JOURS jours devient prioritaire tout
seul, sans qu'on ait à changer le texte à la main chaque semaine.

Usage :
    python agent_relances.py                  -> qui relancer aujourd'hui
    python agent_relances.py "ta question"    -> question ciblée
"""

import sys
import json

from agent_loop import boucle_agent
from clients_agent import ClientsAgent

_agent_clients = ClientsAgent()


def relances_du_jour() -> str:
    """Liste des prospects à relancer, triée par urgence (calcul automatique
    à partir des dates déjà notées, pas une liste figée)."""
    return json.dumps(_agent_clients.relances_prioritaires(), ensure_ascii=False)


OUTILS = [
    {
        "name": "relances_du_jour",
        "description": "Retourne, pour chaque prospect actif, le statut de "
                       "relance calculé automatiquement (À relancer / En "
                       "attente pas encore urgent / Action différente / Rien "
                       "en attente) et le nombre de jours depuis le dernier "
                       "contact connu. Toujours l'utiliser en premier.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

IMPLEMENTATIONS = {
    "relances_du_jour": relances_du_jour,
}

SYSTEM_PROMPT = (
    "Tu es l'agent de relance interne de MP Solutions IA (outil de pilotage, "
    "pas un bot public). Ton rôle : dire à Marc-Paul qui relancer aujourd'hui "
    "et pourquoi, à partir du calcul automatique de relances_du_jour — ne "
    "recalcule rien toi-même, le nombre de jours est déjà fourni. "
    "Structure la réponse en 2 parties : "
    "1) À relancer maintenant (urgence haute) — une ligne par prospect, avec "
    "le nombre de jours d'attente. "
    "2) Le reste, groupé rapidement (en attente pas encore urgent / action "
    "différente à faire), sans détailler chaque prospect un par un si le "
    "groupe est calme. "
    "N'invente aucune date ni aucun contenu de relance : si tu ne sais pas ce "
    "qui a déjà été envoyé, dis-le. Réponds en français, de façon concise et "
    "actionnable."
)


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or (
        "Qui dois-je relancer aujourd'hui parmi mes prospects, et pourquoi ?"
    )
    print(f"Question : {question}\n")
    boucle_agent(question, max_tours=4, outils=OUTILS,
                 implementations=IMPLEMENTATIONS, system=SYSTEM_PROMPT)
