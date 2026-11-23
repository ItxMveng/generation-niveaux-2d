import unittest

from niveaux.evaluation import evaluer, mesurer, profil_surface, proximite
from niveaux.grille import Niveau


class TestEvaluation(unittest.TestCase):
    def test_mesures_calculees_a_la_main(self):
        niveau = Niveau(("........", "........", ".D.....A", "##....##", "##.#####"))
        self.assertEqual(profil_surface(niveau), (3, 3, None, 4, 4, 4, 3, 3))
        mesures = mesurer(niveau)
        self.assertEqual((mesures.colonnes_vides, mesures.nombre_trous, mesures.trou_maximal), (1, 1, 1))
        self.assertEqual((mesures.paires_sol, mesures.changements, mesures.plateau_maximal), (5, 1, 3))
        self.assertEqual(mesures.taux_trous, 1 / 8)
        self.assertEqual(mesures.taux_changements, 1 / 5)

    def test_plateau_interrompu_par_un_trou(self):
        niveau = Niveau(("D......A", "##..#.##"))
        mesures = mesurer(niveau)
        self.assertEqual((mesures.nombre_trous, mesures.trou_maximal, mesures.plateau_maximal), (2, 2, 2))
        self.assertEqual(mesures.changements, 0)

    def test_aucune_paire_sol_et_aucun_sol(self):
        for niveau in (Niveau(("D.A", "#.#")), Niveau(("D.A", "..."))):
            with self.subTest(niveau=niveau):
                mesures = mesurer(niveau)
                self.assertEqual(mesures.taux_changements, 0)
                self.assertEqual(mesures.paires_sol, 0)
                resultat = evaluer(niveau)
                self.assertGreaterEqual(resultat.score_structure, 0)
                self.assertLessEqual(resultat.score_structure, 100)

    def test_score_cible_et_ecarts(self):
        self.assertEqual(proximite(0.1, 0.1), 1)
        self.assertAlmostEqual(proximite(0.05, 0.1), 0.5)
        self.assertAlmostEqual(proximite(0.15, 0.1), 0.5)
        self.assertEqual(proximite(0, 0.1), 0)
        self.assertEqual(proximite(0.4, 0.1), 0)

    def test_terrain_plat_accessible_score_nul(self):
        resultat = evaluer(Niveau(("D...A", "#####")))
        self.assertTrue(resultat.parcours.accessible)
        self.assertEqual(resultat.score, 0)

    def test_score_pondere(self):
        niveau = Niveau(("........", "........", ".D.....A", "##....##", "##.#####"))
        resultat = evaluer(niveau)
        attendu = 100 * (0.35 * 0.75 + 0.35 + 0.30 * (1 - (3 / 8 - 0.30) / 0.70))
        self.assertTrue(resultat.parcours.accessible)
        self.assertAlmostEqual(resultat.score, attendu)

    def test_inaccessible_sans_score_final(self):
        niveau = Niveau(("........", "........", ".D.....A", "##....##", "##.#####"))
        # Un mur au-dessus du trou coupe toutes les traversées.
        bloque = Niveau(tuple(ligne[:2] + "#" + ligne[3:] for ligne in niveau.lignes))
        resultat = evaluer(bloque)
        self.assertFalse(resultat.parcours.accessible)
        self.assertIsNone(resultat.score)
        self.assertGreater(resultat.score_structure, 0)

    def test_surface_des_plateformes(self):
        niveau = Niveau(("D.A", "#.#", "...", "###"))
        self.assertEqual(profil_surface(niveau), (1, 3, 1))


if __name__ == "__main__":
    unittest.main()
