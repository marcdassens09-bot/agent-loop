# 🚀 GUIDE DÉPLOIEMENT RENDER

Déploie `mpsolutionsia.fr` sur Render en 5 minutes!

---

## 📋 PRÉREQUIS

✅ Code pushé sur GitHub: **https://github.com/marcdassens09-bot/agent-loop**
✅ `Procfile` présent dans le repo
✅ `requirements.txt` à jour
✅ Clé API Anthropic: `sk-ant-api03-xxxxx`

---

## 🎯 ÉTAPES DE DÉPLOIEMENT

### ÉTAPE 1️⃣: Créer un Web Service Render (2 min)

1. Va sur **[Render Dashboard](https://dashboard.render.com)**
2. Clique **"New +"** en haut à droite
3. Sélectionne **"Web Service"**

![Render - New Web Service](https://docs.render.com/assets/images/dashboard-new-service-c8e5d1f1a7b1c4f6e2d8a9b1c3d5e7f9.png)

### ÉTAPE 2️⃣: Connecter GitHub (1 min)

1. Dans "Source", clique **"GitHub"**
2. Clique **"Connect Account"** (si première fois)
   - Autorise l'accès à tes repos GitHub
3. Cherche et sélectionne: **`agent-loop`**
4. Clique **"Connect"**

![Render - Select Repository](https://docs.render.com/assets/images/github-select-repo.png)

### ÉTAPE 3️⃣: Configurer le Service (2 min)

Remplis les champs:

| Champ | Valeur |
|-------|--------|
| **Name** | `mpsolutionsia` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn mpsolutionsia_app:app` |
| **Instance Type** | `Free` (ou `Starter` pour plus puissant) |

**Important:** La "Build Command" et "Start Command" doivent correspondre à ce que tu vois. Render va détecter `Procfile` automatiquement.

![Render - Configuration](https://docs.render.com/assets/images/service-config.png)

### ÉTAPE 4️⃣: Ajouter les Variables d'Environnement (1 min)

1. Scroll jusqu'à **"Environment"**
2. Clique **"Add Environment Variable"**
3. Ajoute:

| Name | Value |
|------|-------|
| `ANTHROPIC_API_KEY` | `sk-ant-api03-xxxxx` (ta vraie clé) |

⚠️ **IMPORTANT:** Remplace `sk-ant-api03-xxxxx` par ta **vraie clé API Anthropic**!

4. Clique **"Save Variable"**

![Render - Environment Variables](https://docs.render.com/assets/images/env-variables.png)

### ÉTAPE 5️⃣: Deploy! (1 min)

1. Scroll jusqu'en bas
2. Clique **"Create Web Service"**
3. Render va:
   - Cloner le repo
   - Installer les dépendances
   - Lancer l'app

**Attends ~2-3 minutes** pour que le déploiement se termine.

Tu verras:
```
✓ Build successful
✓ Service started
```

Et une URL comme:
```
https://mpsolutionsia.onrender.com
```

---

## ✅ VÉRIFIER LE DÉPLOIEMENT

### Test 1: Health Check

```bash
curl https://mpsolutionsia.onrender.com/health
```

Réponse attendue:
```json
{"status": "alive", "app": "mpsolutionsia"}
```

### Test 2: Lister Métiers

```bash
curl https://mpsolutionsia.onrender.com/metiers
```

### Test 3: Chat

```bash
curl -X POST https://mpsolutionsia.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "metier": "camping"}'
```

### Test 4: Diagnostic

```bash
curl https://mpsolutionsia.onrender.com/diagnose
```

---

## 🔗 CONFIGURER LE DOMAINE

### Pointer `mpsolutionsia.fr` vers Render

1. Va dans **Render Dashboard** → **Settings** de ton Web Service
2. Cherche **"Custom Domains"**
3. Clique **"Add Custom Domain"**
4. Saisis: `mpsolutionsia.fr`
5. Clique **"Add"**

Render te donnera les **DNS records** à configurer:

```
Type: CNAME
Name: mpsolutionsia
Value: mpsolutionsia.onrender.com
```

6. Va sur ton registrar de domaine (GoDaddy, Namecheap, etc.)
7. Ajoute le CNAME record
8. **Attends 24-48h** pour la propagation DNS

Ensuite, `https://mpsolutionsia.fr` pointera vers ton app Render! 🎉

---

## 📊 MONITORING RENDER

### Voir les Logs

1. Render Dashboard → Ton Web Service
2. Clique **"Logs"** en haut
3. Tu verras tous les logs en temps réel

**Cherche des erreurs:**
```
ERROR
Exception
FAIL
```

### Voir les Métriques

1. Clique **"Metrics"**
2. Vois: CPU, RAM, Requests

### Redémarrer l'App

1. Clique **"Manual Deploy"** → **"Deploy latest commit"**

---

## ⚠️ TROUBLESHOOTING

### "Build Failed"

**Vérifier:**
- `requirements.txt` existe et est à jour
- `Procfile` est présent
- `mpsolutionsia_app.py` n'a pas d'erreurs syntaxe

**Logs de build:**
- Va dans Render Dashboard → Logs
- Cherche `ERROR` ou `Exception`

### "Application Error" après deploy

**Vérifications:**
- `ANTHROPIC_API_KEY` est défini dans les Environment Variables
- La clé API est valide
- `mpsolutionsia_app.py` et `mp_system_prompts.py` existent

**Debug:**
```bash
# Vérifier que l'app démarre localement
python mpsolutionsia_app.py

# Tester les imports
python -c "import mpsolutionsia_app; import mp_system_prompts"
```

### "503 Service Unavailable"

- L'app crash au démarrage
- Vérifier les logs Render
- Vérifier que `PORT` n'est pas en conflict (Render assigne auto)

### "404 Not Found"

- L'app est déployée mais la route n'existe pas
- Vérifie `/health` et `/metiers` fonctionnent
- Vérifier la requête POST `/chat` a les bons fields

---

## 🔄 CONTINUOUS DEPLOYMENT

Render déploie **automatiquement** quand tu push sur GitHub!

```bash
# Après un changement local:
git add .
git commit -m "fix: quelque chose"
git push origin main

# Render détecte le push et redéploie automatiquement
```

Tu peux désactiver ça dans Settings → "Auto Deploy".

---

## 💰 PRICING RENDER

| Plan | Prix | Inclus |
|------|------|--------|
| **Free** | $0/mois | 750h/mois (suffit pour test) |
| **Starter** | $7/mois | 730h/mois (production recommandé) |
| **Standard** | $25/mois | Usage illimité |

**Note:** Free spinning down après 15 min inactivité. Starter/Standard toujours on.

Pour une app de production, **Starter+ ($7/mois) est recommandé**.

---

## 📝 CHECKLIST DÉPLOIEMENT

- [ ] Code pushé sur GitHub
- [ ] `Procfile` présent
- [ ] `requirements.txt` à jour
- [ ] Clé API Anthropic copié-collée
- [ ] Web Service Render créé
- [ ] Variables d'environnement ajoutées
- [ ] Deploy lancé
- [ ] `/health` retourne 200
- [ ] `/metiers` retourne 8 métiers
- [ ] `/chat` fonctionne
- [ ] `/diagnose` retourne "status": "ok"
- [ ] URL Render accessible: `https://mpsolutionsia.onrender.com`
- [ ] (Optionnel) Domaine `mpsolutionsia.fr` pointé vers Render

---

## 🎯 AFTER DEPLOYMENT

**Quelques bonnes pratiques:**

1. **Monitoring:** Vérifie les logs régulièrement
2. **Updates:** Redéploie après chaque commit
3. **Scaling:** Si trop de traffic, upgrade vers Starter
4. **HTTPS:** Render ajoute automatiquement SSL/TLS ✅

---

## 📞 SUPPORT RENDER

- **Docs:** https://docs.render.com
- **Status:** https://status.render.com
- **Email Support:** support@render.com (plan payant)

---

## 🎉 RÉSUMÉ

```
5 minutes:
1. Connecter GitHub à Render
2. Ajouter env var ANTHROPIC_API_KEY
3. Deploy!
4. Vérifier /health
5. Enjoy! 🚀
```

**Ton app est maintenant LIVE sur Render!** 🎊

URL: `https://mpsolutionsia.onrender.com` (remplace par ton URL exacte)

---

**Besoin d'aide? Voir MPSOLUTIONSIA_QUICKSTART.md ou MPSOLUTIONSIA_README.md** 📚
