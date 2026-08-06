"""
tarifs_agent.py — Agent Tarifs MP Solutions IA
Connaît les offres, prix et conditions de MP Solutions IA.
Usage : from tarifs_agent import TarifsAgent
"""

import json
import requests
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

DRIVE_FILE_ID = "1oE96YWFDvMyWbioDyVkswkGLNWhH1KMBwwlrXB9LuYc"  # rempli au premier lancement --init

TARIFS_PAR_DEFAUT = {
    "offres": {
        "solo": {
            "label": "Offre Solo — Artisans et micro-entreprises",
            "setup": 800,
            "mensuel": 60,
            "engagement": "3 mois minimum",
            "preavis": "1 mois",
            "cible": "Artisans, commerçants, indépendants sans salarié",
            "inclus": [
                "Chatbot IA personnalisé",
                "Formation à l'utilisation",
                "Hébergement sur Render",
                "Mises à jour incluses",
                "Support par email"
            ]
        },
        "pme": {
            "label": "Offre PME — Entreprises avec personnel",
            "setup": 1200,
            "mensuel": 120,
            "engagement": "3 mois minimum",
            "preavis": "1 mois",
            "cible": "PME, entreprises avec salariés",
            "inclus": [
                "Chatbot IA personnalisé",
                "Formation équipe",
                "Hébergement sur Render",
                "Mises à jour incluses",
                "Support prioritaire par email et téléphone"
            ]
        }
    },
    "conditions": {
        "engagement_minimum": "3 mois",
        "preavis_resiliation": "1 mois",
        "paiement": "Virement bancaire ou chèque",
        "delai_livraison": "7 à 14 jours ouvrés après signature",
        "siret": "en cours de réception"
    },
    "contact": {
        "nom": "Marc-Paul Dassens",
        "email": "contact@mpsolutionsia.fr",
        "lieu": "Artigat (09130)",
        "tagline": "Ecouter, comprendre, servir — en toute transparence."
    },
    "derniere_mise_a_jour": ""
}


def get_drive_token() -> str:
    with open("token.json", "r") as f:
        return json.load(f)["token"]


def creer_fichier_drive(nom: str) -> str:
    token = get_drive_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    meta = {"name": nom, "mimeType": "application/vnd.google-apps.document"}
    r = requests.post("https://www.googleapis.com/drive/v3/files", headers=headers, json=meta)
    return r.json()["id"]


def sauvegarder_drive(file_id: str, data: dict):
    token = get_drive_token()
    contenu = f"JSON_BRUT:\n{json.dumps(data, ensure_ascii=True, indent=2)}"
    url = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "text/plain; charset=utf-8"}
    r = requests.patch(url, params={"uploadType": "media"}, headers=headers, data=contenu.encode("utf-8"))
    if r.status_code == 200:
        print("✓ Tarifs sauvegardés sur Google Drive.")
    else:
        print(f"⚠️ Erreur Drive {r.status_code}: {r.text}")


def charger_drive(file_id: str) -> dict:
    token = get_drive_token()
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, params={"alt": "media"}, headers=headers)
    if r.status_code != 200:
        return {}
    texte = r.text
    debut = texte.find("{")
    fin = texte.rfind("}") + 1
    if debut == -1:
        return {}
    return json.loads(texte[debut:fin])


class TarifsAgent:
    def __init__(self, drive_file_id: str = ""):
        self.drive_file_id = drive_file_id
        self.data = TARIFS_PAR_DEFAUT.copy()

        if self.drive_file_id:
            try:
                data = charger_drive(self.drive_file_id)
                if data:
                    self.data = data
                    print(f"✓ Tarifs chargés ({self.data.get('derniere_mise_a_jour', '?')})")
            except Exception as e:
                print(f"⚠️ Chargement échoué : {e}")
        else:
            print("⚠️ Pas de DRIVE_FILE_ID — tarifs par défaut utilisés.")

    def sauvegarder(self):
        if not self.drive_file_id:
            print("⚠️ Pas de DRIVE_FILE_ID défini.")
            return
        self.data["derniere_mise_a_jour"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        sauvegarder_drive(self.drive_file_id, self.data)

    def get_contexte(self) -> str:
        """Retourne un bloc texte à injecter dans le system prompt."""
        lignes = ["=== TARIFS MP Solutions IA ==="]

        for cle, offre in self.data.get("offres", {}).items():
            lignes.append(f"\n>> {offre['label']}")
            lignes.append(f"   Setup : {offre['setup']}€ | Mensuel : {offre['mensuel']}€/mois")
            lignes.append(f"   Engagement : {offre['engagement']} | Préavis : {offre['preavis']}")
            lignes.append(f"   Cible : {offre['cible']}")
            lignes.append("   Inclus : " + " | ".join(offre.get("inclus", [])))

        cond = self.data.get("conditions", {})
        lignes.append(f"\n++ CONDITIONS :")
        lignes.append(f"   Paiement : {cond.get('paiement', '')}")
        lignes.append(f"   Délai livraison : {cond.get('delai_livraison', '')}")

        contact = self.data.get("contact", {})
        lignes.append(f"\n-> {contact.get('nom', '')} — {contact.get('email', '')} — {contact.get('lieu', '')}")
        lignes.append(f"   \"{contact.get('tagline', '')}\"")
        lignes.append("\n=================================")
        return "\n".join(lignes)

    def generer_devis(self, nom_client: str, type_offre: str = "solo") -> str:
        """Génère un devis texte rapide."""
        offre = self.data["offres"].get(type_offre, self.data["offres"]["solo"])
        contact = self.data["contact"]
        conditions = self.data["conditions"]

        devis = f"""
DEVIS MP Solutions IA
=====================
Client : {nom_client}
Date : {datetime.now().strftime('%d/%m/%Y')}

OFFRE : {offre['label']}
- Installation : {offre['setup']}€ HT
- Abonnement mensuel : {offre['mensuel']}€ HT/mois
- Engagement minimum : {conditions['engagement_minimum']}
- Préavis résiliation : {conditions['preavis_resiliation']}
- Délai de livraison : {conditions['delai_livraison']}

PRESTATIONS INCLUSES :
{chr(10).join('  ✓ ' + p for p in offre['inclus'])}

TOTAL PREMIÈRE ANNÉE :
  Setup : {offre['setup']}€
  Abonnement (12 mois) : {offre['mensuel'] * 12}€
  TOTAL : {offre['setup'] + offre['mensuel'] * 12}€ HT

---
{contact['nom']} — {contact['email']} — {contact['lieu']}
"{contact['tagline']}"
"""
        return devis

    def afficher(self):
        print("\n💶 TARIFS MP Solutions IA")
        print("=" * 40)
        print(self.get_contexte())
        print("=" * 40)


if __name__ == "__main__":
    import sys

    if "--init" in sys.argv:
        print("Création du fichier Drive...")
        file_id = creer_fichier_drive("Tarifs MP Solutions IA")
        print(f"✓ Fichier créé. ID :\nDRIVE_FILE_ID = \"{file_id}\"")
        agent = TarifsAgent(drive_file_id=file_id)
        agent.sauvegarder()
    else:
        if not DRIVE_FILE_ID:
            print("Lance d'abord : python tarifs_agent.py --init")
        else:
            agent = TarifsAgent(drive_file_id=DRIVE_FILE_ID)
            agent.afficher()
            print("\n--- EXEMPLE DEVIS SOLO ---")
            print(agent.generer_devis("Thomas Fournial", "solo"))
