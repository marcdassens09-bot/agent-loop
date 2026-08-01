"""
search_agent.py — Agent Recherche MP Solutions IA
Cherche sur le web quand Claude bloque sur une question technique.
Usage : from search_agent import SearchAgent
"""

import requests


class SearchAgent:
    def __init__(self):
        self.api_url = "https://api.duckduckgo.com/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def chercher(self, question: str, max_resultats: int = 3) -> str:
        """
        Cherche sur le web et retourne un résumé des résultats.
        Retourne une chaîne à injecter dans le SYSTEM_PROMPT.
        """
        try:
            params = {
                "q": question,
                "format": "json",
                "no_html": 1
            }
            response = requests.get(self.api_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            resultats = data.get("Results", [])

            if not resultats:
                return ""

            lignes = ["=== RECHERCHE WEB ==="]
            for i, r in enumerate(resultats[:max_resultats], 1):
                titre = r.get("Title", "Sans titre")
                description = r.get("Text", "")[:200] or "Pas de description"
                url = r.get("FirstURL", "")

                lignes.append(f"{i}. {titre}")
                lignes.append(f"   {description}...")
                lignes.append(f"   Source : {url}")

            lignes.append("====================")
            return "\n".join(lignes)

        except requests.RequestException as e:
            return f"Recherche impossible : {e}"
        except Exception as e:
            return f"Erreur lors du traitement : {e}"

    def doit_chercher(self, message: str) -> bool:
        """
        Détecte si le message de l'utilisateur nécessite une recherche web.
        Retourne True si oui.
        """
        mots_cles = [
            "comment", "pourquoi", "qu'est-ce", "c'est quoi",
            "erreur", "problème", "bug", "ne marche pas",
            "prix", "tarif", "dernière version", "update",
            "documentation", "doc", "exemple", "tutoriel"
        ]
        message_lower = message.lower()
        return any(mot in message_lower for mot in mots_cles)

    def get_contexte(self, question: str) -> str:
        """
        Lance une recherche et retourne le contexte formaté.
        À appeler uniquement si doit_chercher() retourne True.
        """
        return self.chercher(question)


# ── Exemple d'utilisation ──────────────────────────────────────────────────────
if __name__ == "__main__":
    agent = SearchAgent()

    question = "Flask Python erreur 500 debug"
    print(f"Recherche : {question}\n")

    if agent.doit_chercher(question):
        contexte = agent.get_contexte(question)
        print(contexte)
    else:
        print("Pas besoin de recherche pour cette question.")
