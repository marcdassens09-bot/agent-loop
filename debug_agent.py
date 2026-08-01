"""
debug_agent.py — Agent Débogage MP Solutions IA
Analyse les erreurs Python/Flask et propose des corrections.
Usage : from debug_agent import DebugAgent
"""

import os
import anthropic
import re
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
client = anthropic.Anthropic(api_key=api_key)

SYSTEM_PROMPT = """Tu es l'Agent Débogage de MP Solutions IA.
Tu analyses les erreurs Python/Flask et tu proposes des corrections claires.

Quand on te donne une erreur, réponds TOUJOURS avec ce format exact :

ERREUR DÉTECTÉE : [type d'erreur en une ligne]
CAUSE : [explication simple en 1-2 phrases]
CORRECTION :
[le code corrigé ou la commande à lancer]
VÉRIFICATION : [comment savoir si c'est réglé]"""


class DebugAgent:
    def __init__(self):
        self.erreurs_connues = {
            "ModuleNotFoundError": "pip install {module} --break-system-packages",
            "IndentationError": "Vérifie l'indentation — utilise 4 espaces partout",
            "KeyError": "La clé n'existe pas dans le dictionnaire — vérifie le nom exact",
            "JSONDecodeError": "Le JSON est mal formé — vérifie les guillemets et les virgules",
            "ConnectionRefusedError": "Le serveur n'est pas lancé — lance python app.py d'abord",
            "500": "Erreur serveur — regarde les logs Flask dans le terminal",
            "400": "Requête mal formée — vérifie le Content-Type et le JSON envoyé",
        }

    def est_une_erreur(self, message: str) -> bool:
        """Détecte si le message contient une erreur Python ou HTTP."""
        mots_erreur = [
            "error", "erreur", "traceback", "exception",
            "failed", "cannot", "invalid", "unexpected",
            "500", "400", "404", "refused"
        ]
        message_lower = message.lower()
        return any(mot in message_lower for mot in mots_erreur)

    def solution_rapide(self, erreur: str) -> str:
        """Retourne une solution rapide si l'erreur est connue."""
        for cle, solution in self.erreurs_connues.items():
            if cle.lower() in erreur.lower():
                # Extrait le nom du module si ModuleNotFoundError
                if cle == "ModuleNotFoundError":
                    match = re.search(r"No module named '([^']+)'", erreur)
                    if match:
                        module = match.group(1)
                        return solution.replace("{module}", module)
                return solution
        return ""

    def analyser(self, erreur: str) -> str:
        """
        Envoie l'erreur à Claude pour analyse complète.
        Retourne une analyse structurée.
        """
        # Vérifie d'abord les solutions rapides
        solution_rapide = self.solution_rapide(erreur)
        if solution_rapide:
            contexte = f"Solution rapide connue : {solution_rapide}\n\n"
        else:
            contexte = ""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"{contexte}Voici l'erreur à analyser :\n\n{erreur}"
            }]
        )
        return response.content[0].text.strip()

    def get_contexte(self) -> str:
        """Retourne le contexte pour injection dans un SYSTEM_PROMPT."""
        return """=== AGENT DÉBOGAGE ACTIF ===
Si l'utilisateur colle une erreur Python ou Flask, analyse-la et propose une correction précise.
Erreurs courantes connues : ModuleNotFoundError, IndentationError, KeyError, 500, 400.
============================"""


# ── Exemple d'utilisation ──────────────────────────────────────────────────────
if __name__ == "__main__":
    agent = DebugAgent()

    erreur_test = """
Traceback (most recent call last):
  File "app.py", line 1, in <module>
    from memory_agent import MemoryAgent
ModuleNotFoundError: No module named 'memory_agent'
"""

    print("Test solution rapide :")
    print(agent.solution_rapide(erreur_test))

    print("\nTest analyse complète :")
    print(agent.analyser(erreur_test))
