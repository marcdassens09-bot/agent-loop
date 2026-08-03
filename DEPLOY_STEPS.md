# 🚀 DÉPLOIEMENT RENDER - ÉTAPES SIMPLES

**Durée: 5 minutes | Difficulté: Facile ✅**

---

## ✅ VÉRIFICATIONS PRÉALABLES

Avant de commencer, assure-toi que:

- [x] Code pushé sur GitHub: `https://github.com/marcdassens09-bot/agent-loop`
- [x] `Procfile` présent dans le repo
- [x] `requirements.txt` à jour
- [x] Tu as ta clé API Anthropic: `sk-ant-api03-xxxxx`

```bash
# Vérifier que tout est pushé
git log -1 --oneline
# Doit montrer: cb2f174 docs: ajouter recaps...
```

---

## 🎬 ÉTAPE 1: Créer un Web Service Render

### 1.1 Aller sur Render

👉 Ouvre: **https://dashboard.render.com**

Login avec ton compte Render (ou crée un avec GitHub)

### 1.2 Créer un nouveau service

1. Clique **"New +"** (haut droit)
2. Sélectionne **"Web Service"**

![Aperçu](image-1.png)

---

## 🔗 ÉTAPE 2: Connecter GitHub

### 2.1 Choisir la source

1. Dans "Source", clique **"GitHub"**
2. Si c'est ta première fois: clique **"Connect Account"**
   - GitHub va te demander l'autorisation
   - Accepte l'accès à tes repos

### 2.2 Sélectionner le repo

1. Cherche et clique **`agent-loop`**
2. Clique **"Connect"**

---

## ⚙️ ÉTAPE 3: Configurer le Service

Remplis les champs exactement comme ci-dessous:

### 3.1 Informations de base

```
Name:               mpsolutionsia
Environment:        Python 3
Region:             (laisse par défaut)
Branch:             main
Build Command:      pip install -r requirements.txt
Start Command:      gunicorn mpsolutionsia_app:app
```

### 3.2 Instancee Type

Sélectionne: **Free** (ou Starter si tu veux)

```
Free = Gratuit, parfait pour tester ✅
```

![Screenshot Render Config](image-2.png)

---

## 🔐 ÉTAPE 4: Ajouter la Clé API (IMPORTANT!)

### 4.1 Scroll jusqu'à "Environment"

Vois la section **"Environment Variables"**

### 4.2 Ajouter la variable

1. Clique **"Add Environment Variable"**
2. Remplis:
   ```
   Name:  ANTHROPIC_API_KEY
   Value: sk-ant-api03-xxxxx
   ```
   (Remplace `sk-ant-api03-xxxxx` par ta **vraie clé**)

3. Clique **"Save Variable"**

⚠️ **TRÈS IMPORTANT:** La clé API doit être correcte, sinon l'app ne marchera pas!

![Screenshot Environment](image-3.png)

---

## 🚀 ÉTAPE 5: DEPLOY!

### 5.1 Lancer le déploiement

Scroll jusqu'en bas de la page.

Clique le gros bouton bleu: **"Create Web Service"**

### 5.2 Attendre (~2-3 minutes)

Render va:
1. ✅ Cloner le repo GitHub
2. ✅ Installer Python + dépendances
3. ✅ Lancer l'application

Tu verras dans les logs:
```
Building...
Installing requirements
Starting service
✓ Service started successfully
```

### 5.3 Récupérer l'URL

Quand c'est terminé, tu verras ton **URL Render**:

```
https://mpsolutionsia.onrender.com
```

Copie cette URL! ✨

---

## ✅ ÉTAPE 6: Vérifier que ça marche

### 6.1 Test Health Check

Ouvre ton navigateur et va à:
```
https://mpsolutionsia.onrender.com/health
```

Tu dois voir:
```json
{"status": "alive", "app": "mpsolutionsia"}
```

✅ Si tu vois ça, c'est bon!

### 6.2 Test Métiers

Ouvre:
```
https://mpsolutionsia.onrender.com/metiers
```

Tu dois voir les 8 métiers listés.

### 6.3 Test Chat

Ouvre un terminal et teste:
```bash
curl -X POST https://mpsolutionsia.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "metier": "camping"}'
```

Tu dois recevoir une réponse JSON avec une réponse du camping.

### 6.4 Test Diagnostic

```
https://mpsolutionsia.onrender.com/diagnose
```

Doit retourner: `"status": "ok"`

---

## 🎉 C'EST BON!

Si tous les tests passent, **TON APP EST LIVE!** 🚀

```
✅ App déployée sur Render
✅ Accessible 24/7
✅ Auto-redéploie à chaque push GitHub
✅ Prête pour la production!
```

---

## 📍 PROCHAINES ÉTAPES (Optionnel)

### Étape 7 (Optionnel): Pointer le domaine

Si tu as le domaine `mpsolutionsia.fr`:

1. Va dans Render Dashboard → Settings de ton service
2. Cherche **"Custom Domains"**
3. Ajoute: `mpsolutionsia.fr`
4. Configure les DNS records dans ton registrar de domaine
5. Attends 24-48h

Après, ton app sera accessible via `https://mpsolutionsia.fr` 🎊

### Étape 8 (Optionnel): Upgrade le plan

Si tu as beaucoup de traffic:
- Free: 750h/mois (suffit pour test)
- Starter: $7/mois (recommandé production)

---

## ⚠️ TROUBLESHOOTING RAPIDE

| Problème | Solution |
|----------|----------|
| ❌ **"Failed to build"** | Vérifier `requirements.txt` et `Procfile` |
| ❌ **"Application Error"** | Vérifier `ANTHROPIC_API_KEY` dans Environment |
| ❌ **"/health retourne 404"** | L'app n'a pas démarré. Voir les logs Render |
| ❌ **"503 Service Unavailable"** | L'app crash. Vérifier les logs pour l'erreur |

**Voir Logs Render:**
- Dashboard → Ton service → Onglet "Logs"
- Cherche les `ERROR` ou `Exception`

---

## 📞 BESOIN D'AIDE?

**Documentation complète:** `RENDER_DEPLOYMENT.md`

**Quick Help:**
```bash
# Vérifier que tout compile localement
python mpsolutionsia_app.py

# Vérifier les dépendances
python -m pip install -r requirements.txt
```

---

## 🎯 RÉSUMÉ

```
1. Render Dashboard → New Web Service
2. Connecter GitHub (agent-loop)
3. Configurer: mpsolutionsia / Python 3
4. Ajouter: ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
5. Deploy!
6. Tester: /health
7. ✅ C'est bon!
```

**Total: 5 minutes, c'est TOUT!** ⚡

---

**Ton app est maintenant en production!** 🎉🚀
