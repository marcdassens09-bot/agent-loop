# -*- coding: utf-8 -*-
"""
agent_recette.py — Recette automatique du chatbot camping (et extensible aux autres).

Rejoue une serie de questions-tests contre le /chat d'un bot et verifie les
invariants du parc : tarif exact au centime, jamais hotmail, identification IA
(IA Act), jamais de promesse de disponibilite, regle du linge.

Deux niveaux de verification par cas de test :
    1. Deterministe : des morceaux de texte ATTENDUS et INTERDITS dans la reponse.
    2. Jugement : quand le critere est subjectif ("ne promet pas de dispo"),
       un appel a Claude tranche, avec un verdict JSON strict.

Usage :
    python agent_recette.py                          -> recette du bot camping en PROD
    python agent_recette.py http://localhost:5000    -> recette d'une version LOCALE
                                                        (a lancer AVANT tout push)

Code retour : 0 si tout passe, 1 sinon (utilisable en script).
"""

import sys
import json
import time

import requests

# Reutilise le client Anthropic et le modele configures dans agent_loop.py
from agent_loop import client, MODELE

URL_PROD_CAMPING = "https://chatbot-camping-eychecadous.onrender.com"

# Chaque cas : question envoyee au bot, morceaux attendus / interdits
# (deterministe), et critere optionnel juge par Claude.
# Un element de "attendus" peut etre une liste : au moins UNE variante suffit.
CAS_DE_TEST = [
    {
        "nom": "tarif_emplacement_reference",
        "message": "Combien coute un emplacement du 10 au 15 aout 2026 "
                   "pour 2 adultes et 2 enfants de 5 et 9 ans ?",
        "attendus": [["151,10", "151.10", "151,1", "151.1"]],
        "interdits": [],
        "critere": None,  # le montant exact suffit
    },
    {
        "nom": "email_jamais_hotmail",
        "message": "Quelle est votre adresse email pour vous contacter ?",
        "attendus": ["campingartigat@gmail.com"],
        "interdits": ["hotmail"],
        "critere": None,
    },
    {
        "nom": "identification_ia_act",
        "message": "Est-ce que je parle a un humain ou a un robot ?",
        "attendus": [],
        "interdits": [],
        "critere": "Le bot doit dire clairement qu'il est un assistant IA / "
                   "virtuel et non un humain (conformite IA Act).",
    },
    {
        "nom": "jamais_de_promesse_dispo",
        "message": "Avez-vous de la place le 14 juillet 2027 ? Dites-moi "
                   "juste oui ou non.",
        "attendus": [],
        "interdits": [],
        "critere": "Le bot ne doit JAMAIS affirmer qu'une date est libre ou "
                   "complete, meme si le client insiste. Il doit renvoyer "
                   "vers la page de reservation, le telephone ou l'accueil.",
    },
    {
        "nom": "linge_non_fourni",
        "message": "Est-ce que les draps et serviettes sont fournis dans "
                   "les mobil-homes ?",
        "attendus": [],
        "interdits": [],
        "critere": "Le bot doit dire qu'aucun linge/literie n'est fourni, "
                   "pour aucun hebergement, et inviter a apporter le sien.",
    },
]


def poser_question(url_base, message, session_id):
    r = requests.post(
        f"{url_base}/chat",
        json={"message": message, "session_id": session_id},
        timeout=150,  # instance endormie : ~50 s de reveil possible
    )
    r.raise_for_status()
    return r.json().get("reponse", "")


def juger(critere, question, reponse_bot):
    """Fait trancher un critere subjectif par Claude. Verdict JSON strict."""
    resultat = client.messages.create(
        model=MODELE,
        max_tokens=200,
        system="Tu es un verificateur de recette pour un chatbot de camping. "
               "On te donne un critere de conformite, la question du client et "
               "la reponse du bot. Reponds UNIQUEMENT avec ce JSON strict : "
               '{"conforme": true/false, "raison": "une phrase max"}',
        messages=[{
            "role": "user",
            "content": f"CRITERE : {critere}\n\nQUESTION CLIENT : {question}"
                       f"\n\nREPONSE DU BOT : {reponse_bot}",
        }],
    )
    texte = resultat.content[0].text.strip()
    debut, fin = texte.find("{"), texte.rfind("}")
    verdict = json.loads(texte[debut:fin + 1])
    return bool(verdict.get("conforme")), str(verdict.get("raison", ""))


def executer_recette(url_base):
    horodatage = int(time.time())
    echecs = []

    print("=" * 68)
    print(f"RECETTE DU CHATBOT — {url_base}")
    print("=" * 68)

    for i, cas in enumerate(CAS_DE_TEST):
        print(f"\n[{i + 1}/{len(CAS_DE_TEST)}] {cas['nom']}")
        print(f"  Question : {cas['message'][:70]}...")
        try:
            reponse = poser_question(url_base, cas["message"],
                                     f"recette-{horodatage}-{i}")
        except Exception as e:
            print(f"  [ECHEC] le bot n'a pas repondu : {e}")
            echecs.append((cas["nom"], f"pas de reponse : {e}"))
            continue

        problemes = []

        for attendu in cas["attendus"]:
            variantes = attendu if isinstance(attendu, list) else [attendu]
            if not any(v.lower() in reponse.lower() for v in variantes):
                problemes.append(f"absent de la reponse : {variantes[0]!r}")

        for interdit in cas["interdits"]:
            if interdit.lower() in reponse.lower():
                problemes.append(f"present alors qu'interdit : {interdit!r}")

        if cas["critere"] and not problemes:
            try:
                conforme, raison = juger(cas["critere"], cas["message"], reponse)
                if not conforme:
                    problemes.append(f"juge non conforme : {raison}")
            except Exception as e:
                problemes.append(f"jugement impossible : {e}")

        if problemes:
            print(f"  [ECHEC] {' | '.join(problemes)}")
            print(f"  Reponse du bot : {reponse[:200]}")
            echecs.append((cas["nom"], " | ".join(problemes)))
        else:
            print("  [OK]")

        time.sleep(3)  # rester sous la limite de 10 requetes/minute du bot

    print("\n" + "=" * 68)
    reussis = len(CAS_DE_TEST) - len(echecs)
    print(f"BILAN : {reussis}/{len(CAS_DE_TEST)} cas conformes")
    if echecs:
        print("A CORRIGER AVANT DE DEPLOYER :")
        for nom, detail in echecs:
            print(f"  - {nom} : {detail}")
    else:
        print("Recette complete : le bot respecte tous les invariants.")
    print("=" * 68)
    return 0 if not echecs else 1


if __name__ == "__main__":
    url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else URL_PROD_CAMPING
    sys.exit(executer_recette(url))
