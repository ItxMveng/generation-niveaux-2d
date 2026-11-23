"""Afficher un niveau dans le terminal et enregistrer son rendu SVG."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from niveaux.generation import Parametres, generer
from niveaux.grille import niveau_exemple
from niveaux.parcours import chercher_chemin
from niveaux.rendu import rendre_svg


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
    args = parser.parse_args()
    if args.sortie.suffix.lower() != ".svg":
        parser.error("Le fichier de sortie doit avoir l'extension .svg.")
    try:
        parametres = Parametres(args.largeur, args.hauteur, args.graine, args.trou_max)
    except ValueError as erreur:
        parser.error(str(erreur))
    niveau = niveau_exemple() if args.exemple else generer(parametres)
    parcours = chercher_chemin(niveau, args.saut)
    titre = "Premier terrain" if args.exemple else f"Terrain · graine {args.graine}"
    donnees = {
        "format_version": 2,
        "methode": "exemple" if args.exemple else "constructive",
        "parametres": None if args.exemple else asdict(parametres),
        "grille": niveau.lignes,
        "validation": {"modele": "deplacement-discret-v1", **asdict(parcours)},
    }
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(rendre_svg(niveau, titre, parcours), encoding="utf-8")
    fichier_json = args.sortie.with_suffix(".json")
    fichier_json.write_text(json.dumps(donnees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(niveau.texte())
    print(f"\n{parcours.raison} États explorés : {parcours.etats_explores}.")
    print(f"\nRendu : {args.sortie}")
    print(f"Données : {fichier_json}")


if __name__ == "__main__":
    main()
