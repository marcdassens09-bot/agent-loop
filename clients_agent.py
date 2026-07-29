"""
clients_agent.py — Agent Suivi Clients MP Solutions IA
Suit l'état de chaque client/prospect et rappelle les actions à faire.
Usage : from clients_agent import ClientsAgent
"""

import json
from datetime import datetime, timedelta

# ── Base clients MP Solutions IA ───────────────────────────────────────────────
CLIENTS = {
    "camping": {
        "nom": "Anthony Viviano",
        "entreprise": "Camping Les Eychecadous",
        "statut": "actif",
        "depuis": "2025",
        "mensualite": 60,
        "prochaine_action": "",
        "notes": "Chatbot opérationnel sur Render",
        "url": "chatbot-camping-eychecadous.onrender.com",
    },
    "moucheron": {
        "nom": "Maxime Moucheron",
        "entreprise": "Full Habitat EURL",
        "statut": "actif",
        "depuis": "2025",
        "mensualite": 60,
        "prochaine_action": "",
        "notes": "Électricien/plombier certifié, Baulou 09",
        "url": "",
    },
}

PROSPECTS = {
    "fumeco": {
        "nom": "Thomas Fournial",
        "entreprise": "Fumeco-Lèze",
        "statut": "prospect",
        "secteur": "Fabricant substrats/compost",
        "prochaine_action": "Envoyer dossier commercial",
        "notes": "Artigat — contact à relancer",
    },
    "couleurs_asie": {
        "nom": "Responsable",
        "entreprise": "Couleurs d'Asie",
        "statut": "prospect",
        "secteur": "Restaurant cambodgien",
        "prochaine_action": "Premier contact à faire",
        "notes": "Le Fossat",
    },
    "boulangerie": {
        "nom": "Adrien De Oliveira",
        "entreprise": "Boulangerie De Oliveira",
        "statut": "prospect",
        "secteur": "Boulangerie",
        "prochaine_action": "Premier contact à faire",
        "notes": "Le Fossat",
    },
    "table_fossat": {
        "nom": "Responsable",
        "entreprise": "La Table du Fossat",
        "statut": "prospect",
        "secteur": "Restaurant",
        "prochaine_action": "Premier contact à faire",
        "notes": "Le Fossat",
    },
}


class ClientsAgent:
    def __init__(self):
        self.clients = CLIENTS
        self.prospects = PROSPECTS

    def tableau_de_bord(self) -> str:
        """Retourne un résumé complet clients + prospects."""
        lignes = ["=== TABLEAU DE BORD MP SOLUTIONS IA ===", ""]

        # Clients actifs
        lignes.append("▸ CLIENTS ACTIFS")
        total_mensuel = 0
        for cle, c in self.clients.items():
            lignes.append(f"  ✓ {c['entreprise']} — {c['mensualite']}€/mois")
            if c["prochaine_action"]:
                lignes.append(f"    → Action : {c['prochaine_action']}")
            total_mensuel += c["mensualite"]

        lignes.append(f"  TOTAL MENSUEL : {total_mensuel}€")
        lignes.append("")

        # Prospects
        lignes.append("▸ PROSPECTS EN COURS")
        for cle, p in self.prospects.items():
            lignes.append(f"  ◆ {p['entreprise']} ({p['secteur']})")
            lignes.append(f"    → {p['prochaine_action']}")

        lignes.append("")
        lignes.append(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
        lignes.append("========================================")

        return "\n".join(lignes)

    def actions_a_faire(self) -> list:
        """Retourne la liste des actions urgentes."""
        actions = []
        for cle, p in self.prospects.items():
            if p["prochaine_action"]:
                actions.append({
                    "entreprise": p["entreprise"],
                    "action": p["prochaine_action"],
                    "priorite": "haute" if "relancer" in p["prochaine_action"].lower() else "normale",
                })
        for cle, c in self.clients.items():
            if c["prochaine_action"]:
                actions.append({
                    "entreprise": c["entreprise"],
                    "action": c["prochaine_action"],
                    "priorite": "haute",
                })
        return actions

    def mettre_a_jour(self, cle: str, prochaine_action: str, notes: str = "") -> str:
        """Met à jour l'action suivante pour un client ou prospect."""
        if cle in self.clients:
            self.clients[cle]["prochaine_action"] = prochaine_action
            if notes:
                self.clients[cle]["notes"] = notes
            return f"Client {self.clients[cle]['entreprise']} mis à jour."

        if cle in self.prospects:
            self.prospects[cle]["prochaine_action"] = prochaine_action
            if notes:
                self.prospects[cle]["notes"] = notes
            return f"Prospect {self.prospects[cle]['entreprise']} mis à jour."

        return f"Clé '{cle}' inconnue."

    def revenu_mensuel(self) -> int:
        """Retourne le revenu mensuel total."""
        return sum(c["mensualite"] for c in self.clients.values())

    def get_contexte(self) -> str:
        """Retourne le contexte pour injection dans un SYSTEM_PROMPT."""
        actions = self.actions_a_faire()
        actions_texte = " | ".join([f"{a['entreprise']}: {a['action']}" for a in actions])
        return f"""=== SUIVI CLIENTS MP SOLUTIONS IA ===
Clients actifs : {len(self.clients)} — Revenu mensuel : {self.revenu_mensuel()}€
Prospects : {len(self.prospects)}
Actions à faire : {actions_texte if actions_texte else 'Aucune'}
====================================="""


# ── Exemple d'utilisation ──────────────────────────────────────────────────────
if __name__ == "__main__":
    agent = ClientsAgent()

    print(agent.tableau_de_bord())

    print("\nActions à faire :")
    for action in agent.actions_a_faire():
        print(f"  [{action['priorite'].upper()}] {action['entreprise']} → {action['action']}")

    print(f"\nRevenu mensuel : {agent.revenu_mensuel()}€")
