# -*- coding: utf-8 -*-
"""
rapport_lundi.py — Rapport du lundi MP Solutions IA, envoyé par email.

Rassemble dans un seul email :
    - le rapport IA (/rapport?format=json) de chaque chatbot ;
    - les visiteurs des 7 derniers jours du site vitrine (API GoatCounter).
Envoi par l'API Brevo, depuis l'adresse déjà vérifiée du camping.

Lancé chaque lundi par .github/workflows/rapport-lundi.yml (marche PC éteint).
Variables (secrets GitHub) :
    RAPPORT_CLE_CAMPING, RAPPORT_CLE_BULLE, RAPPORT_CLE_DEMO
    GOATCOUNTER_TOKEN   jeton API GoatCounter (droit « lire les statistiques »)
    BREVO_API_KEY
    RAPPORT_DESTINATAIRE (facultatif, défaut contact@mpsolutionsia.fr)

Le dépôt est public, donc les journaux GitHub Actions aussi : le script
n'affiche jamais le contenu des rapports (questions de visiteurs), seulement
un statut par source.

Usage local : python rapport_lundi.py
"""

import html
import json
import os
import sys
import urllib.request
from datetime import date, timedelta
from urllib.parse import urlencode

import markdown

from verifier_services import ENTETE_SURVEILLANCE

# Instances Render gratuites : premier appel ~50s le temps du réveil.
TIMEOUT = 120

CHATBOTS = [
    # (nom affiché, url, variable de la clé /rapport)
    ("Camping Les Eychecadous", "https://chatbot-camping-eychecadous.onrender.com", "RAPPORT_CLE_CAMPING"),
    ("Bulle du site MP Solutions IA", "https://assistant-mpsolutions.onrender.com", "RAPPORT_CLE_BULLE"),
    ("Démo chatbot", "https://demo-chatbot-ia.onrender.com", "RAPPORT_CLE_DEMO"),
]
GOATCOUNTER = "https://mpsolutionsia.goatcounter.com"
BREVO_URL_ENVOI = "https://api.brevo.com/v3/smtp/email"
EXPEDITEUR = "contact@mpsolutionsia.fr"


def _get_json(url, entetes=None):
    requete = urllib.request.Request(url, headers={**ENTETE_SURVEILLANCE, **(entetes or {})})
    with urllib.request.urlopen(requete, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


def section_chatbot(nom, url, variable):
    """Retourne (html_de_la_section, ok)."""
    cle = os.environ.get(variable, "").strip()
    if not cle:
        return f"<h2>{html.escape(nom)}</h2><p><em>Clé {variable} absente : rapport non récupéré.</em></p>", False
    try:
        texte = _get_json(f"{url}/rapport?{urlencode({'cle': cle, 'format': 'json'})}")["rapport"]
    except Exception as e:
        return (f"<h2>{html.escape(nom)}</h2><p><em>Rapport indisponible "
                f"({html.escape(type(e).__name__)}).</em></p>"), False
    # Le texte vient d'un modèle nourri par les questions des visiteurs : HTML échappé.
    corps = markdown.markdown(html.escape(texte, quote=False), extensions=["tables"])
    return f"<h2>{html.escape(nom)}</h2>{corps}", True


def section_visiteurs(debut, fin):
    jeton = os.environ.get("GOATCOUNTER_TOKEN", "").strip()
    titre = "<h2>Visiteurs du site vitrine (GoatCounter)</h2>"
    if not jeton:
        return titre + "<p><em>GOATCOUNTER_TOKEN absent : chiffres non récupérés.</em></p>", False
    auth = {"Authorization": f"Bearer {jeton}"}
    periode = urlencode({"start": debut.isoformat(), "end": fin.isoformat()})
    try:
        total = _get_json(f"{GOATCOUNTER}/api/v0/stats/total?{periode}", auth)
        pages = _get_json(f"{GOATCOUNTER}/api/v0/stats/hits?{periode}&limit=5", auth)
    except Exception as e:
        return titre + f"<p><em>GoatCounter indisponible ({html.escape(type(e).__name__)}).</em></p>", False
    lignes = "".join(
        f"<tr><td>{html.escape(str(p.get('path', '')))}</td><td>{p.get('count', 0)}</td></tr>"
        for p in pages.get("hits", [])
    )
    return (titre + f"<p><strong>{total.get('total', 0)}</strong> visites du "
            f"{debut:%d/%m} au {fin:%d/%m}.</p>"
            f"<table><tr><th>Page</th><th>Visites</th></tr>{lignes}</table>"), True


def construire_email(aujourd_hui):
    fin = aujourd_hui - timedelta(days=1)
    debut = fin - timedelta(days=6)
    sections, statuts = [], []
    html_visiteurs, ok = section_visiteurs(debut, fin)
    sections.append(html_visiteurs)
    statuts.append(("GoatCounter", ok))
    for nom, url, variable in CHATBOTS:
        html_chatbot, ok = section_chatbot(nom, url, variable)
        sections.append(html_chatbot)
        statuts.append((nom, ok))
    corps = (
        "<div style='font-family:Arial,sans-serif;color:#1b3a2b;max-width:760px'>"
        f"<h1>Rapport du lundi — semaine du {debut:%d/%m} au {fin:%d/%m}</h1>"
        + "<hr>".join(sections)
        + "<p style='font-size:11px;opacity:.6'>Envoyé automatiquement par agent-loop "
          "(rapport_lundi.py).</p></div>"
    )
    return f"Rapport du lundi {aujourd_hui:%d/%m/%Y}", corps, statuts


def envoyer(sujet, corps_html):
    cle = os.environ.get("BREVO_API_KEY", "").strip()
    if not cle:
        raise RuntimeError("BREVO_API_KEY absente")
    donnees = {
        "sender": {"name": "Rapports MP Solutions IA", "email": EXPEDITEUR},
        "to": [{"email": os.environ.get("RAPPORT_DESTINATAIRE", EXPEDITEUR)}],
        "subject": sujet,
        "htmlContent": corps_html,
    }
    requete = urllib.request.Request(
        BREVO_URL_ENVOI, data=json.dumps(donnees).encode("utf-8"), method="POST",
        headers={"api-key": cle, "Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(requete, timeout=30) as r:
        r.read()


def main():
    sujet, corps, statuts = construire_email(date.today())
    for nom, ok in statuts:
        print(f"{'OK ' if ok else 'KO '} {nom}")
    envoyer(sujet, corps)
    print("Email envoyé.")
    # L'email part quand même si une source manque (il le signale) ; le job
    # passe en échec pour que GitHub prévienne.
    return 0 if all(ok for _, ok in statuts) else 1


if __name__ == "__main__":
    sys.exit(main())
