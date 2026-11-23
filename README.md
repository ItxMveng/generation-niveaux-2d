# Génération procédurale de niveaux 2D

Projet IAS — Victor Francis Itoua Mveng — travail individuel.

## Objectif

Construire des niveaux de plateforme 2D, vérifier leur accessibilité et comparer une méthode constructive à une recherche locale. Une petite version jouable permet aussi d'essayer les terrains.

## Lancer le jeu

Python 3.10 ou plus récent et un navigateur récent. Aucune bibliothèque externe à installer.

```sh
python jouer.py --ouvrir
```

La commande génère trois terrains améliorés et ouvre `sorties/jeu.html`. Ce fichier contient tout le jeu et fonctionne ensuite hors ligne. Sans `--ouvrir`, il suffit de l'ouvrir manuellement.

- Flèches ou Q/D : avancer ; Espace ou flèche haute : sauter.
- R : recommencer ; Échap : mettre en pause.
- Rejoindre le drapeau orange pour terminer chaque traversée.
- Trois éclats facultatifs à récupérer par terrain.
- Boutons tactiles et aide pour afficher un chemin possible.

Les trois graines par défaut sont 42, 17 et 7. Pour choisir d'autres terrains : `python jouer.py --graines 42 17 --budget 200`. Une graine inaccessible est refusée avec un message, sans être remplacée silencieusement.

L’interface reprend la maquette « Les Sentiers » : accueil illustré, choix du niveau, partie, analyse, aide et réglages. Les cartes représentent les terrains exportés. L’analyse présente les mesures et l’historique réellement calculés en Python. Le rythme détendu ralentit les déplacements sans changer les règles de saut. Les préférences et les niveaux terminés sont conservés seulement pendant la session.

## Générer et analyser un terrain

```sh
python main.py --graine 42 --sortie sorties/avant.svg
python main.py --graine 42 --ameliorer --budget 200 --graine-recherche 0 --sortie sorties/apres.svg
python main.py --exemple --sortie sorties/exemple.svg
```

Le terminal, le SVG et le JSON présentent le terrain, son chemin et ses mesures. Le JSON version 4 conserve les paramètres, la version du score, les rejets et l'historique des améliorations. Les sorties sont exclues de Git.

## Méthodes

Le générateur construit des plateaux de 3 à 6 colonnes, parfois raccourcis à la fin, et des trous bornés. Les surfaces solides successives diffèrent d'au plus une case. Quatre colonnes plates sont réservées à chaque extrémité.

Le validateur utilise un parcours en largeur sur des états `(x, y, montée restante)`. Le personnage occupe une case, marche au sol, monte pendant deux étapes par défaut, puis descend. En l'air, le déplacement horizontal vaut -1, 0 ou +1 case. Les blocs et leurs coins ne peuvent pas être traversés, et un nouveau saut exige un support. Le jeu utilise les transitions exportées par ce même validateur : ses déplacements ne reposent pas sur un second moteur physique.

La recherche locale modifie une à trois colonnes centrales : monter, descendre, creuser ou combler. Elle conserve les extrémités, les limites de hauteur et de trous. Elle peut créer des plateaux plus courts que le générateur initial. Seuls les gains stricts de score sur des terrains accessibles sont acceptés. Le budget compte toutes les propositions. Le terrain initial doit être accessible.

## Évaluation et limites

Le score `construction-v1` vise 10 % de colonnes sans sol, 20 % de changements parmi les paires de colonnes voisines solides et un plateau maximal d'au plus 30 % de la largeur. Les poids sont 35 %, 35 % et 30 %. Pour les deux premières composantes : `max(0, 1 - abs(valeur - cible) / cible)`. La dernière vaut 1 jusqu'à 30 %, puis décroît jusqu'à 0 pour un terrain entièrement plat. La somme pondérée est ramenée sur 100.

L'accessibilité est obligatoire : le score final vaut `null` si aucun chemin n'existe. Ces cibles sont des choix de conception, pas une mesure du plaisir de jeu. Le profil ne décrit que la plateforme la plus haute de chaque colonne. Le modèle de déplacement n'a ni inertie ni accélération ; la recherche peut stagner et ne garantit pas un optimum global. La comparaison sur 50 graines est présentée ci-dessous.

## Code et tests

- `main.py`, `jouer.py` : commandes d'analyse et d'export du jeu.
- `niveaux/` : grille, génération, parcours, évaluation, recherche, rendu et export.
- `jeu/` : interface HTML/CSS et moteur JavaScript.
- `tests/` : contrôles des règles, des scores et des déplacements.

```sh
python -m unittest discover -s tests -v
python jouer.py
node tests/test_moteur.js sorties/jeu.html
node tests/test_interface.js sorties/jeu.html
```

Node.js sert uniquement aux deux tests JavaScript. Le jeu se lance sans Node. Le test d'interface simule les événements du DOM ; il ne remplace pas un essai visuel dans un navigateur.

## Sources et assistance

Sujet « IAS — Platform level Generation » et consignes de l'équipe enseignante. Les décors sont dessinés par le code, sans pack graphique externe. Une assistance IA est utilisée pour le cadrage, la rédaction et le développement.

### Commandes de saut

Espace, ↑ ou Z permettent de sauter ; maintenir la touche permet de ressauter à l’atterrissage. Un appui anticipé est conservé pendant 320 ms. E (ou le bouton tactile Saut ↗) déclenche un saut vers la droite et conserve cette direction pendant le vol, sauf si une flèche est utilisée. L’avance automatique cesse à l’atterrissage. Ces aides ne changent pas les transitions autorisées et ne permettent pas de double saut.

## Comparaison des méthodes

```sh
python comparer.py --debut 100 --nombre 50 --budget 200
```

Les résultats détaillés sont enregistrés dans `sorties/comparaison/resultats.json` et `resultats.csv`. Les deux méthodes utilisent les mêmes 50 terrains de départ (graines 100 à 149), de 40 × 12 cases, avec un saut de deux cases. La recherche utilise 200 propositions et la graine 0. Les critères sont fixés avant l'expérience. Les départs inaccessibles sont conservés comme échecs, sans remplacement ; les scores sont comparés sur les mêmes départs accessibles.

| Mesure | Construction | Après recherche |
| --- | ---: | ---: |
| Terrains accessibles | 50/50 | 50/50 |
| Score moyen / 100 | 61,22 | 97,89 |
| Écart-type des scores | 12,54 | 0,32 |
| Diversité des profils | 0,683 | 0,670 |
| Temps moyen par terrain, évaluation comprise | 0,64 ms | 59,18 ms au total |

Les 50 scores augmentent, de 36,68 points en moyenne. La diversité est la proportion moyenne de colonnes différentes entre deux profils, trous inclus (1 225 paires). Elle baisse légèrement. Les temps viennent d'un seul passage sur la machine de développement et varient selon la machine. Le score optimisé n'est pas une mesure du plaisir de jeu. Une seule graine de recherche et une seule configuration ont été étudiées : ces résultats ne garantissent pas le même comportement partout.
