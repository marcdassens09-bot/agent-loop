"""
charte_agent.py — Agent Charte PDF MP Solutions IA
Connaît la charte graphique et les règles de mise en page.
Usage : from charte_agent import CharteAgent
"""

import json
import requests
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

DRIVE_FILE_ID = "10m0NCzoEcsH9WvWginzznzrQsb8SISv35kmG6_UNef4"  # rempli au premier lancement --init

CHARTE_PAR_DEFAUT = {
    "identite": {
        "nom": "MP Solutions IA",
        "tagline": "Ecouter, comprendre, servir — en toute transparence.",
        "email": "mpsolutionsia@gmail.com",
        "lieu": "Artigat (09130)",
        "logo": "logo_complet.png"
    },
    "couleurs": {
        "fond": "#FFFFFF",
        "texte_principal": "#1b3a2b",
        "accent_titres": "#E8730A",
        "description": "Fond blanc, texte vert foncé, titres et accents orange"
    },
    "typographie": {
        "police_principale": "DejaVu",
        "police_alternative": "Poppins",
        "regel": "Toujours DejaVu pour les accents français — jamais Helvetica"
    },
    "mise_en_page": {
        "format": "PDF via ReportLab uniquement",
        "header": "Logo MP Solutions IA sur chaque page",
        "footer": "mpsolutionsia@gmail.com + SIRET sur chaque page",
        "style": "Aéré, propre et simple — pas de tableaux colorés",
        "prefixes_sections": ">> pour observations | ++ pour propositions | -> pour signature",
        "icones_autorises": ["✓", "✦", "▸", "●", "◆", "—"],
        "interdits": ["emojis", "tableaux colorés", "Helvetica"]
    },
    "structure_commerciale": {
        "page_1": "Couverture (logo + nom prospect + tagline)",
        "page_2": ">> CE QUE J'OBSERVE (diagnostic terrain)",
        "page_3": "++ CE QUE JE PROPOSE (solution + prix)",
        "page_4": "Comment ça marche (explication simple)",
        "page_5": "Processus d'installation (4 étapes)",
        "page_6": "Formulaire / appel à l'action"
    },
    "structure_docteur": {
        "observer": ">> CE QUE J'OBSERVE — Diagnostiquer le problème concret du client",
        "proposer": "++ CE QUE JE PROPOSE — Solution précise avec prix clair",
        "signer": "-> Marc-Paul Dassens — mpsolutionsia@gmail.com — Artigat (09130)"
    },
    "preview_rule": {
        "etape_1": "Générer une image de chaque page (pdftoppm → PIL → JPG)",
        "etape_2": "Montrer TOUTES les pages visuellement",
        "etape_3": "Zoomer sur header, footer et sauts de page",
        "etape_4": "Attendre l'approbation de Marc-Paul",
        "etape_5": "Livrer le fichier UNIQUEMENT après le go"
    },
    "interdits_commerciaux": [
        "Essai gratuit",
        "Sans engagement",
        "Disponible immédiatement (si ça sonne agressif)",
        "Toute formule de vente sous pression"
    ],
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
        print("✓ Charte sauvegardée sur Google Drive.")
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


class CharteAgent:
    def __init__(self, drive_file_id: str = ""):
        self.drive_file_id = drive_file_id
        self.data = CHARTE_PAR_DEFAUT.copy()

        if self.drive_file_id:
            try:
                data = charger_drive(self.drive_file_id)
                if data:
                    self.data = data
                    print(f"✓ Charte chargée ({self.data.get('derniere_mise_a_jour', '?')})")
            except Exception as e:
                print(f"⚠️ Chargement échoué : {e}")
        else:
            print("⚠️ Pas de DRIVE_FILE_ID — charte par défaut utilisée.")

    def sauvegarder(self):
        if not self.drive_file_id:
            print("⚠️ Pas de DRIVE_FILE_ID défini.")
            return
        self.data["derniere_mise_a_jour"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        sauvegarder_drive(self.drive_file_id, self.data)

    def get_contexte(self) -> str:
        """Retourne un bloc texte à injecter dans le system prompt."""
        c = self.data
        lignes = [
            "=== CHARTE MP Solutions IA ===",
            f"\n>> IDENTITE",
            f"   Nom : {c['identite']['nom']}",
            f"   Tagline : {c['identite']['tagline']}",
            f"   Logo : {c['identite']['logo']}",
            f"\n>> COULEURS",
            f"   Fond : {c['couleurs']['fond']}",
            f"   Texte : {c['couleurs']['texte_principal']}",
            f"   Titres : {c['couleurs']['accent_titres']}",
            f"\n>> TYPOGRAPHIE",
            f"   Police : {c['typographie']['police_principale']}",
            f"   Règle : {c['typographie']['regel']}",
            f"\n>> MISE EN PAGE",
            f"   Format : {c['mise_en_page']['format']}",
            f"   Header : {c['mise_en_page']['header']}",
            f"   Footer : {c['mise_en_page']['footer']}",
            f"   Style : {c['mise_en_page']['style']}",
            f"   Préfixes : {c['mise_en_page']['prefixes_sections']}",
            f"\n>> STRUCTURE DOSSIER COMMERCIAL",
        ]
        for page, contenu in c["structure_commerciale"].items():
            lignes.append(f"   {page} : {contenu}")

        lignes.append(f"\n>> STRUCTURE DOCTEUR")
        for cle, val in c["structure_docteur"].items():
            lignes.append(f"   {val}")

        lignes.append(f"\n++ RÈGLE PREVIEW (obligatoire)")
        for cle, val in c["preview_rule"].items():
            lignes.append(f"   {val}")

        lignes.append(f"\n-- INTERDITS COMMERCIAUX")
        for item in c["interdits_commerciaux"]:
            lignes.append(f"   ✗ {item}")

        lignes.append("\n=================================")
        return "\n".join(lignes)

    def afficher(self):
        print("\n🎨 CHARTE MP Solutions IA")
        print("=" * 40)
        print(self.get_contexte())
        print("=" * 40)


if __name__ == "__main__":
    import sys

    if "--init" in sys.argv:
        print("Création du fichier Drive...")
        file_id = creer_fichier_drive("Charte MP Solutions IA")
        print(f"✓ Fichier créé. ID :\nDRIVE_FILE_ID = \"{file_id}\"")
        agent = CharteAgent(drive_file_id=file_id)
        agent.sauvegarder()
    else:
        if not DRIVE_FILE_ID:
            print("Lance d'abord : python charte_agent.py --init")
        else:
            agent = CharteAgent(drive_file_id=DRIVE_FILE_ID)
            agent.afficher()
