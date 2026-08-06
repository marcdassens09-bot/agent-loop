"""
layout_agent.py — Agent Mise en Page MP Solutions IA
Mémorise la charte graphique et génère des PDF professionnels.
Usage : from layout_agent import LayoutAgent
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os

# ── Charte MP Solutions IA ─────────────────────────────────────────────────────
CHARTE = {
    "couleur_principale": "#1b3a2b",   # vert foncé
    "couleur_accent":     "#E8730A",   # orange
    "couleur_fond":       "#FFFFFF",   # blanc
    "email":              "contact@mpsolutionsia.fr",
    "tagline":            "Ecouter, comprendre, servir — en toute transparence.",
    "auteur":             "Marc-Paul Dassens",
    "ville":              "Artigat (09130)",
    "logo":               "logo_complet.png",
}

VERT  = colors.HexColor(CHARTE["couleur_principale"])
ORANGE = colors.HexColor(CHARTE["couleur_accent"])
BLANC  = colors.white


class LayoutAgent:
    def __init__(self):
        self.charte = CHARTE

    def get_charte(self) -> dict:
        """Retourne la charte graphique complète."""
        return self.charte

    def get_styles(self):
        """Retourne les styles ReportLab aux couleurs MP Solutions IA."""
        styles = getSampleStyleSheet()

        titre = ParagraphStyle(
            "Titre",
            fontName="Helvetica-Bold",
            fontSize=18,
            textColor=ORANGE,
            spaceAfter=12,
            alignment=TA_LEFT,
        )

        sous_titre = ParagraphStyle(
            "SousTitre",
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=VERT,
            spaceAfter=8,
            spaceBefore=12,
        )

        corps = ParagraphStyle(
            "Corps",
            fontName="Helvetica",
            fontSize=11,
            textColor=VERT,
            spaceAfter=6,
            leading=16,
        )

        return {"titre": titre, "sous_titre": sous_titre, "corps": corps}

    def dessiner_entete(self, c: canvas.Canvas, largeur: float, hauteur: float):
        """Dessine l'en-tête sur chaque page."""
        # Bande verte en haut
        c.setFillColor(VERT)
        c.rect(0, hauteur - 2.5*cm, largeur, 2.5*cm, fill=1, stroke=0)

        # Logo si disponible
        if os.path.exists(self.charte["logo"]):
            c.drawImage(
                self.charte["logo"],
                0.8*cm, hauteur - 2.2*cm,
                width=4*cm, height=1.8*cm,
                preserveAspectRatio=True, mask="auto"
            )

        # Tagline
        c.setFillColor(BLANC)
        c.setFont("Helvetica-Oblique", 9)
        c.drawRightString(largeur - 0.8*cm, hauteur - 1.5*cm, self.charte["tagline"])

    def dessiner_pied(self, c: canvas.Canvas, largeur: float, numero_page: int):
        """Dessine le pied de page."""
        c.setFillColor(VERT)
        c.rect(0, 0, largeur, 1.2*cm, fill=1, stroke=0)

        c.setFillColor(BLANC)
        c.setFont("Helvetica", 8)
        c.drawString(0.8*cm, 0.45*cm, self.charte["email"])
        c.drawCentreString(largeur / 2, 0.45*cm, self.charte["ville"])
        c.drawRightString(largeur - 0.8*cm, 0.45*cm, f"Page {numero_page}")

    def generer_pdf(self, nom_fichier: str, titre: str, sections: list[dict]) -> str:
        """
        Génère un PDF avec la charte MP Solutions IA.

        sections : liste de dicts {"titre": "...", "contenu": "..."}
        Retourne le chemin du fichier créé.
        """
        largeur, hauteur = A4
        styles = self.get_styles()
        numero_page = [1]

        def entete_pied(canvas_obj, doc):
            canvas_obj.saveState()
            self.dessiner_entete(canvas_obj, largeur, hauteur)
            self.dessiner_pied(canvas_obj, largeur, numero_page[0])
            numero_page[0] += 1
            canvas_obj.restoreState()

        doc = SimpleDocTemplate(
            nom_fichier,
            pagesize=A4,
            topMargin=3*cm,
            bottomMargin=2*cm,
            leftMargin=2*cm,
            rightMargin=2*cm,
        )

        contenu = []
        contenu.append(Paragraph(titre, styles["titre"]))
        contenu.append(Spacer(1, 0.5*cm))

        for section in sections:
            if section.get("titre"):
                contenu.append(Paragraph(f">> {section['titre']}", styles["sous_titre"]))
            if section.get("contenu"):
                contenu.append(Paragraph(section["contenu"], styles["corps"]))
            contenu.append(Spacer(1, 0.3*cm))

        doc.build(contenu, onFirstPage=entete_pied, onLaterPages=entete_pied)
        return nom_fichier

    def get_contexte(self) -> str:
        """Retourne la charte formatée pour injection dans un SYSTEM_PROMPT."""
        return f"""=== CHARTE GRAPHIQUE MP SOLUTIONS IA ===
Couleur principale : {self.charte['couleur_principale']} (vert foncé)
Couleur accent : {self.charte['couleur_accent']} (orange)
Email pied de page : {self.charte['email']}
Tagline : {self.charte['tagline']}
Structure sections : >> TITRE  ++ PROPOSITION  -> SIGNATURE
========================================="""


# ── Exemple d'utilisation ──────────────────────────────────────────────────────
if __name__ == "__main__":
    agent = LayoutAgent()

    sections = [
        {
            "titre": "CE QUE J'OBSERVE",
            "contenu": "Votre entreprise reçoit de nombreux appels répétitifs qui mobilisent votre temps."
        },
        {
            "titre": "CE QUE JE PROPOSE",
            "contenu": "Un assistant virtuel disponible 24h/24 — 800€ installation + 60€/mois."
        },
    ]

    fichier = agent.generer_pdf("test_mp.pdf", "Dossier Commercial — Prospect Test", sections)
    print(f"PDF créé : {fichier}")
    print("\nContexte charte :")
    print(agent.get_contexte())
