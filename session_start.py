"""
session_start.py — Démarrage de session MP Solutions IA
Lance tous les agents et affiche le contexte à coller dans Claude.
Usage : python session_start.py
"""

from loader import agents

print("\n" + "=" * 50)
print("  MP Solutions IA — DÉMARRAGE DE SESSION")
print("=" * 50)

# Charge tous les agents
agents.charger()

# Récupère le contexte complet
contexte = agents.get_contexte_complet()

print("\n" + "=" * 50)
print("  CONTEXTE À COLLER DANS CLAUDE :")
print("=" * 50)
print(contexte)
print("=" * 50)
print("\n✓ Copie tout ce qui est au-dessus et colle-le dans Claude.")
print("  Puis dis : 'Voici mon contexte de session.'\n")
