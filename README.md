# Génération procédurale de niveaux 2D

Projet IAS — Victor Francis Itoua Mveng — travail individuel.

## Objectif

Générer des niveaux de jeu de plateforme sous forme de grilles de tuiles, puis comparer une méthode constructive à une méthode de recherche. Le projet porte sur les décors et le placement des éléments : créer un jeu complet n'est pas nécessaire.

## Approche prévue

1. Représenter un niveau par une grille et produire un premier exemple fixe.
2. Générer des niveaux avec des règles explicites et une graine aléatoire reproductible.
3. Définir un modèle simplifié de déplacement et vérifier l'existence d'un chemin du départ à l'arrivée.
4. Ajouter une recherche locale pour améliorer les niveaux selon des critères mesurables.
5. Comparer les méthodes sur les mêmes conditions d'évaluation et présenter plusieurs niveaux commentés.

Python est retenu pour une première version simple à lire et à exécuter. Les premières étapes utiliseront la bibliothèque standard. Le choix d'une bibliothèque d'affichage viendra après la représentation des niveaux.

## État actuel

Cadrage uniquement : aucun générateur ni résultat expérimental n'est encore disponible. Il n'y a pas encore de commande d'exécution.

## Limites à examiner

Un niveau visuellement cohérent n'est pas nécessairement franchissable. La vérification dépendra d'hypothèses explicites sur les déplacements ; elle ne prouvera pas la jouabilité dans un moteur physique complet. Une note automatique ne mesure pas à elle seule le plaisir de jeu.

## Assistance et sources

Une assistance IA a été utilisée pour le cadrage et la rédaction initiale.

Le cadrage repose sur le sujet « IAS — Platform level Generation » et les consignes générales fournis par l'équipe enseignante. Les ressources externes effectivement utilisées seront référencées avec leur licence.
