"""
loader.py — Chargeur principal MP Solutions IA
Charge tous les agents au démarrage, ne fait rien tant qu'ils ne sont pas appelés.
Usage : from loader import agents
"""

from dotenv import load_dotenv
load_dotenv()

from memory_agent import MemoryAgent
from clients_context_agent import ClientsContextAgent
from tarifs_agent import TarifsAgent
from charte_agent import CharteAgent
from github_agent import GithubAgent

# ── IDs Google Drive ───────────────────────────────────────────────────────────
DRIVE_IDS = {
    "memory":   "1cu0ow2ieeWpo7odrkS83XFPeHBUbJV8eBtAcWzrVNYc",
    "clients":  "1b5lHVNeILZjygFqKBjo6yzEyA_qP0N9Pl6U1YXuMzxo",
    "tarifs":   "1oE96YWFDvMyWbioDyVkswkGLNWhH1KMBwwlrXB9LuYc",
    "charte":   "10m0NCzoEcsH9WvWginzznzrQsb8SISv35kmG6_UNef4",
    "github":   "1do1ZC2p7ySCXYb8OpGl_Z-ZJux7kjgCZd4ZNwd3XEHM",
}


class AgentLoader:
    def __init__(self):
        self._agents = {}
        self._charge = False

    def charger(self):
        """Charge tous les agents depuis Drive. À appeler une seule fois au démarrage."""
        if self._charge:
            print("⚠️ Agents déjà chargés.")
            return

        print("\n🔄 Chargement des agents MP Solutions IA...")
        print("-" * 40)

        self._agents["memory"]  = MemoryAgent()
        self._agents["clients"] = ClientsContextAgent(drive_file_id=DRIVE_IDS["clients"])
        self._agents["tarifs"]  = TarifsAgent(drive_file_id=DRIVE_IDS["tarifs"])
        self._agents["charte"]  = CharteAgent(drive_file_id=DRIVE_IDS["charte"])
        self._agents["github"]  = GithubAgent(drive_file_id=DRIVE_IDS["github"])

        self._charge = True
        print("-" * 40)
        print("✓ Tous les agents sont prêts.\n")

    def get(self, nom: str):
        """Retourne un agent par son nom."""
        if not self._charge:
            print("⚠️ Lance d'abord loader.charger()")
            return None
        return self._agents.get(nom)

    def get_contexte_complet(self) -> str:
        """Retourne le contexte de tous les agents combiné — pour injecter dans Claude."""
        if not self._charge:
            return ""
        blocs = []
        for nom, agent in self._agents.items():
            try:
                contexte = agent.get_contexte()
                if contexte:
                    blocs.append(contexte)
            except Exception as e:
                print(f"⚠️ Erreur contexte {nom} : {e}")
        return "\n\n".join(blocs)

    def sauvegarder_tout(self):
        """Sauvegarde tous les agents sur Drive — à appeler en fin de session."""
        if not self._charge:
            print("⚠️ Aucun agent chargé.")
            return
        print("\n💾 Sauvegarde de tous les agents...")
        for nom, agent in self._agents.items():
            try:
                agent.sauvegarder()
            except Exception as e:
                print(f"⚠️ Erreur sauvegarde {nom} : {e}")
        print("✓ Sauvegarde terminée.\n")

    def statut(self):
        """Affiche le statut de tous les agents."""
        print("\n📋 STATUT DES AGENTS")
        print("=" * 40)
        if not self._charge:
            print("⚠️ Aucun agent chargé — lance charger() d'abord.")
            return
        for nom in self._agents:
            print(f"  ✓ {nom}")
        print("=" * 40)


# ── Instance globale ───────────────────────────────────────────────────────────
agents = AgentLoader()


# ── Lancement direct ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Charge tous les agents
    agents.charger()

    # Affiche le statut
    agents.statut()

    # Exemple : accéder à un agent spécifique
    # agents.get("clients").afficher()
    # agents.get("tarifs").afficher()

    # Exemple : contexte complet pour Claude
    # print(agents.get_contexte_complet())

    # Exemple : sauvegarder en fin de session
    # agents.sauvegarder_tout()
