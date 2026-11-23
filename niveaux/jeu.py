"""Exporter des terrains jouables dans un seul fichier HTML hors ligne."""

import json
from pathlib import Path

from niveaux.grille import Niveau
from niveaux.parcours import au_sol, chercher_chemin, successeurs


def preparer_niveau(niveau: Niveau, nom: str, hauteur_saut: int = 2):
    parcours = chercher_chemin(niveau, hauteur_saut)
    if not parcours.accessible:
        raise ValueError("Seuls les niveaux accessibles peuvent être proposés dans le jeu.")
    debut = parcours.chemin[0]
    attente = [debut]
    transitions = {}
    sols = {}
    vus = {debut}
    while attente:
        etat = attente.pop()
        cle = ",".join(map(str, etat))
        suivants = list(successeurs(niveau, etat, hauteur_saut))
        transitions[cle] = suivants
        sols[cle] = etat[2] == 0 and au_sol(niveau, etat[0], etat[1])
        for suivant in suivants:
            if suivant not in vus:
                vus.add(suivant)
                attente.append(suivant)
    fragments = []
    for fraction in (0.25, 0.50, 0.75):
        position = parcours.chemin[int((len(parcours.chemin) - 1) * fraction)][:2]
        if position not in fragments and position not in (debut[:2], parcours.chemin[-1][:2]):
            fragments.append(position)
    return {"nom": nom, "grille": niveau.lignes, "depart": debut,
            "arrivee": parcours.chemin[-1], "chemin": parcours.chemin,
            "transitions": transitions, "sols": sols, "fragments": fragments}


def rendre_jeu(niveaux):
    if not niveaux:
        raise ValueError("Le jeu doit contenir au moins un niveau.")
    assets = Path(__file__).resolve().parent.parent / "jeu"
    html = (assets / "index.html").read_text(encoding="utf-8")
    contenus = {
        "/*STYLE*/": (assets / "style.css").read_text(encoding="utf-8"),
        "/*MOTEUR*/": (assets / "moteur.js").read_text(encoding="utf-8"),
        "/*INTERFACE*/": (assets / "interface.js").read_text(encoding="utf-8"),
        "/*DONNEES*/": json.dumps(niveaux, ensure_ascii=False).replace("<", "\\u003c"),
    }
    for marqueur, contenu in contenus.items():
        html = html.replace(marqueur, contenu)
    return html
