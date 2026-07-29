"""
deploy_agent.py — Agent Déploiement MP Solutions IA
Guide le déploiement GitHub → Render étape par étape.
Usage : from deploy_agent import DeployAgent
"""

import subprocess
import os

# Projets connus de Marc-Paul
PROJETS = {
    "camping": {
        "nom": "Camping Les Eychecadous",
        "repo": "chatbot-camping-eychecadous",
        "url": "https://chatbot-camping-eychecadous.onrender.com",
        "dossier": "/c/Projets/chatbot-camping-eychecadous",
    },
    "agent-loop": {
        "nom": "Agent Loop MP Solutions IA",
        "repo": "agent-loop",
        "url": "https://agent-loop.onrender.com",
        "dossier": "/c/Projets/agent-loop",
    },
}


class DeployAgent:
    def __init__(self):
        self.projets = PROJETS

    def verifier_git(self, dossier: str) -> dict:
        """Vérifie l'état Git du projet."""
        resultat = {"statut": "ok", "messages": []}
        try:
            # Fichiers modifiés
            r = subprocess.run(
                ["git", "status", "--short"],
                cwd=dossier, capture_output=True, text=True
            )
            if r.stdout.strip():
                resultat["messages"].append(f"Fichiers modifiés :\n{r.stdout.strip()}")
            else:
                resultat["messages"].append("Aucun fichier modifié — tout est à jour.")

            # Branche courante
            r2 = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=dossier, capture_output=True, text=True
            )
            resultat["branche"] = r2.stdout.strip()

        except Exception as e:
            resultat["statut"] = "erreur"
            resultat["messages"].append(str(e))

        return resultat

    def deployer(self, projet_key: str, message_commit: str = "") -> dict:
        """
        Lance le déploiement complet : git add → commit → push.
        Retourne un rapport détaillé.
        """
        if projet_key not in self.projets:
            return {"statut": "erreur", "message": f"Projet '{projet_key}' inconnu."}

        projet = self.projets[projet_key]
        dossier = projet["dossier"]
        rapport = {"projet": projet["nom"], "etapes": [], "statut": "ok"}

        if not message_commit:
            message_commit = f"mise a jour {projet['nom']}"

        etapes = [
            (["git", "add", "."], "git add ."),
            (["git", "commit", "-m", message_commit], f"git commit -m '{message_commit}'"),
            (["git", "push", "origin", "main"], "git push origin main"),
        ]

        for commande, label in etapes:
            try:
                r = subprocess.run(
                    commande, cwd=dossier,
                    capture_output=True, text=True
                )
                if r.returncode == 0:
                    rapport["etapes"].append({"etape": label, "statut": "✓", "detail": r.stdout.strip()})
                else:
                    rapport["etapes"].append({"etape": label, "statut": "✗", "detail": r.stderr.strip()})
                    rapport["statut"] = "erreur"
                    break
            except Exception as e:
                rapport["etapes"].append({"etape": label, "statut": "✗", "detail": str(e)})
                rapport["statut"] = "erreur"
                break

        if rapport["statut"] == "ok":
            rapport["url"] = projet["url"]
            rapport["message_final"] = f"Déploiement lancé sur Render. Vérifier dans 2-3 minutes : {projet['url']}"

        return rapport

    def guide_deploiement(self, projet_key: str) -> str:
        """Retourne les commandes Git à lancer dans le bon ordre."""
        if projet_key not in self.projets:
            return f"Projet '{projet_key}' inconnu."

        projet = self.projets[projet_key]
        return f"""=== DÉPLOIEMENT {projet['nom'].upper()} ===
1. cd {projet['dossier']}
2. git add .
3. git commit -m "mise a jour"
4. git push origin main
5. Attendre 2-3 minutes
6. Vérifier : {projet['url']}
=========================================="""

    def get_contexte(self) -> str:
        """Retourne le contexte pour injection dans un SYSTEM_PROMPT."""
        projets_liste = ", ".join([v["nom"] for v in self.projets.values()])
        return f"""=== AGENT DÉPLOIEMENT ACTIF ===
Projets connus : {projets_liste}
Commandes : deploy_agent.deployer('camping') ou deploy_agent.deployer('agent-loop')
Vérification : deploy_agent.verifier_git('/c/Projets/mon-projet')
================================"""


# ── Exemple d'utilisation ──────────────────────────────────────────────────────
if __name__ == "__main__":
    agent = DeployAgent()

    print("Guide déploiement camping :")
    print(agent.guide_deploiement("camping"))

    print("\nGuide déploiement agent-loop :")
    print(agent.guide_deploiement("agent-loop"))
