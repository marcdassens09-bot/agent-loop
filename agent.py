import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()

REQUIRED_FIELDS = ["nom", "date_arrivee", "date_depart", "nb_personnes", "type_emplacement", "telephone"]

QUESTIONS = {
    "nom": "Quel est votre nom et prenom ?",
    "date_arrivee": "Quelle est votre date d arrivee ?",
    "date_depart": "Quelle est votre date de depart ?",
    "nb_personnes": "Combien de personnes seront presentes ?",
    "type_emplacement": "Quel type d emplacement ? (tente, caravane, camping-car, chalet)",
    "telephone": "Quel est votre numero de telephone ?"
}

def extraire_infos(messages):
    conversation = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    prompt = f"""Extrait les infos de reservation depuis cette conversation.
Retourne UNIQUEMENT un dict Python valide, sans explication, sans backticks.
Champs : nom, date_arrivee, date_depart, nb_personnes, type_emplacement, telephone
Si absent, ne l inclus pas.

Conversation :
{conversation}

Dict :"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        import ast
        return ast.literal_eval(response.content[0].text.strip())
    except Exception:
        return {}

def agent_camping(messages):
    collected = extraire_infos(messages)
    missing = [f for f in REQUIRED_FIELDS if not collected.get(f)]
    if not missing:
        recap = f"""Bonjour Anthony,

Nouvelle demande de reservation :

- Nom : {collected.get('nom', 'N/A')}
- Arrivee : {collected.get('date_arrivee', 'N/A')}
- Depart : {collected.get('date_depart', 'N/A')}
- Personnes : {collected.get('nb_personnes', 'N/A')}
- Emplacement : {collected.get('type_emplacement', 'N/A')}
- Telephone : {collected.get('telephone', 'N/A')}

Cordialement,
Le chatbot Camping Les Eychecadous"""
        return {"response": recap, "collected": collected, "ready": True}
    next_question = QUESTIONS[missing[0]]
    return {"response": next_question, "collected": collected, "ready": False}
