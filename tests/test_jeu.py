import json
import re
import unittest

from niveaux.generation import Parametres, generer
from niveaux.grille import Niveau
from niveaux.jeu import preparer_niveau, rendre_jeu
from niveaux.parcours import au_sol, successeurs
from niveaux.recherche import ameliorer


class TestJeu(unittest.TestCase):
    def test_transitions_identiques_au_validateur(self):
        niveau = generer(Parametres())
        jeu = preparer_niveau(niveau, "Essai")
        self.assertIn(",".join(map(str, jeu["depart"])), jeu["transitions"])
        for cle, suivants in jeu["transitions"].items():
            etat = tuple(map(int, cle.split(",")))
            self.assertEqual(suivants, list(successeurs(niveau, etat, 2)))
            self.assertEqual(jeu["sols"][cle], etat[2] == 0 and au_sol(niveau, *etat[:2]))
            for suivant in suivants:
                self.assertIn(",".join(map(str, suivant)), jeu["transitions"])

    def test_parcours_et_fragments(self):
        jeu = preparer_niveau(generer(Parametres()), "Essai")
        positions = {e[:2] for e in jeu["chemin"]}
        self.assertEqual(len(jeu["fragments"]), 3)
        self.assertTrue(all(p in positions for p in jeu["fragments"]))
        for a, b in zip(jeu["chemin"], jeu["chemin"][1:]):
            self.assertIn(b, jeu["transitions"][",".join(map(str, a))])

    def test_export_autonome_et_nom_echappe(self):
        jeu = preparer_niveau(generer(Parametres()), "</script><script>danger</script>")
        html = rendre_jeu([jeu])
        donnees = re.search(r'<script id="donnees" type="application/json">(.*?)</script>', html, re.S)[1]
        self.assertNotIn("</script>", donnees)
        self.assertEqual(json.loads(donnees)[0]["nom"], jeu["nom"])
        self.assertNotIn("/*STYLE*/", html)
        self.assertNotIn("/*MOTEUR*/", html)
        self.assertNotIn('src="http', html)

    def test_niveaux_de_la_campagne(self):
        for graine in (42, 17, 7):
            p = Parametres(graine=graine)
            resultat = ameliorer(generer(p), p)
            jeu = preparer_niveau(resultat.niveau, str(graine))
            self.assertEqual(jeu["arrivee"], resultat.evaluation.parcours.chemin[-1])

    def test_refus_jeu_vide_et_niveau_inaccessible(self):
        with self.assertRaises(ValueError):
            rendre_jeu([])
        with self.assertRaises(ValueError):
            preparer_niveau(Niveau(("D#A", "###")), "Bloqué")


if __name__ == "__main__":
    unittest.main()
