# agent-loop

Dépôt d'agents et d'applications Flask pour MP Solutions IA (marc-paul, Ariège).

## Ce dépôt alimente DEUX services Render

| Service Render | Fichier lancé | Rôle |
|---|---|---|
| `mpsolutionsia` | `mpsolutionsia_app.py` | chatbot multi-métiers, 8 métiers via un paramètre `metier` |
| `agent-loop` | `app.py` | ancienne application |

**Piège vérifié le 03/08/2026 :** Render auto-détecte `app.py` à la racine et préremplit sa
**Start Command** avec `gunicorn app:app`. Cette valeur du dashboard **écrase le `Procfile`**.
Résultat : on modifie un fichier qui n'est jamais chargé, et aucun correctif n'a d'effet.
Vérifier la Start Command du service avant de conclure quoi que ce soit.

Diagnostic rapide sur `mpsolutionsia` : `GET /health` doit renvoyer `api_key_set`.
S'il ne renvoie que `{"status":"alive"}`, c'est `app.py` qui tourne.

## Le chatbot du camping N'EST PAS ici

campingartigat.com est servi par un dépôt séparé : `C:\Projets\chatbot-camping-eychecadous`.
Toute modification du bot camping se fait là-bas, pas ici.

## Vérifier le parc

```bash
python verifier_services.py
```

Teste les 7 services Render qui appellent l'API Anthropic et distingue une vraie réponse
d'un message de repli. À lancer avant et après toute rotation de clé.

## secureholiday_api.py n'est pas validé

Ses endpoints ont été **supposés, pas documentés**. Vérifié : `api.secureholiday.net` existe,
mais les chemins codés renvoient 404. Ctoutvert fournit sa documentation sur demande
(voir `EMAIL_CTOUTVERT.md`). Ne pas s'en servir tel quel.

## Conventions

- Clé API dans `.env` (non versionné), jamais en dur.
- Modèle : `claude-sonnet-4-6`.
- Les instances Render gratuites s'endorment : prévoir ~50 s au premier appel.
