"""
memory_agent.py — Agent Mémoire MP Solutions IA
"""
import os
import anthropic
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
client = anthropic.Anthropic(api_key=api_key)

DRIVE_FILE_ID = "1cu0ow2ieeWpo7odrkS83XFPeHBUbJV8eBtAcWzrVNYc"

SYSTEM_PROMPT = """Tu es l'Agent Mémoire de MP Solutions IA.
Réponds UNIQUEMENT avec ce JSON :
{
  "resume": "Résumé court en 2-3 phrases",
  "decisions": ["décision 1"],
  "erreurs_vues": ["erreur résolue 1"],
  "code_produit": ["fichier.py : ce qu'il fait"],
  "prochaine_etape": "Ce qu'il reste à faire"
}"""

def get_drive_token():
    with open("token.json", "r") as f:
        return json.load(f)["token"]

def sauvegarder_drive(memoire):
    token = get_drive_token()
    contenu = f"JSON_BRUT:\n{json.dumps(memoire, ensure_ascii=False, indent=2)}"
    url = f"https://www.googleapis.com/upload/drive/v3/files/{DRIVE_FILE_ID}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "text/plain; charset=utf-8"}
    r = requests.patch(url, params={"uploadType": "media"}, headers=headers, data=contenu.encode("utf-8"))
    if r.status_code == 200:
        print("✓ Mémoire sauvegardée sur Google Drive.")
    else:
        print(f"⚠️ Erreur Drive {r.status_code}: {r.text}")

def charger_drive():
    token = get_drive_token()
    url = f"https://www.googleapis.com/drive/v3/files/{DRIVE_FILE_ID}/export"
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

class MemoryAgent:
    def __init__(self):
        self.memoire = {"resume": "", "decisions": [], "erreurs_vues": [], "code_produit": [], "prochaine_etape": "", "derniere_mise_a_jour": ""}
        self.compteur_messages = 0
        self.FREQUENCE_RESUME = 5
        try:
            data = charger_drive()
            if data:
                self.memoire.update(data)
                print(f"✓ Mémoire chargée ({self.memoire.get('derniere_mise_a_jour','?')})")
        except Exception as e:
            print(f"⚠️ Chargement échoué : {e}")

    def sauvegarder(self):
        sauvegarder_drive(self.memoire)

    def doit_resumer(self):
        self.compteur_messages += 1
        return self.compteur_messages % self.FREQUENCE_RESUME == 0

    def resumer(self, historique):
        historique_court = historique[-20:]
        conversation_texte = "\n".join([f"{m['role'].upper()} : {m['content']}" for m in historique_court])
        prompt = f"Conversation :\n{conversation_texte}\n\nRésumé existant :\n{json.dumps(self.memoire, ensure_ascii=False)}"
        response = client.messages.create(model="claude-sonnet-4-6", max_tokens=1000, system=SYSTEM_PROMPT, messages=[{"role": "user", "content": prompt}])
        texte = response.content[0].text.strip().replace("```json","").replace("```","").strip()
        nouveau = json.loads(texte)
        nouveau["derniere_mise_a_jour"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.memoire = nouveau
        return self.memoire

    def get_contexte(self):
        if not self.memoire["resume"]:
            return ""
        lignes = ["=== MÉMOIRE DE LA CONVERSATION ===", f"Résumé : {self.memoire['resume']}"]
        if self.memoire["decisions"]:
            lignes.append("Décisions : " + " | ".join(self.memoire["decisions"]))
        if self.memoire["erreurs_vues"]:
            lignes.append("Erreurs résolues : " + " | ".join(self.memoire["erreurs_vues"]))
        if self.memoire["code_produit"]:
            lignes.append("Code : " + " | ".join(self.memoire["code_produit"]))
        if self.memoire["prochaine_etape"]:
            lignes.append(f"Prochaine étape : {self.memoire['prochaine_etape']}")
        lignes.append("=================================")
        return "\n".join(lignes)

    def afficher(self):
        print("\n📋 MÉMOIRE ACTUELLE")
        print("=" * 40)
        print(json.dumps(self.memoire, ensure_ascii=False, indent=2))
        print("=" * 40)

if __name__ == "__main__":
    agent = MemoryAgent()
    historique_test = [
        {"role": "user", "content": "On a mis en place le système de mémoire Drive."},
        {"role": "assistant", "content": "Oui, token.json créé, agent mémoire fonctionnel."},
    ]
    agent.resumer(historique_test)
    agent.afficher()
    agent.sauvegarder()
    print("\n📌 CONTEXTE :")
    print(agent.get_contexte())
