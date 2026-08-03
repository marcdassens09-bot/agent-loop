# MP Solutions IA — serveur chatbot multi-métiers

Serveur Flask qui expose un chatbot Claude paramétré par métier.

| Fichier | Rôle |
|---|---|
| `mpsolutionsia_app.py` | Application Flask (point d'entrée) |
| `mp_system_prompts.py` | Les 8 system prompts, un par métier |
| `Procfile` | Commande de démarrage |

## Métiers

`plombier` · `camping` · `boulangerie` · `restaurant` · `artisan_batiment` · `paysagiste` · `jardinerie` · `fabricant_pme`

Variantes acceptées : `artisan bâtiment`, `batiment`, `pme`, `fabricant`.

## Endpoints

| Méthode | Route | Description |
|---|---|---|
| GET | `/health` | État du service + présence de la clé API (503 si absente) |
| GET | `/metiers` | Liste des métiers disponibles |
| GET | `/diagnose` | DNS, HTTP et appel réel à l'API Anthropic |
| POST | `/chat` | Conversation |
| POST | `/reset` | Vide une session |

### POST /chat

```json
{ "message": "Ma baignoire fuit", "metier": "plombier", "session_id": "client_001" }
```

`session_id` est optionnel (défaut : `default_<metier>`). Il conserve l'historique de conversation en mémoire — donc **perdu à chaque redéploiement ou mise en veille**.

Réponse :

```json
{ "response": "...", "session_id": "client_001", "metier": "plombier" }
```

## Configuration

Une seule variable requise :

```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

En local : dans `.env` (non versionné). Sur Render : dans Environment Variables.

## Lancer en local

```bash
pip install -r requirements.txt
python mpsolutionsia_app.py
```

```bash
curl http://localhost:5000/health
```

## Déploiement Render

⚠️ **Le point qui fait perdre des heures.** Render auto-détecte `app.py` à la racine et pré-remplit la Start Command avec `gunicorn app:app`. **Cette valeur du dashboard écrase le `Procfile`.** Le service démarre alors le chatbot camping (`app.py`) au lieu de celui-ci, et aucune modification de `mpsolutionsia_app.py` n'a d'effet.

Settings → **Start Command** doit être exactement :

```
gunicorn mpsolutionsia_app:app
```

Configuration complète :

| Champ | Valeur |
|---|---|
| Environment | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn mpsolutionsia_app:app` |
| Env var | `ANTHROPIC_API_KEY` |

### Vérifier qu'on exécute bien le bon fichier

```bash
curl https://<service>.onrender.com/health
```

- `{"status":"alive","api_key_set":true,...}` → correct, clé présente
- `{"status":"alive"}` seul → **c'est `app.py` qui tourne**, corriger la Start Command
- `api_key_set:false` (503) → la variable d'environnement manque

Les logs de démarrage doivent contenir `[STARTUP] ANTHROPIC_API_KEY présente: True`. Si à la place ils contiennent `SECUREHOLIDAY_API_KEY non configuré`, c'est `app.py` qui démarre.

## Limites connues

- Sessions en mémoire : pas de persistance entre redéploiements.
- Pas d'authentification ni de rate limiting.
- Instance Render gratuite : mise en veille après inactivité, premier appel ~50 s.
- Modèle : `claude-sonnet-4-6`, 1000 tokens max par réponse.
