"""
session_end.py — Fin de session MP Solutions IA
Résume la conversation et sauvegarde tout sur Drive.
Usage : python session_end.py
"""

from loader import agents
import anthropic
from dotenv import load_dotenv
load_dotenv()

print("\n" + "=" * 50)
print("  MP Solutions IA — FIN DE SESSION")
print("=" * 50)

# Charge tous les agents
agents.charger()

# Demande le résumé de la session
print("\nColle ici le résumé de ce qu'on a fait aujourd'hui.")
print("(Appuie sur Entrée deux fois pour terminer)\n")

lignes = []
while True:
    ligne = input()
    if ligne == "":
        if lignes and lignes[-1] == "":
            break
    lignes.append(ligne)

resume_session = "\n".join(lignes).strip()

if resume_session:
    # Met à jour la mémoire avec le résumé
    historique = [
        {"role": "user", "content": resume_session},
        {"role": "assistant", "content": "Résumé enregistré."}
    ]
    memory = agents.get("memory")
    if memory:
        print("\n🔄 Mise à jour de la mémoire...")
        memory.resumer(historique)

# Sauvegarde tout
agents.sauvegarder_tout()

print("✓ Session terminée et sauvegardée sur Drive.")
print("  À la prochaine session, lance : python session_start.py\n")
