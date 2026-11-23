"use strict";
// Simulation des événements de l'interface, sans dépendance ni navigateur installé.
const fs = require("node:fs"), vm = require("node:vm"), assert = require("node:assert/strict");
const html = fs.readFileSync(process.argv[2] || "sorties/jeu.html", "utf8");
const data = html.match(/<script id="donnees" type="application\/json">([\s\S]*?)<\/script>/)[1];
const niveaux = JSON.parse(data), elements = new Map(), evenements = {}, observations = [];
let frame, horloge = 1, commandesDessin = 0;
const ctx = new Proxy({}, { get: (_, nom) => nom === "createLinearGradient"
  ? () => ({addColorStop(){}}) : (...args) => {
    assert.ok(args.filter(a=>typeof a==="number").every(Number.isFinite)); commandesDessin++;
  }, set:()=>true });
class Element {
  constructor(id="") {this.classList={toggle(){}};this.id=id;this.children=[];this.style={};this.attrs={};this.textContent="";this.hidden=false;}
  setAttribute(n,v){this.attrs[n]=String(v);}
  append(e){this.children.push(e);}
  focus(){}
  closest(){return null;}
  getBoundingClientRect(){return {width:this.largeur||1100,height:this.hauteur||390};}
  getContext(){return ctx;}
  setPointerCapture(){}
}
const get = id => {
  if(id !== ".marque") assert.ok(html.includes(`id="${id}"`), `Élément absent du HTML : ${id}`);
  if(!elements.has(id))elements.set(id,new Element(id));return elements.get(id);};
get("donnees").textContent=data;get("progression").parentElement=new Element();
const document = {getElementById:get,createElement:()=>new Element(),querySelector:get,body:new Element(),
  addEventListener:(nom,fn)=>{evenements[nom]=fn;},hidden:false};
const window = {addEventListener:(nom,fn)=>{evenements[nom]=fn;}};
const contexte = vm.createContext({document,window,devicePixelRatio:1,matchMedia:()=>({matches:false}),
  ResizeObserver:class {constructor(fn){this.fn=fn;observations.push(fn);} observe(){this.fn();}},
  requestAnimationFrame:fn=>{frame=fn;},console});
vm.runInContext(fs.readFileSync("jeu/moteur.js","utf8")+"\n"+fs.readFileSync("jeu/interface.js","utf8"),contexte);
frame(horloge);
function touche(type,key){evenements[type]({key,repeat:false,target:get("terrain"),preventDefault(){}});}
function pas(){for(let i=0;i<5;i++){horloge+=29;frame(horloge);}}
assert.equal(get("home").hidden,false);
get("choisir").onclick();assert.equal(get("levels").hidden,false);
get("niveaux").children[0].onclick();
assert.equal(get("game").hidden,false);
assert.equal(get("voile").hidden,false);
get("action").onclick();assert.equal(get("voile").hidden,true);
get("pause").onclick();assert.equal(get("voile").hidden,false);
assert.equal(get("titre-voile").textContent,"Le sentier peut attendre.");
get("action").onclick();get("aide").onclick();assert.equal(get("aide").attrs["aria-pressed"],"true");
get("recommencer").onclick();assert.equal(get("essais").textContent,2);
evenements.blur();assert.equal(get("voile").hidden,false);
// Rejouer chaque solution via les vrais gestionnaires clavier et la boucle d'affichage.
for(let i=0;i<niveaux.length;i++) {
  get("niveaux").children[i].onclick();get("action").onclick();
  const n=niveaux[i];
  for(let j=1;j<n.chemin.length;j++) {
    const a=n.chemin[j-1], b=n.chemin[j], dx=b[0]-a[0];
    const key=dx<0?"ArrowLeft":dx>0?"ArrowRight":null;
    if(key)touche("keydown",key);
    if(n.sols[a.join()]&&b[1]<a[1])touche("keydown"," ");
    pas();
    if(key)touche("keyup",key);touche("keyup"," ");
  }
  assert.equal(get("voile").hidden,false);
  assert.equal(get("badge").textContent,"BIEN JOUÉ");
  assert.equal(get("fragments").textContent,`${n.fragments.length} / ${n.fragments.length}`);
  assert.equal(get("progression").parentElement.attrs["aria-valuenow"],"100");
}
get("nav-analysis").onclick();
assert.equal(get("analysis").hidden,false);
assert.equal(get("aSeed").textContent,niveaux[2].analyse.graine);
assert.equal(get("aScore").textContent,niveaux[2].analyse.score.toFixed(1)+" / 100");
assert.ok(get("historyChart").innerHTML.includes("<svg"));
const essaisAvant=get("essais").textContent;
touche("keydown","r");assert.equal(get("essais").textContent,essaisAvant);
get("nav-settings").onclick();get("rythme").value="210";get("rythme").onchange();
get("reducedMotion").checked=true;get("reducedMotion").onchange();
get("largeText").checked=true;get("largeText").onchange();
get("settingsBack").onclick();assert.equal(get("game").hidden,false);
get("terrain").largeur=360;get("terrain").hauteur=330;observations.forEach(fn=>fn());pas();
assert.ok(commandesDessin>100);
console.log("Interface : navigation, analyse exportée, réglages, clavier, trois victoires et dessin à 360 px vérifiés (simulation DOM).");
