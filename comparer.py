"""Comparer la construction et la recherche locale sur les mêmes graines."""
import argparse
import csv
import json
import platform
from dataclasses import asdict
from itertools import combinations
from pathlib import Path
from statistics import mean, median, pstdev
from time import perf_counter

from niveaux.evaluation import (evaluer, profil_surface, VERSION_SCORE, POIDS,
                                CIBLE_TROUS, CIBLE_CHANGEMENTS, LIMITE_PLATEAU)
from niveaux.generation import Parametres, generer
from niveaux.recherche import ameliorer


def statistiques(valeurs):
    valeurs = [v for v in valeurs if v is not None]
    return {"n": len(valeurs), "moyenne": mean(valeurs) if valeurs else None,
            "mediane": median(valeurs) if valeurs else None,
            "ecart_type": pstdev(valeurs) if valeurs else None,
            "minimum": min(valeurs) if valeurs else None,
            "maximum": max(valeurs) if valeurs else None}


def diversite(profils):
    """Proportion moyenne de colonnes différentes entre deux profils (trous inclus)."""
    distances = [sum(x != y for x, y in zip(a, b)) / len(a)
                 for a, b in combinations(profils, 2)]
    return mean(distances) if distances else None


def comparer(graines, budget=200, graine_recherche=0):
    graines = list(graines)
    if not graines or len(set(graines)) != len(graines):
        raise ValueError("Choisir des graines distinctes, au moins une.")
    if type(budget) is not int or not 0 <= budget <= 5000:
        raise ValueError("Budget attendu entre 0 et 5000.")
    lignes = []
    for graine in graines:
        parametres = Parametres(graine=graine)
        debut = perf_counter()
        niveau = generer(parametres)
        evaluation = evaluer(niveau)
        temps_initial = perf_counter() - debut
        ligne = {"graine": graine, "accessible_avant": evaluation.parcours.accessible,
                 "score_avant": evaluation.score, "profil_avant": profil_surface(niveau),
                 "mesures_avant": asdict(evaluation.mesures), "temps_construction_s": temps_initial}
        if evaluation.score is None:
            # Conserver l'échec : la recherche ne sait pas réparer ce point de départ.
            ligne.update(statut="initial_inaccessible", accessible_apres=False, score_apres=None,
                         gain=None, temps_recherche_s=None, temps_total_s=temps_initial,
                         profil_apres=profil_surface(niveau), mesures_apres=asdict(evaluation.mesures),
                         evaluations=0, invalides=0, inaccessibles=0, sans_gain=0, gains=0, historique=[])
        else:
            debut = perf_counter()
            resultat = ameliorer(niveau, parametres, budget=budget, graine=graine_recherche)
            duree = perf_counter() - debut
            ligne.update(statut="recherche_effectuee", accessible_apres=resultat.evaluation.parcours.accessible,
                         score_apres=resultat.evaluation.score, gain=resultat.evaluation.score-evaluation.score,
                         temps_recherche_s=duree, temps_total_s=temps_initial+duree,
                         profil_apres=profil_surface(resultat.niveau), mesures_apres=asdict(resultat.evaluation.mesures),
                         evaluations=resultat.evaluations, invalides=resultat.invalides,
                         inaccessibles=resultat.inaccessibles, sans_gain=resultat.sans_gain,
                         gains=len(resultat.historique)-1, historique=resultat.historique)
        lignes.append(ligne)
    admissibles = [r for r in lignes if r["accessible_avant"]]
    resume = {"nombre": len(lignes), "accessibles_avant": len(admissibles),
              "accessibles_apres": sum(r["accessible_apres"] for r in lignes),
              "ameliores": sum((r["gain"] or 0) > 1e-9 for r in lignes),
              "scores_avant": statistiques(r["score_avant"] for r in admissibles),
              "scores_apres": statistiques(r["score_apres"] for r in admissibles),
              "gains": statistiques(r["gain"] for r in admissibles),
              "temps_construction_s": statistiques(r["temps_construction_s"] for r in lignes),
              "temps_recherche_s": statistiques(r["temps_recherche_s"] for r in admissibles),
              "temps_total_s": statistiques(r["temps_total_s"] for r in lignes),
              "diversite_avant": diversite([r["profil_avant"] for r in admissibles]),
              "diversite_apres": diversite([r["profil_apres"] for r in admissibles])}
    return {"protocole": {"graines": graines, "largeur": 40, "hauteur": 12, "trou_max": 2,
                         "hauteur_saut": 2, "budget": budget, "graine_recherche": graine_recherche,
                         "score_version": VERSION_SCORE, "poids": POIDS,
                         "cibles": {"trous": CIBLE_TROUS, "changements": CIBLE_CHANGEMENTS, "plateau_max": LIMITE_PLATEAU},
                         "comparaison": "Scores et diversité sur les mêmes départs accessibles ; échecs conservés.",
                         "temps": "Un passage, construction avec évaluation ; recherche inclut sa revalidation initiale.",
                         "python": platform.python_version(), "systeme": platform.platform()},
            "resume": resume, "resultats": lignes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--debut", type=int, default=100)
    parser.add_argument("--nombre", type=int, default=50)
    parser.add_argument("--budget", type=int, default=200)
    parser.add_argument("--graine-recherche", type=int, default=0)
    parser.add_argument("--sortie", type=Path, default=Path("sorties/comparaison"))
    args = parser.parse_args()
    if not 1 <= args.nombre <= 1000:
        parser.error("Le nombre de graines doit être entre 1 et 1000.")
    try:
        resultat = comparer(range(args.debut, args.debut+args.nombre), args.budget, args.graine_recherche)
    except ValueError as erreur:
        parser.error(str(erreur))
    args.sortie.mkdir(parents=True, exist_ok=True)
    (args.sortie / "resultats.json").write_text(json.dumps(resultat, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    champs = [k for k, v in resultat["resultats"][0].items() if not isinstance(v, (tuple, list, dict))]
    with (args.sortie / "resultats.csv").open("w", newline="", encoding="utf-8") as fichier:
        writer = csv.DictWriter(fichier, fieldnames=champs, extrasaction="ignore")
        writer.writeheader(); writer.writerows(resultat["resultats"])
    print(json.dumps(resultat["resume"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
