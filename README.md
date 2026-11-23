# Génération procédurale de niveaux 2D

Projet IAS — Victor Francis Itoua Mveng — travail individuel.

## Objectif

Générer des niveaux de jeu de plateforme sous forme de grilles de tuiles, puis comparer une méthode constructive à une méthode de recherche. Le projet porte sur les décors et le placement des éléments.

## Approche prévue

1. Représenter un niveau par une grille et produire un premier exemple fixe.
2. Générer des niveaux avec des règles explicites et une graine aléatoire reproductible.
3. Définir un modèle simplifié de déplacement et vérifier l'existence d'un chemin du départ à l'arrivée.
4. Ajouter une recherche locale pour améliorer les niveaux selon des critères mesurables.
5. Comparer les méthodes sur les mêmes conditions d'évaluation et présenter plusieurs niveaux commentés.

Le projet utilise Python et sa bibliothèque standard. Le rendu SVG s'ouvre dans un navigateur, sans installation supplémentaire.

## État actuel

- Grille de tuiles et exemple fixe.
- Générateur constructif reproductible : plateaux de 3 à 6 colonnes (le dernier peut être plus court), variations de hauteur limitées à une case, trous de taille bornée.
- Quatre colonnes sans trou aux deux extrémités, départ et arrivée posés sur le sol.
- Affichage texte, rendu SVG et export JSON de la grille et des paramètres.
- Recherche de chemin avec marche, saut et chute dans un modèle discret.
- Chemin visible en pointillés dans le SVG et enregistré dans le JSON.
- La fonction de qualité, la recherche locale et la comparaison restent à réaliser.

## Exécution

Python 3.10 ou plus récent. Depuis le dossier du projet :

```sh
python main.py
python main.py --graine 17 --largeur 48 --trou-max 2 --sortie sorties/terrain-17.svg
python main.py --exemple --sortie sorties/exemple.svg
python main.py --graine 42 --saut 1 --sortie sorties/saut-1.svg
python -m unittest discover -s tests -v
```

Ouvrir ensuite `sorties/niveau.svg` dans un navigateur. `D` indique le départ, `A` l'arrivée, `#` le sol et `.` le vide.

Le JSON associé conserve la grille et les paramètres. À code et paramètres identiques, une même graine reproduit le même niveau. Les sorties générées ne sont pas suivies par Git.

## Organisation du code

- `main.py` : paramètres en ligne de commande et enregistrement des fichiers.
- `niveaux/grille.py` : représentation et vérification de la structure de la grille.
- `niveaux/generation.py` : règles de construction du terrain.
- `niveaux/rendu.py` : dessin du niveau en SVG.
- `niveaux/parcours.py` : déplacements possibles et recherche de chemin en largeur.
- `tests/` : contrôles de structure, de reproductibilité et des règles de génération.

## Limites à examiner

Le personnage occupe une case. Au sol, il peut marcher d'une case à gauche ou à droite, ou sauter. Le saut monte d'une case par étape pendant la hauteur choisie (`--saut`, 2 par défaut), puis le personnage descend d'une case par étape. En l'air, il peut se déplacer horizontalement de -1, 0 ou +1 case à chaque étape. Un plafond interrompt la montée. Les blocs et les coins des blocs ne peuvent pas être traversés ; un nouveau saut exige du sol sous les pieds. Sortir de la grille est interdit et son bord inférieur ne sert pas de sol.

Le départ et l'arrivée doivent être posés sur le sol. Le parcours en largeur trouve un chemin minimal en nombre de transitions, s'il existe. Le JSON version 2 conserve le modèle, la hauteur de saut, les états `(x, y, montée restante)`, le nombre d'états explorés et la conclusion. Un terrain inaccessible reste exporté pour pouvoir l'analyser.

« Accessible » signifie accessible selon ce modèle simplifié : il n'y a ni accélération, ni inertie, ni limite de chute ou vitesse horizontale continue. Cela ne prouve pas la jouabilité dans un moteur physique complet. Une note automatique ne mesure pas non plus le plaisir de jeu.

## Assistance et sources

Une assistance IA est utilisée pour le cadrage, la rédaction et le développement.

Le cadrage repose sur le sujet « IAS — Platform level Generation » et les consignes générales fournis par l'équipe enseignante. Les ressources externes effectivement utilisées seront référencées avec leur licence.
