# Configuration SecureHoliday API

Ce guide t'aide à configurer l'intégration de l'API SecureHoliday pour vérifier les disponibilités en temps réel.

## 📋 Prérequis

- Accès à un compte admin SecureHoliday (https://admin.secureholiday.net/)
- L'ID de ton établissement (example: 5438 pour Camping Les Eychecadous)

## 🔑 Obtenir les identifiants API

### Étape 1: Accéder au portail admin SecureHoliday

1. Va sur: https://admin.secureholiday.net/
2. Connecte-toi avec tes identifiants

### Étape 2: Trouver la section API/Intégrations

Cherche dans le menu admin:
- "Intégrations"
- "API"
- "Paramètres avancés"
- "Connexions externes"

### Étape 3: Générer une clé API

Selon l'interface SecureHoliday:
- Clique sur "Générer une clé API" ou "Créer une intégration"
- Tu recevras:
  - **API Key**: La clé d'authentification (commence souvent par `sh_` ou `sk_`)
  - **API Secret**: La clé secrète (optionnel selon ta configuration)

⚠️ **IMPORTANT**: Copie et sauvegarde ces identifiants maintenant - tu ne pourras pas les voir de nouveau!

## ⚙️ Configurer le fichier .env

Ouvre le fichier `.env` et mets à jour les variables:

```env
SECUREHOLIDAY_API_BASE=https://api.secureholiday.net
SECUREHOLIDAY_ESTABLISHMENT_ID=5438
SECUREHOLIDAY_API_KEY=sk_your_actual_api_key_here
SECUREHOLIDAY_API_SECRET=your_api_secret_here
```

### Variables à configurer:

| Variable | Description | Exemple |
|----------|-------------|---------|
| `SECUREHOLIDAY_API_BASE` | URL de base de l'API SecureHoliday | `https://api.secureholiday.net` |
| `SECUREHOLIDAY_ESTABLISHMENT_ID` | ID unique de ton camping | `5438` |
| `SECUREHOLIDAY_API_KEY` | Clé API pour l'authentification | `sk_live_abcd1234...` |
| `SECUREHOLIDAY_API_SECRET` | Secret API (optionnel) | `sh_secret_xyz...` |

## ✅ Tester la connexion

### Test 1: Via Python (en local)

```bash
python test_secureholiday.py
```

Ce script va:
- ✓ Vérifier la configuration
- ✓ Tester la connexion à l'API
- ✓ Vérifier les disponibilités (test fonctionnel)
- ✓ Lister les types d'hébergement

### Test 2: Via endpoint HTTP (si le serveur tourne)

```bash
curl http://localhost:5000/diagnose/secureholiday
```

Réponse attendue:
```json
{
  "status": "ok",
  "configured": true,
  "connectivity": {
    "config": "✓ Configurée",
    "api_health": "✓ API accessible",
    "availability": "✓ Disponible - Prix: 18.50 EUR"
  },
  "errors": []
}
```

## 🐛 Troubleshooting

### "API Key non configurée"

**Problème**: La clé API n'est pas dans le fichier `.env`

**Solution**:
1. Vérifiez que tu as copié la clé exactement
2. Pas d'espace au début ou à la fin
3. Relance le serveur après modification du `.env`

```bash
# Redémarrer le serveur
python app.py
```

### "API inaccessible" ou "Erreur de connexion"

**Problème**: Impossible de se connecter à l'API SecureHoliday

**Solutions**:
1. Vérifie ta connexion internet
2. Vérifie que `SECUREHOLIDAY_API_BASE` est correct
3. Vérifie que la clé API est valide et active
4. Essaie un autre navigateur/machine pour accéder au portail admin
5. Contacte le support SecureHoliday: support@ctoutvert.com

### "Erreur 401" ou "Non autorisé"

**Problème**: La clé API est invalide

**Solutions**:
1. Vérifie que la clé API est correcte (pas tronquée, pas modifiée)
2. Vérifie que la clé n'a pas expiré
3. Génère une nouvelle clé API dans le portail admin
4. Mets à jour le `.env` avec la nouvelle clé

### Mode "Fallback"

Si l'API n'est pas accessible mais configurée, le chatbot passera en **mode fallback**:
- ✓ Le chatbot collectera toujours les informations
- ✓ Il affichera un récapitulatif
- ✗ Il ne vérifiera PAS les disponibilités en temps réel
- → Un manager devra contacter manuellement le client pour confirmer

## 🔄 Flux de réservation avec SecureHoliday

Voici ce qui se passe quand un client réserve:

```
Client → Chat bot
    ↓
Collecte info (nom, dates, type hébergement, etc.)
    ↓
Tous les champs remplis?
    ├─ NON → Poser la prochaine question
    └─ OUI → Vérifier disponibilité via SecureHoliday
        ↓
    Disponible?
        ├─ OUI → Confirmation instantanée + enregistrement
        ├─ NON → Suggestion d'autres dates
        └─ ERREUR API → Mode fallback (contact manuel)
```

## 📞 Support

- **SecureHoliday Support**: https://ctoutvert.com/support/
- **Documentation officielle**: https://secureholiday.net/documentation/
- **Forum communautaire**: https://forum.ctoutvert.com/

## 🔐 Sécurité

- ⚠️ Ne commit JAMAIS ta clé API dans Git
- ⚠️ Utilise des variables d'environnement ou `.env` (non versionné)
- ⚠️ Régénère ta clé si tu la penses compromise
- ⚠️ Limite les permissions de la clé API au strict nécessaire

## ✨ Prochaines étapes

Une fois configuré, tu peux:

1. **Tester le chat**: Le chatbot affichera des disponibilités réelles
2. **Automatiser les réservations**: Créer des réservations directement via l'API (code déjà préparé dans `secureholiday_api.py`)
3. **Synchroniser le calendrier**: Intégrer un webhook pour les annulations/modifications
4. **Analyser les données**: Tracker les réservations et taux d'occupation

---

Pour toute question, consulte la [documentation Python de l'intégration](./secureholiday_api.py).
