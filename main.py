"""Afficher un niveau dans le terminal et enregistrer son rendu SVG."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from niveaux.generation import Parametres, generer
from niveaux.evaluation import (CIBLE_CHANGEMENTS, CIBLE_TROUS, LIMITE_PLATEAU,
                                POIDS, VERSION_SCORE, evaluer)
from niveaux.grille import niveau_exemple
from niveaux.rendu import rendre_svg
from niveaux.recherche import ameliorer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sortie", type=Path, default=Path("sorties/niveau.svg"))
    parser.add_argument("--exemple", action="store_true", help="Afficher le niveau fixe")
    parser.add_argument("--graine", type=int, default=42)
    parser.add_argument("--largeur", type=int, default=40)
    parser.add_argument("--hauteur", type=int, default=12)
    parser.add_argument("--trou-max", type=int, default=2, help="De 0 (sans trous) à 3")
    parser.add_argument("--saut", type=int, choices=range(1, 5), default=2,
                        help="Hauteur du saut dans le modèle discret (1 à 4 cases)")
    parser.add_argument("--ameliorer", action="store_true", help="Effectuer une recherche locale")
    parser.add_argument("--budget", type=int, default=200, help="Nombre de voisins proposés (0 à 5000)")
    parser.add_argument("--graine-recherche", type=int, default=0)
    args = parser.parse_args()
    if args.sortie.suffix.lower() != ".svg":
        parser.error("Le fichier de sortie doit avoir l'extension .svg.")
    try:
        parametres = Parametres(args.largeur, args.hauteur, args.graine, args.trou_max)
    except ValueError as erreur:
        parser.error(str(erreur))
    niveau = niveau_exemple() if args.exemple else generer(parametres)
    recherche = None
    if args.ameliorer:
        if args.exemple:
            parser.error("La recherche locale s'applique aux terrains générés, pas à l'exemple fixe.")
        try:
            recherche = ameliorer(niveau, parametres, args.saut, args.budget, args.graine_recherche)
        except ValueError as erreur:
            parser.error(str(erreur))
        niveau, evaluation = recherche.niveau, recherche.evaluation
    else:
        evaluation = evaluer(niveau, args.saut)
    parcours = evaluation.parcours
    titre = "Premier terrain" if args.exemple else f"Terrain · graine {args.graine}"
    if recherche is not None:
        titre += " · amélioré"
    donnees = {
        "format_version": 4,
        "methode": "recherche_locale" if recherche else ("exemple" if args.exemple else "constructive"),
        "parametres": None if args.exemple else asdict(parametres),
        "grille": niveau.lignes,
        "validation": {"modele": "deplacement-discret-v1", **asdict(parcours)},
        "evaluation": {
            "version": VERSION_SCORE,
            "cibles": {"taux_trous": CIBLE_TROUS, "taux_changements": CIBLE_CHANGEMENTS,
                       "proportion_plateau_max": LIMITE_PLATEAU},
            "poids": POIDS,
            "mesures": asdict(evaluation.mesures),
            "composantes": evaluation.composantes,
            "score_structure": evaluation.score_structure,
            "score": evaluation.score,
        },
    }
    if recherche is not None:
        donnees["recherche"] = {cle: valeur for cle, valeur in asdict(recherche).items()
                               if cle not in ("niveau", "evaluation")}
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(rendre_svg(niveau, titre, parcours, evaluation), encoding="utf-8")
    fichier_json = args.sortie.with_suffix(".json")
    fichier_json.write_text(json.dumps(donnees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(niveau.texte())
    print(f"\n{parcours.raison} États explorés : {parcours.etats_explores}.")
    score = f"{evaluation.score:.1f}/100" if evaluation.score is not None else "non admissible"
    print(f"Score de construction : {score}")
    if recherche is not None:
        print(f"Avant : {recherche.score_initial:.1f}/100 ; "
              f"{len(recherche.historique) - 1} améliorations sur {recherche.budget} propositions.")
    print(f"Colonnes sans sol : {evaluation.mesures.taux_trous:.1%} ; "
          f"changements de hauteur : {evaluation.mesures.taux_changements:.1%} ; "
          f"plus long plateau : {evaluation.mesures.plateau_maximal} colonnes.")
    print(f"\nRendu : {args.sortie}")
    print(f"Données : {fichier_json}")


if __name__ == "__main__":
    main()
