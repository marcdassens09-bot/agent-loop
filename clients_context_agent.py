"""
clients_context_agent.py — Agent Contexte Client MP Solutions IA
Charge et sauvegarde les fiches clients/prospects dans Google Drive.
Usage : from clients_context_agent import ClientsContextAgent
"""

import json
import requests
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# ── ID du fichier contexte clients sur Google Drive ────────────────────────────
# À créer avec : python clients_context_agent.py --init
DRIVE_FILE_ID = "1b5lHVNeILZjygFqKBjo6yzEyA_qP0N9Pl6U1YXuMzxo"  # sera rempli au premier lancement

CLIENTS_PAR_DEFAUT = {
    "clients": {
        "anthony_viviano": {
            "nom": "Anthony Viviano",
            "entreprise": "Camping Les Eychecadous",
            "lieu": "Artigat",
            "repo": "chatbot-camping-eychecadous",
            "url": "chatbot-camping-eychecadous.onrender.com",
            "offre": "800€ setup + 60€/mois",
            "statut": "actif",
            "notes": ""
        },
        "maxime_moucheron": {
            "nom": "Maxime Moucheron",
            "entreprise": "Full Habitat EURL",
            "secteur": "électricien/plombier certifié",
            "lieu": "Baulou 09",
            "offre": "800€ setup + 60€/mois",
            "statut": "actif",
            "notes": ""
        }
    },
    "prospects": {
        "thomas_fournial": {
            "nom": "Thomas Fournial",
            "entreprise": "Fumeco-Lèze",
            "secteur": "fabricant substrats/compost",
            "lieu": "Artigat",
            "offre": "1200€ setup + 120€/mois",
            "statut": "prospect",
            "notes": ""
        },
        "couleurs_asie": {
            "nom": "Couleurs d'Asie",
            "secteur": "restaurant cambodgien",
            "lieu": "Le Fossat",
            "offre": "800€ setup + 60€/mois",
            "statut": "prospect",
            "notes": ""
        },
        "boulangerie_de_oliveira": {
            "nom": "Adrien De Oliveira",
            "entreprise": "Boulangerie De Oliveira",
            "lieu": "Le Fossat",
            "offre": "800€ setup + 60€/mois",
            "statut": "prospect",
            "notes": ""
        },
        "la_table_du_fossat": {
            "nom": "La Table du Fossat",
            "secteur": "restaurant",
            "lieu": "Le Fossat",
            "offre": "800€ setup + 60€/mois",
            "statut": "prospect",
            "notes": ""
        }
    },
    "derniere_mise_a_jour": ""
}


def get_drive_token() -> str:
    with open("token.json", "r") as f:
        return json.load(f)["token"]


def creer_fichier_drive(nom: str) -> str:
    """Crée un nouveau fichier Drive et retourne son ID."""
    token = get_drive_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    meta = {"name": nom, "mimeType": "application/vnd.google-apps.document"}
    r = requests.post("https://www.googleapis.com/drive/v3/files", headers=headers, json=meta)
    data = r.json()
    return data["id"]


def sauvegarder_drive(file_id: str, data: dict):
    token = get_drive_token()
    contenu = f"JSON_BRUT:\n{json.dumps(data, ensure_ascii=True, indent=2)}"
    url = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/plain; charset=utf-8"
    }
    r = requests.patch(url, params={"uploadType": "media"}, headers=headers, data=contenu.encode("utf-8"))
    if r.status_code == 200:
        print("✓ Contexte clients sauvegardé sur Google Drive.")
    else:
        print(f"⚠️ Erreur Drive {r.status_code}: {r.text}")


def charger_drive(file_id: str) -> dict:
    token = get_drive_token()
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, params={"mimeType": "text/plain"}, headers=headers)
    if r.status_code != 200:
        return {}
    texte = r.text
    debut = texte.find("{")
    fin = texte.rfind("}") + 1
    if debut == -1:
        return {}
    return json.loads(texte[debut:fin])


class ClientsContextAgent:
    def __init__(self, drive_file_id: str = ""):
        self.drive_file_id = drive_file_id
        self.data = CLIENTS_PAR_DEFAUT.copy()

        if self.drive_file_id:
            try:
                data = charger_drive(self.drive_file_id)
                if data:
                    self.data = data
                    print(f"✓ Contexte clients chargé ({self.data.get('derniere_mise_a_jour', '?')})")
            except Exception as e:
                print(f"⚠️ Chargement échoué : {e}")
        else:
            print("⚠️ Pas de DRIVE_FILE_ID — données par défaut utilisées.")

    def sauvegarder(self):
        if not self.drive_file_id:
            print("⚠️ Pas de DRIVE_FILE_ID défini.")
            return
        self.data["derniere_mise_a_jour"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        sauvegarder_drive(self.drive_file_id, self.data)

    def get_contexte(self) -> str:
        """Retourne un bloc texte à injecter dans le system prompt."""
        lignes = ["=== CONTEXTE CLIENTS MP Solutions IA ==="]

        lignes.append("\n>> CLIENTS ACTIFS :")
        for key, c in self.data.get("clients", {}).items():
            lignes.append(f"  ● {c['nom']} — {c.get('entreprise', '')} ({c.get('lieu', '')})")
            if c.get("repo"):
                lignes.append(f"    Repo : {c['repo']} | URL : {c.get('url', '')}")
            if c.get("notes"):
                lignes.append(f"    Notes : {c['notes']}")

        lignes.append("\n>> PROSPECTS :")
        for key, p in self.data.get("prospects", {}).items():
            lignes.append(f"  ◆ {p['nom']} — {p.get('entreprise', p.get('secteur', ''))} ({p.get('lieu', '')})")
            if p.get("notes"):
                lignes.append(f"    Notes : {p['notes']}")

        lignes.append("\n=================================")
        return "\n".join(lignes)

    def ajouter_note(self, cle: str, note: str, categorie: str = "clients"):
        """Ajoute une note à un client ou prospect."""
        if cle in self.data.get(categorie, {}):
            self.data[categorie][cle]["notes"] = note
            print(f"✓ Note ajoutée pour {cle}")
        else:
            print(f"⚠️ Clé '{cle}' introuvable dans '{categorie}'")

    def afficher(self):
        print("\n📋 CONTEXTE CLIENTS")
        print("=" * 40)
        print(self.get_contexte())
        print("=" * 40)


# ── Lancement ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if "--init" in sys.argv:
        # Crée le fichier Drive et affiche l'ID
        print("Création du fichier Drive...")
        file_id = creer_fichier_drive("Contexte Clients MP Solutions IA")
        print(f"✓ Fichier créé. Copie cet ID dans le code :\nDRIVE_FILE_ID = \"{file_id}\"")

        # Sauvegarde immédiate des données par défaut
        agent = ClientsContextAgent(drive_file_id=file_id)
        agent.sauvegarder()
    else:
        if not DRIVE_FILE_ID:
            print("Lance d'abord : python clients_context_agent.py --init")
        else:
            agent = ClientsContextAgent(drive_file_id=DRIVE_FILE_ID)
            agent.afficher()
