# Les Sentiers — Génération de niveaux 2D

Projet IAS · Victor Francis Itoua Mveng · Travail individuel.

Générer des niveaux de plateforme, vérifier leur accessibilité et améliorer leur structure par recherche locale. Une version jouable permet de les essayer.

## Installation et lancement

Python 3.10 ou plus récent et un navigateur récent. Aucune bibliothèque Python externe. Node.js sert uniquement aux tests JavaScript.

Sur GitHub, choisir **Code → Download ZIP**, extraire l’archive et ouvrir un terminal dans le dossier contenant `jouer.py`. Ou utiliser Git :

```sh
git clone https://github.com/ItxMveng/generation-niveaux-2d.git
cd generation-niveaux-2d
python jouer.py --ouvrir
```

Sous Windows, remplacer `python` par `py -3` si nécessaire. Sans `--ouvrir`, ouvrir manuellement `sorties/jeu.html`. Ce fichier contient le jeu et fonctionne hors ligne. Les sorties sont créées automatiquement et exclues de Git.

Flèches ou Q/D : avancer. Espace : sauter. **E : sauter vers la droite avec une seule touche.** Maintenir une touche de saut permet de ressauter à l’atterrissage. R : recommencer. Échap : pause. Rejoindre le drapeau ; les éclats sont facultatifs. Boutons tactiles, aide de chemin et rythme détendu disponibles. La progression dure seulement le temps de la session.

## Choix et adaptations

- **Construction** : plateaux de 3 à 6 colonnes, trous bornés, écart de hauteur maximal d’une case entre surfaces solides successives, quatre colonnes protégées à chaque extrémité.
- **Validation** : parcours en largeur sur `(x, y, montée restante)`, collisions et saut de deux cases par défaut. Un départ inaccessible est signalé, sans remplacement.
- **Recherche locale** : modifier une à trois colonnes et conserver les gains stricts sur des terrains valides et accessibles. Le budget compte toutes les propositions. Un départ inaccessible n’est pas réparé.
- **Ajouts** : jeu hors ligne, interface et analyse des résultats Python. Le jeu utilise les transitions du validateur ; les aides ne permettent pas de double saut.

Le score vise 10 % de colonnes vides, 20 % de changements entre colonnes voisines solides et un plateau maximal de 30 % de la largeur ; poids : 35 %, 35 %, 30 %. Les formules sont dans `niveaux/evaluation.py`. Un terrain inaccessible n’a pas de score admissible.

## Résultats et exemples

```sh
python main.py --graine 105 --sortie sorties/avant.svg
python main.py --graine 105 --ameliorer --sortie sorties/apres.svg
python comparer.py --debut 100 --nombre 50 --budget 200
```

Le rendu produit un SVG et un JSON ; la comparaison produit `sorties/comparaison/resultats.json` et `resultats.csv`. Protocole : mêmes 50 départs, grilles 40 × 12, saut de deux cases, 200 propositions, graine de recherche 0. Critères fixés avant l’expérience ; échecs conservés, scores comparés sur les mêmes départs accessibles.

| Mesure | Construction | Après recherche |
| --- | ---: | ---: |
| Accessibilité | 50/50 | 50/50 |
| Score moyen sur 100 | 61,22 | 97,89 |
| Écart-type | 12,54 | 0,32 |
| Diversité des profils | 0,683 | 0,670 |
| Temps moyen, évaluation incluse | 0,64 ms | 59,18 ms au total |

Les 50 scores augmentent. La diversité est la proportion moyenne de colonnes différentes sur 1 225 paires, trous inclus. Les temps proviennent d’un seul passage et dépendent de la machine.

- **105** : deux trous séparés et quelques retouches ; choix d’une amélioration discrète. Limite : réception surélevée après le premier trou.
- **117** : terrasses, troisième trou ajouté, plateau maximal réduit de 18 à 11 colonnes ; choix d’un cas intermédiaire. Limite : un saut supplémentaire peut être nécessaire.
- **143** : plateau maximal réduit de 32 à 11 colonnes ; transformation visible. Limite : deux trous proches n’ont qu’une colonne d’appui entre eux.

Pour les jouer : `python jouer.py --graines 105 117 143 --sortie sorties/selection.html`.

## Vérifications et suites possibles

```sh
python -m unittest discover -s tests
python jouer.py
node tests/test_moteur.js sorties/jeu.html
node tests/test_interface.js sorties/jeu.html
```

39 tests Python et tests JavaScript, dont 1 860 transitions sur les terrains par défaut. Les tests d’interface simulent le DOM ; ils ne valident pas le rendu visuel. Organisation : `niveaux/` pour les algorithmes, `jeu/` pour l’interface, `tests/` pour les contrôles.

Le déplacement est discret, sans inertie ; la recherche peut stagner. Le score ne mesure pas le plaisir de jeu. Avec plus de temps, je répéterais les départs avec plusieurs graines de recherche, budgets et dimensions pour mesurer la stabilité. Je comparerais aussi les scores au taux de réussite, au nombre d’essais et aux avis de joueurs.

## Sources et assistance

Sujet « IAS — Platform level Generation », Anne-Gwenn Bosser, et consignes du module. Interface adaptée de ma maquette ; décors dessinés dans le projet. Une assistance IA est utilisée pour la rédaction.
