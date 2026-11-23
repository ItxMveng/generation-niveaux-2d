"use strict";
// Usage : node tests/test_moteur.js sorties/jeu.html
const fs = require("node:fs"), assert = require("node:assert/strict");
const { Partie } = require("../jeu/moteur.js");
const html = fs.readFileSync(process.argv[2] || "sorties/jeu.html", "utf8");
const niveaux = JSON.parse(html.match(/<script id="donnees" type="application\/json">([\s\S]*?)<\/script>/)[1]);
let mouvements = 0;
for (const niveau of niveaux) {
  const partie = new Partie(niveau);
  // Rejouer la solution au moyen des commandes humaines, pas par téléportation.
  for (const suivant of niveau.chemin.slice(1)) {
    const [x,y] = partie.etat;
    const saut = niveau.sols[partie.etat.join()] && suivant[1] < y;
    assert.ok(partie.avancer(suivant[0]-x, saut));
    assert.deepEqual(partie.etat, suivant); mouvements++;
  }
  assert.ok(partie.gagne); assert.equal(partie.ramasses.size,niveau.fragments.length);
  assert.equal(partie.avancer(1),false);
  partie.recommencer(); assert.deepEqual(partie.etat,niveau.depart);
  assert.equal(partie.ramasses.size,0); assert.equal(partie.gagne,false);
  assert.equal(partie.suivre(niveau.arrivee),false);
  assert.throws(()=>partie.avancer(9));
  // Chaque arête du modèle doit être déclenchable par une commande.
  for(const [cle,suivants] of Object.entries(niveau.transitions)) {
    if(cle===niveau.arrivee.join())continue;
    const etat=cle.split(",").map(Number);
    for(const suivant of suivants) {
      partie.etat=[...etat];partie.gagne=false;partie.perdu=false;
      assert.ok(partie.avancer(suivant[0]-etat[0],niveau.sols[cle]&&suivant[1]<etat[1]));
      assert.deepEqual(partie.etat,suivant);mouvements++;
    }
    if(!suivants.length && !niveau.sols[cle]) {
      partie.etat=[...etat];partie.actualiser();assert.ok(partie.perdu);
      partie.recommencer();assert.equal(partie.perdu,false);
    }
  }
}
console.log(`${niveaux.length} terrains : victoire, éclats, chutes, reprise et ${mouvements} transitions vérifiés.`);
