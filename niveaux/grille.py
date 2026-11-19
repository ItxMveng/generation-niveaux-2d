"""Un niveau est une grille de caractères, lue de haut en bas."""

from dataclasses import dataclass

VIDE = "."
SOL = "#"
DEPART = "D"
ARRIVEE = "A"


@dataclass(frozen=True)
class Niveau:
    lignes: tuple[str, ...]

    def __post_init__(self):
        if not self.lignes or not self.lignes[0]:
            raise ValueError("La grille ne peut pas être vide.")
        if any(len(ligne) != self.largeur for ligne in self.lignes):
            raise ValueError("Les lignes doivent avoir la même largeur.")
        contenu = "".join(self.lignes)
        if set(contenu) - {VIDE, SOL, DEPART, ARRIVEE}:
            raise ValueError("La grille contient une tuile inconnue.")
        if contenu.count(DEPART) != 1 or contenu.count(ARRIVEE) != 1:
            raise ValueError("Il faut exactement un départ et une arrivée.")

    @property
    def largeur(self):
        return len(self.lignes[0])

    @property
    def hauteur(self):
        return len(self.lignes)

    def texte(self):
        return "\n".join(self.lignes)


def niveau_exemple():
    """Petit niveau fixe pour vérifier la représentation et l'affichage."""
    return Niveau((
        "........................",
        "........................",
        "........................",
        "........................",
        "........................",
        "..............####......",
        ".......###..............",
        "..D..................A..",
        "######...###############",
        "######...###############",
    ))
