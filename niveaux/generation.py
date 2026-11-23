"""Construire un terrain par plateaux, séparés parfois par des trous."""

from dataclasses import dataclass
import random

from niveaux.grille import ARRIVEE, DEPART, SOL, VIDE, Niveau


@dataclass(frozen=True)
class Parametres:
    largeur: int = 40
    hauteur: int = 12
    graine: int = 42
    trou_max: int = 2

    def __post_init__(self):
        for valeur in (self.largeur, self.hauteur, self.graine, self.trou_max):
            if type(valeur) is not int:
                raise ValueError("Les paramètres doivent être des entiers.")
        if not 16 <= self.largeur <= 120:
            raise ValueError("La largeur doit être comprise entre 16 et 120.")
        if not 8 <= self.hauteur <= 40:
            raise ValueError("La hauteur doit être comprise entre 8 et 40.")
        if not 0 <= self.trou_max <= 3:
            raise ValueError("La taille maximale des trous doit être comprise entre 0 et 3.")


def generer(parametres: Parametres):
    hasard = random.Random(parametres.graine)
    largeur, hauteur = parametres.largeur, parametres.hauteur
    surface = hauteur - 3
    # Chaque colonne contient la hauteur du sol, ou None pour un trou.
    profil = [surface] * largeur
    x = 4
    fin = largeur - 4
    while x < fin:
        surface += hasard.choice((-1, 0, 1))
        surface = max(hauteur - 5, min(hauteur - 2, surface))
        longueur = min(hasard.randint(3, 6), fin - x)
        for colonne in range(x, x + longueur):
            profil[colonne] = surface
        x += longueur

        # Garder au moins trois colonnes après un trou avant la zone d'arrivée.
        if parametres.trou_max and hasard.random() < 0.35:
            trou = hasard.randint(1, parametres.trou_max)
            if x + trou + 3 <= fin:
                for colonne in range(x, x + trou):
                    profil[colonne] = None
                x += trou

    profil[fin:] = [surface] * 4
    return niveau_depuis_profil(profil, hauteur)


def niveau_depuis_profil(profil, hauteur):
    """Transformer un profil avec extrémités solides en grille de terrain."""
    largeur = len(profil)
    grille = [[VIDE] * largeur for _ in range(hauteur)]
    for colonne, sol in enumerate(profil):
        if sol is not None:
            for ligne in range(sol, hauteur):
                grille[ligne][colonne] = SOL
    grille[profil[1] - 1][1] = DEPART
    grille[profil[-2] - 1][-2] = ARRIVEE
    return Niveau(tuple("".join(ligne) for ligne in grille))
