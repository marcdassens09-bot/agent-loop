# -*- coding: utf-8 -*-
"""
agent_onboarding.py — Installe le chatbot d'un nouveau client MP Solutions IA.

On lui decrit le client en francais libre (nom, ville, activite, horaires,
tarifs, contact...) ; l'agent structure les informations, genere un projet
de bot complet depuis modele_bot/, puis verifie sa conformite (phrase IA Act,
pas de hotmail, pas de placeholder oublie, syntaxe Python).

Le projet est cree dans C:\\Projets\\<slug>\\ — le deploiement GitHub + Render
reste manuel, guide par le README genere (checklist incluant le piege de la
Start Command).

Usage :
    python agent_onboarding.py "Nouveau client : Boulangerie Dupont a Foix,
        ouverte 6h-19h sauf lundi, tel 05 61 00 00 00, ..."

REGLE D'OR : l'agent n'invente JAMAIS une information client. Ce qui n'a pas
ete fourni est signale comme manquant, pas comble.
"""

import sys
import json
import re
import py_compile
from datetime import date
from pathlib import Path

from agent_loop import boucle_agent

DOSSIER_MODELE = Path(__file__).parent / "modele_bot"
DOSSIER_PROJETS = Path("C:/Projets")

FICHIERS_MODELE = {
    "app_modele.py": "app.py",
    "README_modele.md": "README.md",
    "requirements_modele.txt": "requirements.txt",
    "Procfile_modele": "Procfile",
    "env_modele.txt": ".env.example",
}

PHRASE_IA_ACT = "assistant IA, pas un humain"


# ---------------------------------------------------------------------------
# OUTILS
# ---------------------------------------------------------------------------

def creer_projet_bot(slug: str, nom_entreprise: str, ville: str,
                     description_activite: str, infos_pratiques: str) -> str:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,40}", slug):
        raise ValueError("slug invalide : minuscules, chiffres et tirets "
                         "uniquement (ex. chatbot-boulangerie-dupont)")
    cible = DOSSIER_PROJETS / slug
    if cible.exists():
        raise ValueError(f"Le dossier {cible} existe deja : choisir un autre "
                         "slug ou le supprimer d'abord (je ne supprime rien).")

    remplacements = {
        "{{NOM_ENTREPRISE}}": nom_entreprise,
        "{{VILLE}}": ville,
        "{{DESCRIPTION_ACTIVITE}}": description_activite,
        "{{INFOS_PRATIQUES}}": infos_pratiques,
        "{{DATE_GENERATION}}": date.today().isoformat(),
    }

    cible.mkdir(parents=True)
    fichiers_crees = []
    for source, destination in FICHIERS_MODELE.items():
        contenu = (DOSSIER_MODELE / source).read_text(encoding="utf-8")
        for cle, valeur in remplacements.items():
            contenu = contenu.replace(cle, valeur)
        (cible / destination).write_text(contenu, encoding="utf-8", newline="\n")
        fichiers_crees.append(destination)
    (cible / ".gitignore").write_text(".env\n__pycache__/\n*.pyc\n",
                                      encoding="utf-8", newline="\n")
    fichiers_crees.append(".gitignore")

    return json.dumps({"dossier": str(cible), "fichiers": fichiers_crees},
                      ensure_ascii=False)


def verifier_conformite(slug: str) -> str:
    cible = DOSSIER_PROJETS / slug
    problemes = []

    app_py = cible / "app.py"
    if not app_py.exists():
        return json.dumps({"conforme": False,
                           "problemes": [f"{app_py} introuvable"]})

    contenu_app = app_py.read_text(encoding="utf-8")
    if PHRASE_IA_ACT not in contenu_app:
        problemes.append("phrase IA Act absente du prompt ('%s')" % PHRASE_IA_ACT)

    for fichier in cible.iterdir():
        if fichier.suffix in (".py", ".md", ".txt", "") and fichier.is_file():
            texte = fichier.read_text(encoding="utf-8", errors="replace")
            if "{{" in texte:
                problemes.append(f"placeholder non remplace dans {fichier.name}")
            if "hotmail" in texte.lower():
                problemes.append(f"adresse hotmail dans {fichier.name} "
                                 "(interdite : regression connue)")

    try:
        py_compile.compile(str(app_py), doraise=True)
    except py_compile.PyCompileError as e:
        problemes.append(f"erreur de syntaxe dans app.py : {e}")

    return json.dumps({"conforme": not problemes, "problemes": problemes},
                      ensure_ascii=False)


OUTILS = [
    {
        "name": "creer_projet_bot",
        "description": "Cree le projet complet d'un nouveau chatbot client "
                       "dans C:\\Projets\\<slug>\\ a partir du modele du parc "
                       "(app.py, README avec checklist Render, requirements, "
                       "Procfile, .env.example). Echoue si le dossier existe.",
        "input_schema": {
            "type": "object",
            "properties": {
                "slug": {"type": "string",
                         "description": "Nom du dossier/futur service, en "
                                        "minuscules-avec-tirets, commencant "
                                        "par 'chatbot-' (ex. chatbot-boulangerie-dupont)"},
                "nom_entreprise": {"type": "string"},
                "ville": {"type": "string"},
                "description_activite": {"type": "string",
                                         "description": "Courte apposition, ex. "
                                                        "'boulangerie-patisserie artisanale'"},
                "infos_pratiques": {"type": "string",
                                    "description": "Bloc texte structure en sections "
                                                   "(=== HORAIRES ===, === CONTACT ===, "
                                                   "=== TARIFS ===...) avec UNIQUEMENT "
                                                   "les informations fournies par "
                                                   "marc-paul. Ne rien inventer."},
            },
            "required": ["slug", "nom_entreprise", "ville",
                         "description_activite", "infos_pratiques"],
        },
    },
    {
        "name": "verifier_conformite",
        "description": "Verifie le projet genere : phrase IA Act presente, "
                       "aucun placeholder oublie, aucune adresse hotmail, "
                       "syntaxe Python valide. A appeler systematiquement "
                       "apres creer_projet_bot.",
        "input_schema": {
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
    },
]

IMPLEMENTATIONS = {
    "creer_projet_bot": creer_projet_bot,
    "verifier_conformite": verifier_conformite,
}

SYSTEM_PROMPT = (
    "Tu es l'agent d'onboarding interne de MP Solutions IA : tu installes le "
    "chatbot d'un nouveau client a partir de la description donnee par "
    "marc-paul. Demarche : 1) structurer les informations fournies (le bloc "
    "infos_pratiques en sections === HORAIRES ===, === CONTACT ===, etc.) ; "
    "2) creer le projet avec creer_projet_bot ; 3) verifier avec "
    "verifier_conformite ; 4) conclure avec : ce qui a ete cree, le resultat "
    "de la conformite, les informations MANQUANTES a demander au client, et "
    "les prochaines etapes (voir le README genere). REGLE D'OR : ne JAMAIS "
    "inventer une information client (horaires, tarifs, telephone...). Ce qui "
    "n'a pas ete fourni est liste comme manquant. Si la description est trop "
    "pauvre pour un bot utile (ni contact ni horaires), cree quand meme le "
    "projet mais dis clairement ce qu'il faudra completer avant deploiement. "
    "Precision technique : la cle API du parc est une cle ANTHROPIC "
    "(ANTHROPIC_API_KEY), ne jamais parler d'OpenAI. Reponds en francais."
)


if __name__ == "__main__":
    description = " ".join(sys.argv[1:])
    if not description.strip():
        print("Usage : python agent_onboarding.py \"Nouveau client : ...\"")
        sys.exit(1)
    boucle_agent(description, max_tours=8, outils=OUTILS,
                 implementations=IMPLEMENTATIONS, system=SYSTEM_PROMPT)
