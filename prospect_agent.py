"""
prospect_agent.py — Agent Prospect MP Solutions IA
Gère les dossiers commerciaux : fiche découverte, dossier, bon de commande, questionnaire.
Usage : from prospect_agent import ProspectAgent
"""

import os
import anthropic
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
client = anthropic.Anthropic(api_key=api_key)

SYSTEM_PROMPT = """Tu es l'Agent Prospect de MP Solutions IA.
Tu aides Marc-Paul Dassens à préparer ses dossiers commerciaux.

Structure obligatoire "Docteur Commercial" :
>> CE QUE J'OBSERVE — diagnostic terrain, problème concret du client
++ CE QUE JE PROPOSE — solution précise avec prix assumé
-> SIGNATURE — Marc-Paul Dassens | contact@mpsolutionsia.fr | Artigat (09130)

Tarifs :
- Artisan solo : 800€ installation + 60€/mois
- PME avec salariés : 1200€ installation + 120€/mois

Interdit dans tout document commercial :
- Essai gratuit
- Sans engagement
- Disponible immédiatement (si ça sonne agressif)

Réponds UNIQUEMENT en JSON valide :
{
  "type": "fiche_decouverte|dossier_commercial|bon_de_commande|questionnaire_technique",
  "prospect": "nom du prospect",
  "contenu": "contenu complet du document",
  "prochaine_etape": "ce que Marc-Paul doit faire ensuite"
}"""


# Prospects actifs MP Solutions IA
PROSPECTS = {
    "fumeco": {
        "nom": "Thomas Fournial",
        "entreprise": "Fumeco-Lèze",
        "secteur": "Fabricant substrats/compost",
        "ville": "Artigat",
        "tarif": "800€ + 60€/mois",
    },
    "couleurs_asie": {
        "nom": "Responsable",
        "entreprise": "Couleurs d'Asie",
        "secteur": "Restaurant cambodgien",
        "ville": "Le Fossat",
        "tarif": "800€ + 60€/mois",
    },
    "boulangerie": {
        "nom": "Adrien De Oliveira",
        "entreprise": "Boulangerie De Oliveira",
        "secteur": "Boulangerie",
        "ville": "Le Fossat",
        "tarif": "800€ + 60€/mois",
    },
    "table_fossat": {
        "nom": "Responsable",
        "entreprise": "La Table du Fossat",
        "secteur": "Restaurant",
        "ville": "Le Fossat",
        "tarif": "800€ + 60€/mois",
    },
}

DOCUMENTS = [
    "fiche_decouverte",
    "dossier_commercial",
    "bon_de_commande",
    "questionnaire_technique",
]


class ProspectAgent:
    def __init__(self):
        self.prospects = PROSPECTS
        self.historique = []

    def lister_prospects(self) -> list:
        """Retourne la liste des prospects actifs."""
        return [
            f"{v['entreprise']} ({v['ville']})"
            for v in self.prospects.values()
        ]

    def generer_document(self, prospect_key: str, type_doc: str) -> dict:
        """
        Génère un document commercial pour un prospect.
        prospect_key : clé du prospect (fumeco, couleurs_asie, etc.)
        type_doc : fiche_decouverte | dossier_commercial | bon_de_commande | questionnaire_technique
        """
        if prospect_key not in self.prospects:
            return {"erreur": f"Prospect '{prospect_key}' inconnu."}

        if type_doc not in DOCUMENTS:
            return {"erreur": f"Type de document '{type_doc}' inconnu."}

        prospect = self.prospects[prospect_key]

        prompt = f"""Génère un {type_doc} pour ce prospect :

Nom : {prospect['nom']}
Entreprise : {prospect['entreprise']}
Secteur : {prospect['secteur']}
Ville : {prospect['ville']}
Tarif applicable : {prospect['tarif']}
Date : {datetime.now().strftime('%d/%m/%Y')}

Suis strictement la structure Docteur Commercial et les règles MP Solutions IA."""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )

        texte = response.content[0].text.strip()
        texte = texte.replace("```json", "").replace("```", "").strip()

        try:
            resultat = json.loads(texte)
        except json.JSONDecodeError:
            resultat = {"type": type_doc, "contenu": texte, "prospect": prospect["entreprise"]}

        self.historique.append({
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "prospect": prospect["entreprise"],
            "document": type_doc,
        })

        return resultat

    def get_contexte(self) -> str:
        """Retourne le contexte pour injection dans un SYSTEM_PROMPT."""
        prospects_liste = ", ".join([v["entreprise"] for v in self.prospects.values()])
        return f"""=== AGENT PROSPECT ACTIF ===
Prospects actifs : {prospects_liste}
Documents disponibles : fiche_decouverte, dossier_commercial, bon_de_commande, questionnaire_technique
Pour générer : prospect_agent.generer_document('cle_prospect', 'type_doc')
============================"""


# ── Exemple d'utilisation ──────────────────────────────────────────────────────
if __name__ == "__main__":
    agent = ProspectAgent()

    print("Prospects actifs :")
    for p in agent.lister_prospects():
        print(f"  - {p}")

    print("\nGénération fiche découverte Fumeco...")
    doc = agent.generer_document("fumeco", "fiche_decouverte")
    print(json.dumps(doc, ensure_ascii=False, indent=2))
