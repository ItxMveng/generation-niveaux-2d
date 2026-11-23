"use strict";
(() => {
  const niveaux = JSON.parse(document.getElementById("donnees").textContent);
  const $ = id => document.getElementById(id);
  const canvas = $("terrain"), ctx = canvas.getContext("2d");
  const touches = new Set(), termines = new Set();
  let index = 0, partie, precedent, ecoule = 0, essais = 1, joue = false, aide = false;
  const commandeSaut = new CommandesSaut();
  let phase = 0, derniere = 0;
  let camera = 0, largeur = 1000, hauteur = 390, actionVoile = () => {};
  let page = "home", pas = 145, reduit = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const formatTemps = ms => `${Math.floor(ms / 60000)}:${String(Math.floor(ms / 1000) % 60).padStart(2, "0")}`;

  function message(texte) { $("message").textContent = texte; }
  function voile(badge, titre, texte, bouton, action) {
    joue = false; touches.clear(); commandeSaut.reinitialiser();
    $("badge").textContent = badge; $("titre-voile").textContent = titre;
    $("texte-voile").textContent = texte; $("action").textContent = bouton;
    $("voile").hidden = false; actionVoile = action;
    $("bilan").hidden = badge !== "BIEN JOUÉ";
    $("bilan-fragments").textContent = $("fragments").textContent;
    $("bilan-temps").textContent = formatTemps(ecoule);
    $("bilan-essais").textContent = essais;
    if (page === "game") $("action").focus();
  }
  function commencer() { $("voile").hidden = true; joue = true; phase = 0; canvas.focus({preventScroll:true}); }
  function charger(i) {
    afficherPage("game");
    index = i; partie = new Partie(niveaux[i]); precedent = [...partie.etat]; camera = 0;
    ecoule = 0; essais = 1; phase = 0;
    $("numero").textContent = `TRAVERSÉE ${i + 1} / ${niveaux.length}`;
    $("nom").textContent = niveaux[i].nom;
    actualiser();
    voile("À TOI DE JOUER", niveaux[i].nom,
      "Rejoins le drapeau orange. E : sauter vers la droite avec une seule touche. Flèches et Espace : commandes classiques.",
      "Commencer la traversée →", commencer);
  }
  function recommencer() {
    touches.clear(); commandeSaut.reinitialiser();
    essais++; partie.recommencer(); precedent = [...partie.etat]; phase = 0;
    actualiser(); commencer();
    message("Nouveau départ. Observe les trous et prépare ton saut avant le bord.");
  }
  function actualiser() {
    $("fragments").textContent = `${partie.ramasses.size} / ${partie.niveau.fragments.length}`;
    $("essais").textContent = essais;
    const taux = Math.max(0, Math.min(100, 100 * (partie.etat[0] - partie.niveau.depart[0]) /
      Math.max(1, partie.niveau.arrivee[0] - partie.niveau.depart[0])));
    $("progression").style.width = `${taux}%`;
    $("progression").parentElement.setAttribute("aria-valuenow", Math.round(taux));
    [...$("niveaux").children].forEach((b, i) => {
      b.children[1].children[0].textContent = `${termines.has(i) ? "✓ " : ""}${niveaux[i].nom}`;
      b.setAttribute("aria-current", i === index ? "true" : "false");
    });
  }
  function pause() {
    if (joue) voile("PETITE PAUSE", "Le sentier peut attendre.", "Reprends quand tu es prêt.", "Reprendre →", commencer);
  }
  $("action").onclick = () => actionVoile();
  $("recommencer").onclick = recommencer;
  $("pause").onclick = pause;
  $("aide").onclick = () => {
    aide = !aide; $("aide").setAttribute("aria-pressed", aide);
    $("aide").textContent = aide ? "Masquer le chemin" : "Afficher le chemin";
    message(aide ? "La ligne montre un passage possible. Tu gardes le contrôle du personnage." : "À toi de trouver ta route.");
  };
  function afficherPage(destination) {
    if (page === "game" && destination !== "game") pause();
    page = destination; touches.clear(); commandeSaut.reinitialiser();
    for (const nom of ["home", "levels", "game", "analysis", "help", "settings"]) {
      $(nom).hidden = nom !== page; $(nom).classList.toggle("active", nom === page);
      if (nom !== "game") $("nav-" + nom).setAttribute("aria-current", nom === page ? "page" : "false");
    }
    if (page === "analysis") analyser();
    if (page === "game") redimensionner();
    (page === "game" && !$("voile").hidden ? $("action") : $(page)).focus({preventScroll:true});
  }
  function analyser() {
    const n = niveaux[index], a = n.analyse;
    $("analyse-nom").textContent = n.nom;
    if (!a) { $("aRecherche").textContent = "Analyse indisponible pour cet export."; return; }
    const valeurs = {aSeed:a.graine,aWidth:n.grille[0].length,aHoles:a.mesures.colonnes_vides,
      aHeight:a.mesures.changements,aFlat:a.mesures.plateau_maximal,aAccessible:"Oui",
      aBefore:a.score_initial.toFixed(1)+" / 100",aScore:a.score.toFixed(1)+" / 100"};
    for (const [id,v] of Object.entries(valeurs)) $(id).textContent = v;
    $("aMeter").style.width = a.score + "%";
    $("aRecherche").textContent = `${a.budget} propositions, ${a.evaluations} évaluations et ${a.historique.length-1} améliorations acceptées.`;
    $("analysisChart").innerHTML = miniature(n);
    const x = t => 35 + 345*t/Math.max(1,a.budget), y = v => 160-1.4*v;
    let trace = `M ${x(0)} ${y(a.score_initial)}`;
    for(const [t,v] of a.historique.slice(1)) trace += ` H ${x(t)} V ${y(v)}`;
    trace += ` H ${x(a.budget)}`;
    $("historyChart").innerHTML = `<svg viewBox="0 0 400 190" role="img" aria-label="Évolution du score de construction"><path d="M35 20V160H380" fill="none" stroke="#95aaa4"/><path d="${trace}" fill="none" stroke="#edc575" stroke-width="3"/><g fill="#b8c9c2" font-size="12"><text x="3" y="25">100</text><text x="18" y="164">0</text><text x="35" y="180">0</text><text x="350" y="180">${a.budget}</text></g></svg>`;
  }
  function miniature(n) {
    const w=n.grille[0].length, h=n.grille.length;
    let formes = "";
    n.grille.forEach((ligne,y)=>[...ligne].forEach((c,x)=>{
      if(c==="#") formes += `<rect x="${x}" y="${y}" width="1" height="1" fill="${y===0||n.grille[y-1][x]!=="#"?"#85b88a":"#385c50"}"/>`;
      if(c==="D"||c==="A") formes += `<rect x="${x}" y="${y}" width="1" height="1" fill="${c==="D"?"#e8e7c5":"#edb361"}"/>`;
    }));
    return `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="Aperçu du terrain"><rect width="${w}" height="${h}" fill="#173742"/>${formes}</svg>`;
  }
  document.querySelector(".marque").onclick = e => { e.preventDefault(); afficherPage("home"); };
  for(const nom of ["home","levels","analysis","help","settings"]) $("nav-"+nom).onclick=()=>afficherPage(nom);
  for(const id of ["choisir","retour-niveaux","helpPlay"]) $(id).onclick=()=>afficherPage("levels");
  for(const id of ["analysisBack","settingsBack"]) $(id).onclick=()=>afficherPage("game");
  $("voir-analyse").onclick=()=>afficherPage("analysis");
  $("startAdventure").onclick=()=>{charger(0);commencer();};
  $("nombre-niveaux").textContent = `${niveaux.length} niveaux`;
  $("rythme").onchange=()=>{pas=Number($("rythme").value)===210?210:145;phase=0;};
  $("reducedMotion").checked=reduit;
  $("reducedMotion").onchange=()=>{reduit=$("reducedMotion").checked;document.body.classList.toggle("reducedMotion",reduit);};
  $("largeText").onchange=()=>document.body.classList.toggle("largeText",$("largeText").checked);
  window.addEventListener("keydown", e => {
    if (page !== "game" || e.target.closest("input,select,textarea")) return;
    if (e.key === "Tab" && !$("voile").hidden) {
      e.preventDefault(); (document.activeElement === $("action") ? $("retour-niveaux") : $("action")).focus(); return;
    }
    if (e.target.closest("button,a") && [" ", "Enter"].includes(e.key)) return;
    const k = e.key.toLowerCase();
    if (["arrowleft","arrowright","arrowup"," ","q","a","d","r","escape","z","p","e"].includes(k)) e.preventDefault();
    if (k === "r" && !e.repeat) return recommencer();
    if ((k === "escape" || k === "p") && !e.repeat) return pause();
    if (!joue) return;
    touches.add(k);
    if ([" ","arrowup","z","e"].includes(k) && !e.repeat) commandeSaut.demander(ecoule, k === "e");
  });
  window.addEventListener("keyup", e => touches.delete(e.key.toLowerCase()));
  window.addEventListener("blur", () => { touches.clear(); pause(); });
  document.addEventListener("visibilitychange", () => { if (document.hidden) pause(); });
  for (const [id, touche] of [["gauche","arrowleft"],["droite","arrowright"],["sauter"," "],["sauter-droite","e"]]) {
    const bouton = $(id);
    bouton.onpointerdown = e => {
      e.preventDefault(); bouton.setPointerCapture(e.pointerId);
      if (!joue) return;
      touches.add(touche); if (touche === " " || touche === "e") commandeSaut.demander(ecoule, touche === "e");
    };
    bouton.onpointerup = bouton.onpointercancel = bouton.onlostpointercapture = () => touches.delete(touche);
  }
  function redimensionner() {
    const r = canvas.getBoundingClientRect(); if (!r.width || !r.height) return; largeur = r.width; hauteur = r.height;
    const dpr = Math.min(devicePixelRatio || 1, 2); canvas.width = Math.round(largeur*dpr); canvas.height = Math.round(hauteur*dpr);
    ctx.setTransform(dpr,0,0,dpr,0,0);
  }
  new ResizeObserver(redimensionner).observe(canvas);
  function polygone(points, couleur) {
    ctx.fillStyle=couleur; ctx.beginPath(); points.forEach(([x,y],i) => i ? ctx.lineTo(x,y) : ctx.moveTo(x,y)); ctx.closePath(); ctx.fill();
  }
  function dessiner(t) {
    const grille = partie.niveau.grille, h = grille.length, w = grille[0].length;
    const tuile = Math.min(38, (hauteur-58)/h), oy = hauteur - h*tuile - 20;
    const alpha = reduit || !joue ? 1 : Math.min(1, phase/pas);
    const px = precedent[0] + (partie.etat[0]-precedent[0])*alpha;
    const py = precedent[1] + (partie.etat[1]-precedent[1])*alpha;
    const cible = Math.max(0, Math.min(w*tuile - largeur + 40, px*tuile - largeur*.35));
    camera += (cible-camera)*(reduit ? 1 : .15);
    const ox = 20-camera;
    const fond = ctx.createLinearGradient(0,0,0,hauteur); fond.addColorStop(0,"#d6ebe4"); fond.addColorStop(1,"#edf0d7");
    ctx.fillStyle=fond; ctx.fillRect(0,0,largeur,hauteur);
    ctx.fillStyle="#faf3cd";ctx.beginPath();ctx.arc(largeur*.78-camera*.08,70,32,0,Math.PI*2);ctx.fill();
    for(let i=-1;i<7;i++) {
      const x=i*260-camera*.23;
      polygone([[x,hauteur],[x+100,hauteur*.35],[x+270,hauteur]],"#bdd6bf");
      polygone([[x+100,hauteur],[x+210,hauteur*.48],[x+360,hauteur]],"#cbdcc3");
    }
    if(aide) {
      ctx.strokeStyle="#4b8d8190";ctx.lineWidth=2;ctx.setLineDash([4,6]);ctx.beginPath();
      partie.niveau.chemin.forEach(([x,y],i)=>i?ctx.lineTo(ox+(x+.5)*tuile,oy+(y+.5)*tuile):ctx.moveTo(ox+(x+.5)*tuile,oy+(y+.5)*tuile));ctx.stroke();ctx.setLineDash([]);
    }
    grille.forEach((ligne,y)=>[...ligne].forEach((c,x)=>{
      const xx=ox+x*tuile, yy=oy+y*tuile;
      if(xx < -tuile || xx > largeur) return;
      if(c==="#") {
        ctx.fillStyle=(x+y)%2?"#967c5a":"#9e825f";ctx.fillRect(xx,yy,tuile+.4,tuile+.4);
        ctx.strokeStyle="#816b4e33";ctx.strokeRect(xx+.5,yy+.5,tuile-1,tuile-1);
        if(y===0 || grille[y-1][x]!=="#") {
          ctx.fillStyle="#4d7954";ctx.fillRect(xx,yy,tuile+.4,5);ctx.fillStyle="#6f945e";ctx.fillRect(xx,yy,tuile+.4,2);
          if(x%3===0) {ctx.strokeStyle="#759a60";ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(xx+6,yy);ctx.lineTo(xx+4,yy-5);ctx.moveTo(xx+8,yy);ctx.lineTo(xx+10,yy-7);ctx.stroke();}
        }
      } else if(c==="A") {
        ctx.fillStyle="#567655";ctx.fillRect(xx+tuile*.35,yy-8,3,tuile+8);
        polygone([[xx+tuile*.35+3,yy-8],[xx+tuile*.35+23,yy-2],[xx+tuile*.35+3,yy+7]],"#d98143");
      }
    }));
    partie.niveau.fragments.forEach(([x,y],i)=>{
      if(partie.ramasses.has(i))return;
      const xx=ox+(x+.5)*tuile, yy=oy+(y+.5)*tuile+(reduit?0:Math.sin(t/450+i)*2);
      ctx.fillStyle="#f7e6a077";ctx.beginPath();ctx.arc(xx,yy,13,0,Math.PI*2);ctx.fill();
      polygone([[xx,yy-7],[xx+5,yy],[xx,yy+7],[xx-5,yy]],"#bd8b2b");
      polygone([[xx,yy-5],[xx+2,yy],[xx,yy+3],[xx-2,yy]],"#ffe4a0");
    });
    const x=ox+px*tuile, y=oy+py*tuile, s=tuile/28;
    ctx.save();ctx.translate(x,y);ctx.scale(s,s);
    ctx.fillStyle="#365945";ctx.fillRect(7,23,5,4);ctx.fillRect(17,23,5,4);
    ctx.fillStyle="#3b8178";ctx.beginPath();ctx.roundRect(6,3,17,21,5);ctx.fill();
    ctx.fillStyle="#f4e6bb";ctx.beginPath();ctx.roundRect(8,7,13,8,3);ctx.fill();
    ctx.fillStyle="#314b3e";ctx.fillRect(16,9,2,3);ctx.fillStyle="#d88b48";ctx.fillRect(5,16,19,3);ctx.fillRect(3,17,5,6);
    ctx.restore();
  }
  function boucle(t) {
    const dt=Math.min(60,t-(derniere||t));derniere=t;
    if(joue) {
      ecoule+=dt;phase+=dt;
      if(phase>=pas) {
        phase-=pas;precedent=[...partie.etat];
        const gauche=touches.has("arrowleft")||touches.has("q")||touches.has("a");
        const droite=touches.has("arrowright")||touches.has("d");
        commandeSaut.avancer(partie, Number(droite)-Number(gauche),
          touches.has(" ") || touches.has("arrowup") || touches.has("z"), touches.has("e"), ecoule);
        actualiser();
        if(partie.perdu) {
          voile("ON RÉESSAIE ?","Un peu trop loin…","Le sentier est toujours là. Repars du début et essaie un autre saut.","Recommencer →",recommencer);
          message("Tu es tombé. Le bouton Afficher le chemin peut t’aider.");
        } else if(partie.gagne) {
          termines.add(index);actualiser();
          const dernier=index===niveaux.length-1;
          voile("BIEN JOUÉ",dernier?"Au bout des sentiers.":"Passage réussi !",
            `${partie.ramasses.size} éclats sur ${partie.niveau.fragments.length} · ${formatTemps(ecoule)} · ${essais} essai${essais>1?"s":""}.`,
            dernier?"Rejouer la traversée →":"Traversée suivante →",dernier?recommencer:()=>{charger(index+1);commencer();});
          message("Tu peux rejouer pour récupérer tous les éclats, ou choisir une autre traversée.");
        }
      }
    }
    $("temps").textContent=formatTemps(ecoule);if(page === "game") dessiner(t);requestAnimationFrame(boucle);
  }
  niveaux.forEach((n, i) => {
    const b=document.createElement("button");b.className="level";
    const apercu=document.createElement("span");apercu.className="thumb";apercu.innerHTML=miniature(n);
    const titre=document.createElement("strong");titre.textContent=n.nom;
    const detail=document.createElement("small");detail.textContent=`${n.grille[0].length} colonnes · ${n.fragments.length} éclats`;
    const contenu=document.createElement("span");contenu.className="detail";contenu.append(titre);contenu.append(detail);
    b.append(apercu);b.append(contenu);
    b.onclick=()=>charger(i);$("niveaux").append(b);
  });
  charger(0);afficherPage("home");redimensionner();requestAnimationFrame(boucle);
})();
