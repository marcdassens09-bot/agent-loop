# Demande d'accès API SecureHoliday — Camping Les Eychecadous

**Destinataire :** commercial@ctoutvert.com
**Téléphone :** +33 5 61 47 23 53

> Prêt à envoyer. SIRET vérifié au registre public le 08/08/2026.

---

## Version 1 — envoyée par Anthony (recommandée)

C'est la sienne, sur son compte SecureHoliday : Ctoutvert répond plus vite et
sans poser de question de mandat quand la demande vient directement du
titulaire. À lui transmettre pour qu'il l'envoie depuis sa propre adresse,
en mettant `contact@mpsolutionsia.fr` en copie — la réponse de Ctoutvert
arrive alors aux deux en même temps.

### À copier-coller

```
Objet : Demande d'accès API SecureHoliday — Camping Les Eychecadous (établissement 5438)

Bonjour,

Je suis le gérant du Camping Les Eychecadous (établissement 5438), à
Artigat en Ariège.

Nous travaillons avec un prestataire technique, MP Solutions IA (Marc-Paul
Dassens), qui a mis en place l'assistant conversationnel de notre site. Il
oriente aujourd'hui nos visiteurs vers notre page de réservation
SecureHoliday avec leurs dates pré-remplies.

Nous souhaitons aller plus loin et afficher directement les disponibilités
et les tarifs dans la conversation, ce qui suppose un accès à l'API
SecureHoliday liée à notre établissement.

Pourriez-vous transmettre à mon prestataire, que je mets en copie de ce
message :

1. la documentation technique de l'API SecureHoliday ;
2. les modalités d'authentification et d'obtention des identifiants ;
3. l'accès à un environnement de test, s'il en existe un ;
4. le contact technique à qui adresser les questions d'intégration.

Je confirme par la présente que MP Solutions IA est autorisé à échanger
avec vous sur ce sujet pour le compte du Camping Les Eychecadous.

Cordialement,

Anthony Viviano
Camping Les Eychecadous
Artigat (09130), Ariège
campingartigat@gmail.com
```

Prête à envoyer telle quelle.

---

## Version 2 — envoyée par Marc-Paul (repli)

À utiliser seulement si Anthony préfère ne pas écrire lui-même. Moins
efficace : Ctoutvert demandera probablement une confirmation du camping
avant de répondre, ce que la version 1 évite.

### Objet

```
Demande d'accès API SecureHoliday — Camping Les Eychecadous (établissement 5438)
```

### Corps du message

```
Bonjour,

Je suis prestataire du Camping Les Eychecadous (établissement 5438, Artigat,
Ariège), pour lequel j'ai développé et mis en service un assistant
conversationnel qui répond aux questions des vacanciers.

Cet assistant oriente aujourd'hui les visiteurs vers votre page de
réservation avec leurs dates pré-remplies. Nous souhaitons aller plus loin
et afficher directement les disponibilités et les tarifs dans la
conversation, ce qui suppose un accès à votre API.

Pourriez-vous m'indiquer la marche à suivre, et me transmettre :

1. la documentation technique de l'API SecureHoliday ;
2. les modalités d'authentification et d'obtention des identifiants ;
3. l'accès à un environnement de test, s'il en existe un ;
4. le contact technique à qui adresser les questions d'intégration.

Le camping confirmera bien entendu cette demande de son côté si vous le
souhaitez, s'agissant de son établissement et de ses données.

Je reste à votre disposition.

Cordialement,

Marc-Paul Dassens
MP Solutions IA — micro-entreprise
SIRET 108 354 739 00014
09130 Artigat, Ariège
contact@mpsolutionsia.fr
https://mpsolutionsia.fr
```

---

## Pourquoi cette version

Un éditeur ne remet pas d'accès technique à un inconnu : il vérifie d'abord
à qui il parle, et surtout si le titulaire du compte est d'accord. La
version 1 répond à cette question avant qu'elle soit posée — c'est
pourquoi elle est recommandée. La version 2 reste utile si Anthony n'a pas
le temps ou préfère déléguer, mais elle repose sur une identité vérifiable
(raison sociale, SIRET, domaine) plutôt que sur le mandat direct.

Le téléphone reste plus rapide que l'e-mail pour ce type de demande.
À dire : « Je suis le prestataire technique du camping 5438, je cherche à
savoir si une API est disponible et à quelles conditions. »

## Dénouement (26/08/2026) : pas d'API, ni même limitée

Ctoutvert (Rachel, `commercial@ctoutvert.com`) a refusé tout accès API le
18/08, puis confirmé le 24/08 qu'il n'existe pas non plus d'« API light »
pour un client seul. `secureholiday_api.py` reste donc définitivement
inutilisable tel quel — pas de clés à attendre dans `.env`.

La solution retenue est la **construction d'URL** vers le moteur de
réservation public, avec les paramètres transmis par Rachel le 24/08
(`dateStart`/`dateEnd`, `travelers`, `productType`). Implémentée dans
`chatbot-camping-eychecadous` (`lien_reservation()` dans `app.py`,
[PR #1](https://github.com/marcdassens09-bot/chatbot-camping-eychecadous/pull/1),
fusionnée le 27/08/2026).

Point ouvert : le paramètre `/product/<id>` pour cibler un hébergement
précis, annoncé par Rachel, renvoie une 404 en pratique (testé le
27/08/2026 sur `/fr/5438/product/79658`). Relance envoyée le 27/08/2026
dans le même fil, copie Anthony, demandant le format exact. En attendant,
ce ciblage est désactivé côté code (pas de lien casse envoyé à un client).

## Suivi

- [x] SIRET renseigné dans le message (version 2)
- [x] Nom de famille d'Anthony renseigné (version 1)
- [x] Version 1 envoyée par Anthony le 08/08/2026, `contact@mpsolutionsia.fr` en copie
- [x] Documentation reçue (24/08/2026) : construction d'URL, pas d'API
- [x] Lien de réservation enrichi (dates, participants, type d'hébergement) — fusionné 27/08/2026
- [ ] Relance du 27/08/2026 sur le format `/product/<id>` (404 constaté) : en attente de réponse de Rachel
- [ ] Une fois le bon format confirmé : réactiver le ciblage produit dans `lien_reservation()`
