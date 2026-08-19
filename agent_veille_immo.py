# -*- coding: utf-8 -*-
"""
agent_veille_immo.py — Prototype de veille immobilière (pour ADESIMMO).

Troisième agent loop du dépôt : réutilise la boucle générique de
agent_loop.py, avec un seul outil, volontairement simple et générique :
lire le contenu texte d'une page web donnée.

Ce que ce prototype démontre : le mécanisme de la boucle d'agent
(demande d'outil -> exécution -> résultat -> synthèse par Claude)
appliqué à une page immobilière réelle.

Ce que ce prototype NE fait PAS (limites assumées, à dire à ADESIMMO) :
    - il ne contourne aucune protection anti-robot ni CAPTCHA — les grands
      portails d'annonces (SeLoger, Leboncoin, Bien'ici...) bloquent ce
      type d'accès automatisé et l'interdisent dans leurs conditions
      d'utilisation ; on ne les vise pas ici ;
    - il n'interroge pas l'API officielle DVF (Cerema/data.gouv.fr), qui
      serait la vraie source pour les ventes réalisées : son point d'accès
      public était instable au moment de ce prototype (pas de schéma
      disponible, requêtes en timeout) — à revérifier avant de s'appuyer
      dessus en production ;
    - il lit UNE page dont on lui donne l'URL — le site d'ADESIMMO
      lui-même, une source publique, ou tout autre lien fourni par eux.

Usage :
    python agent_veille_immo.py
    python agent_veille_immo.py "Résume les ventes récentes sur https://..."
"""

import sys
import re
import json
import urllib.request

from agent_loop import boucle_agent


# ---------------------------------------------------------------------------
# 1. L'OUTIL
# ---------------------------------------------------------------------------

def lire_page_web(url: str) -> str:
    """Récupère le texte lisible d'une page web publique (pas de JS, pas de
    contournement anti-robot : si la page bloque, l'outil échoue proprement)."""
    requete = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; MPSolutionsIA-veille/1.0)"},
    )
    try:
        with urllib.request.urlopen(requete, timeout=15) as reponse:
            html = reponse.read().decode("utf-8", errors="replace")
    except Exception as e:
        raise ValueError(f"Page inaccessible ({url}) : {e}")

    # Extraction de texte minimaliste, sans dépendance externe (pas de bs4
    # dans requirements.txt) : on retire scripts/styles puis toutes les balises.
    html = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    texte = re.sub(r"(?s)<[^>]+>", " ", html)
    texte = re.sub(r"\s+", " ", texte).strip()

    return json.dumps({
        "url": url,
        "extrait": texte[:4000],
        "tronque": len(texte) > 4000,
    }, ensure_ascii=False)


OUTILS = [
    {
        "name": "lire_page_web",
        "description": "Récupère et nettoie le texte d'une page web publique "
                       "(sans JavaScript, sans contournement anti-robot). "
                       "À utiliser pour lire une annonce, une page de "
                       "résultats ou toute page dont l'URL est donnée par "
                       "l'utilisateur — jamais une URL inventée.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL complète de la page à lire"},
            },
            "required": ["url"],
        },
    },
]

IMPLEMENTATIONS = {
    "lire_page_web": lire_page_web,
}

SYSTEM_PROMPT = (
    "Tu es un agent de veille immobilière interne, prototype pour ADESIMMO "
    "(agence immobilière). Tu disposes d'un outil pour lire le texte d'une "
    "page web dont l'URL t'est fournie. Tu ne visites jamais d'URL que tu "
    "aurais inventée toi-même — seulement celles données dans la question. "
    "Si l'outil échoue (page protégée, inaccessible), dis-le clairement "
    "plutôt que d'inventer un contenu. Résume ce que tu trouves de façon "
    "utile pour un professionnel de l'immobilier (biens, prix, statut). "
    "Réponds en français, de façon concise, sans emoji."
)


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or (
        "Lis cette page et résume ce qu'elle dit sur les ventes immobilières "
        "en France : https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres"
    )
    print(f"Question : {question}\n")
    boucle_agent(question, max_tours=6, outils=OUTILS,
                 implementations=IMPLEMENTATIONS, system=SYSTEM_PROMPT)
