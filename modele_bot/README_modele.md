# Chatbot {{NOM_ENTREPRISE}}

Bot généré par l'agent d'onboarding MP Solutions IA le {{DATE_GENERATION}}.

## Test en local

1. Copier `.env.example` vers `.env` et y coller la clé API Anthropic.
2. `pip install -r requirements.txt`
3. `python app.py` puis ouvrir un second terminal :
   `python C:/Projets/agent-loop/agent_recette.py http://localhost:5000`
   (seuls les cas communs s'appliquent : identification IA, vraie réponse)

## Déploiement Render — checklist

1. Créer le dépôt GitHub et pousser ce dossier.
2. Sur dashboard.render.com : **New → Web Service**, connecter le dépôt.
3. ⚠️ **PIÈGE CONNU** : Render préremplit la Start Command avec
   `gunicorn app:app`. La remplacer par : `python app.py`
   (sinon le service peut se comporter différemment du test local).
4. Onglet **Environment** : ajouter `ANTHROPIC_API_KEY` avec la clé du parc.
   Chaque service Render a SES propres variables — rien n'est partagé.
5. Après le déploiement, vérifier dans l'ordre :
   - `https://<service>.onrender.com/health` → doit contenir `"api_key_set": true`
   - `https://<service>.onrender.com/diagnose` → doit répondre `"status": "OK"`
6. Ajouter le service dans `SERVICES` de
   `C:/Projets/agent-loop/verifier_services.py` (méthode `diagnose`)
   et dans `SUITES` de `agent_recette.py` → il entre dans la surveillance
   quotidienne de 8h et dans la recette du parc.

## Règles du parc (ne pas retirer)

- La phrase « Je suis un assistant IA, pas un humain » dans le prompt (IA Act).
- Email de contact : uniquement l'adresse officielle validée par le client
  (jamais une ancienne adresse — vérifier avec `agent_recette.py`).
- Le bot ne promet jamais ce qu'il ne peut pas vérifier (dispo, stock, délai).

## Niveau d'autonomie de ce bot

Ce bot est niveau **observation/préparation** : il répond aux questions des
visiteurs, mais ne modifie rien et n'agit sur aucun système externe (pas
d'email envoyé, pas de réservation prise, pas de paiement). `OUTILS` est vide
dans `app.py`.

Si un outil qui **agit** (envoi de mail, prise de réservation...) est ajouté
plus tard, mettre à jour cette section pour refléter le nouveau niveau.
