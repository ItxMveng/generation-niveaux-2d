"""Afficher un niveau dans le terminal et enregistrer son rendu SVG."""

import argparse
from pathlib import Path

from niveaux.grille import niveau_exemple
from niveaux.rendu import rendre_svg


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sortie", type=Path, default=Path("sorties/niveau.svg"))
    args = parser.parse_args()
    niveau = niveau_exemple()
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(rendre_svg(niveau, "Premier terrain"), encoding="utf-8")
    print(niveau.texte())
    print(f"\nRendu : {args.sortie}")


if __name__ == "__main__":
    main()
