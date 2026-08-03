# 🚀 MP Solutions IA - Application Flask Multi-Métiers

Application Flask pour mpsolutionsia.fr avec support de **8 métiers** différents.

---

## 📋 Vue d'ensemble

### Ce qu'elle fait

Un serveur Flask avec route `/chat` qui:
- ✅ Reçoit un message + un métier
- ✅ Charge le system prompt adapté au métier
- ✅ Appelle Claude Sonnet via l'API Anthropic
- ✅ Retourne la réponse

### Les 8 métiers supportés

1. **Plombier** - Diagnostics, réparations, devis
2. **Camping** - Réservations, hébergements, activités
3. **Boulangerie** - Produits frais, commandes spéciales
4. **Restaurant** - Menu, réservations, recommandations
5. **Artisan Bâtiment** - Rénovation, construction, devis
6. **Paysagiste** - Aménagement extérieur, jardins
7. **Jardinerie** - Plantes, outils, conseils jardinage
8. **Fabricant PME** - Production, devis, commandes

---

## 📁 Fichiers créés

| Fichier | Description |
|---------|-------------|
| `mpsolutionsia_app.py` | Application Flask principale |
| `mp_system_prompts.py` | System prompts pour les 8 métiers |
| `Procfile` | Configuration Render |
| `requirements.txt` | Dépendances Python |

---

## 🎯 Endpoints disponibles

### Health Check
```
GET /health
```
Réponse:
```json
{"status": "alive", "app": "mpsolutionsia"}
```

### Lister les métiers
```
GET /metiers
```
Réponse:
```json
{
  "metiers": ["plombier", "camping", "boulangerie", ...],
  "count": 8
}
```

### Chat (Principal)
```
POST /chat
Content-Type: application/json
```

**Requête:**
```json
{
  "message": "Je voudrais commander un pain complet",
  "metier": "boulangerie",
  "session_id": "optional_client_123"
}
```

**Réponse:**
```json
{
  "response": "Bonjour! Nous avons d'excellents pains complets...",
  "session_id": "optional_client_123",
  "metier": "boulangerie"
}
```

### Réinitialiser une session
```
POST /reset
Content-Type: application/json
```

**Requête:**
```json
{
  "session_id": "client_123"
}
```

**Réponse:**
```json
{
  "status": "ok",
  "session_id": "client_123",
  "message": "Session réinitialisée"
}
```

### Diagnostic
```
GET /diagnose
```

Vérifie:
- ✅ Clé API Anthropic présente
- ✅ Résolution DNS (api.anthropic.com)
- ✅ Connectivité HTTP
- ✅ Appel API Anthropic fonctionnel

---

## 🔧 Configuration

### Variables d'environnement (.env)

```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...
PORT=5000
```

### Fichier .env requis

La clé API **doit** être dans le fichier `.env`:

```bash
echo "ANTHROPIC_API_KEY=sk-ant-api03-xxxxx" > .env
```

⚠️ **Ne commit JAMAIS le .env** - Il est dans `.gitignore`

---

## 🚀 Lancer en local

### 1️⃣ Installation des dépendances

```bash
pip install -r requirements.txt
```

### 2️⃣ Créer le fichier .env

```bash
# Créer .env et ajouter ta clé API
echo "ANTHROPIC_API_KEY=sk-ant-api03-xxxxx" > .env
```

### 3️⃣ Lancer l'app

```bash
python mpsolutionsia_app.py
```

App disponible sur: `http://localhost:5000`

### 4️⃣ Tester

**Health check:**
```bash
curl http://localhost:5000/health
```

**Lister métiers:**
```bash
curl http://localhost:5000/metiers
```

**Chat (exemple: boulangerie):**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Avez-vous des croissants aujourd'\''hui?",
    "metier": "boulangerie"
  }'
```

**Diagnostic:**
```bash
curl http://localhost:5000/diagnose
```

---

## 🌐 Déployer sur Render

### Prérequis

- Compte [Render.com](https://render.com)
- Repository GitHub avec le code

### 1️⃣ Créer un Web Service sur Render

1. Va sur [Render Dashboard](https://dashboard.render.com)
2. Clique "New +" → "Web Service"
3. Connecte ton repository GitHub
4. Remplace la commande de démarrage:

```
gunicorn mpsolutionsia_app:app
```

### 2️⃣ Ajouter les variables d'environnement

Dans les paramètres Render, ajoute:

```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...
```

### 3️⃣ Déployer

- Render détecte automatiquement `Procfile`
- Installe les dépendances de `requirements.txt`
- Lance l'application

URL: `https://mpsolutionsia.onrender.com` (exemple)

---

## 📊 Exemple d'utilisation complet

### Conversation avec un plombier

```bash
# Message 1: Question
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Ma baignoire fuit. Quel peut être le problème?",
    "metier": "plombier",
    "session_id": "client_001"
  }'
```

Réponse:
```json
{
  "response": "Bonjour! Une fuite de baignoire peut provenir de plusieurs sources...",
  "session_id": "client_001",
  "metier": "plombier"
}
```

```bash
# Message 2: Question de suivi (même session)
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Combien ça coûte pour une réparation?",
    "metier": "plombier",
    "session_id": "client_001"
  }'
```

Réponse:
```json
{
  "response": "Le coût dépend de la nature de la réparation...",
  "session_id": "client_001",
  "metier": "plombier"
}
```

---

## 🔐 Sécurité

✅ **Clé API protégée:**
- Stockée dans `.env` (non committé)
- Variable d'environnement à la runtime
- Utilisée uniquement en backend

✅ **Timeouts configurés:**
- 60 secondes pour Render
- Retry automatique (3 tentatives)

✅ **Gestion d'erreurs:**
- Messages d'erreur sécurisés
- Logs détaillés en backend
- Fallback gracieux

---

## 🧪 Tests

### Test complet avec tous les métiers

```bash
#!/bin/bash

METIERS=("plombier" "camping" "boulangerie" "restaurant" "artisan_batiment" "paysagiste" "jardinerie" "fabricant_pme")

for metier in "${METIERS[@]}"; do
  echo "Test $metier..."
  curl -X POST http://localhost:5000/chat \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Bonjour\", \"metier\": \"$metier\"}"
  echo "\n---\n"
done
```

### Test de diagnostic

```bash
curl http://localhost:5000/diagnose | jq
```

Résultat attendu:
```json
{
  "status": "ok",
  "api_key_present": true,
  "connectivity": {
    "dns": "✓ Résolvé en 1.1.1.1",
    "http": "✓ Status 200",
    "anthropic_api": "✓ API fonctionne"
  },
  "errors": []
}
```

---

## 📝 Structure du code

### `mpsolutionsia_app.py`

**Routes:**
- `GET /health` - Health check
- `GET /metiers` - Liste métiers
- `GET /diagnose` - Diagnostic
- `POST /chat` - Chat principal
- `POST /reset` - Réinitialiser session

**Fonctionnalités:**
- Validation des requêtes
- Gestion des conversations (avec session_id)
- Gestion des erreurs API
- Logging complet
- Compatible Render

### `mp_system_prompts.py`

**Contient:**
- 8 system prompts personnalisés (un par métier)
- Fonction `get_system_prompt(metier)` pour charger le prompt
- Fonction `get_available_metiers()` pour lister les métiers
- Normalisation des noms de métiers

---

## 🔄 Architecture

```
Utilisateur
    ↓
POST /chat
{"message": "...", "metier": "plombier"}
    ↓
Charger system prompt (plombier)
    ↓
Appeler Claude Sonnet (Anthropic API)
    ↓
Retourner réponse
    ↓
Response JSON
{"response": "...", "metier": "plombier"}
```

---

## 📈 Métriques

- **Modèle:** Claude Sonnet 4.6
- **Max tokens:** 1000 par réponse
- **Timeout:** 60 secondes
- **Retries:** 3 tentatives
- **Sessions:** Illimitées (stockées en mémoire)

---

## ⚠️ Limitations

- Sessions stockées en mémoire (perdues au redémarrage)
- Maximum 1000 tokens par réponse
- Pas de persistance de base de données
- Pas d'authentification (à ajouter en production)

### Évolutions futures

- Base de données (PostgreSQL/MongoDB) pour les sessions
- Authentification utilisateur
- Rate limiting
- Analytics/logging
- Personnalisation per-métier avancée

---

## 🆘 Troubleshooting

### "ANTHROPIC_API_KEY not found"

```bash
# Vérifier que .env existe
ls -la .env

# Vérifier que la clé est dedans
cat .env | grep ANTHROPIC_API_KEY

# Relancer après modification
python mpsolutionsia_app.py
```

### "API returned 401 Unauthorized"

- Clé API invalide ou expirée
- Vérifier dans console Anthropic
- Générer une nouvelle clé

### "Connection timeout"

- Problème de connexion réseau
- Vérifier DNS
- Tester: `curl https://api.anthropic.com`

### "Métier non reconnu"

```bash
# Lister les métiers valides
curl http://localhost:5000/metiers

# Utiliser un métier de la liste
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "...", "metier": "plombier"}'
```

---

## 📞 Support

- Documenter dans `/diagnose`
- Vérifier les logs de l'app
- Tester chaque endpoint individuellement

---

## ✅ Checklist déploiement

- [ ] Fichier `.env` avec `ANTHROPIC_API_KEY`
- [ ] `requirements.txt` à jour
- [ ] `Procfile` présent
- [ ] App testée en local
- [ ] `GET /diagnose` retourne `"status": "ok"`
- [ ] Repository GitHub créé
- [ ] Web Service Render configuré
- [ ] Variable `ANTHROPIC_API_KEY` ajoutée sur Render
- [ ] Déploiement réussi
- [ ] URL mpsolutionsia accessible

---

**Prêt à déployer?** 🚀 Toute l'infrastructure est en place!
