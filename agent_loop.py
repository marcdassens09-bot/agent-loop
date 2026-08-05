# -*- coding: utf-8 -*-
"""
agent_loop.py — Modèle de boucle d'agent (agent loop) pour MP Solutions IA.

Différence avec les autres bots du dépôt (agent.py, mpsolutionsia_app.py...) :
ceux-là font UN SEUL appel à l'API et Claude répond avec ce qu'il sait.
Ici, Claude dispose d'OUTILS (des fonctions Python ci-dessous). Le déroulé :

    1. On envoie la question + la liste des outils.
    2. Claude répond soit avec du texte (fini), soit avec une demande
       d'outil (stop_reason == "tool_use").
    3. Notre code exécute l'outil demandé et renvoie le résultat.
    4. Retour à l'étape 2 — Claude peut enchaîner plusieurs outils.

C'est cette boucle "demande d'outil -> exécution -> résultat -> on continue"
qu'on appelle une agent loop.

Usage :
    python agent_loop.py                       -> question de démonstration
    python agent_loop.py "ta question ici"     -> ta propre question
"""

import os
import sys
import json
from datetime import date
from pathlib import Path

import httpx
import requests
from dotenv import load_dotenv
from anthropic import Anthropic

# Charger le .env qui est À CÔTÉ de ce script, peu importe d'où on lance la commande
load_dotenv(Path(__file__).parent / ".env")

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY", "").strip(),
    timeout=httpx.Timeout(60.0),
    max_retries=3,
)

MODELE = "claude-sonnet-4-6"

# Les 7 services Render du parc (repris de verifier_services.py)
SERVICES = {
    "mpsolutionsia": "https://mpsolutionsia.onrender.com",
    "agent-loop": "https://agent-loop.onrender.com",
    "chatbot-camping-eychecadous": "https://chatbot-camping-eychecadous.onrender.com",
    "assistant-mpsolutions": "https://assistant-mpsolutions.onrender.com",
    "demo-chatbot-ia": "https://demo-chatbot-ia.onrender.com",
    "chatbot-ia-cleanpro-1": "https://chatbot-ia-cleanpro-1.onrender.com",
    "chatbot-ia-camping": "https://chatbot-ia-camping.onrender.com",
}


# ---------------------------------------------------------------------------
# 1. LES OUTILS — de simples fonctions Python.
#    Claude ne les exécute pas lui-même : il DEMANDE à les utiliser,
#    et c'est notre boucle qui les exécute et lui renvoie le résultat.
# ---------------------------------------------------------------------------

def calculer_nombre_nuits(date_arrivee: str, date_depart: str) -> str:
    arrivee = date.fromisoformat(date_arrivee)
    depart = date.fromisoformat(date_depart)
    nuits = (depart - arrivee).days
    if nuits <= 0:
        raise ValueError("La date de départ doit être après la date d'arrivée.")
    return json.dumps({"nombre_nuits": nuits})


def calculer_tarif_emplacement(
    nb_nuits: int,
    nb_adultes: int,
    nb_enfants_7_a_17: int = 0,
    nb_enfants_3_a_7: int = 0,
    nb_enfants_moins_3: int = 0,
    vehicules_supplementaires: int = 0,
) -> str:
    """Tarifs emplacements du Camping Les Eychecadous (saison 2026)."""
    personnes_7_et_plus = nb_adultes + nb_enfants_7_a_17
    if personnes_7_et_plus < 1:
        raise ValueError("Il faut au moins un adulte.")

    if personnes_7_et_plus == 1 and nb_enfants_3_a_7 == 0 and nb_enfants_moins_3 == 0:
        base = 11.00          # forfait randonneur (1 personne + 1 véhicule)
        supplement_personnes = 0.0
    else:
        base = 18.50          # forfait 2 personnes avec électricité
        supplement_personnes = (
            max(0, personnes_7_et_plus - 2) * 4.50
            + nb_enfants_3_a_7 * 3.50
            # moins de 3 ans : gratuit
        )

    par_nuit = base + supplement_personnes + vehicules_supplementaires * 2.50
    taxe_sejour = 0.86 * nb_adultes * nb_nuits
    total = par_nuit * nb_nuits + taxe_sejour + 10.00  # + frais de dossier

    return json.dumps({
        "prix_par_nuit_hors_taxe": round(par_nuit, 2),
        "taxe_sejour": round(taxe_sejour, 2),
        "frais_dossier": 10.00,
        "total_sejour": round(total, 2),
    })


def verifier_service_render(nom_service: str) -> str:
    """Teste si un service Render du parc répond (attention : ~50 s s'il dort)."""
    url = SERVICES.get(nom_service)
    if url is None:
        raise ValueError(f"Service inconnu. Choisir parmi : {', '.join(SERVICES)}")
    try:
        reponse = requests.get(f"{url}/health", timeout=70)
        return json.dumps({"service": nom_service, "code_http": reponse.status_code,
                           "corps": reponse.text[:300]})
    except requests.RequestException as erreur:
        return json.dumps({"service": nom_service, "erreur": str(erreur)})


# Ce que Claude voit : nom, description, et schéma des paramètres.
# La description est cruciale — c'est elle qui lui dit QUAND utiliser l'outil.
OUTILS = [
    {
        "name": "calculer_nombre_nuits",
        "description": "Calcule le nombre de nuits entre deux dates. À utiliser "
                       "dès qu'un séjour est donné avec des dates plutôt qu'un "
                       "nombre de nuits.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date_arrivee": {"type": "string", "description": "Format AAAA-MM-JJ"},
                "date_depart": {"type": "string", "description": "Format AAAA-MM-JJ"},
            },
            "required": ["date_arrivee", "date_depart"],
        },
    },
    {
        "name": "calculer_tarif_emplacement",
        "description": "Calcule le tarif exact d'un séjour en emplacement au "
                       "Camping Les Eychecadous (taxe de séjour et frais de "
                       "dossier inclus). Toujours utiliser cet outil pour un "
                       "prix : ne jamais calculer de tête.",
        "input_schema": {
            "type": "object",
            "properties": {
                "nb_nuits": {"type": "integer"},
                "nb_adultes": {"type": "integer", "description": "18 ans et plus"},
                "nb_enfants_7_a_17": {"type": "integer"},
                "nb_enfants_3_a_7": {"type": "integer"},
                "nb_enfants_moins_3": {"type": "integer"},
                "vehicules_supplementaires": {"type": "integer",
                                              "description": "Véhicules au-delà du premier"},
            },
            "required": ["nb_nuits", "nb_adultes"],
        },
    },
    {
        "name": "verifier_service_render",
        "description": "Vérifie qu'un des 7 services Render de MP Solutions "
                       "répond. Peut prendre ~50 secondes si l'instance "
                       "gratuite dort.",
        "input_schema": {
            "type": "object",
            "properties": {
                "nom_service": {"type": "string", "enum": list(SERVICES)},
            },
            "required": ["nom_service"],
        },
    },
]

IMPLEMENTATIONS = {
    "calculer_nombre_nuits": calculer_nombre_nuits,
    "calculer_tarif_emplacement": calculer_tarif_emplacement,
    "verifier_service_render": verifier_service_render,
}

SYSTEM_PROMPT = (
    "Tu es un agent interne de MP Solutions IA (outil de démonstration, pas un "
    "bot public). Tu disposes d'outils : utilise-les plutôt que de deviner. "
    "Réponds en français, de façon concise."
)


# ---------------------------------------------------------------------------
# 2. LA BOUCLE D'AGENT — le cœur du fichier.
# ---------------------------------------------------------------------------

def boucle_agent(question: str, max_tours: int = 10,
                 outils=None, implementations=None, system=None) -> str:
    """Boucle générique : réutilisable par d'autres agents du dépôt
    (voir agent_surveillance.py) en passant leurs propres outils."""
    outils = OUTILS if outils is None else outils
    implementations = IMPLEMENTATIONS if implementations is None else implementations
    system = SYSTEM_PROMPT if system is None else system

    messages = [{"role": "user", "content": question}]
    texte_final = ""

    for tour in range(1, max_tours + 1):
        reponse = client.messages.create(
            model=MODELE,
            max_tokens=2048,
            system=system,
            tools=outils,
            messages=messages,
        )

        # Afficher le texte éventuel de ce tour
        for bloc in reponse.content:
            if bloc.type == "text":
                texte_final = bloc.text
                print(bloc.text)

        # Claude a fini ? On sort de la boucle.
        if reponse.stop_reason != "tool_use":
            break

        # Sinon : exécuter TOUS les outils demandés ce tour-ci,
        # et renvoyer TOUS les résultats dans un seul message user.
        messages.append({"role": "assistant", "content": reponse.content})
        resultats = []
        for bloc in reponse.content:
            if bloc.type != "tool_use":
                continue
            print(f"  [outil] {bloc.name}({json.dumps(bloc.input, ensure_ascii=False)})")
            try:
                contenu = implementations[bloc.name](**bloc.input)
                erreur = False
            except Exception as e:
                # On renvoie l'erreur à Claude (is_error) : il peut se corriger
                contenu = f"Erreur : {e}"
                erreur = True
            print(f"  [resultat] {contenu}")
            resultats.append({
                "type": "tool_result",
                "tool_use_id": bloc.id,   # doit correspondre à la demande
                "content": contenu,
                "is_error": erreur,
            })
        messages.append({"role": "user", "content": resultats})
    else:
        print(f"(arrêt de sécurité après {max_tours} tours)")

    return texte_final


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or (
        "Combien coûte un séjour en emplacement du 2026-08-10 au 2026-08-15 "
        "pour 2 adultes et 2 enfants de 5 et 9 ans ?"
    )
    print(f"Question : {question}\n")
    boucle_agent(question)
