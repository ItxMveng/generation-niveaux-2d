"use strict";

// Les déplacements autorisés proviennent du validateur Python.
class Partie {
  constructor(niveau) { this.niveau = niveau; this.recommencer(); }
  recommencer() {
    this.etat = [...this.niveau.depart];
    this.gagne = false; this.perdu = false; this.ramasses = new Set(); this.etapes = 0;
    this.actualiser();
  }
  actualiser() {
    this.niveau.fragments.forEach(([x, y], i) => {
      if (x === this.etat[0] && y === this.etat[1]) this.ramasses.add(i);
    });
    this.gagne = this.etat.join() === this.niveau.arrivee.join();
    const cle = this.etat.join();
    this.perdu = !this.gagne && !this.niveau.sols[cle] && this.niveau.transitions[cle].length === 0;
  }
  suivre(suivant) {
    if (this.gagne || this.perdu) return false;
    const autorise = this.niveau.transitions[this.etat.join()].some(e => e.join() === suivant.join());
    if (!autorise) return false;
    this.etat = [...suivant]; this.etapes++; this.actualiser(); return true;
  }
  avancer(direction = 0, saut = false) {
    if (![-1, 0, 1].includes(direction)) throw new Error("Direction invalide");
    if (this.gagne || this.perdu) return false;
    const [x, y] = this.etat, cle = this.etat.join();
    const possibles = this.niveau.transitions[cle];
    let choix;
    if (this.niveau.sols[cle]) {
      if (saut) {
        choix = possibles.find(e => e[0] === x + direction && e[1] === y - 1)
             || possibles.find(e => e[0] === x && e[1] === y - 1);
      } else if (direction) choix = possibles.find(e => e[0] === x + direction && e[1] === y);
    } else {
      choix = possibles.find(e => e[0] === x + direction) || possibles.find(e => e[0] === x);
    }
    return choix ? this.suivre(choix) : false;
  }
}

// Une commande anticipée reste disponible 320 ms ; aucun saut supplémentaire en l'air.
class CommandesSaut {
  constructor() { this.reinitialiser(); }
  reinitialiser() { this.expiration = -1; this.versDroite = false; this.enVol = false; }
  demander(temps, versDroite = false) {
    this.expiration = temps + 320; this.versDroite = versDroite;
  }
  avancer(partie, direction, maintenu, droiteMaintenue, temps) {
    const auSol = Boolean(partie.niveau.sols[partie.etat.join()]);
    if (auSol) this.enVol = false;
    const attente = temps <= this.expiration;
    const saut = auSol && (attente || maintenu || droiteMaintenue);
    const automatique = this.enVol || (saut && (droiteMaintenue || (attente && this.versDroite)));
    const y = partie.etat[1];
    const bouge = partie.avancer(direction || (automatique ? 1 : 0), saut);
    if (saut && bouge && partie.etat[1] < y) {
      this.expiration = -1; this.versDroite = false; this.enVol = automatique;
    }
    if (partie.niveau.sols[partie.etat.join()]) this.enVol = false;
    return bouge;
  }
}

if (typeof module !== "undefined") module.exports = { Partie, CommandesSaut };
