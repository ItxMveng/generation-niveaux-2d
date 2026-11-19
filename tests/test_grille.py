import unittest
import xml.etree.ElementTree as ET

from niveaux.grille import Niveau, niveau_exemple
from niveaux.rendu import rendre_svg


class TestGrille(unittest.TestCase):
    def test_exemple(self):
        niveau = niveau_exemple()
        self.assertEqual((niveau.largeur, niveau.hauteur), (24, 10))
        self.assertEqual(len(niveau.texte().splitlines()), 10)

    def test_grilles_invalides(self):
        for lignes in [(), ("",), ("D.A", "##"), ("DXA",), ("D..",), ("DDA",)]:
            with self.subTest(lignes=lignes), self.assertRaises(ValueError):
                Niveau(lignes)

    def test_svg_et_titre_echappe(self):
        racine = ET.fromstring(rendre_svg(niveau_exemple(), "Test <1> & <2>"))
        self.assertEqual(racine.find("{http://www.w3.org/2000/svg}title").text, "Test <1> & <2>")


if __name__ == "__main__":
    unittest.main()
