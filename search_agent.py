"""
search_agent.py — Agent Recherche MP Solutions IA
Cherche sur le web quand Claude bloque sur une question technique.
Usage : from search_agent import SearchAgent
"""

from ddgs import DDGS


class SearchAgent:
    def __init__(self):
        self.ddgs = DDGS()

    def chercher(self, question: str, max_resultats: int = 3) -> str:
        """
        Cherche sur le web et retourne un résumé des résultats.
        Retourne une chaîne à injecter dans le SYSTEM_PROMPT.
        """
        try:
            resultats = list(self.ddgs.text(question, max_results=max_resultats))

            if not resultats:
                return ""

            lignes = ["=== RECHERCHE WEB ==="]
            for i, r in enumerate(resultats, 1):
                lignes.append(f"{i}. {r['title']}")
                lignes.append(f"   {r['body'][:200]}...")
                lignes.append(f"   Source : {r['href']}")

            lignes.append("====================")
            return "\n".join(lignes)

        except Exception as e:
            return f"Recherche impossible : {e}"

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
