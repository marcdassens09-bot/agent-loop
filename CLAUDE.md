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

## Le site vitrine non plus — et il vit HORS de C:\Projets

Deux dépôts, tous deux dans `C:\Users\marcd\` (vérifié le 04/08/2026) :

| Dépôt | Rôle | Branche |
|---|---|---|
| `C:\Users\marcd\site-mpsolutions` | `index.html` statique, la bulle verte | `master` |
| `C:\Users\marcd\assistant-mpsolutions` | backend Flask de la bulle — **le `SYSTEM_PROMPT` est là** | `master` |

La bulle du site appelle `assistant-mpsolutions.onrender.com`. Modifier le discours du bot
vitrine = modifier `assistant-mpsolutions`, jamais `site-mpsolutions`.

**`C:\Projets\mon-premier-IA` est un clone obsolète** de `chatbot-ia-cleanpro` (même remote,
code plus ancien). Ne jamais y committer.

## Conformité IA Act (article 50)

Chaque prompt système d'un bot face au public contient la phrase d'identification, sur le
modèle : « Tu es un assistant IA, pas un humain. » Passe complète faite le 04/08/2026 sur les
7 bots publics (ici : `agent.py` + les 8 métiers de `mp_system_prompts.py`). Tout nouveau
prompt doit la porter. Vérification : chercher `assistant IA, pas un humain` dans les `.py`.
Les agents internes (debug, memory, prospect, patchs) ne sont pas concernés.

## L'email du camping est GMAIL

`campingartigat@gmail.com` — confirmé par marc-paul et par le site public le 04/08/2026.
`campingartigat@hotmail.fr` est l'ancienne adresse : si elle réapparaît, c'est une régression.
Piège : un remplacement global hotmail→gmail avait transformé la règle « jamais hotmail »
en « jamais gmail ». Après tout remplacement dans un prompt, relire entières les lignes
d'interdiction (« jamais X », « pas X »).

## Vérifier le parc

```bash
python verifier_services.py
```

Teste les 7 services Render qui appellent l'API Anthropic et distingue une vraie réponse
d'un message de repli. À lancer avant et après toute rotation de clé.

## Boucles d'agents (ajouté le 05/08/2026)

Deux agents à outils, distincts des chatbots à appel unique du dépôt :

- `agent_loop.py` — modèle pédagogique : Claude enchaîne des outils Python
  (nuits, tarif emplacement camping, ping d'un service) jusqu'à la réponse finale.
  Sa fonction `boucle_agent(question, outils=, implementations=, system=)` est
  **générique** : tout nouvel agent du dépôt doit la réutiliser au lieu de recopier la boucle.
- `agent_surveillance.py` — vérifie le parc via `verifier_services.py`, consulte un mémo
  des pannes connues, diagnostique et propose le correctif sans rien modifier.
  `python agent_surveillance.py` = bilan complet (long : réveil des instances) ;
  `python agent_surveillance.py "question"` = test ciblé.

Le `.env` local est un endroit de plus à mettre à jour lors d'une rotation de clé
(oublié le 03/08 → 401 en local le 05/08 alors que la prod tournait).

## secureholiday_api.py n'est pas validé

Ses endpoints ont été **supposés, pas documentés**. Vérifié : `api.secureholiday.net` existe,
mais les chemins codés renvoient 404. Ctoutvert fournit sa documentation sur demande
(voir `EMAIL_CTOUTVERT.md`). Ne pas s'en servir tel quel.

## Conventions

- Clé API dans `.env` (non versionné), jamais en dur.
- Modèle : `claude-sonnet-4-6`.
- Les instances Render gratuites s'endorment : prévoir ~50 s au premier appel.
- Un correctif n'est « fait » que **commité et poussé** : vérifier `git show HEAD:fichier`,
  pas le fichier sur disque. (Le 03/08, la phrase IA Act du camping a dormi 24 h en local
  pendant que la prod tournait sans elle.)
