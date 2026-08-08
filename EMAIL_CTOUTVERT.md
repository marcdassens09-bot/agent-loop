# Demande d'accès API SecureHoliday — Camping Les Eychecadous

**Destinataire :** commercial@ctoutvert.com
**Téléphone :** +33 5 61 47 23 53

> Prêt à envoyer. SIRET vérifié au registre public le 08/08/2026.

---

## Objet

```
Demande d'accès API SecureHoliday — Camping Les Eychecadous (établissement 5438)
```

## Corps du message

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

Le brouillon précédent se présentait comme « en charge du développement des
outils digitaux » avec une adresse Gmail, et réclamait des clés API dès le
premier message. Un éditeur ne remet pas d'accès technique à un inconnu :
il vérifie d'abord à qui il parle, et surtout si le titulaire du compte est
d'accord.

Cette version corrige trois points :

- **une identité vérifiable** — raison sociale, SIRET, domaine, adresse
  professionnelle. C'est ce qui distingue un prestataire d'un curieux ;
- **une demande proportionnée** — on demande la marche à suivre et la
  documentation, pas des clés de production d'emblée ;
- **le mandat du camping évoqué d'entrée** — c'est la question que Ctoutvert
  posera de toute façon, autant y répondre avant qu'elle soit posée.

## Le point qui décide

Ctoutvert traitera plus vite si la demande vient **du camping** ou si le
camping est en copie : c'est son établissement, son contrat, ses données.
Le plus efficace est de demander au gérant de mettre `contact@mpsolutionsia.fr`
en copie d'un message envoyé depuis son adresse, ou de te mandater par écrit.

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

- [x] SIRET renseigné dans le message
- [ ] Camping informé, mandat ou mise en copie obtenue
- [ ] Message envoyé à commercial@ctoutvert.com
- [ ] Relance téléphonique au +33 5 61 47 23 53 si sans réponse sous une semaine
- [ ] Documentation reçue
- [ ] `secureholiday_api.py` réécrit d'après la documentation
