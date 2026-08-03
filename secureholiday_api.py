import os
import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class SecureHolidayAPI:
    """Intégration avec l'API SecureHoliday pour vérifier les disponibilités et créer des réservations."""

    def __init__(self):
        # À configurer dans .env
        self.base_url = os.getenv("SECUREHOLIDAY_API_BASE", "https://api.secureholiday.net").rstrip("/")
        self.establishment_id = os.getenv("SECUREHOLIDAY_ESTABLISHMENT_ID", "5438")
        self.api_key = os.getenv("SECUREHOLIDAY_API_KEY", "").strip()
        self.api_secret = os.getenv("SECUREHOLIDAY_API_SECRET", "").strip()
        self.timeout = 10

        if not self.api_key:
            logger.warning("SECUREHOLIDAY_API_KEY non configuré")

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }

    def check_availability(self, check_in: str, check_out: str, accommodation_type: str) -> Dict:
        """
        Vérifie les disponibilités pour les dates données.

        Args:
            check_in: Date d'arrivée (format: YYYY-MM-DD)
            check_out: Date de départ (format: YYYY-MM-DD)
            accommodation_type: Type d'hébergement (emplacement, mobil-home, tente_lodge)

        Returns:
            Dict contenant les disponibilités et les tarifs
        """
        try:
            logger.info(f"Vérification disponibilité: {check_in} à {check_out}, type: {accommodation_type}")

            # Endpoint pour vérifier les disponibilités
            endpoint = f"{self.base_url}/establishments/{self.establishment_id}/availability"

            params = {
                "check_in": check_in,
                "check_out": check_out,
                "accommodation_type": accommodation_type
            }

            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"Réponse disponibilité: {data}")

            return {
                "available": data.get("available", False),
                "accommodation_type": accommodation_type,
                "check_in": check_in,
                "check_out": check_out,
                "price": data.get("price"),
                "currency": data.get("currency", "EUR"),
                "message": data.get("message", "")
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la vérification des disponibilités: {str(e)}")
            return {
                "available": None,
                "error": f"Erreur de connexion à SecureHoliday: {str(e)}",
                "fallback": True
            }
        except Exception as e:
            logger.error(f"Erreur inattendue: {str(e)}")
            return {
                "available": None,
                "error": str(e),
                "fallback": True
            }

    def create_booking(self, booking_data: Dict) -> Dict:
        """
        Crée une réservation dans SecureHoliday.

        Args:
            booking_data: Dict contenant:
                - guest_name: Nom du client
                - guest_email: Email du client
                - guest_phone: Téléphone du client
                - check_in: Date d'arrivée (YYYY-MM-DD)
                - check_out: Date de départ (YYYY-MM-DD)
                - accommodation_type: Type d'hébergement
                - num_guests: Nombre de personnes

        Returns:
            Dict contenant la confirmation de réservation ou l'erreur
        """
        try:
            logger.info(f"Création réservation pour: {booking_data.get('guest_name')}")

            endpoint = f"{self.base_url}/establishments/{self.establishment_id}/bookings"

            payload = {
                "guest": {
                    "name": booking_data.get("guest_name", ""),
                    "email": booking_data.get("guest_email", ""),
                    "phone": booking_data.get("guest_phone", "")
                },
                "check_in": booking_data.get("check_in", ""),
                "check_out": booking_data.get("check_out", ""),
                "accommodation_type": booking_data.get("accommodation_type", ""),
                "num_guests": booking_data.get("num_guests", 0)
            }

            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"Réservation créée: {data.get('booking_id')}")

            return {
                "success": True,
                "booking_id": data.get("booking_id"),
                "confirmation_number": data.get("confirmation_number"),
                "message": "Réservation enregistrée avec succès"
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la création de réservation: {str(e)}")
            return {
                "success": False,
                "error": f"Erreur lors de l'enregistrement: {str(e)}",
                "fallback": True
            }
        except Exception as e:
            logger.error(f"Erreur inattendue: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback": True
            }

    def get_accommodation_types(self) -> List[Dict]:
        """Récupère les types d'hébergement disponibles."""
        try:
            endpoint = f"{self.base_url}/establishments/{self.establishment_id}/accommodation-types"

            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            return response.json().get("types", [])

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des types d'hébergement: {str(e)}")
            return []

    def is_configured(self) -> bool:
        """Vérifie si l'API est correctement configurée."""
        return bool(self.api_key and self.establishment_id)

    def health_check(self) -> bool:
        """Teste la connexion à l'API SecureHoliday."""
        try:
            if not self.is_configured():
                logger.warning("SecureHoliday API non configurée")
                return False

            endpoint = f"{self.base_url}/establishments/{self.establishment_id}"
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            logger.info("✓ Connexion SecureHoliday OK")
            return True

        except Exception as e:
            logger.error(f"✗ Erreur connexion SecureHoliday: {str(e)}")
            return False
