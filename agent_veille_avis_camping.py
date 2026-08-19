# -*- coding: utf-8 -*-
"""
agent_veille_avis_camping.py — Veille avis clients du Camping Les Eychecadous.

Réutilise la boucle générique de agent_loop.py, avec un seul outil (même
principe que agent_veille_immo.py) : lire le texte d'une page publique
donnée. Trois pages d'avis connues sont préconfigurées (TripAdvisor,
Camping2be, Petit Futé) — trouvées le 19/08/2026 par recherche web, testées
et exploitables en HTTP simple (pas de rendu JS bloquant à ce jour).

Ce que ce prototype démontre : synthétiser plusieurs sources d'avis en un
point unique, sans qu'Anthony ait à aller les consulter une par une.

Ce que ce prototype NE fait PAS (limites assumées) :
    - il ne couvre pas Booking.com (HTTP 202 observé, probablement un
      défi anti-robot/JS — non exploité ici) ni Google Business Profile
      (URL non identifiée pour ce camping au 19/08/2026, à trouver si
      Anthony a une fiche) ;
    - il ne détecte pas les nouveaux avis depuis la dernière fois (pas de
      mémoire d'un état précédent) : chaque lancement resynthétise tout
      ce qui est visible sur la page, pas seulement les avis récents ;
    - les sites d'avis peuvent changer leur protection anti-robot à tout
      moment — un échec de lecture n'est pas forcément un signe qu'il n'y
      a rien à signaler.

Usage :
    python agent_veille_avis_camping.py                  -> tour des 3 sources connues
    python agent_veille_avis_camping.py "ta question"    -> question ciblée
"""

import sys
import re
import json
import urllib.request

from agent_loop import boucle_agent

SOURCES_CONNUES = {
    "tripadvisor": "https://www.tripadvisor.com/Hotel_Review-g5456675-d15127892-Reviews-Camping_Les_Eychecadous-Artigat_Ariege_Occitanie.html",
    "camping2be": "https://en.camping2be.com/france/artigat/client-reviews-camping-les-eychecadous",
    "petit_fute": "https://www.petitfute.com/v22927-artigat-09130/c1166-hebergement/c1047-camping-hotellerie-de-plein-air/c178-camping/516434-camping-les-eychecadous.html",
}


# ---------------------------------------------------------------------------
# 1. LES OUTILS
# ---------------------------------------------------------------------------

def lire_page_avis(source: str) -> str:
    """Récupère le texte lisible d'une page d'avis — soit une des sources
    connues (nom court), soit une URL complète fournie par l'utilisateur."""
    url = SOURCES_CONNUES.get(source, source)
    requete = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; MPSolutionsIA-veille/1.0)"},
    )
    try:
        with urllib.request.urlopen(requete, timeout=15) as reponse:
            html = reponse.read().decode("utf-8", errors="replace")
    except Exception as e:
        raise ValueError(f"Page inaccessible ({url}) : {e}")

    html = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    texte = re.sub(r"(?s)<[^>]+>", " ", html)
    texte = re.sub(r"\s+", " ", texte).strip()

    return json.dumps({
        "source": source,
        "url": url,
        "extrait": texte[:6000],
        "tronque": len(texte) > 6000,
    }, ensure_ascii=False)


OUTILS = [
    {
        "name": "lire_page_avis",
        "description": "Récupère le texte d'une page d'avis clients du "
                       "Camping Les Eychecadous. Utiliser un des noms courts "
                       "connus (tripadvisor, camping2be, petit_fute) pour "
                       "faire le tour des sources habituelles, ou une URL "
                       "complète si l'utilisateur en donne une nouvelle. "
                       "Ne jamais inventer une URL non fournie.",
        "input_schema": {
            "type": "object",
            "properties": {
                "source": {"type": "string",
                           "description": "Nom court (tripadvisor, camping2be, "
                                          "petit_fute) ou URL complète"},
            },
            "required": ["source"],
        },
    },
]

IMPLEMENTATIONS = {
    "lire_page_avis": lire_page_avis,
}

SYSTEM_PROMPT = (
    "Tu es l'agent de veille avis clients du Camping Les Eychecadous, "
    "outil interne de MP Solutions IA (pas un bot public). Ton rôle : lire "
    "les pages d'avis (TripAdvisor, Camping2be, Petit Futé, ou toute URL "
    "fournie) et en tirer une synthèse utile pour Anthony (le gérant), qui "
    "n'ira pas les consulter une par une. Structure la réponse en 2 "
    "parties : 1) Note et tendance générale par source — reste factuel, ne "
    "moyenne pas des notes sur des échelles différentes (/5, /10, /20) "
    "sans le préciser. 2) Ce qui ressort des avis — points positifs "
    "récurrents, et surtout tout avis négatif ou point de friction "
    "signalé, à traiter en priorité. Si une page est inaccessible (bloquée, "
    "changée), dis-le clairement plutôt que d'inventer un contenu. Ne "
    "cite jamais un avis in extenso — reformule. Réponds en français, "
    "sans emoji (charte MP Solutions IA), ton simple pour quelqu'un qui "
    "gère un camping, pas un technicien."
)


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or (
        "Fais le tour des 3 sources d'avis connues (tripadvisor, "
        "camping2be, petit_fute) et synthétise ce qu'il faut retenir pour "
        "Anthony."
    )
    print(f"Question : {question}\n")
    boucle_agent(question, max_tours=6, outils=OUTILS,
                 implementations=IMPLEMENTATIONS, system=SYSTEM_PROMPT)
