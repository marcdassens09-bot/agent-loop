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

## Quand les identifiants arriveront

Ils vont dans le fichier `.env` du dépôt `chatbot-camping-eychecadous`, jamais
en dur dans le code et jamais collés dans une conversation. Voir
[SECUREHOLIDAY_SETUP.md](./SECUREHOLIDAY_SETUP.md) pour la suite, et garder en
tête que les endpoints actuels de `secureholiday_api.py` sont **supposés et
faux** : tout sera à réécrire d'après la documentation reçue.

## Suivi

- [x] SIRET renseigné dans le message (version 2)
- [x] Nom de famille d'Anthony renseigné (version 1)
- [x] Version 1 envoyée par Anthony le 08/08/2026, `contact@mpsolutionsia.fr` en copie
- [ ] Relance téléphonique au +33 5 61 47 23 53 si sans réponse sous une semaine (relancer à partir du 15/08/2026)
- [ ] Documentation reçue
- [ ] `secureholiday_api.py` réécrit d'après la documentation
