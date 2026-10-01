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

## Le site vitrine non plus

Deux dépôts, tous deux dans `C:\Projets\` (**re-vérifié le 06/08/2026** — ils ont vécu un
temps dans `C:\Users\marcd\`, ce n'est plus le cas) :

| Dépôt | Rôle | Branche |
|---|---|---|
| `C:\Projets\site-mpsolutions` | `index.html` statique, la bulle verte | `master` |
| `C:\Projets\assistant-mpsolutions` | backend Flask de la bulle — **le `SYSTEM_PROMPT` est là** | `master` |

La bulle du site appelle `assistant-mpsolutions.onrender.com`. Modifier le discours du bot
vitrine = modifier `assistant-mpsolutions`, jamais `site-mpsolutions`.

`site-mpsolutions` sert **mpsolutionsia.fr** (domaine personnalisé Render sur le service
`site-mpsolutions`, HTTPS actif depuis le 06/08/2026). Le dépôt ne contient qu'`index.html` :
`widget.js` a été supprimé, il n'était chargé par aucune page. Deux pièges de ce dépôt sont
documentés en mémoire — il a **deux commits racines sans ancêtre commun**, et le cache de
build de Render **conserve les fichiers supprimés** tant qu'on ne fait pas
« Clear build cache & deploy ».

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

Depuis le 09/08/2026, `.github/workflows/recette-mpsolutionsia.yml` relance
`agent_recette.py mpsolutionsia` automatiquement à chaque push sur `main` (secret GitHub
`ANTHROPIC_API_KEY` requis). Attention au faux positif/négatif juste après un push : Render
met ~45 s à finir son déploiement, la CI peut taper l'ancien code encore en ligne ou le
nouveau pas encore stabilisé — ne pas conclure sur le tout premier run, relancer
(« Re-run all jobs ») une fois certain que le déploiement est terminé.

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
- `agent_recette.py` — recette des 6 bots publics. Le camping a sa suite complète
  (tarif 151,10 € au centime, jamais hotmail, identification IA, jamais de promesse de
  dispo, linge non fourni) ; les autres passent les cas communs (identification IA,
  vraie réponse pas de repli). Vérifs déterministes + juge Claude pour les critères
  subjectifs — le juge ne présuppose pas l'activité du bot (leçon du 05/08 : un critère
  « camping » codé en dur avait déclaré non conforme une réponse correcte du bot vitrine).
  Usage : `python agent_recette.py` (tout le parc) ; `python agent_recette.py <nom-service>`
  (un bot) ; `python agent_recette.py http://localhost:5000` (version locale du camping,
  **avant tout push**). Code retour 0/1. Attention : un réveil d'instance gratuite peut
  dépasser le timeout et simuler une panne — revérifier un échec une fois l'instance chaude.

- `agent_onboarding.py` — installe le chatbot d'un nouveau client : on lui décrit le
  client en français libre, il génère un projet complet dans `C:\Projets\<slug>\` depuis
  `modele_bot/` (Flask + boucle d'agent prête à outiller + phrase IA Act garantie +
  README avec checklist Render) puis vérifie la conformité. **Règle d'or : il n'invente
  jamais une info client** — le manquant est listé, pas comblé. Déploiement GitHub/Render
  manuel, guidé par le README généré. Piège vérifié le 05/08 : la règle « jamais telle
  adresse email » écrite telle quelle dans un fichier déclenche le détecteur de
  conformité sur son propre texte — formuler les interdictions sans le mot interdit.

Le `.env` local est un endroit de plus à mettre à jour lors d'une rotation de clé
(oublié le 03/08 → 401 en local le 05/08 alors que la prod tournait).

## Environnement WSL (ajouté le 10/08/2026)

Un environnement Linux est disponible en plus de Windows, pour coller à ce que Render
exécute en prod. Ubuntu 26.04 LTS via WSL2, utilisateur `marcd`.

- Le venv Python est dans **`~/venvs/agent-loop`** (système de fichiers Linux natif),
  **pas** sur `/mnt/c` : `python -m venv` y échoue (`ensurepip` plante) à cause des
  limitations de symlinks du système de fichiers Windows monté (DrvFs).
- Le code reste sur `/mnt/c/Projets/agent-loop` (le même dossier Windows qu'aujourd'hui,
  rien à dupliquer) ; le `.env` s'y lit tel quel depuis WSL, pas de copie de clé à gérer.
- Activation :
  ```bash
  source ~/venvs/agent-loop/bin/activate
  cd /mnt/c/Projets/agent-loop
  ```
- Vérifié bout-en-bout le 10/08/2026 : `python3 agent_loop.py` (question par défaut)
  donne bien 151,10 € — cohérent avec le cas de référence camping d'`agent_recette.py`.

## secureholiday_api.py n'est pas validé

Ses endpoints ont été **supposés, pas documentés**. Vérifié : `api.secureholiday.net` existe,
mais les chemins codés renvoient 404. Ctoutvert fournit sa documentation sur demande
(voir `EMAIL_CTOUTVERT.md`). Ne pas s'en servir tel quel.

## La mémoire Drive (memory_agent.py, clients_context_agent.py) est morte (constaté le 22/08/2026)

`memory_agent.py` et `clients_context_agent.py` (chargés par `loader.py`) sauvegardent sur des
fichiers Google Drive dédiés (`DRIVE_IDS` dans `loader.py`). Vérifié le 22/08/2026 : les deux
fichiers Drive contiennent encore les données de test du tout premier lancement, datées du
**29/07/2026** — jamais mis à jour depuis en usage réel. Ne pas s'y fier pour retrouver le
contexte d'une session passée. Les sources fiables sont **ce fichier CLAUDE.md** et l'historique
git — et, pour tout ce qui touche à la prospection commerciale réelle (dossiers envoyés,
financement), **les emails envoyés du compte Gmail** (voir ci-dessous), pas Drive.

## `clients_agent.py` est la seule liste de prospects à jour (22/08/2026)

Il existe **trois** listes de prospects différentes dans l'écosystème MP Solutions IA :
`clients_agent.py` (ce dépôt, 25 entrées), `clients_context_agent.py`/Drive (4 entrées, mortes
depuis le 29/07), et `prospect_agent.py` (4 entrées, ancien module de génération de documents,
non branché sur la liste actuelle). **Seul `clients_agent.py` est à jour** — s'y référer, pas
aux deux autres.

**Piège vérifié le 22/08/2026 : aucun dossier prospect n'a réellement été envoyé.** Le fichier
contenait des `prochaine_action` du type « envoyé le 17/08/2026 » ou « livré le 17/08/2026 » sur
une douzaine de prospects — c'était faux. Marc-Paul **n'a pas de véhicule** pour aller démarcher
les prospects (artisans BTP, Lézat-sur-Lèze, etc.) en zone rurale ; les dossiers PDF existent et
sont validés, mais rien n'est physiquement parti. Corrigé : `prochaine_action` dit maintenant
« Dossier prêt, pas encore livré (pas de véhicule pour aller démarcher sur place) ». Ne jamais
remarquer un dossier comme « envoyé »/« livré » sans confirmation explicite que l'envoi a eu
lieu (email réellement parti, ou dépôt physique confirmé) — vérifier si besoin dans les emails
envoyés Gmail plutôt que de prendre le texte existant du fichier pour argent comptant.

## Le dossier de financement « Initiative Ariège » vit dans les emails envoyés, pas sur Drive

Marc-Paul a demandé un prêt d'honneur à Initiative Ariège (`contact@initiativeariege.org`).
Le dossier Drive (`MP_Solutions_IA_Initiative_Ariege*.pdf`, 3 versions PDF de juillet 2026,
8500€/9500€) est **obsolète** : la vraie version de référence a été envoyée par email le
**20/08/2026**, en pièce jointe `.docx` (`dossier_ariege_initiative_mp_solutions_ia_maj_20-08.docx`),
montant **11 025 €**, avec SIRET définitif (108 354 739 00014) et ACRE acceptée. Pour retrouver
la version à jour d'un dossier envoyé à un tiers, chercher dans `in:sent` sur Gmail plutôt que
sur Drive. Le budget de ce dossier finance justement un véhicule d'occasion (8 000 €) pour la
prospection rurale — donc directement lié au blocage « pas de véhicule » ci-dessus : tant que ce
prêt n'est pas obtenu, les dossiers prospects BTP ne peuvent pas être livrés sur place.

Une version mise à jour (22/08/2026, avec les 6 nouveaux prospects — campagne BTP Artigat +
secteur vétérinaire) a été préparée et envoyée à marc-paul pour relecture, **pas encore
renvoyée** à Initiative Ariège — vérifier avec lui avant tout envoi.

## Le dépôt `mp-solutions-ia` (attaché le 22/08/2026)

Contient `docs_template/` (`mp_template.py` = socle ReportLab commun, jamais à modifier
directement — voir le skill `mp-pdf-template` ; `dossier_fumeco.py`, `dossier_pons.py` =
dossiers par prospect qui l'importent) et `index.html` (site vitrine, voir aussi
`site-mpsolutions` plus haut — vérifier qu'il ne s'agit pas du même contenu en double).
`feedback_pdf_equilibrer_pages.md` documente la règle : jamais de grand blanc en bas de la
dernière page d'un dossier PDF, resserrer (styles locaux au fichier du dossier, pas
`mp_template.py`) plutôt que déborder sur une page quasi vide.

## Prospection par secteur — méthode et résultats (session du 22/08/2026)

En plus de la campagne BTP Artigat, prospection étendue à d'autres secteurs en Ariège, toujours
avec la même méthode (recherche web + vérification SIRET + exclusion des enseignes nationales
et des sites déjà en place). Résultats ajoutés à `clients_agent.py` (28 prospects au total) :

- **Location de matériel** : 1 trouvé sur ~15 candidats explorés — SNLC Appameteck (Cyril
  Charbonnier, Pamiers, sono/éclairage événementiel). Le secteur est globalement déjà bien
  couvert par des structures avec site (AMB, Stockbat, Proloc, Mél'ocation...) — rendement
  faible, ne pas y retourner sans nouvelle piste.
- **Sport** : 2 trouvés — Move Fitness (Saverdun, salle de fitness) et L'Éterlou Sport
  (Ax-les-Thermes/Luzenac, magasin d'articles de sport). Écartés : tous les coachs/guides
  outdoor identifiés (Nadège Paci, Ariège Canyon Aventure, etc.) ont déjà un site ; les coachs
  sportifs listés sur des plateformes marketplace (OwnSport) sont impossibles à identifier
  pleinement (nom complet masqué, page bloquée) — ne pas les ajouter sans SIRET vérifié.
- **Santé/bien-être : abandonné le 22/08.** Un seul candidat potentiel trouvé (Marie Esthétique,
  Le Fossat, institut de beauté depuis 2005) mais **SIRET introuvable** malgré une dizaine de
  recherches — piste laissée de côté plutôt que d'inventer un numéro. Piège évité au passage :
  ne pas confondre avec « BEAUTY MARIE », société homonyme sans rapport basée à Orchies (59).

**Limite technique de cet environnement (sessions cloud) :** PagesJaunes, Pappers,
annuaire-entreprises.data.gouv.fr, societe.com et ownsport.fr sont **bloqués par le proxy
d'egress réseau** — seul `WebSearch` (résultats indexés) fonctionne, pas `WebFetch` direct sur
ces domaines. Ça limite la vérification SIRET aux extraits que WebSearch remonte ; si rien ne
sort, ne pas inventer le numéro — dire que c'est introuvable, comme pour Marie Esthétique.

**Nouveau type de dossier : « découverte, sans tarif ».** Pour un prospect qui n'a pas encore eu
de premier contact, ne jamais afficher de tarif dans le dossier PDF (contrairement aux dossiers
« envoyés » du 17/08 qui avaient un tableau tarif) — la structure Docteur Commercial se termine
par une section « Prochaine étape » invitant à un échange, pas par un prix imposé. Exemples :
`dossier_snlc_appameteck.py`, `dossier_move_fitness.py`, `dossier_eterlou_sport.py` sur
`mp-solutions-ia`. Le tarif n'apparaît que dans un dossier commercial complet, après un premier
échange.

**Process de validation établi cette session :** toujours montrer le diff (`git diff`/`git show`)
avant `git push`, même après un `git commit` déjà fait — ne pas pousser à l'aveugle sur la
confirmation d'un commit seul.

## Repositionnement commercial « agent qui coordonne » (24-26/08/2026)

Marc-Paul a poussé lui-même, en direct sur GitHub (commits `92cd586` et `82841b5`, auteur
`marcdassens06@gmail.com` — pas une session Claude), un changement de discours sur
`mp-solutions-ia` : on ne vend plus « un chatbot », mais un « agent qui coordonne » — il vérifie
une info avant de répondre, transmet, signale l'urgent. Nouveau fichier maître :
`docs_template/fiche_commerciale_generique.py` (2 pages, fusion de l'ancien prospectus
philosophique et de la fiche capacités), plus `prospectus_mp_solutions_ia.pdf` et
`build_prospectus.py`. Le nouveau paragraphe type "++ CE QUE JE PROPOSE" ("Je n'installe pas
seulement un chatbot : j'intègre l'IA...") a été réappliqué aux 22 dossiers prospects existants.
**Leçon : ce dépôt peut évoluer hors session Claude — toujours `git fetch origin main` avant de
retoucher `mp-solutions-ia`, ne pas supposer que le dernier push connu est encore le HEAD.**

**Ajout du 26/08 : la création de site web fait partie de l'offre**, pour les prospects qui n'en
ont pas. Ajouté à trois endroits de `fiche_commerciale_generique.py` (puce page 1, ligne du
tableau des bénéfices page 2, précision dans "Comment ça marche") — une seule mention ne suffisait
pas, il a fallu que Marc-Paul la redemande deux fois de plus pour que ce soit visible. Appliqué
aussi aux 7 dossiers prospects "sans site" existants (Batisse et Deco, CB Couverture, Claustre,
Dupuy, Sans et Fils, Bois Ariégeois, Garrigues) **en plus de**, pas à la place de, leur offre
existante de page de contact simple.

**Piège rencontré : ajouter une phrase, même courte, à un dossier 2 pages déjà tassé au pixel
près peut le faire déborder sur une 3e page quasi vide** (vécu sur Batisse et Deco et Garrigues :
juste 1 ligne en trop faisait basculer tout le reste sur une page 3 à 60 % vide). Un seul essai
de resserrage des espacements ne suffit pas forcément — il faut aussi raccourcir la phrase
elle-même à une seule ligne (~85 caractères) si la page était déjà pleine jusqu'au bas. Toujours
regénérer en PDF et vérifier visuellement (`pdftoppm`) après ce genre d'ajout, pas seulement
compter les pages de tête.

## Documents de prospection — où trouver quoi (26/08/2026)

Sur `mp-solutions-ia`, chaque prospect de `clients_agent.py` a maintenant potentiellement 3
niveaux de dossier PDF différents selon son avancement : dossier « découverte sans tarif »
(prospects jamais contactés, ex. SNLC Appameteck/Move Fitness/L'Éterlou Sport — voir plus haut),
dossier complet avec tableau tarif (prospects prêts à être livrés, ex. Fumeco/Pons), ou fiche
générique sans nom de prospect (`fiche_commerciale_generique.py`, utilisable telle quelle en
premier contact). Vérifier `git log --oneline` sur `mp-solutions-ia` en début de session pour
voir si de nouveaux dossiers sont apparus depuis la dernière fois.

## Adresse de contact MP Solutions IA (29/09/2026)

- **Adresse officielle : `contact@mpsolutionsia.fr`** — confirmée par marc-paul, elle reçoit
  bien dans sa boîte. À utiliser partout : documents, prompts de bots, notifications.
- `mpsolutionsia@gmail.com` **n'existe pas** (confirmé par marc-paul). Un test d'envoi depuis
  sa boîte n'a renvoyé aucun rejet, ce qui ne prouve rien : ne jamais conclure « elle existe »
  sur l'absence de rejet. Des visiteurs de la bulle du site ont pu écrire à cette adresse
  jusqu'au 29/09 : ces messages sont perdus.
- `marcdassens09@gmail.com` est son adresse personnelle : ne pas l'utiliser comme adresse
  professionnelle ni comme destinataire des notifications de prospects
  (marc-paul : « contact@mpsolutionsia.fr à la place de marcdassens09@gmail.com »).
- Corrigé le 29/09 : signature des 22 dossiers de `mp-solutions-ia` (PDF régénérés), prompt
  du bot vitrine (`assistant-mpsolutions/app.py`), pied de page du dashboard du camping.
  Le camping garde sa propre adresse (`campingartigat@gmail.com`, voir plus haut).
- **Reste à faire** : `demo-chatbot-ia/app.py` utilise `mpsolutionsia@gmail.com` comme
  identifiant de connexion SMTP (`GMAIL_USER`) : l'envoi de notification ne peut pas
  fonctionner tant qu'un vrai compte Gmail + mot de passe d'application ne sont pas
  configurés. `contact@mpsolutionsia.fr` n'est pas un compte Gmail : il ne peut pas servir
  de login SMTP, seulement de destinataire.
- Après tout remplacement d'adresse : chercher l'ancienne dans les `.py`, `.html` **et les
  PDF** (les PDF sont générés, la source seule ne suffit pas).

## Rotation de clé API — pièges vécus le 30/09/2026

Rotation faite en une journée au lieu de 10 minutes. Ce qui a coûté du temps :

- **`/health` ne prouve pas que la clé est valide.** `api_key_set: true` veut dire qu'une
  clé est présente, pas qu'Anthropic l'accepte. Le vrai test est un appel réel :
  `python verifier_services.py`. Symptôme d'une clé morte : `500` sur `/chat` côté client,
  `401 API key is invalid` dans les logs Render.
- **Noms de clés qui se ressemblent** (`Claude_code_local_2` / `claude_code_local_2`) : la
  bonne clé a été supprimée par erreur, `mpsolutionsia` est tombé. Nommer chaque clé par
  son usage (`mpsolutionsia-render-2026-09`) et faire une capture de la liste avant toute
  suppression. Une clé supprimée ne se récupère pas, il faut en recréer une.
- **Expiration par défaut : 30 jours** dans la console. Pour un bot en production, une clé
  qui expire provoque une panne. Choisir « Jamais » (ou une date lointaine notée dans
  l'agenda). Les clés « héritées » n'expirent pas.
- **Le test local peut mentir.** `python agent_loop.py` a donné 151,10 € avec une autre clé
  que celle du `.env` (variable système ou autre source). Tester le `.env` directement :
  `python -c 'from dotenv import dotenv_values; import anthropic; k=dotenv_values(".env")["ANTHROPIC_API_KEY"]; print(len(k),k[:16],k[-4:]); anthropic.Anthropic(api_key=k).messages.create(model="claude-sonnet-5",max_tokens=10,messages=[{"role":"user","content":"ok"}],thinking={"type":"disabled"}); print("CLE .env OK")'`
- **Render : la modification peut ne pas avoir pris.** Comparer les 16 premiers et les 4
  derniers caractères de la variable avec le `.env`, et vérifier qu'un déploiement manuel
  est bien passé à « Live » (`list_deploys`). « Save » seul ne redéploie pas.
- **GitHub : un secret ne se relit jamais**, on ne peut que le remplacer. Utiliser
  Settings → Secrets and variables → Actions → **Repository secrets** (pas
  « Environment secrets », qui est une autre page). Vérifier ensuite avec « Re-run all jobs ».
- **Ne jamais coller la clé entière dans un chat.** Donner seulement le début (16 caractères)
  et la fin (4). Une clé collée est à considérer comme exposée.
- Ordre sûr : nouvelle clé → `.env` → test direct → Render → `verifier_services.py` →
  secret GitHub → CI vert → **seulement alors** supprimer l'ancienne.

## Fumeco-Lèze — état au 01/10/2026

- **Un mail a bien été envoyé le 17/08/2026** à `contact@fumeco.fr` (objet « Un chatbot pour
  désengorger l'accueil client de FUMECO-LEZE ? », trouvé dans `in:sent` Gmail). Aucune réponse
  vue dans la boîte au 01/10. L'ancienne note « jamais réellement envoyé » ne valait que pour le
  **dossier PDF**, pas pour ce mail.
- **01/10 : deux documents créés** (aperçus validés par marc-paul, PDF téléchargés) : un
  courrier de **premier contact** 1 page, sans tarif (structure Docteur Commercial, « agent qui
  coordonne », prochaine étape = il passe à l'entreprise), et une **fiche d'entrevue** 2 pages
  recto verso, interne, avec ROI en cases vides. Marc-Paul les remet **en main propre**
  (voisin à Artigat) — **remise pas encore confirmée** : ne pas écrire « livré » avant qu'il
  le dise (date + à qui).
- **Sources Drive** : dossiers « Fumeco-Lèze » `1MNRS6MvxbypKrQgCq2oRoS-vfJmHSgSm` et
  `1gcF1wwYtMqHJ7xyJHhPIx4lpP8DfAzdR` (plan d'attaque, mail de prospection, prompts chatbot web
  et agent vocal, PDF v4/v5/v6). **Les PDF v4/v5/v6 sont signés `mpsolutionsia@gmail.com`**
  (adresse inexistante) — la bonne est `contact@mpsolutionsia.fr`.
- **Chiffres qui se contredisent, ne pas les citer comme faits** : salariés (20 dans le plan
  d'attaque, « +15 » dans `clients_agent.py`) ; références produits (60+ / 50). Dans le
  courrier on a écrit « un large catalogue ». L'histoire du Dr Caissel et la citation des
  40 ans (plan d'attaque) n'ont pas de source vérifiée : non reprises.
- **À ne pas réutiliser** : le plan d'attaque Drive propose un « essai gratuit » (formule
  interdite dans les documents commerciaux) ; le simulateur de devis Drive donne un ROI négatif
  et un abonnement à 800 € (erreur).
- **Coordonnées sur les documents** : Marc-Paul Dassens, 06 44 00 22 52,
  `contact@mpsolutionsia.fr`, Artigat (09130).
- **Les scripts générateurs sont versionnés** sur `mp-solutions-ia` (PR #2, fusionnée le
  01/10/2026) : `docs_template/premier_contact_fumeco.py` et `fiche_entrevue_fumeco.py`, avec
  leurs PDF. Polices DejaVu cherchées sous Linux, `C:/Windows/Fonts/` ou à côté du script ;
  non testé sous Windows. Leçons de mise en page : le slogan est déjà dans le logo
  du header, ne pas le répéter dans le corps ; `build_document(..., show_page_number=False)`
  retire le « 1/1 » sans toucher `mp_template.py` ; pour remplir une page A4 sans blanc,
  corps 10 pt / interligne 17 / espaces de section 16-17 (dernière ligne vers y≈759 sur 771) ;
  DejaVu-Oblique absent du conteneur Linux, `pip install reportlab` nécessaire.

### Fumeco — reste à faire (01/10/2026)

- **Après la remise en main propre** : marc-paul donne la date et la personne qui a pris le
  courrier → mettre `clients_agent.py` à jour (`prochaine_action`, `notes`). Tant qu'il ne l'a
  pas dit, ne pas écrire « livré ».
- **Après l'entrevue** : la fiche d'entrevue remplie sert à calculer le ROI avec des vrais
  chiffres ; ensuite seulement viennent le dossier commercial complet (avec tarif), le bon de
  commande et le questionnaire technique (étapes 2 à 4 de la structure commerciale).
- **Corriger le Drive** : les PDF v4/v5/v6 signés `mpsolutionsia@gmail.com`.

### Méthode de travail sur les documents PDF (session du 01/10/2026)

- Ordre validé par marc-paul : accord sur le contenu → génération → **aperçus JPG envoyés avec
  `SendUserFile`** (page entière + zoom header/bas de page) → corrections → « go » → PDF final.
  Il dit « montre » pour revoir l'aperçu ; **le PDF n'est envoyé qu'après « go »**.
- **Renvoyer le PDF final après chaque modification** : il télécharge ce qu'on lui envoie
  (risque constaté : il a dit « je l'ai téléchargé » alors qu'on n'avait envoyé que des JPG d'aperçu). Vérifier le nom et la date.
- Il corrige à l'œil et directement : slogan en double, « 1/1 » inutile, blanc en bas de page,
  ajout de son numéro. Les messages dictés à la voix peuvent être brouillés : dire comment on
  les a compris, il corrigera si besoin.
- **Git sur ce dépôt** : après une PR fusionnée, repartir de `origin/main`
  (`git checkout -B <branche> origin/main`), jamais empiler sur l'historique fusionné. Pour
  pousser sur `mp-solutions-ia`, l'attacher en écriture (`add_repo` avec `access: push`) : le
  clone est alors à `/home/user/mp-solutions-ia` (pas dans `/home/user/marcdassens09-bot/`).
  Marc-Paul demande lui-même la pull request, puis la fusion : ne pas fusionner de lui-même.

## Conventions

- Clé API dans `.env` (non versionné), jamais en dur.
- Modèle : `claude-sonnet-5` (migré le 09/08/2026, tous les bots publics du parc). Sur ce
  modèle, `thinking` est activé par défaut si on ne le précise pas — ajouter
  `thinking={"type": "disabled"}` sur les appels à `max_tokens` serré, sinon le
  raisonnement peut manger le budget avant la réponse. Vérifier aussi la version du SDK
  `anthropic` dans `requirements.txt` : une version trop ancienne ne connaît pas ce
  paramètre (`TypeError`, vécu en prod sur `mpsolutionsia` le 09/08, voir mémoire
  `migration-sonnet-5-bots`).
- Les instances Render gratuites s'endorment : prévoir ~50 s au premier appel. Un ping
  UptimeRobot (5 min) est en place depuis le 09/08 sur les 6 bots publics + `agent-loop`,
  ça limite le risque mais ne l'élimine pas totalement.
- Un correctif n'est « fait » que **commité et poussé** : vérifier `git show HEAD:fichier`,
  pas le fichier sur disque. (Le 03/08, la phrase IA Act du camping a dormi 24 h en local
  pendant que la prod tournait sans elle.)
