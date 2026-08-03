# ⚡ Quick Start - MP Solutions IA

## 5 minutes pour démarrer

### 1️⃣ Créer le fichier .env (30 secondes)

```bash
echo "ANTHROPIC_API_KEY=sk-ant-api03-xxxxx" > .env
```

Remplace `sk-ant-api03-xxxxx` par ta **vraie clé API Anthropic**.

### 2️⃣ Lancer l'app (30 secondes)

```bash
python mpsolutionsia_app.py
```

Tu verras:
```
 * Running on http://127.0.0.1:5000
```

### 3️⃣ Tester (2 minutes)

#### Test 1: Health check
```bash
curl http://localhost:5000/health
```

Réponse:
```json
{"status": "alive", "app": "mpsolutionsia"}
```

#### Test 2: Lister les métiers
```bash
curl http://localhost:5000/metiers
```

Réponse:
```json
{
  "metiers": ["plombier", "camping", "boulangerie", "restaurant", "artisan_batiment", "paysagiste", "jardinerie", "fabricant_pme"],
  "count": 8
}
```

#### Test 3: Chat
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Bonjour, j'\''aimerais réserver", "metier": "camping"}'
```

Réponse:
```json
{
  "response": "Bonjour et bienvenue au Camping Les Eychecadous...",
  "session_id": "default_camping",
  "metier": "camping"
}
```

### 4️⃣ Diagnostic (30 secondes)

```bash
curl http://localhost:5000/diagnose
```

Doit retourner:
```json
{
  "status": "ok",
  "connectivity": {
    "dns": "✓ Résolvé en ...",
    "http": "✓ Status 200",
    "anthropic_api": "✓ API fonctionne"
  }
}
```

---

## 🚀 Déployer sur Render

### 1️⃣ Créer Web Service

- Va sur [Render Dashboard](https://dashboard.render.com)
- "New" → "Web Service"
- Connecte ton GitHub
- Remplace la commande: `gunicorn mpsolutionsia_app:app`

### 2️⃣ Ajouter variable d'environnement

**Nom:** `ANTHROPIC_API_KEY`
**Valeur:** `sk-ant-api03-xxxxx`

### 3️⃣ Deploy!

Render lance automatiquement et ton app est live! 🎉

URL: `https://mpsolutionsia.onrender.com`

---

## 📍 8 Métiers disponibles

| Métier | Code | Exemple requête |
|--------|------|-----------------|
| 🔧 Plombier | `plombier` | "Ma baignoire fuit" |
| 🏕️ Camping | `camping` | "Je veux réserver" |
| 🥖 Boulangerie | `boulangerie` | "Avez-vous des croissants?" |
| 🍽️ Restaurant | `restaurant` | "Table pour 4 demain" |
| 🏗️ Artisan Bâtiment | `artisan_batiment` | "Besoin de rénover" |
| 🌱 Paysagiste | `paysagiste` | "Aménager mon jardin" |
| 🪴 Jardinerie | `jardinerie` | "Quelle plante pour..." |
| 🏭 Fabricant PME | `fabricant_pme` | "Pouvez-vous fabriquer..." |

---

## 🧪 Test complet (copier-coller)

```bash
#!/bin/bash

# Test tous les métiers
echo "🧪 Test de tous les métiers..."

curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Bonjour", "metier": "plombier"}'

echo -e "\n---\n"

curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Je veux réserver", "metier": "camping"}'

echo -e "\n---\n"

curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Avez-vous des croissants?", "metier": "boulangerie"}'

echo "\n✓ Tests terminés!"
```

---

## ❌ Erreurs courantes

### "ANTHROPIC_API_KEY not found"
```bash
# Créer/vérifier .env
cat .env
```

### "Métier non reconnu"
```bash
# Voir métiers valides
curl http://localhost:5000/metiers
```

### "Connection timeout"
```bash
# Tester la connexion API
curl http://localhost:5000/diagnose
```

---

## 📚 Plus d'info

Voir: `MPSOLUTIONSIA_README.md` pour documentation complète

---

**Besoin d'aide?** Tester `/diagnose` pour diagnostic complet! 🔍
