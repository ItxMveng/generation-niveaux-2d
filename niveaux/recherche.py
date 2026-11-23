"""Recherche locale : proposer une petite modification et garder les gains."""

from dataclasses import dataclass
import random

from niveaux.evaluation import Evaluation, evaluer, profil_surface
from niveaux.generation import Parametres, niveau_depuis_profil
from niveaux.grille import Niveau


@dataclass(frozen=True)
class Recherche:
    niveau: Niveau
    evaluation: Evaluation
    score_initial: float
    budget: int
    graine: int
    evaluations: int
    invalides: int
    inaccessibles: int
    sans_gain: int
    historique: tuple[tuple[int, float], ...]


def profil_valide(profil, parametres):
    trou = 0
    precedente = None
    for surface in profil:
        if surface is None:
            trou += 1
            if trou > parametres.trou_max:
                return False
        else:
            trou = 0
            if not parametres.hauteur - 5 <= surface <= parametres.hauteur - 2:
                return False
            if precedente is not None and abs(surface - precedente) > 1:
                return False
            precedente = surface
    return True


def proposer_voisin(profil, hasard):
    voisin = list(profil)
    debut = hasard.randrange(4, len(profil) - 4)
    fin = min(debut + hasard.randint(1, 3), len(profil) - 4)
    action = hasard.choice(("monter", "descendre", "creuser", "combler"))
    for x in range(debut, fin):
        if action == "creuser":
            voisin[x] = None
        elif action == "combler" and profil[x] is None:
            # Prendre la surface solide la plus proche à gauche.
            voisin[x] = next(profil[i] for i in range(x - 1, -1, -1) if profil[i] is not None)
        elif action in ("monter", "descendre") and profil[x] is not None:
            voisin[x] += -1 if action == "monter" else 1
    return tuple(voisin)


def ameliorer(niveau: Niveau, parametres: Parametres, hauteur_saut=2, budget=200, graine=0):
    if type(budget) is not int or not 0 <= budget <= 5000:
        raise ValueError("Le budget doit être un entier entre 0 et 5000.")
    if type(graine) is not int:
        raise ValueError("La graine de recherche doit être un entier.")
    if (niveau.largeur, niveau.hauteur) != (parametres.largeur, parametres.hauteur):
        raise ValueError("Les dimensions du niveau et des paramètres doivent correspondre.")
    profil = profil_surface(niveau)
    # La recherche porte uniquement sur les terrains pleins sous leur surface.
    if (any(surface is None for surface in profil[:4] + profil[-4:])
            or len(set(profil[:4])) != 1 or len(set(profil[-4:])) != 1
            or not profil_valide(profil, parametres)
            or niveau_depuis_profil(profil, niveau.hauteur) != niveau):
        raise ValueError("La recherche exige un terrain constructif avec ses extrémités protégées.")
    evaluation = evaluer(niveau, hauteur_saut)
    if evaluation.score is None:
        raise ValueError("Le terrain initial est inaccessible ; la recherche ne le répare pas.")
    initial = evaluation.score
    hasard = random.Random(graine)
    historique = [(0, initial)]
    evaluations = invalides = inaccessibles = sans_gain = 0
    for essai in range(1, budget + 1):
        voisin = proposer_voisin(profil, hasard)
        if voisin == profil or not profil_valide(voisin, parametres):
            invalides += 1
            continue
        candidat = niveau_depuis_profil(voisin, niveau.hauteur)
        resultat = evaluer(candidat, hauteur_saut)
        evaluations += 1
        if resultat.score is None:
            inaccessibles += 1
        elif resultat.score > evaluation.score + 1e-9:
            niveau, profil, evaluation = candidat, voisin, resultat
            historique.append((essai, resultat.score))
        else:
            sans_gain += 1
    return Recherche(niveau, evaluation, initial, budget, graine, evaluations,
                     invalides, inaccessibles, sans_gain, tuple(historique))
