import random
import unittest

from niveaux.generation import Parametres, generer


class TestGeneration(unittest.TestCase):
    def test_reproductibilite(self):
        parametres = Parametres(graine=12)
        self.assertEqual(generer(parametres), generer(parametres))
        variantes = {generer(Parametres(graine=i)).lignes for i in range(10)}
        self.assertGreater(len(variantes), 1)

    def test_hasard_global_inchange(self):
        etat = random.getstate()
        generer(Parametres())
        self.assertEqual(random.getstate(), etat)

    def test_parametres_invalides(self):
        for valeurs in [dict(largeur=15), dict(largeur=121), dict(hauteur=7),
                        dict(hauteur=41), dict(trou_max=-1), dict(trou_max=4),
                        dict(graine=1.2), dict(largeur=True)]:
            with self.subTest(valeurs=valeurs), self.assertRaises(ValueError):
                Parametres(**valeurs)

    def test_regles_sur_plusieurs_graines(self):
        for largeur, hauteur in [(16, 8), (40, 12), (120, 40)]:
            for trou_max in range(4):
                for graine in range(50):
                    p = Parametres(largeur, hauteur, graine, trou_max)
                    with self.subTest(parametres=p):
                        niveau = generer(p)
                        self.assertEqual((niveau.largeur, niveau.hauteur), (largeur, hauteur))
                        profil = []
                        trou = 0
                        derniere_surface = None
                        for x in range(largeur):
                            colonne = [ligne[x] for ligne in niveau.lignes]
                            sol = colonne.index("#") if "#" in colonne else None
                            profil.append(sol)
                            if sol is None:
                                trou += 1
                                self.assertLessEqual(trou, trou_max)
                            else:
                                trou = 0
                                self.assertTrue(all(c == "#" for c in colonne[sol:]))
                                self.assertGreaterEqual(sol, hauteur - 5)
                                self.assertLessEqual(sol, hauteur - 2)
                                if derniere_surface is not None:
                                    self.assertLessEqual(abs(sol - derniere_surface), 1)
                                derniere_surface = sol
                            for symbole in ("D", "A"):
                                if symbole in colonne:
                                    self.assertEqual(colonne.index(symbole) + 1, sol)
                        self.assertNotIn(None, profil[:4] + profil[-4:])
                        self.assertEqual(len(set(profil[:4])), 1)
                        self.assertEqual(len(set(profil[-4:])), 1)


if __name__ == "__main__":
    unittest.main()
