# ⚡ Quick Start - Intégration SecureHoliday

## 📋 Checklist rapide

- [ ] J'ai accès à https://admin.secureholiday.net/
- [ ] J'ai généré une clé API SecureHoliday
- [ ] J'ai noté mon `SECUREHOLIDAY_ESTABLISHMENT_ID` (probablement 5438)

## 🎯 5 minutes pour activer

### Étape 1: Ouvrir `.env` et ajouter tes identifiants

```bash
# Dans le fichier .env, remplace:
SECUREHOLIDAY_API_KEY=sk_your_actual_api_key_here
SECUREHOLIDAY_API_SECRET=your_api_secret_here
```

Par tes vraies identifiants.

### Étape 2: Tester la connexion

```bash
python test_secureholiday.py
```

Tu dois voir:
```
✓ Connexion à l'API SecureHoliday: SUCCÈS
✓ Disponibilité vérifiée
✓ DIAGNOSTIC TERMINÉ
```

### Étape 3: Lancer le serveur

```bash
python app.py
```

### Étape 4: Tester le chatbot

Va sur l'URL de ton app et essaie:
- "Je veux réserver du 15 au 22 août pour 4 personnes"

Le bot affichera:
```
✦ Nom : [collecté]
✦ Arrivée : 2026-08-15
✦ Départ : 2026-08-22
✦ Personnes : 4
✦ Hébergement : [collecté]
✦ Téléphone : [collecté]

✓ DISPONIBLE ! Prix : 18.50 EUR
```

## ✅ C'est bon!

Le chatbot peut maintenant:
- ✓ Vérifier les dispo en temps réel
- ✓ Afficher les prix
- ✓ Confirmer instantanément

## 🐛 Ça ne marche pas?

### Test rapide: `/diagnose/secureholiday`

Ouvre dans ton navigateur:
```
http://localhost:5000/diagnose/secureholiday
```

Regarde le statut:
- `"status": "ok"` → Tout fonctionne
- `"status": "not_configured"` → Ajoute tes identifiants
- `"status": "error"` → Vérifiez la clé API

### Mode Fallback

Si SecureHoliday n'est pas accessible:
- Le chatbot collectera quand même les infos
- Il affichera "Anthony vous contactera..."
- Pas de vérification automatique (fallback)

C'est normal et sûr!

## 📚 Besoin de plus d'infos?

- [INTEGRATION_SUMMARY.md](./INTEGRATION_SUMMARY.md) - Vue d'ensemble complète
- [SECUREHOLIDAY_SETUP.md](./SECUREHOLIDAY_SETUP.md) - Guide détaillé de configuration
- [secureholiday_api.py](./secureholiday_api.py) - Code de l'intégration

---

**Questions?** Consulte les guides ou teste avec `python test_secureholiday.py` 🚀
