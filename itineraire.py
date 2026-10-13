"""Page « Itinéraire découverte » pour generateur.py (étape B : lieux à visiter et restaurants réels)."""
from pathlib import Path

# Adresse de votre Worker Cloudflare
WORKER_URL = "https://itineraire.myhotelcompare.com"

TEMPLATE = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Itinéraire sans autoroute en Europe : visites et coût | MyHotelCompare</title>
<meta name="description" content="Planifiez un trajet sans autoroute en Europe : étapes de conduite, visites, restaurants, hôtels et comparaison du coût avec l'autoroute.">
<link rel="canonical" href="%%SITE_URL%%/itineraire-decouverte.html">
<meta property="og:type" content="website">
<meta property="og:title" content="Itinéraire sans autoroute en Europe : visites et coût">
<meta property="og:description" content="Un trajet par les petites routes, découpé en étapes avec visites, restaurants et hôtels, et comparé au coût de l'autoroute.">
<meta property="og:url" content="%%SITE_URL%%/itineraire-decouverte.html">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
%%STYLE%%
<style>
.it-road{display:inline-block;min-width:36px;text-align:center;padding:0 7px;border-radius:5px;font-weight:800;font-size:.8rem;line-height:22px}
.it-road.N{background:#c8322b;color:#fff}
.it-road.D{background:#f2c230;color:#123443;box-shadow:inset 0 0 0 2px #123443}
.it-form{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;margin:24px 0;align-items:end}
.it-form label{display:block;font-weight:700;color:var(--muted);margin-bottom:6px}
.it-form input,.it-form select{width:100%;padding:11px 12px;border-radius:12px;border:1px solid var(--line);background:#fff;color:var(--text);font-size:.97rem}
.it-msg{padding:12px 16px;border-radius:12px;margin-bottom:18px;font-weight:600}
.it-msg.err{background:#fde8e6;color:#9a2a22}.it-msg.info{background:var(--panel);color:var(--secondary)}
#itRes{display:none}
.it-cmp{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:0 0 14px}
.it-cmp .glass-box.win{border:2px solid var(--success)}
.it-cmp h2{font-size:1.15rem;margin:0 0 10px}
.it-row{display:flex;justify-content:space-between;gap:10px;padding:5px 0;border-bottom:1px solid var(--line)}
.it-row:last-child{border:0}
.it-save{background:var(--success-soft);color:var(--success);border-radius:12px;padding:12px 16px;font-weight:700;margin-bottom:8px}
.it-note{color:var(--muted);font-size:.85rem;margin:0 0 22px}
#itMap{height:380px;border-radius:16px;margin-bottom:22px;box-shadow:var(--shadow)}
.it-tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px}
.it-tab{font:inherit;font-weight:700;cursor:pointer;background:#fff;color:var(--text);border:1px solid var(--line);border-radius:999px;padding:9px 18px}
.it-tab[aria-selected=true]{background:var(--secondary);color:#fff;border-color:var(--secondary)}
.it-tab:focus-visible{outline:3px solid var(--warning);outline-offset:2px}
.it-dayhead{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.it-dayhead h2{margin:0;font-size:1.4rem}
.it-dayhead span{color:var(--muted)}
.it-roads{display:flex;gap:10px 14px;flex-wrap:wrap;margin-bottom:16px;align-items:center}
.it-roads small{color:var(--muted)}
.it-bloc{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px 18px;margin-bottom:14px}
.it-bloc h3{margin:0 0 8px;font-size:1.05rem}
.it-lieux{list-style:none;margin:0;padding:0}
.it-lieu{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:8px 0;border-bottom:1px solid var(--line)}
.it-lieu:last-child{border:0}
.it-lieu small{display:block;color:var(--muted)}
.it-lieu a{font-weight:700;margin-left:12px;white-space:nowrap}
.it-wait{color:var(--muted);margin:0}
.it-budget{margin-bottom:22px}
.it-bt{display:grid;grid-template-columns:1.6fr 1fr 1fr;gap:8px 12px;align-items:center}
.it-bt .fort{font-weight:800;border-top:1px solid var(--line);padding-top:8px}
.it-bt small{color:var(--muted)}
.it-all{margin-bottom:18px}
.it-all p{margin:6px 0 0}
.it-gps{display:flex;gap:10px;flex-wrap:wrap;margin:8px 0 14px}
.it-btn{display:inline-block;padding:10px 16px;border-radius:12px;font-weight:700;text-decoration:none;font-size:.95rem}
.it-btn.g{background:#1a73e8;color:#fff}
.it-btn.w{background:#33ccff;color:#06364a}
.it-btn:hover{filter:brightness(.95)}
.it-btn:focus-visible{outline:3px solid var(--warning);outline-offset:2px}
@media (max-width:620px){.it-cmp{grid-template-columns:1fr}.it-lieu{align-items:flex-start;flex-direction:column;gap:4px}.it-lieu a{margin:0 12px 0 0}}
</style>
</head>
<body><div class="container">
%%MENU%%
<div class="hero-banner">
  <div class="hero-badges"><span>🛣️ Sans autoroute</span><span>🌍 Toute l'Europe</span><span>📍 Visites et restaurants</span><span>💶 Coût comparé à l'autoroute</span></div>
  <h1 style="color:#fff;margin:0 0 10px;font-size:clamp(1.8rem,4vw,2.8rem)">Voyagez par les petites routes</h1>
  <p style="margin:0;max-width:700px;line-height:1.7;color:#effcff">Indiquez votre départ et votre arrivée en Europe : nous calculons un trajet par les nationales et départementales, découpé en étapes avec des lieux à visiter, des restaurants et une nuit, et nous le comparons à l'autoroute.</p>
</div>

<form id="itForm" class="glass-box it-form">
  <div><label for="itDep">Départ</label><input id="itDep" list="itDl1" autocomplete="off" required placeholder="Strasbourg"><datalist id="itDl1"></datalist></div>
  <div><label for="itArr">Arrivée</label><input id="itArr" list="itDl2" autocomplete="off" required placeholder="Avignon"><datalist id="itDl2"></datalist></div>
  <div><label for="itRythme">Conduite par jour</label><select id="itRythme"><option value="3">3 h environ</option><option value="4" selected>4 h environ</option><option value="5">5 h environ</option></select></div>
  <div><label for="itDate">Date de départ (facultatif)</label><input id="itDate" type="date"></div>
  <div><label for="itVeh">Véhicule</label><select id="itVeh"><option value="th">Thermique</option><option value="ev">Électrique</option></select></div>
  <div><label for="itConso" id="itConsoL">Consommation (L/100 km)</label><input id="itConso" type="number" value="6" min="2" max="20" step="0.1"></div>
  <div><label for="itPrix" id="itPrixL">Carburant (€/L)</label><input id="itPrix" type="number" value="1.80" min="0.5" max="4" step="0.01"></div>
  <div><label for="itPers">Personnes</label><input id="itPers" type="number" value="2" min="1" max="12"></div>
  <div><label for="itRepas">Repas par personne et par jour (€)</label><input id="itRepas" type="number" value="45" min="0" max="300" step="1"></div>
  <div id="itAutoDiv" style="display:none"><label for="itAuto">Autonomie réelle (km)</label><input id="itAuto" type="number" value="300" min="80" max="900" step="10"></div>
  <button class="btn-compare" type="submit" id="itGo">Calculer mon itinéraire</button>
</form>
<div id="itMsg" role="status"></div>

<section id="itRes">
  <section class="it-cmp" aria-label="Comparatif avec l'autoroute">
    <div class="glass-box"><h2>Par l'autoroute</h2><div id="itA"></div></div>
    <div class="glass-box win"><h2>Parcours découverte</h2><div id="itB"></div></div>
  </section>
  <div class="it-save" id="itSave"></div>
  <p class="it-note" id="itFerry" style="display:none"></p>
  <p class="it-note" id="itNoteC">Estimations en euros : péage à 0,10 €/km sur les tronçons à péage (vignettes de Suisse, d'Autriche et d'autres pays non incluses), consommation majorée de 15 % à 130 km/h et réduite de 5 % sur routes secondaires.</p>
  <section class="glass-box it-budget" id="itBudget" aria-label="Budget estimé du voyage"></section>
  <div id="itMap"></div>
  <div id="itGps"></div>
  <div class="it-tabs" role="tablist" id="itTabs"></div>
  <section id="itDay" role="tabpanel" aria-live="polite"></section>
  <p class="it-note">Lieux et restaurants : données &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors, via <a href="https://www.geoapify.com/" target="_blank" rel="noopener">Geoapify</a>. Vérifiez les horaires et l'ouverture avant de partir.</p>
</section>

<section class="glass-box it-seo" style="margin:24px 0">
  <h2 style="margin-top:0">Pourquoi voyager sans autoroute ?</h2>
  <p>Prendre les routes nationales et départementales transforme le trajet en première étape des vacances : villages, panoramas, marchés et tables locales se trouvent le long de la route, pas sur les aires d'autoroute. Notre planificateur calcule un itinéraire sans autoroute entre deux villes d'Europe, le découpe en journées de conduite raisonnables et propose, pour chaque journée, des lieux à visiter, des restaurants et une ville pour dormir.</p>
  <h3>Questions fréquentes</h3>
  <details><summary><b>Est-ce moins cher que l'autoroute ?</b></summary><p>Vous économisez les péages, mais le trajet est plus long et peut consommer un peu plus. Le comparatif affiche les deux calculs côte à côte, à partir d'estimations : péage moyen de 0,10 €/km, sans les vignettes de Suisse ou d'Autriche, et prix du carburant que vous pouvez modifier.</p></details>
  <details><summary><b>Le planificateur convient-il aux voitures électriques ?</b></summary><p>Oui : choisissez « Électrique », indiquez la consommation en kWh/100 km, le prix de l'électricité et l'autonomie réelle de votre voiture. Le coût est recalculé et, pour chaque journée, la page propose des bornes de recharge près du déjeuner et de la ville d'étape, avec la puissance quand elle est connue.</p></details>
  <details><summary><b>Les repas et les visites sont-ils inclus dans le coût ?</b></summary><p>Le comparatif de route (péages, carburant ou électricité) est calculé séparément. Un second tableau estime le budget du voyage : repas selon un montant par personne et par jour que vous choisissez, et visites payantes estimées d'après le type de lieu. L'hébergement n'est pas inclus. Ces montants sont indicatifs.</p></details>
  <details><summary><b>Et si une mer sépare mon départ et mon arrivée (Corse, Sardaigne, Royaume-Uni...) ?</b></summary><p>Quand un ferry existe dans nos données, la traversée est intégrée : elle est exclue du temps de conduite, comptée à part avec une durée et un prix estimés, et la nuit n'est jamais placée en pleine mer. Les tarifs réels varient beaucoup selon la compagnie, la date et la saison : réservez à l'avance. L'Eurostar ne transporte pas les voitures, contrairement au Shuttle d'Eurotunnel.</p></details>
  <details><summary><b>Quels pays sont couverts ?</b></summary><p>Les villes de départ et d'arrivée peuvent se trouver dans la plupart des pays d'Europe, et le calcul d'itinéraire traverse les frontières.</p></details>
  <details><summary><b>D'où viennent les visites et les restaurants ?</b></summary><p>Ils proviennent d'OpenStreetMap, une carte collaborative. La qualité varie selon les régions : vérifiez toujours les horaires et l'ouverture avant de partir.</p></details>
  <details><summary><b>Puis-je envoyer l'itinéraire vers mon GPS ?</b></summary><p>Oui : des boutons ouvrent le trajet dans Google Maps, avec les villes d'étape et l'option « éviter les autoroutes ». Waze accepte seulement une destination, donc un bouton par journée est proposé.</p></details>
</section>

%%FOOTER%%
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const WORKER_URL="%%WORKER_URL%%";
const TARIF_PEAGE=0.10,F_AUTO=1.15,F_DECOUV=0.95;
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const eur=n=>Math.round(n).toLocaleString("fr-FR")+" €";
const hh=sec=>{const m=Math.round(sec/60);return Math.floor(m/60)+" h "+String(m%60).padStart(2,"0")};
const badge=r=>`<span class="it-road ${r[0]}">${esc(r[1])}</span>`;
const base=t=>String(t).split(" (")[0];
let ETAT={id:0,jours:null,lieux:[],cur:0};
const EV=()=>$("itVeh").value==="ev";
const NOTE_TH="Estimations en euros : péage à 0,10 €/km sur les tronçons à péage (vignettes de Suisse, d'Autriche et d'autres pays non incluses), consommation majorée de 15 % à 130 km/h et réduite de 5 % sur routes secondaires.";
const NOTE_EV="Estimations en euros : péage à 0,10 €/km sur les tronçons à péage (vignettes non incluses), consommation électrique majorée de 30 % à 130 km/h et réduite de 10 % sur routes secondaires. Le prix de l'électricité dépend de la borne : environ 0,25 €/kWh à domicile et 0,40 à 0,60 € sur une borne publique rapide.";
$("itVeh").addEventListener("change",()=>{
 const e=EV();
 $("itConsoL").textContent=e?"Consommation (kWh/100 km)":"Consommation (L/100 km)";
 $("itPrixL").textContent=e?"Électricité (€/kWh)":"Carburant (€/L)";
 $("itConso").value=e?18:6;$("itPrix").value=e?"0.45":"1.80";
 $("itAutoDiv").style.display=e?"block":"none";
});

// Appel au Worker (clé Geoapify gardée côté serveur)
async function worker(corps){
 const r=await fetch(WORKER_URL,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(corps)});
 const d=await r.json();if(!r.ok)throw new Error(d.error||"Erreur du serveur");return d;
}
// Autocomplétion des villes d'Europe
const sugg={};
function etiquette(v){return v.nom+" ("+(v.region?v.region+", ":"")+v.pays+")"}
function brancher(input,dl){
 let t;
 input.addEventListener("input",()=>{clearTimeout(t);const q=input.value.trim();if(q.length<3)return;
  t=setTimeout(async()=>{try{
   const d=await worker({action:"villes",q});
   dl.innerHTML="";
   d.villes.forEach(v=>{const lab=etiquette(v);sugg[lab]={c:[v.lon,v.lat],pays:v.pays};const o=document.createElement("option");o.value=lab;dl.appendChild(o)});
  }catch(e){}},300)});
}
brancher($("itDep"),$("itDl1"));brancher($("itArr"),$("itDl2"));
async function resoudre(input){
 const v=input.value.trim();if(sugg[v])return sugg[v];
 const d=await worker({action:"villes",q:v,limit:1});
 if(!d.villes.length)throw new Error("Ville introuvable : "+v+". Essayez le nom d'une ville d'Europe.");
 const x=d.villes[0];return{c:[x.lon,x.lat],pays:x.pays};
}

// Numéro de route lu dans le nom du tronçon (N83, D1083...)
function roadRef(n){
 // N, RN, B (Allemagne, Autriche), SS, A (Royaume-Uni) : routes nationales ; D, RD, L, K, S, SP, SR, C : routes régionales
 for(const part of String(n).split(/[,;\/]/)){
  const m=part.match(/^\s*(RN|RD|SS|SP|SR|N|D|B|A|L|K|S|C)\s*[-.]?\s*(\d{1,4})\s*[A-Za-z]*\s*$/i);
  if(m){const k=/^(RN|SS|N|B|A)$/i.test(m[1])?"N":"D";return[k,m[1].toUpperCase().replace(/^R([ND])$/,"$1")+m[2]]}
 }
 return null;
}
const km2=(a,b)=>{const t=Math.PI/180,x=Math.sin((b[1]-a[1])*t/2)**2+Math.cos(a[1]*t)*Math.cos(b[1]*t)*Math.sin((b[0]-a[0])*t/2)**2;return 12742*Math.asin(Math.sqrt(x))};
// Pour chaque nuit : la ville la plus importante près du point de coupure idéal, puis le tronçon le plus proche d'elle
async function villeEtape(steps,cum,cible,prev){
 let idx0=cum.findIndex(x=>x>=cible);if(idx0<0)idx0=steps.length-2;idx0=Math.max(idx0,prev+1);while(idx0>prev+1&&steps[idx0]&&steps[idx0].f)idx0--;
 try{
  const v=await worker({action:"etape",pt:steps[Math.min(idx0,steps.length-1)].c});
  let best=-1,bd=1e9;
  steps.forEach((s,i)=>{if(i>prev&&i<steps.length-1&&!s.f&&Math.abs(cum[i]-cible)<=2400){const d=km2(s.c,[v.lon,v.lat]);if(d<bd){bd=d;best=i}}});
  return{idx:best>=0?best:idx0,nom:v.nom,pays:v.pays,c:[v.lon,v.lat]};
 }catch(e){console.warn("Ville d'étape introuvable",e);return null}
}
async function decouperVilles(steps,nb,fin,paysFin,arrC){
 const total=steps.reduce((a,s)=>a+s.s,0),cum=[];let t=0;steps.forEach(s=>{t+=s.s;cum.push(t)});
 const coupes=[],noms=[],pays=[],centres=[];let prev=-1;
 for(let k=1;k<nb;k++){
  const cible=k*total/nb;
  let r=await villeEtape(steps,cum,cible,prev);
  if(!r){let idx=cum.findIndex(x=>x>=cible);if(idx<=prev)idx=prev+1;r={idx:Math.min(idx,steps.length-2),nom:"Étape "+k,pays:"",c:steps[Math.min(idx,steps.length-2)].c}}
  coupes.push(r.idx);noms.push(r.nom);pays.push(r.pays);centres.push(r.c);prev=r.idx;
 }
 const jours=[];let a=0;coupes.forEach(i=>{jours.push(steps.slice(a,i+1));a=i+1});jours.push(steps.slice(a));
 noms.push(fin);pays.push(paysFin||"");centres.push(arrC);return{jours,noms,pays,centres};
}

let map,layer,layerL;
function dessiner(coords,fins){
 if(!map){map=L.map("itMap");L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:18,attribution:"&copy; OpenStreetMap"}).addTo(map);layer=L.layerGroup().addTo(map);layerL=L.layerGroup().addTo(map)}
 layer.clearLayers();layerL.clearLayers();
 const line=L.polyline(coords.map(c=>[c[1],c[0]]),{color:"#075985",weight:5}).addTo(layer);
 fins.forEach(f=>L.marker([f.c[1],f.c[0]]).addTo(layer).bindPopup(esc(f.t)));
 map.invalidateSize();map.fitBounds(line.getBounds().pad(0.1));
}
function marqueurs(d){
 if(!layerL||!d||!d.visites)return;
 d.visites.forEach(x=>L.circleMarker([x.lat,x.lon],{radius:6,color:"#c8322b",weight:2,fillColor:"#fff",fillOpacity:1}).bindPopup(esc(x.nom)+"<br>"+esc(x.genre)).addTo(layerL));
}
// Estimation d'une traversée pour le véhicule et ses passagers (tarif très variable)
function trav(f){
 if(!f)return 0;
 const k=f.km,pers=Math.max(1,+$("itPers").value||2);
 return Math.min(650,Math.round((k<=60?40+1.8*k:148+0.65*(k-60))+(k>100?0.12*k*pers:0)));
}
function ferryJour(fk){
 if(!fk)return"";
 const h=Math.max(1,Math.round(fk/32*2)/2);
 return `<div class="it-bloc"><h3>Traversée en ferry</h3><p class="it-wait" style="color:var(--text)">Traversée d'environ ${Math.round(fk)} km (environ ${hh(h*3600)}), estimée à ${eur(trav({km:fk}))} pour le véhicule et ses passagers. Réservez à l'avance : les traversées longues se font souvent de nuit, avec cabine possible.</p></div>`;
}
function noteFerry(f,prix){
 const dans=c=>c[1]>49.3&&c[1]<51.6&&c[0]>-2&&c[0]<2.6;
 return "Votre trajet comprend une traversée maritime d'environ "+Math.round(f.km)+" km (environ "+hh(f.sec)+" de traversée), comptée "+eur(prix)+" pour le véhicule et ses passagers. Ce tarif est une estimation très variable selon la compagnie, la date et la saison : réservez à l'avance."
  +(dans(f.de)&&dans(f.a)?" Pour la Manche, Le Shuttle (Eurotunnel) transporte aussi les voitures ; l'Eurostar ne transporte que les voyageurs, sans véhicule.":"");
}
function bloc(d){return `<div class="it-row"><span>${d.ferry?"Distance de conduite":"Distance"}</span><b>${Math.round(d.km)} km</b></div>
<div class="it-row"><span>Temps de conduite</span><b>${hh(d.sec)}</b></div>
${d.ferry?`<div class="it-row"><span>Traversée (durée estimée)</span><b>${hh(d.ferry.sec)}</b></div>`:""}
<div class="it-row"><span>Péages</span><b>${eur(d.peage)}</b></div>
<div class="it-row"><span>Carburant</span><b>${eur(d.carb)}</b></div>
${d.traversee?`<div class="it-row"><span>Traversée en ferry (estimation)</span><b>${eur(d.traversee)}</b></div>`:""}
<div class="it-row"><span>Total route</span><b>${eur(d.peage+d.carb+(d.traversee||0))}</b></div>`}

// Lieux d'une journée, demandés au Worker un jour après l'autre
async function chargerLieux(jours,dep,id){
 for(let k=0;k<jours.length;k++){
  if(ETAT.id!==id)return;
  const st=jours[k].steps,rt=st.filter(s=>!s.f),pas=Math.max(1,Math.ceil(rt.length/25));
  const debut=k===0?dep:jours[k-1].steps[jours[k-1].steps.length-1].c;
  const poly=[debut].concat(rt.filter((_,x)=>x%pas===0).map(s=>s.c));
  if(poly.length<2){ETAT.lieux[k]={visites:[],dejeuner:[],diner:[]};majBudget();if(ETAT.cur===k)afficherJour(k,jours);continue}
  const tot=rt.reduce((a,s)=>a+s.s,0);let t=0,midi=(rt[0]||st[0]).c;
  for(const s of rt){t+=s.s;if(t>=tot/2){midi=s.c;break}}
  try{
   const r=await fetch(WORKER_URL,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({action:"lieux",poly,midi,fin:st[st.length-1].c,ev:ETAT.ev})});
   const d=await r.json();if(!r.ok)throw new Error(d.error||"Erreur du serveur");
   ETAT.lieux[k]=d;
  }catch(e){ETAT.lieux[k]={erreur:e.message}}
  if(ETAT.id!==id)return;
  marqueurs(ETAT.lieux[k]);majBudget();
  if(ETAT.cur===k)afficherJour(k,jours);
 }
}
function lieuHtml(x,sous,pin){
 // pin : repère exact sur les coordonnées (bornes) ; sinon recherche du nom, centrée sur le lieu
 const carte=pin?"https://www.google.com/maps/search/?api=1&query="+x.lat+","+x.lon
  :"https://www.google.com/maps/search/"+encodeURIComponent(x.nom)+"/@"+x.lat+","+x.lon+",16z";
 const wz=pin?`<a href="${esc("https://waze.com/ul?ll="+x.lat+","+x.lon+"&navigate=yes")}" target="_blank" rel="noopener nofollow">Waze</a>`:"";
 const site=/^https?:\/\//i.test(x.site||"")?`<a href="${esc(x.site)}" target="_blank" rel="noopener nofollow">Site</a>`:"";
 return `<li class="it-lieu"><div><b>${esc(x.nom)}</b>${sous?`<small>${esc(sous)}</small>`:""}</div><span>${site}<a href="${esc(carte)}" target="_blank" rel="noopener nofollow">Carte</a>${wz}</span></li>`;
}
function liste(titre,arr,sous,vide,pin){
 return `<div class="it-bloc"><h3>${titre}</h3>${arr&&arr.length?`<ul class="it-lieux">${arr.map(x=>lieuHtml(x,sous(x),pin)).join("")}</ul>`:`<p class="it-wait">${vide}</p>`}</div>`;
}

// Envoi vers Google Maps (trajet avec étapes, autoroutes évitées) et Waze (destination seule)
const ll=c=>c[1].toFixed(5)+","+c[0].toFixed(5);
const gMaps=(o,d,w)=>"https://www.google.com/maps/dir/?api=1&origin="+ll(o)+"&destination="+ll(d)+(w&&w.length?"&waypoints="+encodeURIComponent(w.map(ll).join("|")):"")+"&travelmode=driving&avoid=highways";
const waze=d=>"https://waze.com/ul?ll="+ll(d)+"&navigate=yes";
const lien=(cls,url,txt)=>`<a class="it-btn ${cls}" href="${esc(url)}" target="_blank" rel="noopener nofollow">${txt}</a>`;
function gpsTout(){
 const J=ETAT.jours,w=J.slice(0,-1).map(j=>j.centre).filter(Boolean),pas=Math.max(1,Math.ceil(w.length/9)),wp=w.filter((_,k)=>k%pas===0).slice(0,9);
 return `<div class="glass-box it-all"><b>Envoyer le trajet vers votre GPS</b><div class="it-gps">${lien("g",gMaps(ETAT.dep,ETAT.arr,wp),"Tout le voyage dans Google Maps")}</div>
 <p class="it-note">Google Maps reçoit les villes d'étape et évite les autoroutes (certains téléphones n'acceptent que 3 étapes). Waze accepte seulement une destination : utilisez les boutons de chaque journée.</p></div>`;
}
function gpsJour(i,lx){
 const j=ETAT.jours[i];if(!j.centre)return"";
 const o=i===0?ETAT.dep:ETAT.jours[i-1].centre,d=j.centre;
 const v=((lx&&lx.visites)||[]).slice(0,3).map(x=>[x.lon,x.lat]);
 return `<div class="it-gps">${lien("g",gMaps(o,d),"Jour "+(i+1)+" dans Google Maps")}${v.length?lien("g",gMaps(o,d,v),"avec "+v.length+" visite"+(v.length>1?"s":"")):""}${lien("w",waze(d),"Waze jusqu'à "+esc(j.fin))}</div>`;
}

// Budget estimé : route + repas + visites payantes (selon le type de lieu proposé)
const PRIX_VISITE={"Musée":10,"Château":8,"Abbaye":6,"Loisirs":20};
function majBudget(){
 const c=ETAT.cout;if(!c)return;
 const rep_=ETAT.lieux.filter(Boolean),fini=rep_.length>=ETAT.jours.length,ok=rep_.filter(l=>!l.erreur);
 let v=0;ok.forEach(l=>(l.visites||[]).forEach(x=>{v+=PRIX_VISITE[x.genre]||0}));
 const visites=v*c.pers,rA=c.A.peage+c.A.carb+(c.A.traversee||0),rD=c.D.peage+c.D.carb+(c.D.traversee||0),mA=c.nbA*c.repas*c.pers,mD=c.nbD*c.repas*c.pers;
 const ligne=(t,a,d,fort)=>{const k=fort?' class="fort"':"";return `<span${k}>${t}</span><span${k}>${a}</span><span${k}>${d}</span>`};
 const jr=n=>n+" jour"+(n>1?"s":"");
 const partiel=fini&&ok.length<rep_.length?" <small>(partiel)</small>":"";
 $("itBudget").innerHTML=`<h2 style="margin-top:0">Budget estimé du voyage</h2><div class="it-bt"><span></span><b>Autoroute</b><b>Découverte</b>`
  +ligne("Route (carburant ou électricité, péages, ferry)",eur(rA),eur(rD))
  +ligne("Repas pour "+c.pers+" personne"+(c.pers>1?"s":""),eur(mA)+" <small>("+jr(c.nbA)+")</small>",eur(mD)+" <small>("+jr(c.nbD)+")</small>")
  +ligne("Visites payantes","<small>aucune prévue</small>",fini?eur(visites)+partiel:"<small>calcul en cours...</small>")
  +ligne("Total estimé",eur(rA+mA),fini?eur(rD+mD+visites):"<small>en cours...</small>",true)
  +`</div><p class="it-note" style="margin:10px 0 0">Hébergement non inclus. Repas : ${eur(c.repas)} par personne et par jour. Visites : estimation selon le type des lieux proposés (musée 10 €, château 8 €, abbaye 6 €, parc de loisirs 20 €, gratuit pour les autres), par personne, si vous les faites tous. Montants indicatifs.</p>`;
}
function borneSous(x){return [x.puissance?"jusqu'à "+x.puissance+" kW":"",x.points?x.points+" point"+(x.points>1?"s":""):"",x.operateur,x.ville].filter(Boolean).join(", ")}
function rechargeJour(km,lx,ville){
 if(!ETAT.ev)return"";
 const a=ETAT.auto,n=Math.ceil(km/a)-1;
 const msg=km<=a*0.8?"Journée de "+Math.round(km)+" km : votre autonomie de "+a+" km suffit sans recharge en route. Une recharge pendant le déjeuner reste un confort."
  :km<=a?"Journée de "+Math.round(km)+" km, proche de votre autonomie de "+a+" km : prévoyez de recharger pendant le déjeuner."
  :"Journée de "+Math.round(km)+" km, au-delà de votre autonomie de "+a+" km : prévoyez au moins "+n+" recharge"+(n>1?"s":"")+" en route.";
 let corps="";
 if(lx&&!lx.erreur){
  corps=liste("Recharger près du déjeuner",lx.bornes_midi,borneSous,"Aucune borne trouvée près du milieu de la journée.",true)
   +liste("Recharger à "+esc(ville),lx.bornes_nuit,borneSous,"Aucune borne trouvée dans cette ville. Vérifiez si votre hôtel en propose une.",true);
 }
 return `<div class="it-bloc"><h3>Recharge</h3><p class="it-wait" style="color:var(--text)">${esc(msg)}</p></div>${corps}`;
}

function afficherJour(i,jours){
 ETAT.cur=i;
 [...$("itTabs").children].forEach((b,k)=>b.setAttribute("aria-selected",k===i));
 const j=jours[i],m=j.steps.filter(s=>!s.f).reduce((a,s)=>a+s.d,0),fk=j.steps.filter(s=>s.f).reduce((a,s)=>a+s.d,0)/1000,sec=j.steps.reduce((a,s)=>a+s.s,0),r={};
 j.steps.forEach(s=>{const ref=roadRef(s.n);if(ref)r[ref[1]]=(r[ref[1]]||0)+s.d});
 const top=Object.entries(r).sort((a,b)=>b[1]-a[1]).slice(0,6);
 const roads=top.length?top.map(([n,d])=>`<span>${badge([n[0],n])} <small>${Math.round(d/1000)} km</small></span>`).join(""):"<small>Numéros de route non indiqués sur ce parcours.</small>";
 const ville=j.fin,pays=j.pays||"",d0=$("itDate").value;
 let dates="";
 if(d0){const a=new Date(d0+"T12:00:00");a.setDate(a.getDate()+i);const b=new Date(a);b.setDate(b.getDate()+1);const f=x=>x.toISOString().slice(0,10);dates="&checkin="+f(a)+"&checkout="+f(b)}
 const bk="https://www.booking.com/searchresults.fr.html?ss="+encodeURIComponent(pays?ville+", "+pays:ville)+"&group_adults=2&no_rooms=1&group_children=0"+dates+"&aid=8012379";
 const lx=ETAT.lieux[i];
 let corps;
 if(!lx)corps='<div class="it-bloc"><p class="it-wait">Recherche des lieux à visiter et des restaurants autour de votre trajet...</p></div>';
 else if(lx.erreur)corps='<div class="it-bloc"><p class="it-wait">Lieux indisponibles pour le moment : '+esc(lx.erreur)+'</p></div>';
 else corps=liste("À voir en chemin",lx.visites,x=>x.genre,"Aucun lieu remarquable trouvé sur ce tronçon.")
  +liste("Où déjeuner",lx.dejeuner,x=>x.cuisine?"Cuisine "+x.cuisine:"","Aucun restaurant trouvé près du milieu de la journée.")
  +liste("Où dîner à "+esc(ville),lx.diner,x=>x.cuisine?"Cuisine "+x.cuisine:"","Aucun restaurant trouvé dans cette ville.");
 $("itDay").innerHTML=`<div class="it-dayhead"><h2>${esc(j.titre)}</h2><span>${Math.round(m/1000)} km, ${hh(sec)} de conduite</span></div>
 <div class="it-roads">${roads}</div>${gpsJour(i,lx)}${ferryJour(fk)}${rechargeJour(m/1000,lx,ville)}${corps}
 <div class="it-bloc"><h3>Dormir à ${esc(ville)}</h3><a class="btn-booking" style="display:inline-block" href="${bk}" target="_blank" rel="noopener sponsored nofollow">Chercher un hôtel à ${esc(ville)}</a></div>`;
}

$("itForm").addEventListener("submit",async e=>{
 e.preventDefault();
 const msg=$("itMsg"),go=$("itGo");
 if(WORKER_URL.startsWith("COLLER")){msg.innerHTML='<div class="it-msg err">L\'adresse du Worker n\'est pas encore renseignée dans itineraire.py.</div>';return}
 go.disabled=true;go.textContent="Calcul en cours...";msg.innerHTML='<div class="it-msg info">Calcul de votre itinéraire...</div>';$("itRes").style.display="none";
 try{
  const [vd,va]=await Promise.all([resoudre($("itDep")),resoudre($("itArr"))]);
  const dep=vd.c,arr=va.c;
  const r=await fetch(WORKER_URL,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({depart:dep,arrivee:arr})});
  const data=await r.json();if(!r.ok)throw new Error(data.error||"Erreur du serveur");
  const conso=+$("itConso").value,prix=+$("itPrix").value,rythme=+$("itRythme").value;
  const FA=EV()?1.30:F_AUTO,FD=EV()?0.90:F_DECOUV;
  const A={km:data.autoroute.km,sec:data.autoroute.sec,peage:data.autoroute.peageKm*TARIF_PEAGE,carb:data.autoroute.km*conso*FA/100*prix,traversee:trav(data.autoroute.ferry),ferry:data.autoroute.ferry};
  const D={km:data.decouverte.km,sec:data.decouverte.sec,peage:0,carb:data.decouverte.km*conso*FD/100*prix,traversee:trav(data.decouverte.ferry),ferry:data.decouverte.ferry};
  $("itNoteC").textContent=EV()?NOTE_EV:NOTE_TH;
  $("itA").innerHTML=bloc(A);$("itB").innerHTML=bloc(D);
  const eco=(A.peage+A.carb+A.traversee)-(D.peage+D.carb+D.traversee);
  const fer=data.decouverte.ferry||data.autoroute.ferry;
  $("itFerry").style.display=fer?"block":"none";$("itFerry").textContent=fer?noteFerry(fer,trav(fer)):"";
  $("itSave").textContent=(eco>=0?"Vous économisez ":"Surcoût de ")+eur(Math.abs(eco))+" sur la route, pour "+hh(Math.max(0,D.sec-A.sec))+" de conduite en plus.";
  const nb=Math.max(1,Math.ceil(D.sec/(rythme*3600)));
  const debut=base($("itDep").value),fin=base($("itArr").value);
  const {jours,noms,pays,centres}=await decouperVilles(data.decouverte.steps,nb,fin,va.pays,arr);
  jours.forEach((j,i)=>{j.steps=j;j.fin=noms[i];j.pays=pays[i];j.centre=centres[i];j.titre="Jour "+(i+1)+" : "+(i?noms[i-1]:debut)+" à "+noms[i]});
  const pers=Math.max(1,+$("itPers").value||2),repas=Math.max(0,+$("itRepas").value||45),nbA=Math.max(1,Math.round(A.sec/(rythme*3600)));
  ETAT={id:Date.now(),jours,lieux:[],cur:0,dep,arr,ev:EV(),cout:{A,D,nbA,nbD:jours.length,pers,repas},auto:Math.max(50,+$("itAuto").value||300)};
  $("itTabs").innerHTML="";
  jours.forEach((j,i)=>{const b=document.createElement("button");b.className="it-tab";b.type="button";b.setAttribute("role","tab");b.textContent=jours.length>1?"Jour "+(i+1):"Trajet";b.onclick=()=>afficherJour(i,jours);$("itTabs").appendChild(b)});
  $("itGps").innerHTML=gpsTout();majBudget();$("itRes").style.display="block";msg.innerHTML="";
  dessiner(data.decouverte.coords,jours.slice(0,-1).map((j,i)=>({c:j.steps[j.steps.length-1].c,t:"Nuit "+(i+1)+" : "+j.fin})));
  afficherJour(0,jours);
  chargerLieux(jours,dep,ETAT.id);
 }catch(err){msg.innerHTML='<div class="it-msg err">'+esc(err.message)+"</div>"}
 go.disabled=false;go.textContent="Calculer mon itinéraire";
});
</script>
</body>
</html>
"""


def generate_itineraire_page(output_dir, global_style, menu_html, footer_html, site_url):
    """Écrit itineraire-decouverte.html dans le dossier de sortie, avec l'en-tête, le menu et le pied de page du site."""
    html = (
        TEMPLATE.replace("%%STYLE%%", global_style)
        .replace("%%MENU%%", menu_html)
        .replace("%%FOOTER%%", footer_html)
        .replace("%%SITE_URL%%", site_url)
        .replace("%%WORKER_URL%%", WORKER_URL)
    )
    chemin = Path(output_dir) / "itineraire-decouverte.html"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(html, encoding="utf-8")