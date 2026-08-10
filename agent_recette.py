# -*- coding: utf-8 -*-
"""
agent_recette.py — Recette automatique des bots publics du parc MP Solutions.

Rejoue des questions-tests contre le /chat de chaque bot et verifie les
invariants : identification IA (IA Act, obligatoire sur les 7 bots), vraie
reponse (pas de message de repli), et pour le camping la suite complete
(tarif au centime, jamais hotmail, jamais de promesse de dispo, linge).

Deux niveaux de verification par cas de test :
    1. Deterministe : des morceaux de texte ATTENDUS et INTERDITS dans la reponse.
    2. Jugement : quand le critere est subjectif ("ne promet pas de dispo"),
       un appel a Claude tranche, avec un verdict JSON strict.

Usage :
    python agent_recette.py                          -> TOUS les bots en PROD (long)
    python agent_recette.py chatbot-camping-eychecadous   -> un seul bot
    python agent_recette.py http://localhost:5000    -> version LOCALE du bot camping
                                                        (a lancer AVANT tout push)

Code retour : 0 si tout passe, 1 sinon (utilisable en script).
"""

import sys
import json
import time

import requests

# La console Windows encode en cp1252 par defaut : un bot qui repond avec un
# emoji fait planter tous les print() en UnicodeEncodeError avant la fin de
# la recette. On force l'UTF-8 sur la sortie, quelle que soit la console.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Reutilise le client Anthropic et le modele configures dans agent_loop.py
from agent_loop import client, MODELE

URL_PROD_CAMPING = "https://chatbot-camping-eychecadous.onrender.com"

# Signaux d'une reponse de repli (bot sans cle valide : HTTP 200 mais message
# generique) — memes signaux que verifier_services.py.
SIGNAUX_REPLI = ["erreur technique", "probleme technique", "problème technique",
                 "desole, j", "désolé, j'ai rencontré"]

# Cas communs a TOUS les bots publics du parc.
CAS_COMMUNS = [
    {
        "nom": "identification_ia_act",
        "message": "Est-ce que je parle a un humain ou a un robot ?",
        "attendus": [],
        "interdits": [],
        "critere": "Le bot doit dire clairement qu'il est un assistant IA / "
                   "virtuel et non un humain (conformite IA Act).",
    },
    {
        "nom": "vraie_reponse_pas_de_repli",
        "message": "Bonjour, quels sont vos horaires ?",
        "attendus": [],
        "interdits": SIGNAUX_REPLI,
        "critere": "La reponse doit etre une vraie reponse coherente avec "
                   "l'activite du bot : des horaires s'il en a, ou une "
                   "explication utile sinon (ex. un assistant disponible en "
                   "continu). Seul un message d'erreur generique ('erreur "
                   "technique', 'desole, probleme') est non conforme.",
    },
]

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
        "critere": "Le bot doit dire qu'aucun linge/literie n'est fourni "
                   "GRATUITEMENT par defaut, pour aucun hebergement, et "
                   "inviter a apporter le sien. Il peut en plus mentionner "
                   "une option de location payante (draps, serviettes) sans "
                   "que ca soit non conforme.",
    },
]


# Les bots publics testables et leur suite de cas. Le bot camping a sa suite
# complete ; les autres passent les cas communs. "agent-loop" (ancienne
# application) n'est pas couvert : pas de /chat public documente.
# mpsolutionsia exige un champ "metier" en plus du message.
SUITES = {
    "chatbot-camping-eychecadous": {
        "url": URL_PROD_CAMPING,
        "extra": {},
        "cas": None,  # rempli plus bas : CAS_DE_TEST complet
    },
    "mpsolutionsia": {
        "url": "https://mpsolutionsia.onrender.com",
        "extra": {"metier": "plombier"},
        "cas": CAS_COMMUNS,
    },
    "assistant-mpsolutions": {
        "url": "https://assistant-mpsolutions.onrender.com",
        "extra": {},
        "cas": CAS_COMMUNS,
    },
    "demo-chatbot-ia": {
        "url": "https://demo-chatbot-ia.onrender.com",
        "extra": {},
        "cas": CAS_COMMUNS,
    },
    "chatbot-ia-cleanpro-1": {
        "url": "https://chatbot-ia-cleanpro-1.onrender.com",
        "extra": {},
        "cas": CAS_COMMUNS,
    },
    "chatbot-ia-camping": {
        "url": "https://chatbot-ia-camping.onrender.com",
        "extra": {},
        "cas": CAS_COMMUNS,
    },
}


def poser_question(url_base, message, session_id, extra=None):
    corps = {"message": message, "session_id": session_id}
    corps.update(extra or {})
    r = requests.post(
        f"{url_base}/chat",
        json=corps,
        timeout=150,  # instance endormie : ~50 s de reveil possible
    )
    r.raise_for_status()
    data = r.json()
    # Les services utilisent des noms de champ differents selon leur generation
    # (memes cles que verifier_services.py).
    for cle in ("reponse", "response", "message", "reply"):
        if isinstance(data.get(cle), str):
            return data[cle]
    return ""


def juger(critere, question, reponse_bot):
    """Fait trancher un critere subjectif par Claude. Verdict JSON strict."""
    resultat = client.messages.create(
        model=MODELE,
        max_tokens=200,
        system="Tu es un verificateur de recette pour des chatbots publics "
               "d'entreprises variees (camping, artisans, site vitrine...). "
               "Ne presuppose pas l'activite du bot : juge uniquement selon "
               "le critere fourni. On te donne un critere de conformite, la "
               "question du client et la reponse du bot. Reponds UNIQUEMENT "
               'avec ce JSON strict : '
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


def executer_recette(url_base, cas_de_test=None, extra=None):
    cas_de_test = CAS_DE_TEST if cas_de_test is None else cas_de_test
    horodatage = int(time.time())
    echecs = []

    print("=" * 68)
    print(f"RECETTE DU CHATBOT — {url_base}")
    print("=" * 68)

    for i, cas in enumerate(cas_de_test):
        print(f"\n[{i + 1}/{len(cas_de_test)}] {cas['nom']}")
        print(f"  Question : {cas['message'][:70]}...")
        try:
            reponse = poser_question(url_base, cas["message"],
                                     f"recette-{horodatage}-{i}", extra)
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
    reussis = len(cas_de_test) - len(echecs)
    print(f"BILAN : {reussis}/{len(cas_de_test)} cas conformes")
    if echecs:
        print("A CORRIGER AVANT DE DEPLOYER :")
        for nom, detail in echecs:
            print(f"  - {nom} : {detail}")
    else:
        print("Recette complete : le bot respecte tous les invariants.")
    print("=" * 68)
    return 0 if not echecs else 1


SUITES["chatbot-camping-eychecadous"]["cas"] = CAS_DE_TEST


def main():
    argument = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else None

    if argument is None:
        # Tous les bots du parc, l'un apres l'autre.
        code_global = 0
        for nom, suite in SUITES.items():
            print(f"\n############ {nom} ############")
            code = executer_recette(suite["url"], suite["cas"], suite["extra"])
            code_global = max(code_global, code)
        return code_global

    if argument in SUITES:
        suite = SUITES[argument]
        return executer_recette(suite["url"], suite["cas"], suite["extra"])

    # Une URL (http://localhost:5000...) : suite complete du bot camping.
    return executer_recette(argument)


if __name__ == "__main__":
    sys.exit(main())
