"""Verifie que tous les services MP Solutions repondent encore.

Usage :
    python verifier_services.py

A lancer AVANT une rotation de cle Anthropic pour etablir une reference,
puis APRES avoir remplace les cles, et enfin une derniere fois apres avoir
revoque l'ancienne cle. Un service qui passait et qui echoue signale une
cle manquante ou invalide sur ce service.

Aucun secret n'est manipule ici : le script interroge uniquement les URLs
publiques et regarde si la reponse est coherente.
"""

import json
import sys
import time
import urllib.request
import urllib.error

# Instances Render gratuites : premier appel ~50s le temps du reveil.
TIMEOUT = 120

# Les 6 services Render qui appellent l'API Anthropic.
# Les 2 restants (mp-solutions-ia, site-mpsolutions) sont des sites statiques :
# ils n'ont pas de cle et n'ont rien a verifier ici.
# agent-loop suspendu le 10/08/2026 (ancien doublon du bot camping, retire) :
# ne plus le tester ici tant qu'il n'est pas reactive.
SERVICES = [
    # (nom, url, methode de verification)
    ("mpsolutionsia",              "https://mpsolutionsia.onrender.com",              "diagnose"),
    ("chatbot-camping-eychecadous", "https://chatbot-camping-eychecadous.onrender.com", "diagnose"),
    ("assistant-mpsolutions",      "https://assistant-mpsolutions.onrender.com",      "chat"),
    ("demo-chatbot-ia",            "https://demo-chatbot-ia.onrender.com",            "chat"),
    ("chatbot-ia-cleanpro-1",      "https://chatbot-ia-cleanpro-1.onrender.com",      "chat"),
    ("chatbot-ia-camping",         "https://chatbot-ia-camping.onrender.com",         "chat"),
]

MESSAGE_TEST = "Bonjour, quels sont vos horaires ?"


def _appel(url, donnees=None):
    """Retourne (code_http, corps_texte) ou (None, message_erreur)."""
    corps = json.dumps(donnees).encode() if donnees is not None else None
    entetes = {"Content-Type": "application/json"} if donnees is not None else {}
    requete = urllib.request.Request(url, data=corps, headers=entetes)
    try:
        with urllib.request.urlopen(requete, timeout=TIMEOUT) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def verifier_diagnose(url):
    code, corps = _appel(url + "/diagnose")
    if code is None:
        return False, corps
    try:
        data = json.loads(corps)
    except ValueError:
        return False, f"HTTP {code}, reponse non-JSON"

    # mpsolutionsia : {"status": "ok"|"error", "connectivity": {...}}
    # camping       : {"status": "OK", "message": "Connexion Anthropic fonctionnelle"}
    statut = str(data.get("status", "")).lower()
    if statut == "ok":
        return True, data.get("message") or "API Anthropic joignable"
    erreurs = data.get("errors") or []
    return False, f"status={data.get('status')} {erreurs[:1]}"


def verifier_chat(url):
    code, corps = _appel(url + "/chat", {"message": MESSAGE_TEST})
    if code is None:
        return False, corps
    if code != 200:
        return False, f"HTTP {code} : {corps[:120]}"
    try:
        data = json.loads(corps)
    except ValueError:
        return False, "reponse non-JSON"

    # Les services utilisent des noms de champ differents selon leur generation.
    texte = ""
    for cle in ("reponse", "response", "message", "reply"):
        if isinstance(data.get(cle), str):
            texte = data[cle]
            break
    if not texte:
        return False, f"aucun champ texte reconnu (cles: {list(data)[:5]})"

    # Un service sans cle API valide renvoie 200 avec un message d'erreur
    # generique plutot qu'une vraie reponse.
    signaux = ["erreur technique", "probleme technique", "problème technique",
               "desole, j", "désolé, j'ai rencontré"]
    bas = texte.lower()
    if any(s in bas for s in signaux):
        return False, f"reponse de repli : {texte[:90]}"
    return True, f"{len(texte)} caracteres de reponse"


def main():
    print("=" * 68)
    print("VERIFICATION DES SERVICES MP SOLUTIONS")
    print("Premier appel lent : les instances gratuites se reveillent (~50s)")
    print("=" * 68)

    resultats = []
    for nom, url, methode in SERVICES:
        print(f"\n{nom}")
        print(f"  {url}")
        debut = time.time()
        if methode == "diagnose":
            ok, detail = verifier_diagnose(url)
        else:
            ok, detail = verifier_chat(url)
        duree = time.time() - debut
        marque = "OK  " if ok else "ECHEC"
        print(f"  [{marque}] {detail}  ({duree:.0f}s)")
        resultats.append((nom, ok))

    print("\n" + "=" * 68)
    reussis = sum(1 for _, ok in resultats if ok)
    print(f"BILAN : {reussis}/{len(resultats)} services operationnels")
    echecs = [n for n, ok in resultats if not ok]
    if echecs:
        print("A corriger : " + ", ".join(echecs))
        print("\nSi un service echoue APRES la rotation, sa variable")
        print("ANTHROPIC_API_KEY sur Render contient encore l'ancienne cle.")
    print("=" * 68)
    return 0 if not echecs else 1


if __name__ == "__main__":
    sys.exit(main())
