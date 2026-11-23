"""Recherche de chemin avec marche, saut et chute sur une grille discrète."""

from collections import deque
from dataclasses import dataclass

from niveaux.grille import ARRIVEE, DEPART, SOL, Niveau

# x, y et nombre de cases de montée restantes.
Etat = tuple[int, int, int]


@dataclass(frozen=True)
class Parcours:
    accessible: bool
    chemin: tuple[Etat, ...]
    etats_explores: int
    hauteur_saut: int
    raison: str


def case_libre(niveau: Niveau, x: int, y: int):
    return (0 <= x < niveau.largeur and 0 <= y < niveau.hauteur
            and niveau.lignes[y][x] != SOL)


def au_sol(niveau: Niveau, x: int, y: int):
    return (case_libre(niveau, x, y) and y + 1 < niveau.hauteur
            and niveau.lignes[y + 1][x] == SOL)


def passage_libre(niveau: Niveau, x: int, y: int, nx: int, ny: int):
    """Refuser aussi les diagonales qui coupent le coin d'un bloc."""
    return (case_libre(niveau, nx, ny)
            and case_libre(niveau, x, ny)
            and case_libre(niveau, nx, y))


def successeurs(niveau: Niveau, etat: Etat, hauteur_saut: int):
    x, y, montee = etat
    if montee > 0:
        if not case_libre(niveau, x, y - 1):
            # Un plafond arrête la montée ; la chute commence au prochain pas.
            yield (x, y, 0)
        else:
            for dx in (-1, 0, 1):
                if passage_libre(niveau, x, y, x + dx, y - 1):
                    yield (x + dx, y - 1, montee - 1)
    elif au_sol(niveau, x, y):
        for dx in (-1, 1):
            if case_libre(niveau, x + dx, y):
                yield (x + dx, y, 0)
        for dx in (-1, 0, 1):
            if passage_libre(niveau, x, y, x + dx, y - 1):
                yield (x + dx, y - 1, hauteur_saut - 1)
    else:
        # Pas de vol stationnaire ni de nouveau saut en l'air.
        for dx in (-1, 0, 1):
            if passage_libre(niveau, x, y, x + dx, y + 1):
                yield (x + dx, y + 1, 0)


def chercher_chemin(niveau: Niveau, hauteur_saut: int = 2):
    """Parcours en largeur : un chemin minimal en nombre de transitions."""
    if type(hauteur_saut) is not int or not 1 <= hauteur_saut <= 4:
        raise ValueError("La hauteur de saut doit être comprise entre 1 et 4.")
    positions = {
        tuile: (x, y)
        for y, ligne in enumerate(niveau.lignes)
        for x, tuile in enumerate(ligne)
        if tuile in (DEPART, ARRIVEE)
    }
    depart, arrivee = positions[DEPART], positions[ARRIVEE]
    for nom, position in (("Départ", depart), ("Arrivée", arrivee)):
        if not au_sol(niveau, *position):
            return Parcours(False, (), 0, hauteur_saut, f"{nom} sans sol sous les pieds.")

    debut = (*depart, 0)
    attente = deque([debut])
    parents = {debut: None}
    explores = 0
    while attente:
        etat = attente.popleft()
        explores += 1
        if etat == (*arrivee, 0):
            chemin = []
            courant = etat
            while courant is not None:
                chemin.append(courant)
                courant = parents[courant]
            return Parcours(True, tuple(reversed(chemin)), explores, hauteur_saut,
                            "Arrivée atteinte selon le modèle discret.")
        for suivant in successeurs(niveau, etat, hauteur_saut):
            if suivant not in parents:
                parents[suivant] = etat
                attente.append(suivant)
    return Parcours(False, (), explores, hauteur_saut,
                    "Aucun chemin selon le modèle discret.")
