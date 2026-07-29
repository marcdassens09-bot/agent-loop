"""
memory_agent.py — Agent Mémoire MP Solutions IA
Résume la conversation et retient les décisions importantes.
Usage : from memory_agent import MemoryAgent
"""

import anthropic
import json
from datetime import datetime

client = anthropic.Anthropic()  # lit ANTHROPIC_API_KEY depuis .env

SYSTEM_PROMPT = """Tu es l'Agent Mémoire de MP Solutions IA.
Ton seul rôle : analyser une conversation et produire un résumé structuré en JSON.

Réponds UNIQUEMENT avec ce JSON, rien d'autre :
{
  "resume": "Résumé court de la conversation en 2-3 phrases",
  "decisions": ["décision 1", "décision 2"],
  "erreurs_vues": ["erreur 1 déjà résolue", "erreur 2 déjà résolue"],
  "code_produit": ["fichier1.py : ce qu'il fait", "fichier2.py : ce qu'il fait"],
  "prochaine_etape": "Ce qu'il reste à faire"
}"""


class MemoryAgent:
    def __init__(self):
        self.memoire = {
            "resume": "",
            "decisions": [],
            "erreurs_vues": [],
            "code_produit": [],
            "prochaine_etape": "",
            "derniere_mise_a_jour": ""
        }
        self.compteur_messages = 0
        self.FREQUENCE_RESUME = 5  # résume toutes les 5 messages

    def doit_resumer(self) -> bool:
        """Retourne True si on doit faire un nouveau résumé."""
        self.compteur_messages += 1
        return self.compteur_messages % self.FREQUENCE_RESUME == 0

    def resumer(self, historique: list[dict]) -> dict:
        """
        Envoie l'historique à Claude et récupère un résumé structuré.
        historique : liste de dicts {"role": "user"/"assistant", "content": "..."}
        """
        # On prend les 20 derniers messages max pour ne pas exploser les tokens
        historique_court = historique[-20:]

        conversation_texte = "\n".join([
            f"{msg['role'].upper()} : {msg['content']}"
            for msg in historique_court
        ])

        prompt = f"""Voici la conversation à résumer :

{conversation_texte}

Résumé existant (à enrichir si besoin) :
{json.dumps(self.memoire, ensure_ascii=False, indent=2)}"""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )

        texte = response.content[0].text.strip()

        # Nettoie les balises markdown si présentes
        texte = texte.replace("```json", "").replace("```", "").strip()

        nouveau_resume = json.loads(texte)
        nouveau_resume["derniere_mise_a_jour"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.memoire = nouveau_resume
        return self.memoire

    def get_contexte(self) -> str:
        """
        Retourne le contexte mémorisé formaté pour l'injecter dans un SYSTEM_PROMPT.
        Utilise ~150-200 tokens seulement.
        """
        if not self.memoire["resume"]:
            return ""

        lignes = [
            "=== MÉMOIRE DE LA CONVERSATION ===",
            f"Résumé : {self.memoire['resume']}",
        ]

        if self.memoire["decisions"]:
            lignes.append("Décisions prises : " + " | ".join(self.memoire["decisions"]))

        if self.memoire["erreurs_vues"]:
            lignes.append("Erreurs déjà résolues : " + " | ".join(self.memoire["erreurs_vues"]))

        if self.memoire["code_produit"]:
            lignes.append("Code produit : " + " | ".join(self.memoire["code_produit"]))

        if self.memoire["prochaine_etape"]:
            lignes.append(f"Prochaine étape : {self.memoire['prochaine_etape']}")

        lignes.append("=================================")
        return "\n".join(lignes)

    def afficher(self):
        """Affiche la mémoire actuelle dans le terminal."""
        print("\n📋 MÉMOIRE ACTUELLE")
        print("=" * 40)
        print(json.dumps(self.memoire, ensure_ascii=False, indent=2))
        print("=" * 40)


# ── Exemple d'utilisation ──────────────────────────────────────────────────────
if __name__ == "__main__":
    agent = MemoryAgent()

    # Simule un historique de conversation
    historique_test = [
        {"role": "user", "content": "Je veux créer un chatbot pour le Camping Les Eychecadous."},
        {"role": "assistant", "content": "D'accord. On va créer agent.py avec Flask. Commence par installer flask et anthropic."},
        {"role": "user", "content": "J'ai une erreur : ModuleNotFoundError: No module named 'flask'"},
        {"role": "assistant", "content": "Lance : pip install flask anthropic python-dotenv"},
        {"role": "user", "content": "Ça marche ! Maintenant j'ai une erreur 500 sur /chat"},
        {"role": "assistant", "content": "Vérifie que ta clé API est bien dans le fichier .env : ANTHROPIC_API_KEY=sk-ant-..."},
    ]

    print("Résumé en cours...")
    resume = agent.resumer(historique_test)
    agent.afficher()

    print("\n📌 CONTEXTE À INJECTER DANS LE SYSTEM PROMPT :")
    print(agent.get_contexte())
