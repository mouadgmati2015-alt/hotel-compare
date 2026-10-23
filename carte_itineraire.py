"""
carte_itineraire.py : carte interactive + étapes + lieux + spots pour les articles du blog.

Utilisation dans generateur.py (2 lignes) :
    from carte_itineraire import generer_carte_itineraire          # en haut avec les autres imports
    {generer_carte_itineraire(art)}                                 # dans le gabarit article_page

Dans blog_data.json, ajouter à un article le champ optionnel "carte" (voir carte_strasbourg_milan.json).
Un article SANS "carte" est généré exactement comme avant.

Format du champ "carte" :
{
  "jours": [
    {
      "titre": "Jour 1 · Strasbourg → Lucerne",
      "distance": "230 km",            (optionnel)
      "duree": "3 h 30",               (optionnel)
      "trace": [[lat, lng], ...],      (optionnel : tracé réel exporté d'un GPX ; sinon ligne droite en pointillés)
      "lieux": [
        {
          "nom": "Lucerne",
          "type": "etape" | "visite" | "spot" | "resto",
          "lat": 47.0516, "lng": 8.3075,
          "texte": "Courte description.",
          "lien": "https://...",       (optionnel)
          "lien_texte": "Voir l'hôtel", (optionnel)
          "sur_route": true            (optionnel, false = détour : pas dans la ligne ni dans le lien Google Maps)
        }
      ]
    }
  ]
}
"""

import json
import html

TYPES = {
    "etape": ("🛏️", "Ville-étape", "#e59a21"),
    "visite": ("📍", "À visiter", "#087f9b"),
    "spot": ("📸", "Spot", "#16805b"),
    "resto": ("🍽️", "Restaurant", "#c2410c"),
}
COULEURS_JOURS = ["#087f9b", "#e59a21", "#16805b", "#075985", "#c2410c", "#7c3aed"]

LEAFLET_CSS = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
LEAFLET_JS = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"

_CSS = """
<style>
.mhc-carte { margin: 22px 0; }
.mhc-carte h2 { margin: 0 0 12px; }
#mhc-map { width: 100%; height: 440px; border-radius: 16px; border: 1px solid var(--line); box-shadow: var(--shadow); z-index: 0; background: var(--panel); }
.mhc-note { color: var(--muted); font-size: .85rem; margin: 8px 2px 0; }
.mhc-toolbar { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; align-items: center; }
.mhc-chip { border: 1px solid var(--line); background: #fff; color: var(--text); border-radius: 999px; padding: 6px 12px; font-size: .85rem; font-weight: 700; cursor: pointer; }
.mhc-chip[aria-pressed="false"] { opacity: .45; }
.mhc-btn { display: inline-block; border: 0; border-radius: 12px; padding: 9px 14px; font-weight: 700; font-size: .9rem; cursor: pointer; text-decoration: none; background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: #fff; }
.mhc-btn.secondaire { background: var(--panel-strong); color: var(--text); }
.mhc-jour { margin: 26px 0 8px; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.mhc-jour h3 { margin: 0; }
.mhc-dot { width: 14px; height: 14px; border-radius: 50%; display: inline-block; }
.mhc-meta { color: var(--muted); font-size: .9rem; }
.mhc-lieux { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px; }
.mhc-lieu { background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 14px; }
.mhc-lieu h4 { margin: 0 0 6px; font-size: 1rem; }
.mhc-lieu p { margin: 0 0 10px; font-size: .9rem; line-height: 1.5; color: var(--text); }
.mhc-lieu .mhc-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.mhc-type { font-size: .75rem; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
.mhc-pin { width: 34px; height: 34px; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); border: 3px solid #fff; box-shadow: 0 2px 8px rgba(0,0,0,.4); display: flex; align-items: center; justify-content: center; }
.mhc-pin span { transform: rotate(45deg); font-size: 16px; line-height: 1; }
@media (max-width: 600px) { #mhc-map { height: 340px; } }
</style>
"""

_JS = """
<script>
(function () {
  var D = __DATA__;
  var cartePrete = typeof L !== 'undefined';
  var map, markers = {}, groupes = {};

  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }

  function pin(type) {
    var t = D.types[type] || D.types.visite;
    return L.divIcon({
      className: '',
      html: '<div class="mhc-pin" style="background:' + t.couleur + '"><span>' + t.emoji + '</span></div>',
      iconSize: [34, 34], iconAnchor: [17, 34], popupAnchor: [0, -32]
    });
  }

  if (cartePrete) {
    map = L.map('mhc-map', { scrollWheelZoom: false });
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
    map.once('click', function () { map.scrollWheelZoom.enable(); });

    var tous = [];
    D.jours.forEach(function (j, ji) {
      var ligne = j.trace && j.trace.length ? j.trace : j.ligne;
      if (ligne && ligne.length > 1) {
        L.polyline(ligne, {
          color: j.couleur, weight: 5, opacity: .85,
          dashArray: j.trace && j.trace.length ? null : '8 10'
        }).addTo(map);
      }
      j.lieux.forEach(function (l, li) {
        var m = L.marker([l.lat, l.lng], { icon: pin(l.type), title: l.nom });
        m.bindPopup('<strong>' + esc(l.nom) + '</strong>' + (l.texte ? '<br>' + esc(l.texte) : ''));
        (groupes[l.type] = groupes[l.type] || L.layerGroup()).addLayer(m);
        markers[ji + '-' + li] = m;
        tous.push([l.lat, l.lng]);
      });
    });
    Object.keys(groupes).forEach(function (k) { groupes[k].addTo(map); });
    if (tous.length) { map.fitBounds(tous, { padding: [40, 40] }); }
  } else {
    var el = document.getElementById('mhc-map');
    el.style.display = 'flex'; el.style.alignItems = 'center'; el.style.justifyContent = 'center';
    el.innerHTML = '<p class="mhc-note">La carte n\\'a pas pu se charger. Les étapes restent consultables ci-dessous.</p>';
  }

  // Filtres par type
  document.querySelectorAll('.mhc-chip').forEach(function (b) {
    b.addEventListener('click', function () {
      var on = b.getAttribute('aria-pressed') !== 'true';
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      var g = groupes[b.getAttribute('data-type')];
      if (g && cartePrete) { on ? g.addTo(map) : map.removeLayer(g); }
    });
  });

  // « Voir sur la carte »
  document.querySelectorAll('.mhc-voir').forEach(function (b) {
    b.addEventListener('click', function () {
      if (!cartePrete) { return; }
      var m = markers[b.getAttribute('data-id')];
      if (!m) { return; }
      document.getElementById('mhc-map').scrollIntoView({ behavior: 'smooth', block: 'center' });
      var g = groupes[b.getAttribute('data-type')];
      if (g && !map.hasLayer(g)) { g.addTo(map); }
      map.flyTo(m.getLatLng(), 11, { duration: .8 });
      setTimeout(function () { m.openPopup(); }, 900);
    });
  });

  // Export GPX (waypoints + trace), généré dans le navigateur
  function xml(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  var bGpx = document.getElementById('mhc-gpx');
  if (bGpx) {
    bGpx.addEventListener('click', function () {
      var g = '<?xml version="1.0" encoding="UTF-8"?>\\n<gpx version="1.1" creator="MyHotelCompare" xmlns="http://www.topografix.com/GPX/1/1">\\n';
      g += '<metadata><name>' + xml(D.titre) + '</name></metadata>\\n';
      D.jours.forEach(function (j) {
        j.lieux.forEach(function (l) {
          g += '<wpt lat="' + l.lat + '" lon="' + l.lng + '"><name>' + xml(l.nom) + '</name>' +
               (l.texte ? '<desc>' + xml(l.texte) + '</desc>' : '') + '</wpt>\\n';
        });
      });
      D.jours.forEach(function (j) {
        if (j.trace && j.trace.length) {
          // vrai tracé : exporté tel quel
          g += '<trk><name>' + xml(j.titre) + '</name><trkseg>\\n';
          j.trace.forEach(function (p) { g += '<trkpt lat="' + p[0] + '" lon="' + p[1] + '"></trkpt>\\n'; });
          g += '</trkseg></trk>\\n';
        } else if (j.ligne && j.ligne.length > 1) {
          // pas de tracé réel : on exporte une ROUTE (points de passage), que l'appli GPS calcule sur les vraies routes
          g += '<rte><name>' + xml(j.titre) + '</name>\\n';
          j.ligne.forEach(function (p) { g += '<rtept lat="' + p[0] + '" lon="' + p[1] + '"></rtept>\\n'; });
          g += '</rte>\\n';
        }
      });
      g += '</gpx>';
      var a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob([g], { type: 'application/gpx+xml' }));
      a.download = D.fichier + '.gpx';
      document.body.appendChild(a); a.click(); document.body.removeChild(a);
    });
  }
})();
</script>
"""


def _esc(valeur):
    return html.escape(str(valeur if valeur is not None else ""), quote=True)


def _nombre(valeur):
    try:
        return float(valeur)
    except (TypeError, ValueError):
        return None


def _lien_google_maps(points):
    """Lien d'itinéraire Google Maps (origine, étapes, destination). Limité à 9 étapes intermédiaires."""
    if len(points) < 2:
        return ""
    origine, destination, milieu = points[0], points[-1], points[1:-1]
    if len(milieu) > 9:
        pas = len(milieu) / 9.0
        milieu = [milieu[int(i * pas)] for i in range(9)]
    fmt = lambda p: f"{p[0]:.5f},{p[1]:.5f}"
    url = f"https://www.google.com/maps/dir/?api=1&origin={fmt(origine)}&destination={fmt(destination)}&travelmode=driving"
    if milieu:
        url += "&waypoints=" + "%7C".join(fmt(p) for p in milieu)
    return url


def generer_carte_itineraire(art):
    """Retourne le bloc HTML (carte + étapes) d'un article, ou "" si l'article n'a pas de champ "carte"."""
    carte = (art or {}).get("carte")
    if not carte or not carte.get("jours"):
        return ""

    jours_js, jours_html = [], []
    types_utilises = []
    fin_precedente = None  # dernier point « sur la route » de la veille

    for ji, jour in enumerate(carte["jours"]):
        couleur = COULEURS_JOURS[ji % len(COULEURS_JOURS)]
        lieux_valides, points_route = [], []
        for lieu in jour.get("lieux", []):
            lat, lng = _nombre(lieu.get("lat")), _nombre(lieu.get("lng"))
            if lat is None or lng is None:
                print(f"[carte] lieu ignoré (coordonnées manquantes) : {lieu.get('nom')!r}")
                continue
            type_ = lieu.get("type") if lieu.get("type") in TYPES else "visite"
            if type_ not in types_utilises:
                types_utilises.append(type_)
            lieux_valides.append({
                "nom": str(lieu.get("nom", "")), "type": type_, "lat": lat, "lng": lng,
                "texte": str(lieu.get("texte", "")),
            })
            if lieu.get("sur_route", True):
                points_route.append((lat, lng))

        ligne = ([fin_precedente] if fin_precedente else []) + points_route
        trace = [[_nombre(p[0]), _nombre(p[1])] for p in jour.get("trace", []) if len(p) == 2]
        jours_js.append({"titre": str(jour.get("titre", f"Jour {ji + 1}")), "couleur": couleur,
                         "lieux": lieux_valides, "ligne": ligne, "trace": trace})
        if points_route:
            fin_precedente = points_route[-1]

        meta = " · ".join(x for x in (_esc(jour.get("distance", "")), _esc(jour.get("duree", ""))) if x)
        gm = _lien_google_maps(ligne)
        cartes = []
        for li, (lieu_src, lieu) in enumerate(zip([l for l in jour.get("lieux", [])
                                                  if _nombre(l.get("lat")) is not None and _nombre(l.get("lng")) is not None],
                                                 lieux_valides)):
            emoji, libelle, _ = TYPES[lieu["type"]]
            lien = ""
            if str(lieu_src.get("lien", "")).startswith(("http://", "https://")):
                lien = (f'<a class="mhc-btn secondaire" href="{_esc(lieu_src["lien"])}" target="_blank" '
                        f'rel="noopener sponsored">{_esc(lieu_src.get("lien_texte") or "En savoir plus")}</a>')
            cartes.append(f"""
        <div class="mhc-lieu">
          <div class="mhc-type">{emoji} {libelle}</div>
          <h4>{_esc(lieu["nom"])}</h4>
          {f'<p>{_esc(lieu["texte"])}</p>' if lieu["texte"] else ''}
          <div class="mhc-actions">
            <button type="button" class="mhc-btn secondaire mhc-voir" data-id="{ji}-{li}" data-type="{lieu["type"]}">Voir sur la carte</button>
            {lien}
          </div>
        </div>""")
        jours_html.append(f"""
    <div class="mhc-jour">
      <span class="mhc-dot" style="background:{couleur}"></span>
      <h3>{_esc(jour.get("titre", f"Jour {ji + 1}"))}</h3>
      {f'<span class="mhc-meta">{meta}</span>' if meta else ''}
      {f'<a class="mhc-btn" href="{_esc(gm)}" target="_blank" rel="noopener">Itinéraire du jour (Google Maps)</a>' if gm else ''}
    </div>
    <div class="mhc-lieux">{''.join(cartes)}
    </div>""")

    if not any(j["lieux"] for j in jours_js):
        return ""

    puces = "".join(
        f'<button type="button" class="mhc-chip" aria-pressed="true" data-type="{t}">{TYPES[t][0]} {TYPES[t][1]}</button>'
        for t in types_utilises
    )
    donnees = {
        "titre": str(art.get("titre", "Itinéraire")),
        "fichier": str(art.get("slug") or "itineraire"),
        "types": {k: {"emoji": v[0], "libelle": v[1], "couleur": v[2]} for k, v in TYPES.items()},
        "jours": jours_js,
    }
    data_js = json.dumps(donnees, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\!--")
    indicatif = any(not j["trace"] for j in jours_js)

    return f"""
<link rel="stylesheet" href="{LEAFLET_CSS}">
{_CSS}
<section class="mhc-carte">
  <h2>🗺️ Carte du parcours et étapes</h2>
  <div class="mhc-toolbar">{puces}
    <button type="button" class="mhc-btn" id="mhc-gpx">⬇️ Télécharger la trace GPX</button>
  </div>
  <div id="mhc-map" role="region" aria-label="Carte de l'itinéraire"></div>
  {'<p class="mhc-note">Tracé indicatif en pointillés : suivez les routes de l’itinéraire et vérifiez l’ouverture des cols avant de partir.</p>' if indicatif else ''}
  {''.join(jours_html)}
</section>
<script src="{LEAFLET_JS}"></script>
{_JS.replace("__DATA__", data_js)}
"""