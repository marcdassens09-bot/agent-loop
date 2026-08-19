# -*- coding: utf-8 -*-
"""
agent_digest_camping.py — Digest reporting du Camping Les Eychecadous.

Réutilise la boucle générique de agent_loop.py. Un seul outil : interroger
la route JSON /reporting/api du bot camping en prod (ajoutée dans
chatbot-camping-eychecadous/reporting_dashboard.py — même auth HTTP basique
que le dashboard /reporting existant, mot de passe REPORTING_PASSWORD).

But : au lieu d'attendre que quelqu'un aille consulter le dashboard,
produire un résumé lisible (tendance, urgences, questions sans réponse,
mots-clés) qu'on peut lire d'un coup d'œil ou envoyer à Anthony.

Ce que l'agent NE fait PAS : il ne modifie rien, n'envoie aucun message à
Anthony lui-même — il produit le texte du digest, à relire et envoyer.

Prérequis : la variable d'environnement CAMPING_REPORTING_PASSWORD doit
contenir le mot de passe REPORTING_PASSWORD du service Render
chatbot-camping-eychecadous (Dashboard Render -> Environment). Absente du
.env local au 19/08/2026 (voir mémoire dashboard-reporting-camping) — à
ajouter avant le premier usage réel.

Usage :
    python agent_digest_camping.py                  -> digest des 30 derniers jours
    python agent_digest_camping.py "ta question"    -> question ciblée
"""

import os
import sys
import json

import requests
from dotenv import load_dotenv
from pathlib import Path

from agent_loop import boucle_agent

load_dotenv(Path(__file__).parent / ".env")

URL_RAPPORT = "https://chatbot-camping-eychecadous.onrender.com/reporting/api"
MOT_DE_PASSE = os.getenv("CAMPING_REPORTING_PASSWORD", "").strip()


# ---------------------------------------------------------------------------
# 1. L'OUTIL
# ---------------------------------------------------------------------------

def recuperer_stats_reporting_camping() -> str:
    """Interroge la route JSON du dashboard reporting du bot camping en prod
    (30 derniers jours : volume, urgences, sans réponse, profils, mots-clés)."""
    if not MOT_DE_PASSE:
        raise ValueError(
            "CAMPING_REPORTING_PASSWORD absent du .env — récupérer la valeur "
            "de REPORTING_PASSWORD dans le Dashboard Render du service "
            "chatbot-camping-eychecadous (onglet Environment) avant de "
            "pouvoir interroger le reporting."
        )
    try:
        reponse = requests.get(URL_RAPPORT, auth=("", MOT_DE_PASSE), timeout=70)
    except requests.RequestException as e:
        raise ValueError(f"Reporting camping inaccessible : {e}")
    if reponse.status_code == 401:
        raise ValueError("Mot de passe reporting refusé (401) — vérifier CAMPING_REPORTING_PASSWORD.")
    if reponse.status_code != 200:
        raise ValueError(f"Reporting camping : code HTTP {reponse.status_code}")
    return reponse.text


OUTILS = [
    {
        "name": "recuperer_stats_reporting_camping",
        "description": "Récupère les statistiques de conversation des 30 "
                       "derniers jours du chatbot du Camping Les Eychecadous "
                       "(volume, urgences, messages sans réponse, profils de "
                       "visiteurs, mots-clés). Toujours l'utiliser avant de "
                       "rédiger le digest — ne jamais inventer de chiffre.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

IMPLEMENTATIONS = {
    "recuperer_stats_reporting_camping": recuperer_stats_reporting_camping,
}

SYSTEM_PROMPT = (
    "Tu es l'agent de digest reporting du Camping Les Eychecadous, un outil "
    "interne de MP Solutions IA (pas un bot public). Tu résumes les "
    "statistiques du chatbot du camping pour Anthony (le gérant), qui n'ira "
    "pas consulter le dashboard lui-même. Structure toujours la réponse en "
    "3 parties courtes : 1) Volume et tendance (le chiffre du total et son "
    "évolution sur les 7 derniers jours). 2) Points d'attention — messages "
    "urgents et sans réponse en premier, ils comptent plus que le volume. "
    "3) Ce que demandent les visiteurs — les mots-clés qui reviennent, "
    "traduits en langage clair (pas juste la liste brute). Si les "
    "statistiques sont vides ou minimes, dis-le simplement plutôt que "
    "d'extrapoler. Réponds en français, ton simple, pour quelqu'un qui gère "
    "un camping, pas un technicien. Jamais d'emoji (charte MP Solutions IA)."
)


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or (
        "Fais le digest reporting du camping des 30 derniers jours, prêt à "
        "envoyer à Anthony."
    )
    print(f"Question : {question}\n")
    boucle_agent(question, max_tours=4, outils=OUTILS,
                 implementations=IMPLEMENTATIONS, system=SYSTEM_PROMPT)
