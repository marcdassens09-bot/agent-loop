"""
clients_agent.py — Agent Suivi Clients MP Solutions IA
Suit l'état de chaque client/prospect et rappelle les actions à faire.
Usage : from clients_agent import ClientsAgent
"""

import json
import re
from datetime import datetime, timedelta

# Nombre de jours sans réponse au-delà duquel une relance est proposée.
SEUIL_RELANCE_JOURS = 5

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
    # ── Artigat ──────────────────────────────────────────────────────────
    "batisse_deco": {
        "nom": "Responsable",
        "entreprise": "Batisse et Deco",
        "statut": "prospect",
        "secteur": "Terrassement/VRD, SIRET 808 559 736 00018",
        "prochaine_action": "Dossier prêt, pas encore livré (pas de véhicule pour aller démarcher sur place)",
        "notes": "Artigat — campagne BTP Artigat, méthode vérif SIRET/pas de réseau national/sans site du 17/08. Dossier PDF généré et validé, jamais livré au prospect.",
    },

    # ── Le Fossat ────────────────────────────────────────────────────────
    "fumeco": {
        "nom": "Thomas Fournial",
        "entreprise": "Fumeco-Lèze",
        "statut": "prospect",
        "secteur": "Fabricant substrats/compost, +15 salariés",
        "prochaine_action": "Dossier prêt, pas encore envoyé (pas de véhicule pour aller démarcher sur place)",
        "notes": "Artigat — dossier prêt depuis le 17/08/2026, jamais réellement envoyé à contact@fumeco.fr",
    },
    "couleurs_asie": {
        "nom": "Responsable",
        "entreprise": "Couleurs d'Asie",
        "statut": "prospect",
        "secteur": "Restaurant cambodgien",
        "prochaine_action": "Relancer pour signature",
        "notes": "Le Fossat — dossier en cours depuis le 13/07, menus HTML déjà prêts, pas encore signé",
    },
    "boulangerie": {
        "nom": "Adrien De Oliveira",
        "entreprise": "Boulangerie De Oliveira",
        "statut": "prospect",
        "secteur": "Boulangerie",
        "prochaine_action": "Compléter questionnaire + bon de commande avant relance",
        "notes": "Le Fossat — dossier créé le 07/08/2026, rien envoyé depuis",
    },
    "table_fossat": {
        "nom": "Responsable",
        "entreprise": "La Table du Fossat",
        "statut": "écarté",
        "secteur": "Restaurant",
        "prochaine_action": "",
        "notes": "Le Fossat — gérant ne veut pas se développer, ne pas reproposer",
    },
    "trattoria": {
        "nom": "Yoann Bertrant",
        "entreprise": "La Trattoria (ex-Nanie's Coffee)",
        "statut": "prospect",
        "secteur": "Bar-restaurant",
        "prochaine_action": "Déposer le dossier à jour sur Drive (glisser-déposer manuel)",
        "notes": "Le Fossat — connaissance personnelle de marc-paul, dossier mis à jour le 11/08/2026",
    },
    "dupuy_services": {
        "nom": "Responsable",
        "entreprise": "Menuiseries Dupuy Services",
        "statut": "prospect",
        "secteur": "Menuiserie, SIRET 823 554 886 00015",
        "prochaine_action": "Dossier prêt, pas encore livré (pas de véhicule pour aller démarcher sur place)",
        "notes": "Le Fossat — campagne BTP Artigat, méthode vérif SIRET/pas de réseau national/sans site du 17/08. Dossier PDF généré et validé, jamais livré au prospect.",
    },
    "pons_plaquiste": {
        "nom": "Responsable",
        "entreprise": "Pons Plaquiste Peintre",
        "statut": "prospect",
        "secteur": "Plaquiste-peintre, SAS, 3-5 salariés RGE Qualibat, SIRET 823 725 601 00012",
        "prochaine_action": "Dossier prêt, pas encore livré (pas de véhicule pour aller démarcher sur place)",
        "notes": "Le Fossat — campagne BTP Artigat. Dossier resserré sur 1 page (docs_template/dossier_pons.py sur mp-solutions-ia), validé le 22/08/2026, jamais livré au prospect.",
    },
    "ajmp": {
        "nom": "Responsable",
        "entreprise": "AJMP Plombier Chauffagiste",
        "statut": "prospect",
        "secteur": "Plomberie/chauffage, PME",
        "prochaine_action": "Premier contact à faire",
        "notes": "Foix — dossier créé le 17/08/2026, jamais envoyé",
    },
    "labadie": {
        "nom": "Sébastien Labadie",
        "entreprise": "Labadie Plombier Chauffagiste",
        "statut": "prospect",
        "secteur": "Plomberie/chauffage, artisan solo",
        "prochaine_action": "Premier contact à faire",
        "notes": "Pamiers — dossier créé le 07/08/2026, jamais envoyé",
    },
    "hg_habitat": {
        "nom": "Hugo Galibert",
        "entreprise": "HG Habitat",
        "statut": "prospect",
        "secteur": "Plomberie/chauffage RGE, artisan solo",
        "prochaine_action": "Premier contact à faire",
        "notes": "Foix/Pamiers — dossier créé le 17/08/2026, jamais envoyé",
    },

    # ── Lézat-sur-Lèze ───────────────────────────────────────────────────
    "garrigues": {
        "nom": "Alain Garrigues",
        "entreprise": "Garage Garrigues Alain (AD Expert)",
        "statut": "prospect",
        "secteur": "Garage-carrosserie, PME",
        "prochaine_action": "Dossier prêt, pas encore livré (pas de véhicule pour aller démarcher sur place)",
        "notes": "Lézat-sur-Lèze — dossier prêt depuis le 17/08/2026, jamais livré",
    },
    "cantine_prieure": {
        "nom": "Responsable",
        "entreprise": "La Cantine du Prieuré (SARL La Commanderie)",
        "statut": "prospect",
        "secteur": "Restaurant, PME",
        "prochaine_action": "Dossier prêt, pas encore livré (pas de véhicule pour aller démarcher sur place)",
        "notes": "Lézat-sur-Lèze — dossier prêt depuis le 17/08/2026, jamais livré",
    },
    "cb_couverture": {
        "nom": "Christophe Burkler",
        "entreprise": "CB Couverture",
        "statut": "prospect",
        "secteur": "Couverture RGE, PME",
        "prochaine_action": "Confirmer coordonnées directes, puis dossier prêt mais pas encore livré (pas de véhicule)",
        "notes": "Lézat-sur-Lèze — dossier prêt depuis le 17/08/2026, jamais livré",
    },
    "sans_et_fils": {
        "nom": "Thomas et Lucas Sans",
        "entreprise": "Sans et Fils",
        "statut": "prospect",
        "secteur": "Chauffage/clim/photovoltaïque, PME",
        "prochaine_action": "Dossier prêt, pas encore livré (pas de véhicule pour aller démarcher sur place)",
        "notes": "Lézat-sur-Lèze — dossier prêt depuis le 17/08/2026, jamais livré, site jamais publié",
    },
    "briques_et_galets": {
        "nom": "Responsable",
        "entreprise": "Briques et Galets",
        "statut": "prospect",
        "secteur": "Maçonnerie/couverture/isolation, PME",
        "prochaine_action": "Dossier prêt, pas encore livré (pas de véhicule pour aller démarcher sur place)",
        "notes": "Lézat-sur-Lèze — dossier prêt depuis le 17/08/2026, jamais livré",
    },
    "jardinerie_franquine": {
        "nom": "Dominique Franquine",
        "entreprise": "Jardinerie Franquine",
        "statut": "prospect",
        "secteur": "Jardinerie/fleuriste, artisan solo",
        "prochaine_action": "Dossier prêt, pas encore livré (pas de véhicule pour aller démarcher sur place)",
        "notes": "Lézat-sur-Lèze — demandé nommément par marc-paul, dossier prêt depuis le 17/08/2026, jamais livré",
    },
    "domaine_lastronques": {
        "nom": "Laure Zeller",
        "entreprise": "Domaine de Lastronques",
        "statut": "prospect",
        "secteur": "Domaine viticole, artisan solo",
        "prochaine_action": "Marc-paul envoie lui-même le mail de prise de contact (texte déjà prêt)",
        "notes": "Lézat-sur-Lèze — connaissance personnelle de marc-paul (y a travaillé)",
    },

    # ── Autres pistes personnelles ──────────────────────────────────────
    "adesimmo": {
        "nom": "Jean-François",
        "entreprise": "ADESIMMO",
        "statut": "prospect",
        "secteur": "Agence immobilière",
        "prochaine_action": "Validation finale du dossier par marc-paul avant envoi",
        "notes": "Saint-Sulpice-sur-Lèze — ami personnel de marc-paul, dossier condensé (2 pages) prêt",
    },
    "bordenave": {
        "nom": "Nicolas Bordenave",
        "entreprise": "Bordenave (plaquiste-jointeur RGE)",
        "statut": "prospect",
        "secteur": "Plaquiste, artisan solo",
        "prochaine_action": "Dossier prêt, pas encore livré (pas de véhicule pour aller démarcher sur place)",
        "notes": "Le Fossat — dossier prêt depuis le 17/08/2026, jamais livré",
    },
    "claustre": {
        "nom": "Loïc Claustre",
        "entreprise": "Claustre (plombier-chauffagiste QualiPac)",
        "statut": "prospect",
        "secteur": "Plomberie/chauffage RGE, artisan solo/PME",
        "prochaine_action": "Dossier prêt, pas encore livré (pas de véhicule pour aller démarcher sur place)",
        "notes": "Le Mas-d'Azil — dossier prêt depuis le 17/08/2026, jamais livré",
    },
    "electron": {
        "nom": "Responsable",
        "entreprise": "Électron",
        "statut": "prospect",
        "secteur": "Électricien",
        "prochaine_action": "Dossier prêt, pas encore livré (pas de véhicule pour aller démarcher sur place)",
        "notes": "Sabarat — dossier prêt depuis le 17/08/2026, jamais livré, ancien site tombé",
    },

    # ── Vétérinaires (Ariège/Haute-Garonne) ─────────────────────────────
    "veto_damin": {
        "nom": "Dr Julie Damin",
        "entreprise": "Dr Julie Damin (nom du cabinet inconnu)",
        "statut": "prospect",
        "secteur": "Vétérinaire",
        "prochaine_action": "Monter le dossier (pas encore commencé)",
        "notes": "Lézat-sur-Lèze — repérée sans site, pas encore de premier contact",
    },
    "veto_trichet": {
        "nom": "Dr Trichet",
        "entreprise": "Dr Trichet (nom du cabinet inconnu)",
        "statut": "prospect",
        "secteur": "Vétérinaire",
        "prochaine_action": "Monter le dossier (pas encore commencé)",
        "notes": "Saverdun — repéré sans site, pas encore de premier contact",
    },
    "veto_castaing": {
        "nom": "Castaing",
        "entreprise": "Castaing (nom du cabinet inconnu)",
        "statut": "prospect",
        "secteur": "Vétérinaire",
        "prochaine_action": "Monter le dossier (pas encore commencé)",
        "notes": "Saverdun — repéré sans site, pas encore de premier contact",
    },

    # ── Location de matériel (Ariège) ───────────────────────────────────
    "snlc_appameteck": {
        "nom": "Cyril Charbonnier",
        "entreprise": "SNLC Appameteck",
        "statut": "prospect",
        "secteur": "Location sono/éclairage événementiel, auto-entrepreneur, SIRET 512199415 00039",
        "prochaine_action": "Dossier découverte prêt (sans tarif), premier contact à faire",
        "notes": "Pamiers — actif depuis 2009, repéré sans site fonctionnel (deux sites abandonnés "
                 "trouvés, e-monsite et Wix). Dossier découverte généré le 22/08/2026 "
                 "(dossier_snlc_appameteck.py sur mp-solutions-ia) — pas de tarif proposé avant "
                 "premier échange. Pas encore envoyé.",
    },

    # ── Sport (Ariège) ───────────────────────────────────────────────────
    "move_fitness": {
        "nom": "Gualter Da Silva Machado",
        "entreprise": "Move Fitness",
        "statut": "prospect",
        "secteur": "Salle de fitness, SIRET 821902434 00017",
        "prochaine_action": "Monter le dossier découverte (pas encore commencé)",
        "notes": "Saverdun — active depuis 2016, repérée sans site propre (Facebook et annuaires "
                 "uniquement), pas encore de premier contact",
    },
    "eterlou_sport": {
        "nom": "Responsable",
        "entreprise": "L'Éterlou Sport",
        "statut": "prospect",
        "secteur": "Magasin d'articles de sport (ski, montagne), SARL, 3-5 salariés, "
                   "SIRET 334501400 00017",
        "prochaine_action": "Monter le dossier découverte (pas encore commencé)",
        "notes": "Ax-les-Thermes / Luzenac — 40 ans d'activité (créée en 1985), repérée sans site "
                 "propre, pas encore de premier contact",
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

    def relances_prioritaires(self, seuil_jours: int = SEUIL_RELANCE_JOURS) -> list:
        """
        Calcule automatiquement qui relancer, à partir des dates déjà écrites
        dans prochaine_action/notes (ex. "envoyé le 17/08/2026") — au lieu de
        se fier au texte statique de actions_a_faire(). Un prospect "en
        attente de réponse" depuis plus de seuil_jours devient une relance
        prioritaire ; en dessous du seuil, il reste "en attente, pas encore
        urgent".
        """
        aujourdhui = datetime.now().date()
        resultats = []

        for cle, p in self.prospects.items():
            if p["statut"] == "écarté":
                continue

            texte = f"{p['prochaine_action']} {p['notes']}"
            dates_trouvees = re.findall(r"(\d{2})/(\d{2})/(\d{4})", texte)
            derniere_date = None
            if dates_trouvees:
                jj, mm, aaaa = dates_trouvees[-1]
                try:
                    derniere_date = datetime(int(aaaa), int(mm), int(jj)).date()
                except ValueError:
                    derniere_date = None

            en_attente = "attente" in p["prochaine_action"].lower()
            jours_ecoules = (aujourdhui - derniere_date).days if derniere_date else None

            if en_attente and jours_ecoules is not None and jours_ecoules >= seuil_jours:
                statut_relance = "À relancer"
                urgence = "haute"
            elif en_attente:
                statut_relance = "En attente, pas encore urgent"
                urgence = "basse"
            elif "relancer" in p["prochaine_action"].lower():
                statut_relance = "À relancer"
                urgence = "haute"
            elif p["prochaine_action"]:
                statut_relance = "Action différente à faire"
                urgence = "normale"
            else:
                statut_relance = "Rien en attente"
                urgence = "basse"

            resultats.append({
                "entreprise": p["entreprise"],
                "cle": cle,
                "statut_relance": statut_relance,
                "urgence": urgence,
                "jours_depuis_dernier_contact": jours_ecoules,
                "prochaine_action_actuelle": p["prochaine_action"],
            })

        ordre_urgence = {"haute": 0, "normale": 1, "basse": 2}
        resultats.sort(key=lambda r: (
            ordre_urgence[r["urgence"]],
            -(r["jours_depuis_dernier_contact"] or 0),
        ))
        return resultats

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
