"use strict";
// Usage : node tests/test_moteur.js sorties/jeu.html
const fs = require("node:fs"), assert = require("node:assert/strict");
const { Partie, CommandesSaut } = require("../jeu/moteur.js");
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

// Les aides aux commandes empruntent toujours des transitions du validateur.
const n = niveaux[0], commandes = new CommandesSaut(), p = new Partie(n);
const descente = Object.entries(n.transitions).find(([cle, suivants]) =>
  !n.sols[cle] && suivants.some(e => e[0] === Number(cle.split(",")[0]) && n.sols[e.join()] &&
    n.transitions[e.join()].some(s => s[0] === e[0] && s[1] === e[1]-1)));
assert.ok(descente, "Une descente suivie d'un saut doit être testable");
function avantAtterrissage() {
  p.recommencer(); p.etat=descente[0].split(",").map(Number); p.actualiser(); commandes.reinitialiser();
}
avantAtterrissage();
const hauteurAvant=p.etat[1]; commandes.demander(0);
commandes.avancer(p,0,false,false,145);
assert.ok(p.etat[1]>hauteurAvant, "L'appui anticipé ne crée pas de double saut");
assert.ok(n.sols[p.etat.join()]);
const sol=p.etat[1]; commandes.avancer(p,0,false,false,290);
assert.equal(p.etat[1],sol-1,"L'appui anticipé déclenche le saut à l'atterrissage");
avantAtterrissage(); commandes.demander(0); commandes.avancer(p,0,false,false,400);
const etatExpire=[...p.etat]; commandes.avancer(p,0,false,false,545);
assert.deepEqual(p.etat,etatExpire,"Un appui expiré ne provoque pas un saut tardif");
commandes.avancer(p,0,true,false,690);
assert.equal(p.etat[1],etatExpire[1]-1,"Maintenir saut fonctionne sans nouvel appui");
commandes.reinitialiser(); p.recommencer(); commandes.demander(0,true);
const departX=p.etat[0]; commandes.avancer(p,0,false,false,145);
assert.equal(p.etat[0],departX+1,"Une pression suffit pour sauter vers la droite");
let temps=145, etapes=0;
while(!n.sols[p.etat.join()] && !p.perdu && !p.gagne && etapes++<15) {
  const avant=p.etat.join(); temps+=145; commandes.avancer(p,0,false,false,temps);
  assert.ok(n.transitions[avant].some(e=>e.join()===p.etat.join()));
}
assert.ok(n.sols[p.etat.join()],"Le saut assisté revient au sol");
const apresSaut=[...p.etat]; commandes.avancer(p,0,false,false,temps+145);
assert.deepEqual(p.etat,apresSaut,"L'avance automatique s'arrête à l'atterrissage");
commandes.demander(temps,true); commandes.reinitialiser(); commandes.avancer(p,0,false,false,temps+145);
assert.deepEqual(p.etat,apresSaut,"Pause et reprise effacent une commande en attente");
console.log("Sauts : anticipation, expiration, maintien, saut vers la droite et arrêt à l'atterrissage vérifiés.");
