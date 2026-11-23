import unittest
from unittest.mock import patch
from comparer import comparer, diversite, statistiques
from niveaux.grille import niveau_exemple


class ComparaisonTests(unittest.TestCase):
    def test_budget_nul_et_reproductibilite(self):
        a = comparer([100, 101, 102], budget=0)
        b = comparer([100, 101, 102], budget=0)
        for x, y in zip(a['resultats'], b['resultats']):
            self.assertEqual(x['profil_apres'], y['profil_apres'])
            self.assertEqual(x['score_avant'], x['score_apres'])
            self.assertEqual(x['profil_avant'], x['profil_apres'])
        self.assertEqual(a['resume']['ameliores'], 0)

    def test_gains_et_comptage(self):
        for r in comparer([100, 101], budget=15)['resultats']:
            self.assertGreaterEqual(r['gain'], 0)
            self.assertEqual(r['invalides'] + r['evaluations'], 15)
            self.assertEqual(r['gains'] + r['sans_gain'] + r['inaccessibles'], r['evaluations'])

    def test_echec_conserve(self):
        with patch('comparer.generer', return_value=niveau_exemple()):
            r = comparer([0])
        self.assertEqual(r['resume']['nombre'], 1)
        self.assertEqual(r['resume']['accessibles_avant'], 0)
        self.assertIsNone(r['resultats'][0]['score_apres'])
        self.assertIsNone(r['resume']['gains']['moyenne'])

    def test_statistiques_et_diversite(self):
        self.assertEqual(statistiques([None, 2, 4])['moyenne'], 3)
        self.assertEqual(diversite([(1, None), (1, 2)]), .5)
        self.assertIsNone(diversite([(1,)]))
        with self.assertRaises(ValueError):
            comparer([1, 1])
