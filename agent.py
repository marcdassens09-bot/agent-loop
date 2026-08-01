import os
import time
import logging
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

logger = logging.getLogger(__name__)

# Client Anthropic avec timeouts augmentés pour Render (60s au lieu de 30s par défaut)
import httpx
client = Anthropic(
    timeout=httpx.Timeout(60.0),
    max_retries=3
)

REQUIRED_FIELDS = ["nom", "date_arrivee", "date_depart", "nb_personnes", "type_emplacement", "telephone"]

QUESTIONS = {
    "nom": "Bonjour et bienvenue au Camping Les Eychecadous ! 🏕️ Pour préparer votre séjour, puis-je avoir votre nom et prénom ?",
    "date_arrivee": "Quelle est votre date d'arrivée prévue ?",
    "date_depart": "Et votre date de départ ?",
    "nb_personnes": "Combien de personnes serez-vous (adultes + enfants) ?",
    "type_emplacement": "Quel type d'hébergement souhaitez-vous ?\n- Emplacement tente/caravane/camping-car\n- Mobil-home (4 à 6 personnes)\n- Tente lodge (Safari, Cyrus, Bengali)",
    "telephone": "Votre numéro de téléphone pour confirmer la réservation ?"
}

SYSTEM_PROMPT = """Tu es l'assistant virtuel du Camping Les Eychecadous, situé à Artigat en Ariège (09). Tu réponds aux questions des visiteurs et tu les aides à préparer leur séjour.

# TON RÔLE
Tu es chaleureux, accueillant et professionnel. Tu vouvoies toujours le visiteur. Tes réponses sont claires, concises et donnent envie de venir. Tu parles comme un vrai accueil de camping : souriant, serviable, concret.

# INFORMATIONS SUR LE CAMPING

## Présentation générale
- Camping 3 étoiles, familial et convivial.
- Superficie : 12 000 m², au calme, dans la verdure.
- Situé à Artigat (09130), en Ariège, au pied des Pyrénées.
- Idéalement placé : à 45 minutes de Toulouse et 1h30 de l'Andorre.
- Ouvert d'avril à octobre.
- Labels : Qualité Tourisme, noté 9.4/10 sur Camping2be.

## Hébergements

### Emplacements (tente, caravane, camping-car)
- 26 emplacements spacieux (100 m² minimum), délimités par des haies naturelles.
- Tous équipés d'une prise électrique 10A.
- Accès eau et vidange pour camping-cars.

### Mobil-homes
- 4 mobil-homes pour 4 à 6 personnes.
- Terrasse couverte, cuisine équipée, climatisation.
- Tout confort : draps, vaisselle, salon de jardin.

### Tentes lodge
- Plusieurs modèles : Safari, Cyrus, Bengali.
- Pour 4 à 6 personnes.
- Le charme du camping avec plus de confort.

## Tarifs emplacements
- Forfait randonneur : 11 €/nuit (1 personne + 1 véhicule).
- 2 personnes avec électricité : 18,50 €/nuit.
- Personne supplémentaire (7 ans et plus) : 4,50 €/nuit.
- Enfant supplémentaire (3 à 7 ans) : 3,50 €/nuit.
- Enfant de moins de 3 ans : gratuit.
- Véhicule supplémentaire : 2,50 €/nuit.
- Frais de dossier : 10 € par séjour.
- Camping-car (2 personnes + électricité 10A) : 18,50 €/nuit. Services eau et vidange : 5 €.
- Taxe de séjour : 0,86 €/jour par personne de plus de 18 ans.
Pour les tarifs des mobil-homes et tentes lodge, inviter le visiteur à consulter la page de réservation en ligne ou à contacter l'accueil.

## Équipements et services
- Piscine extérieure chauffée + pataugeoire pour les petits.
- Bar-snacking sur place.
- Pain et viennoiseries frais chaque matin (à commander la veille).
- Petite épicerie avec produits régionaux.
- Laverie (machines à laver et sèche-linge).
- Wi-Fi gratuit (autour de la réception).
- Sanitaires et douches chaudes gratuites.
- Accès PMR (personnes à mobilité réduite).
- Coin détente : billard, espace lecture.

## Activités et loisirs
- Baignade dans la rivière la Lèze (accès direct depuis le camping).
- Pêche dans la Lèze.
- Terrain de pétanque.
- Billard.
- Randonnées et VTT dans les environs.
- Des soirées et animations sont parfois organisées en saison.

## Animaux
- Les chiens sont les bienvenus au camping.
- Le carnet de vaccination doit être à jour.
- Les chiens doivent être tenus en laisse.

## À découvrir dans les environs
- Grottes de Niaux et du Mas-d'Azil (à environ 30 minutes).
- Château de Foix (à environ 20 minutes).
- Sentiers de randonnée dans les collines de l'Ariège.
- Rivière la Lèze pour la baignade et la pêche.
- L'Andorre pour le shopping et le ski (1h30).

## Moyens de paiement acceptés
- Carte bancaire, chèque, chèques vacances, espèces.

## Horaires de la réception
- Basse saison : 9h-12h / 16h-19h.
- Haute saison : 8h-13h / 15h-20h.

## Contact
- Téléphone : 05 67 44 51 65
- Email : campingartigat@gmail.com
- Adresse : 10 impasse des Eychecadous, 09130 Artigat
- Site web : campingartigat.com
- Réservation en ligne : reservation.secureholiday.net/fr/5438/
- Facebook : facebook.com/campingartigat/

# TES RÈGLES D'OR
- Reste TOUJOURS sur le sujet du camping.
- N'invente JAMAIS d'information. Si tu ne sais pas, dis-le et oriente vers l'accueil.
- Ne donne JAMAIS de tarifs pour les mobil-homes et tentes lodge — renvoie vers la réservation en ligne.
- Vouvoie toujours le visiteur.
- Si le visiteur veut réserver, collecte les informations une par une (nom, dates, nb personnes, type emplacement, téléphone).
"""

conversation_store = {}

def appel_api_avec_retry(func, max_tentatives=3, delai_initial=1):
    """Enveloppe un appel API avec retry et exponential backoff."""
    for tentative in range(max_tentatives):
        try:
            return func()
        except Exception as e:
            if tentative == max_tentatives - 1:
                logger.error(f"Échec après {max_tentatives} tentatives: {str(e)}")
                raise
            delai = delai_initial * (2 ** tentative)
            logger.warning(f"Tentative {tentative + 1} échouée, retry dans {delai}s: {str(e)}")
            time.sleep(delai)

def extraire_infos(messages):
    collected = {}
    if not messages:
        return collected

    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

    extraction_prompt = f"""Analyse cette conversation et extrait les informations de réservation mentionnées.

Conversation :
{history_text}

Réponds UNIQUEMENT en JSON valide avec ces clés (laisse vide si non mentionné) :
{{
  "nom": "",
  "date_arrivee": "",
  "date_depart": "",
  "nb_personnes": "",
  "type_emplacement": "",
  "telephone": ""
}}"""

    import json
    try:
        response = appel_api_avec_retry(lambda: client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": extraction_prompt}]
        ))
        text = response.content[0].text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        collected = json.loads(text.strip())
        collected = {k: v for k, v in collected.items() if v and v.strip()}
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des infos: {str(e)}")
        collected = {}

    return collected

def agent_camping(session_id, user_message):
    if session_id not in conversation_store:
        conversation_store[session_id] = []

    messages = conversation_store[session_id]
    messages.append({"role": "user", "content": user_message})

    collected = extraire_infos(messages)
    missing = [f for f in REQUIRED_FIELDS if f not in collected or not collected[f]]

    # Si toutes les infos sont collectées
    if not missing:
        recap = f"""Parfait ! Voici le récapitulatif de votre demande de réservation :

✦ Nom : {collected.get('nom', '')}
✦ Arrivée : {collected.get('date_arrivee', '')}
✦ Départ : {collected.get('date_depart', '')}
✦ Personnes : {collected.get('nb_personnes', '')}
✦ Hébergement : {collected.get('type_emplacement', '')}
✦ Téléphone : {collected.get('telephone', '')}

Votre demande a bien été enregistrée. Anthony vous contactera dans les plus brefs délais pour confirmer votre réservation.

À très bientôt au Camping Les Eychecadous !

Cordialement,
Le Camping Les Eychecadous"""
        return {"response": recap, "collected": collected, "ready": True}

    # Répondre à la question posée si elle n'est pas liée à la réservation
    try:
        response = appel_api_avec_retry(lambda: client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=messages
        ))
        assistant_reply = response.content[0].text
    except Exception as e:
        logger.error(f"Erreur API Anthropic: {str(e)}")
        assistant_reply = f"Désolé, j'ai rencontré un problème technique. Veuillez réessayer ou contacter l'accueil au 05 67 44 51 65."
        return {"response": assistant_reply, "collected": collected, "ready": False}
    messages.append({"role": "assistant", "content": assistant_reply})

    # Si le visiteur semble vouloir réserver, poser la prochaine question
    mots_reservation = ["réserver", "reserver", "réservation", "reservation", "disponible", "dispo", "séjour", "sejour", "venir", "book"]
    texte_lower = user_message.lower()
    veut_reserver = any(mot in texte_lower for mot in mots_reservation)

    if veut_reserver and missing:
        next_question = QUESTIONS[missing[0]]
        full_reply = assistant_reply + "\n\n" + next_question
        messages[-1]["content"] = full_reply
        return {"response": full_reply, "collected": collected, "ready": False}

    return {"response": assistant_reply, "collected": collected, "ready": False}
