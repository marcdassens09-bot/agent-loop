#!/usr/bin/env python3
"""Script de diagnostic pour vérifier la connexion à l'API SecureHoliday."""

import os
import logging
from dotenv import load_dotenv
from secureholiday_api import SecureHolidayAPI
from datetime import datetime, timedelta

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

def test_secureholiday():
    """Teste la connexion et les fonctionnalités SecureHoliday."""

    print("\n" + "="*60)
    print("TEST DE CONNEXION SECUREHOLIDAY")
    print("="*60 + "\n")

    # Initialiser le client
    sh_api = SecureHolidayAPI()

    # Vérifier la configuration
    print("1️⃣  VÉRIFICATION DE LA CONFIGURATION")
    print("-" * 60)
    print(f"API Base URL: {sh_api.base_url}")
    print(f"Establishment ID: {sh_api.establishment_id}")
    print(f"API Key configurée: {'✓ OUI' if sh_api.api_key else '✗ NON'}")
    if sh_api.api_key:
        print(f"  Format: {sh_api.api_key[:20]}...{sh_api.api_key[-10:]}")
    print(f"API Secret configurée: {'✓ OUI' if sh_api.api_secret else '✗ NON'}")

    if not sh_api.is_configured():
        print("\n⚠️  ATTENTION: Les identifiants SecureHoliday ne sont pas configurés!")
        print("\n📋 À FAIRE:")
        print("   1. Va sur: https://admin.secureholiday.net/")
        print("   2. Connecte-toi avec tes identifiants")
        print("   3. Trouve la section 'Intégrations' ou 'API'")
        print("   4. Génère une clé API")
        print("   5. Ajoute ces variables dans le fichier .env:")
        print("      SECUREHOLIDAY_API_KEY=ta_clé_api")
        print("      SECUREHOLIDAY_API_SECRET=ton_secret (si requis)")
        print("      SECUREHOLIDAY_ESTABLISHMENT_ID=5438")
        return False

    # Test de connexion
    print("\n2️⃣  TEST DE CONNEXION")
    print("-" * 60)

    if sh_api.health_check():
        print("✓ Connexion à l'API SecureHoliday: SUCCÈS")
    else:
        print("✗ Connexion à l'API SecureHoliday: ÉCHEC")
        print("\n⚠️  La connexion a échoué. Vérifiez:")
        print("   - La clé API est correcte")
        print("   - L'establishment ID est correct")
        print("   - L'URL de base est accessible")
        return False

    # Test de vérification de disponibilité
    print("\n3️⃣  TEST DE VÉRIFICATION DE DISPONIBILITÉ")
    print("-" * 60)

    # Dates de test (7 jours à partir d'aujourd'hui)
    today = datetime.now()
    check_in = (today + timedelta(days=7)).strftime("%Y-%m-%d")
    check_out = (today + timedelta(days=14)).strftime("%Y-%m-%d")

    print(f"Test avec dates:")
    print(f"  - Arrivée: {check_in}")
    print(f"  - Départ: {check_out}")
    print(f"  - Type: emplacement")

    availability = sh_api.check_availability(check_in, check_out, "emplacement")

    if availability.get("error"):
        print(f"✗ Erreur: {availability['error']}")
        if availability.get("fallback"):
            print("   (Mode fallback activé - le chatbot marchera en mode limité)")
    else:
        print(f"✓ Disponibilité vérifiée")
        print(f"  - Disponible: {availability.get('available')}")
        if availability.get('price'):
            print(f"  - Prix: {availability.get('price')} {availability.get('currency', 'EUR')}")

    # Test des types d'hébergement
    print("\n4️⃣  TYPES D'HÉBERGEMENT DISPONIBLES")
    print("-" * 60)

    types = sh_api.get_accommodation_types()
    if types:
        for acc_type in types:
            print(f"  ✓ {acc_type.get('name', 'N/A')} (ID: {acc_type.get('id', 'N/A')})")
    else:
        print("  ℹ️  Impossible de récupérer les types (API peut nécessiter auth supplémentaire)")

    print("\n" + "="*60)
    print("✓ DIAGNOSTIC TERMINÉ")
    print("="*60 + "\n")

    return True

if __name__ == "__main__":
    success = test_secureholiday()
    exit(0 if success else 1)
