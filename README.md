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

Un premier niveau fixe est représenté par une grille et affiché en texte et en SVG. Le générateur et la vérification des chemins restent à réaliser.

## Exécution

Python 3.10 ou plus récent. Depuis le dossier du projet :

```sh
python main.py
python -m unittest discover -s tests -v
```

Ouvrir ensuite `sorties/niveau.svg` dans un navigateur. `D` indique le départ, `A` l'arrivée, `#` le sol et `.` le vide.

## Limites à examiner

Un niveau visuellement cohérent n'est pas nécessairement franchissable. La vérification dépendra d'hypothèses explicites sur les déplacements ; elle ne prouvera pas la jouabilité dans un moteur physique complet. Une note automatique ne mesure pas à elle seule le plaisir de jeu.

## Assistance et sources

Une assistance IA est utilisée pour le cadrage, la rédaction et le développement.

Le cadrage repose sur le sujet « IAS — Platform level Generation » et les consignes générales fournis par l'équipe enseignante. Les ressources externes effectivement utilisées seront référencées avec leur licence.
