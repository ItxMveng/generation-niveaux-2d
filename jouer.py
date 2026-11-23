"""Construire trois terrains et exporter un petit jeu jouable hors ligne."""

import argparse
from pathlib import Path
import webbrowser

from niveaux.generation import Parametres, generer
from niveaux.jeu import preparer_niveau, rendre_jeu
from niveaux.recherche import ameliorer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graines", nargs="+", type=int, default=[42, 17, 7])
    parser.add_argument("--budget", type=int, default=200)
    parser.add_argument("--sortie", type=Path, default=Path("sorties/jeu.html"))
    parser.add_argument("--ouvrir", action="store_true")
    args = parser.parse_args()
    if args.sortie.suffix.lower() != ".html":
        parser.error("La sortie doit être un fichier .html.")
    if not 1 <= len(args.graines) <= 10:
        parser.error("Choisir entre 1 et 10 graines.")
    terrains = []
    noms = ["La clairière", "Les terrasses", "Le dernier sentier"]
    try:
        for i, graine in enumerate(args.graines):
            parametres = Parametres(graine=graine)
            resultat = ameliorer(generer(parametres), parametres, budget=args.budget, graine=0)
            nom = noms[i] if i < len(noms) else f"Sentier {i + 1}"
            terrains.append(preparer_niveau(resultat.niveau, nom))
    except ValueError as erreur:
        parser.error(f"Graine {graine} : {erreur}")
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(rendre_jeu(terrains), encoding="utf-8")
    print(f"Jeu prêt : {args.sortie.resolve()}")
    if args.ouvrir:
        webbrowser.open(args.sortie.resolve().as_uri())


if __name__ == "__main__":
    main()
