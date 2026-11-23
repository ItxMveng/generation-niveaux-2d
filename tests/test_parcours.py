import unittest
import xml.etree.ElementTree as ET

from niveaux.grille import Niveau
from niveaux.parcours import chercher_chemin, passage_libre, successeurs
from niveaux.rendu import rendre_svg


class TestParcours(unittest.TestCase):
    def test_marche_et_chemin_minimal(self):
        niveau = Niveau((".......", ".D...A.", "#######"))
        resultat = chercher_chemin(niveau)
        self.assertTrue(resultat.accessible)
        self.assertEqual(resultat.chemin, tuple((x, 1, 0) for x in range(1, 6)))

    def test_trou_franchissable(self):
        niveau = Niveau(("........", "........", "........", ".D....A.", "###..###"))
        resultat = chercher_chemin(niveau)
        self.assertTrue(resultat.accessible)
        self.assertTrue(any(y < 3 for _, y, _ in resultat.chemin))

    def test_trou_trop_large_sans_double_saut(self):
        niveau = Niveau(("............", "............", "............",
                         "............", "............",
                         ".D........A.", "###......###"))
        self.assertFalse(chercher_chemin(niveau, 2).accessible)
        self.assertTrue(chercher_chemin(niveau, 4).accessible)

    def test_mur_et_plafond(self):
        mur = Niveau(("...#...", "...#...", ".D.#.A.", "#######"))
        plafond = Niveau(("########", ".D....A.", "###..###"))
        for niveau in (mur, plafond):
            with self.subTest(niveau=niveau):
                resultat = chercher_chemin(niveau)
                self.assertFalse(resultat.accessible)
                self.assertEqual(resultat.chemin, ())

    def test_marqueurs_sans_support(self):
        for niveau in (Niveau(("D.A", "..#")), Niveau(("D.A", "#.."))):
            resultat = chercher_chemin(niveau)
            self.assertFalse(resultat.accessible)
            self.assertEqual(resultat.etats_explores, 0)
            self.assertIn("sans sol", resultat.raison)

    def test_pas_de_traversee_en_diagonale(self):
        niveau = Niveau((".#A", "D..", "###"))
        self.assertFalse(passage_libre(niveau, 0, 1, 1, 0))
        self.assertFalse(passage_libre(niveau, 1, 1, 2, 0))

    def test_chute_et_arret_au_plafond(self):
        niveau = Niveau(("#####", "D...A", "#...#", "....."))
        self.assertEqual(set(successeurs(niveau, (2, 1, 1), 2)), {(2, 1, 0)})
        self.assertEqual(set(successeurs(niveau, (2, 1, 0), 2)),
                         {(1, 2, 0), (2, 2, 0), (3, 2, 0)})
        self.assertEqual(list(successeurs(niveau, (2, 3, 0), 2)), [])

    def test_saut_invalide(self):
        niveau = Niveau(("D.A", "###"))
        for saut in (0, 5, True, 1.5):
            with self.subTest(saut=saut), self.assertRaises(ValueError):
                chercher_chemin(niveau, saut)

    def test_rendu_du_chemin(self):
        niveau = Niveau((".......", ".D...A.", "#######"))
        resultat = chercher_chemin(niveau)
        racine = ET.fromstring(rendre_svg(niveau, parcours=resultat))
        trace = racine.find(".//{http://www.w3.org/2000/svg}polyline")
        self.assertEqual(len(trace.attrib["points"].split()), len(resultat.chemin))
        self.assertIn("Accessible selon le modèle discret", "".join(racine.itertext()))


if __name__ == "__main__":
    unittest.main()
