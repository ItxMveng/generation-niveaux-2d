import random
import unittest

from niveaux.evaluation import evaluer, profil_surface
from niveaux.generation import Parametres, generer
from niveaux.grille import niveau_exemple
from niveaux.recherche import ameliorer, proposer_voisin, profil_valide


class TestRecherche(unittest.TestCase):
    def setUp(self):
        self.parametres = Parametres()
        self.niveau = generer(self.parametres)

    def test_gain_et_regles(self):
        resultat = ameliorer(self.niveau, self.parametres)
        self.assertGreater(resultat.evaluation.score, resultat.score_initial)
        self.assertTrue(resultat.evaluation.parcours.accessible)
        self.assertTrue(profil_valide(profil_surface(resultat.niveau), self.parametres))
        initial, final = profil_surface(self.niveau), profil_surface(resultat.niveau)
        self.assertEqual(initial[:4] + initial[-4:], final[:4] + final[-4:])
        scores = [score for _, score in resultat.historique]
        self.assertTrue(all(b > a for a, b in zip(scores, scores[1:])))
        self.assertEqual(resultat.evaluations + resultat.invalides, resultat.budget)
        self.assertEqual(resultat.evaluations,
                         resultat.inaccessibles + resultat.sans_gain + len(scores) - 1)
        self.assertEqual(resultat.evaluation, evaluer(resultat.niveau))

    def test_reproductibilite_et_hasard_global(self):
        etat = random.getstate()
        a = ameliorer(self.niveau, self.parametres, budget=30, graine=8)
        b = ameliorer(self.niveau, self.parametres, budget=30, graine=8)
        self.assertEqual(a, b)
        self.assertEqual(random.getstate(), etat)

    def test_budget_nul(self):
        resultat = ameliorer(self.niveau, self.parametres, budget=0)
        self.assertEqual(resultat.niveau, self.niveau)
        self.assertEqual(len(resultat.historique), 1)
        self.assertEqual(resultat.evaluations, 0)

    def test_refus_terrain_inaccessible(self):
        with self.assertRaisesRegex(ValueError, "inaccessible"):
            ameliorer(self.niveau, self.parametres, hauteur_saut=1)

    def test_refus_entrees_invalides(self):
        for budget in (-1, 5001, True):
            with self.subTest(budget=budget), self.assertRaises(ValueError):
                ameliorer(self.niveau, self.parametres, budget=budget)
        with self.assertRaises(ValueError):
            ameliorer(niveau_exemple(), Parametres(largeur=24, hauteur=10))

    def test_voisinage_local(self):
        profil = profil_surface(self.niveau)
        hasard = random.Random(4)
        for _ in range(100):
            voisin = proposer_voisin(profil, hasard)
            changes = [i for i, (a, b) in enumerate(zip(profil, voisin)) if a != b]
            self.assertLessEqual(len(changes), 3)
            self.assertTrue(all(4 <= x < len(profil) - 4 for x in changes))


if __name__ == "__main__":
    unittest.main()
