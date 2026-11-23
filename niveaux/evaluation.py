"""Mesurer le terrain et calculer un score de construction explicite."""

from dataclasses import dataclass

from niveaux.grille import SOL, Niveau
from niveaux.parcours import Parcours, chercher_chemin

VERSION_SCORE = "construction-v1"
CIBLE_TROUS = 0.10
CIBLE_CHANGEMENTS = 0.20
LIMITE_PLATEAU = 0.30
POIDS = {"trous": 0.35, "changements": 0.35, "plateaux": 0.30}


@dataclass(frozen=True)
class Mesures:
    colonnes_vides: int
    nombre_trous: int
    trou_maximal: int
    paires_sol: int
    changements: int
    plateau_maximal: int
    taux_trous: float
    taux_changements: float


@dataclass(frozen=True)
class Evaluation:
    parcours: Parcours
    mesures: Mesures
    composantes: dict[str, float]
    score_structure: float
    score: float | None


def profil_surface(niveau: Niveau):
    """Première case solide de chaque colonne ; None si la colonne est vide."""
    return tuple(next((y for y, ligne in enumerate(niveau.lignes)
                       if ligne[x] == SOL), None) for x in range(niveau.largeur))


def mesurer(niveau: Niveau):
    profil = profil_surface(niveau)
    colonnes_vides = nombre_trous = trou_maximal = 0
    plateau_maximal = longueur_plateau = longueur_trou = 0
    for x, surface in enumerate(profil):
        if surface is None:
            colonnes_vides += 1
            if longueur_trou == 0:
                nombre_trous += 1
            longueur_trou += 1
            trou_maximal = max(trou_maximal, longueur_trou)
            longueur_plateau = 0
        else:
            longueur_trou = 0
            if x > 0 and profil[x - 1] == surface:
                longueur_plateau += 1
            else:
                longueur_plateau = 1
            plateau_maximal = max(plateau_maximal, longueur_plateau)
    paires = [(a, b) for a, b in zip(profil, profil[1:])
              if a is not None and b is not None]
    changements = sum(a != b for a, b in paires)
    return Mesures(colonnes_vides, nombre_trous, trou_maximal, len(paires),
                   changements, plateau_maximal, colonnes_vides / niveau.largeur,
                   changements / len(paires) if paires else 0.0)


def proximite(valeur: float, cible: float):
    """1 à la cible, 0 dès que l'écart atteint la cible."""
    return max(0.0, 1.0 - abs(valeur - cible) / cible)


def evaluer(niveau: Niveau, hauteur_saut: int = 2):
    mesures = mesurer(niveau)
    parcours = chercher_chemin(niveau, hauteur_saut)
    proportion_plateau = mesures.plateau_maximal / niveau.largeur
    composantes = {
        "trous": proximite(mesures.taux_trous, CIBLE_TROUS),
        "changements": proximite(mesures.taux_changements, CIBLE_CHANGEMENTS),
        "plateaux": max(0.0, 1.0 - max(0.0, proportion_plateau - LIMITE_PLATEAU)
                        / (1.0 - LIMITE_PLATEAU)),
    }
    score_structure = 100 * sum(POIDS[nom] * valeur for nom, valeur in composantes.items())
    # L'accessibilité est obligatoire : une bonne structure ne compense pas un échec.
    score = score_structure if parcours.accessible else None
    return Evaluation(parcours, mesures, composantes, score_structure, score)
