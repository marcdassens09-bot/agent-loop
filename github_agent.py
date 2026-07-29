"""
github_agent.py — Agent GitHub MP Solutions IA
Connaît les repos, branches et fichiers importants.
Usage : from github_agent import GithubAgent
"""

import json
import requests
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

DRIVE_FILE_ID = "1do1ZC2p7ySCXYb8OpGl_Z-ZJux7kjgCZd4ZNwd3XEHM"  # rempli au premier lancement --init

GITHUB_PAR_DEFAUT = {
    "compte": {
        "username": "marcdassens09-bot",
        "url": "https://github.com/marcdassens09-bot"
    },
    "repos": {
        "agent_loop": {
            "nom": "agent-loop",
            "branche": "main",
            "description": "Agents IA MP Solutions IA",
            "url": "https://github.com/marcdassens09-bot/agent-loop",
            "fichiers_cles": [
                "memory_agent.py — memoire des sessions",
                "clients_context_agent.py — fiches clients/prospects",
                "tarifs_agent.py — offres et devis",
                "charte_agent.py — charte graphique PDF",
                "github_agent.py — contexte repos GitHub",
                "layout_agent.py — mise en page PDF",
                "debug_agent.py — analyse erreurs Python/Flask",
                "prospect_agent.py — dossiers commerciaux",
                "deploy_agent.py — guide deploiement",
                "clients_agent.py — suivi clients",
                "search_agent.py — recherche web"
            ]
        },
        "camping": {
            "nom": "chatbot-camping-eychecadous",
            "branche": "main",
            "description": "Chatbot Anthony Viviano — Camping Les Eychecadous",
            "url": "https://github.com/marcdassens09-bot/chatbot-camping-eychecadous",
            "render_url": "chatbot-camping-eychecadous.onrender.com",
            "fichiers_cles": [
                "agent.py — serveur Flask principal",
                "app.py — application principale",
                ".env — cle API Anthropic (local uniquement)"
            ]
        }
    },
    "workflow": {
        "commandes_base": [
            "git add . — ajouter tous les fichiers modifies",
            "git commit -m 'message' — sauvegarder les changements",
            "git push — envoyer sur GitHub",
            "git status — voir l'etat du repo",
            "git log --oneline — historique des commits"
        ],
        "deploiement_render": [
            "1. git push sur main",
            "2. Render detecte automatiquement le push",
            "3. Render rebuild et redeploie",
            "4. Verifier les logs sur render.com si erreur"
        ],
        "bonnes_pratiques": [
            "Ne jamais pusher le fichier .env",
            "Toujours tester localement avant de pusher",
            "Messages de commit clairs et courts",
            "Une fonctionnalite = un commit"
        ]
    },
    "environnement": {
        "os": "Windows 10",
        "machine": "Acer Aspire E15",
        "terminal": "Git Bash",
        "dossier_projets": "C:/Projets/",
        "python": "Python 3.12",
        "stack": "Python / Flask / GitHub / Render"
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
        print("✓ GitHub context sauvegarde sur Google Drive.")
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


class GithubAgent:
    def __init__(self, drive_file_id: str = ""):
        self.drive_file_id = drive_file_id
        self.data = GITHUB_PAR_DEFAUT.copy()

        if self.drive_file_id:
            try:
                data = charger_drive(self.drive_file_id)
                if data:
                    self.data = data
                    print(f"✓ GitHub context charge ({self.data.get('derniere_mise_a_jour', '?')})")
            except Exception as e:
                print(f"⚠️ Chargement echoue : {e}")
        else:
            print("⚠️ Pas de DRIVE_FILE_ID — donnees par defaut utilisees.")

    def sauvegarder(self):
        if not self.drive_file_id:
            print("⚠️ Pas de DRIVE_FILE_ID defini.")
            return
        self.data["derniere_mise_a_jour"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        sauvegarder_drive(self.drive_file_id, self.data)

    def get_contexte(self) -> str:
        lignes = ["=== GITHUB MP Solutions IA ==="]
        compte = self.data.get("compte", {})
        lignes.append(f"\n>> COMPTE : {compte.get('username', '')} — {compte.get('url', '')}")
        lignes.append("\n>> REPOS :")
        for cle, repo in self.data.get("repos", {}).items():
            lignes.append(f"\n   ● {repo['nom']} ({repo['branche']})")
            lignes.append(f"     {repo['description']}")
            if repo.get("render_url"):
                lignes.append(f"     Render : {repo['render_url']}")
            for f in repo.get("fichiers_cles", []):
                lignes.append(f"       - {f}")
        env = self.data.get("environnement", {})
        lignes.append(f"\n>> ENVIRONNEMENT : {env.get('os', '')} | {env.get('terminal', '')} | {env.get('stack', '')}")
        lignes.append("\n=================================")
        return "\n".join(lignes)

    def afficher(self):
        print("\n GITHUB MP Solutions IA")
        print("=" * 40)
        print(self.get_contexte())
        print("=" * 40)


if __name__ == "__main__":
    import sys

    if "--init" in sys.argv:
        print("Création du fichier Drive...")
        file_id = creer_fichier_drive("GitHub Context MP Solutions IA")
        print(f"✓ Fichier créé. ID :\nDRIVE_FILE_ID = \"{file_id}\"")
        agent = GithubAgent(drive_file_id=file_id)
        agent.sauvegarder()
    else:
        if not DRIVE_FILE_ID:
            print("Lance d'abord : python github_agent.py --init")
        else:
            agent = GithubAgent(drive_file_id=DRIVE_FILE_ID)
            agent.afficher()
