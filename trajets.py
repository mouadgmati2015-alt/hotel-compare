"""Pages « trajet sans autoroute » : une page par trajet de trajets.json, construite à partir de data_trajets/.

Aucun appel réseau ici : les données ont été récupérées auparavant par trajets_fetch.py.
"""
import html
import json
import re
import datetime
from pathlib import Path
from urllib.parse import quote, urlencode

BASE = Path(__file__).resolve().parent
DATA = BASE / "data_trajets"
LISTE = BASE / "trajets.json"
AID = "8012379"          # identifiant d'affiliation Booking, comme ailleurs sur le site
PAGE_INDEX = "trajets-sans-autoroute.html"

# Routes nommées : on ne les mentionne que si le tracé calculé les emprunte réellement (refs, km minimum)
ROUTES_NOMMEES = {
    "paris-menton-sans-autoroute": ("l'ancienne Nationale 7, la « route des vacances »", ["N7"], 120),
    "grasse-grenoble-sans-autoroute": ("la Route Napoléon", ["N85"], 80),
}
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
ICONES = {"Musée": "🏛️", "Château": "🏰", "Abbaye": "⛪", "Lieu de culte": "⛪", "Point de vue": "🌄",
          "Cascade": "💧", "Loisirs": "🎡", "Patrimoine": "🏺", "À voir": "📍"}


def esc(s):
    return html.escape(str(s), quote=True)


def eur(n):
    return f"{round(n):,}".replace(",", "\u202f") + " €"


def hms(sec):
    m = round(sec / 60)
    return f"{m // 60} h {m % 60:02d}"


def jours_txt(n):
    return f"{n} jour" + ("s" if n > 1 else "")


def date_fr(iso):
    try:
        d = datetime.date.fromisoformat(iso)
        return f"{d.day} {MOIS[d.month - 1]} {d.year}"
    except Exception:
        return ""


def css_planificateur():
    """Reprend le style de la page du planificateur pour que les deux restent cohérentes."""
    try:
        from itineraire import TEMPLATE
        m = re.search(r"%%STYLE%%\s*<style>(.*?)</style>", TEMPLATE, re.S)
        return m.group(1) if m else ""
    except Exception:
        return ""


# ---------- Coûts (mêmes hypothèses que le planificateur) ----------

def trav(km, pers=2):
    if not km:
        return 0
    base = 40 + 1.8 * km if km <= 60 else 148 + 0.65 * (km - 60)
    return min(650, round(base + (0.12 * km * pers if km > 100 else 0)))


def couts(d):
    ev = d["vehicule"] == "electrique"
    conso, prix = (18, 0.45) if ev else (6, 1.80)
    fa, fd = (1.30, 0.90) if ev else (1.15, 0.95)
    a, c = d["autoroute"], d["decouverte"]
    A = {"km": a["km"], "sec": a["sec"], "peage": a["peageKm"] * 0.10, "carb": a["km"] * conso * fa / 100 * prix,
         "ferry": a.get("ferry"), "trav": trav((a.get("ferry") or {}).get("km"))}
    D = {"km": c["km"], "sec": c["sec"], "peage": 0, "carb": c["km"] * conso * fd / 100 * prix,
         "ferry": c.get("ferry"), "trav": trav((c.get("ferry") or {}).get("km"))}
    for x in (A, D):
        x["route"] = x["peage"] + x["carb"] + x["trav"]
        x["total_sec"] = x["sec"] + (x["ferry"]["sec"] if x["ferry"] else 0)
    return A, D, conso, prix, ev


def qualite(d):
    """Une page n'est publiée que si elle apporte de vraies informations."""
    try:
        if not d["jours"] or d["decouverte"]["km"] <= 0 or not d["autoroute"].get("km"):
            return False
        visites = sum(len(((j.get("lieux") or {}).get("visites")) or []) for j in d["jours"])
        return visites >= 2
    except Exception:
        return False


# ---------- Éléments de page ----------

def ico_cuisine(c):
    t = (c or "").lower()
    for motif, e in (("pizza", "🍕"), ("ital", "🍝"), ("japon|sushi", "🍣"), ("chin|asiat|vietnam|thaï", "🥡"), ("indi", "🍛"),
                     ("burger", "🍔"), ("crêp", "🥞"), ("kebab|turq|liban|maroc", "🥙"), ("mer", "🦐"), ("grill", "🥩")):
        if re.search(motif, t):
            return e
    return "🍽️"


def sous_resto(x):
    c = x.get("cuisine") or ""
    if not c:
        return ""
    return c.capitalize() if re.fullmatch(r"pizzeria|crêperie|kebab|burgers|sushi|grillades", c) else "Cuisine " + c


def borne_sous(x):
    return ", ".join(filter(None, [f"jusqu'à {x['puissance']} kW" if x.get("puissance") else "",
                                    f"{x['points']} point{'s' if x['points'] > 1 else ''}" if x.get("points") else "",
                                    x.get("operateur"), x.get("ville")]))


def lien_ext(url, texte):
    return f'<a href="{esc(url)}" target="_blank" rel="noopener nofollow">{texte}</a>'


def lieu_html(x, sous="", kind=None, pin=False):
    if pin:
        carte = f"https://www.google.com/maps/search/?api=1&query={x['lat']},{x['lon']}"
        waze = lien_ext(f"https://waze.com/ul?ll={x['lat']},{x['lon']}&navigate=yes", "Waze")
    else:
        carte = f"https://www.google.com/maps/search/{quote(x['nom'])}/@{x['lat']},{x['lon']},16z"
        waze = ""
    site = lien_ext(x["site"], "Site") if re.match(r"https?://", x.get("site") or "", re.I) else ""
    vig = ""
    if kind:
        img = f'<img src="{esc(x["image"])}" alt="" loading="lazy" width="76" height="76">' if (x.get("image") or "").startswith("https://") else ""
        vig = f'<div class="it-vig">{img or (ICONES.get(x.get("genre"), "📍") if kind == "v" else ico_cuisine(x.get("cuisine")))}</div>'
    res = f'<p class="it-res">{esc(x["resume"])}</p>' if x.get("resume") else ""
    meta = []
    if x.get("adresse"):
        meta.append("📍 " + esc(x["adresse"]))
    if x.get("horaires"):
        meta.append("🕒 " + esc(x["horaires"]))
    if x.get("infos"):
        meta.append(esc(", ".join(x["infos"])))
    if x.get("tel"):
        meta.append(f'📞 <a href="tel:{esc(re.sub(chr(32), "", x["tel"]))}">{esc(x["tel"])}</a>')
    credit = []
    src = x.get("source") or {}
    if str(src.get("url", "")).startswith("https://"):
        credit.append(f'texte : {lien_ext(src["url"], esc(src.get("nom", "Wikipédia")))} (CC BY-SA)')
    if "wikimedia.org" in (x.get("image") or ""):
        credit.append("image : Wikimedia")
    if credit:
        meta.append(", ".join(credit))
    metas = "".join(f'<small class="it-meta">{m}</small>' for m in meta)
    s = f"<small>{esc(sous)}</small>" if sous else ""
    return (f'<li class="it-lieu">{vig}<div class="it-txt"><b>{esc(x["nom"])}</b>{s}{res}{metas}</div>'
            f'<span class="it-liens">{site}{lien_ext(carte, "Carte")}{waze}</span></li>')


def liste(titre, arr, sous, vide, kind=None, pin=False):
    if arr:
        corps = '<ul class="it-lieux">' + "".join(lieu_html(x, sous(x), kind, pin) for x in arr) + "</ul>"
    else:
        corps = f'<p class="it-wait">{esc(vide)}</p>'
    return f'<div class="it-bloc"><h3>{esc(titre)}</h3>{corps}</div>'


def badge(ref, kind):
    return f'<span class="it-road {kind}">{esc(ref)}</span>'


def lien_booking(ville, pays):
    ss = f"{ville}, {pays}" if pays else ville
    return f"https://www.booking.com/searchresults.fr.html?ss={quote(ss)}&group_adults=2&no_rooms=1&group_children=0&aid={AID}"


def lien_planificateur(d):
    ev = d["vehicule"] == "electrique"
    de, ar = d["depart"], d["arrivee"]
    q = {"d": f"{de['nom']} ({de['pays']})", "dc": f"{de['lon']},{de['lat']}", "dp": de["pays"],
         "a": f"{ar['nom']} ({ar['pays']})", "ac": f"{ar['lon']},{ar['lat']}", "ap": ar["pays"],
         "r": 4, "v": "ev" if ev else "th", "c": 18 if ev else 6, "p": 0.45 if ev else 1.8, "n": 2, "m": 45}
    if ev:
        q["u"] = 300
    q.update({"utm_source": "pages-trajets", "utm_medium": "site", "utm_campaign": "trajet"})
    return "itineraire-decouverte.html?" + urlencode(q)


def route_nommee(slug, d):
    regle = ROUTES_NOMMEES.get(slug)
    if not regle:
        return ""
    nom, refs, mini = regle
    km = sum(r[2] for j in d["jours"] for r in j["routes"] if r[0] in refs)
    return f"Le tracé calculé emprunte {nom} sur environ {round(km)} km." if km >= mini else ""


# ---------- Page d'un trajet ----------

def textes(d, A, D, conso, prix, ev, slug):
    de, ar = d["depart"]["nom"], d["arrivee"]["nom"]
    nb = len(d["jours"])
    eco_peage = A["peage"]
    eco = A["route"] - D["route"]
    dt = D["total_sec"] - A["total_sec"]
    p1 = (f"Pour aller de {de} à {ar} sans autoroute, comptez environ {round(D['km'])} km et {hms(D['sec'])} de conduite, "
          f"soit {jours_txt(nb)} à raison d'environ 4 h de route par jour. "
          f"Par l'autoroute, le même trajet fait {round(A['km'])} km en {hms(A['sec'])}, avec environ {eur(A['peage'])} de péages estimés.")
    if D["ferry"]:
        p1 += (f" Le trajet comprend une traversée maritime d'environ {round(D['ferry']['km'])} km "
               f"(environ {hms(D['ferry']['sec'])}), comptée {eur(D['trav'])} pour le véhicule et ses passagers (estimation).")
    if abs(eco) < 5 and A["peage"] < 5:
        p2 = "Ce trajet utilise peu ou pas d'autoroute : les deux itinéraires sont proches."
    elif eco >= 0:
        p2 = (f"En évitant l'autoroute, vous économisez environ {eur(eco)} sur la route (péages et "
              f"{'électricité' if ev else 'carburant'}), pour environ {hms(abs(dt))} de trajet {'en plus' if dt >= 0 else 'en moins'}.")
    else:
        p2 = (f"Sans autoroute, la route coûte environ {eur(-eco)} de plus (le trajet est plus long) "
              f"et prend environ {hms(abs(dt))} {'de plus' if dt >= 0 else 'de moins'} ; vous gagnez en revanche des paysages et des étapes.")
    routes = {}
    for j in d["jours"]:
        for ref, kind, km in j["routes"]:
            routes[(ref, kind)] = routes.get((ref, kind), 0) + km
    top = sorted(routes.items(), key=lambda kv: -kv[1])[:3]
    p3 = ""
    if top:
        p3 = "Les routes les plus empruntées sont " + ", ".join(f"la {ref} ({round(km)} km)" for (ref, _), km in top) + "."
    nommee = route_nommee(slug, d)
    hyp = (f"Estimations pour un véhicule électrique consommant {conso} kWh/100 km, avec l'électricité à {str(prix).replace('.', ',')} €/kWh"
           if ev else f"Estimations pour un véhicule thermique consommant {conso} l/100 km, avec le carburant à {str(prix).replace('.', ',')} €/l")
    etapes = ", ".join(j["fin"]["nom"] for j in d["jours"])
    faq = [
        (f"Quelle est la distance de {de} à {ar} sans autoroute ?",
         f"Environ {round(D['km'])} km, soit {hms(D['sec'])} de conduite et {jours_txt(nb)} à raison d'environ 4 h par jour. Par l'autoroute, le trajet fait {round(A['km'])} km en {hms(A['sec'])}."),
        (f"Combien coûte le trajet de {de} à {ar} ?",
         f"{hyp}, la route coûte environ {eur(D['route'])} sans autoroute contre {eur(A['route'])} par l'autoroute (péages compris). Les repas, les visites et l'hébergement ne sont pas inclus."),
        (f"Où s'arrêter entre {de} et {ar} ?",
         f"Les étapes proposées sont : {etapes}. Pour chaque journée, la page indique des lieux à visiter, des restaurants pour le déjeuner et le dîner, et un lien pour réserver une nuit."),
    ]
    if ev:
        faq.append((f"Où recharger une voiture électrique de {de} à {ar} ?",
                    "Pour chaque journée, la page liste des bornes de recharge près du lieu de déjeuner et dans la ville d'étape, avec la puissance quand elle est connue. Vérifiez la disponibilité dans l'application de votre réseau de recharge."))
    else:
        faq.append((f"Y a-t-il des péages entre {de} et {ar} sans autoroute ?",
                    "Le parcours évite les autoroutes à péage. Quelques ouvrages (tunnels, ponts) peuvent rester payants : ils ne sont pas inclus dans l'estimation."))
    return p1, p2, p3, nommee, hyp, faq


def page_trajet(d, slug, trajets, site_url, global_style, menu_html, footer_html, css):
    A, D, conso, prix, ev = couts(d)
    de, ar = d["depart"], d["arrivee"]
    p1, p2, p3, nommee, hyp, faq = textes(d, A, D, conso, prix, ev, slug)
    nb = len(d["jours"])
    titre = d["titre"]
    meta = (f"{de['nom']} {ar['nom']} sans autoroute : {round(D['km'])} km, {jours_txt(nb)}, "
            f"{eur(A['peage'])} de péages évités. Étapes, visites, restaurants et comparaison avec l'autoroute.")
    if ev:
        meta = (f"{de['nom']} {ar['nom']} en voiture électrique : {round(D['km'])} km sans autoroute, {jours_txt(nb)}. "
                "Étapes, bornes de recharge, visites, restaurants et coût.")
    url = f"{site_url}/{slug}.html"

    def ligne(lbl, a, b):
        return f'<div class="it-row"><span>{lbl}</span><b>{a}</b></div>'

    def colonne(x):
        l = [ligne("Distance de conduite" if x["ferry"] else "Distance", f"{round(x['km'])} km", ""),
             ligne("Temps de conduite", hms(x["sec"]), "")]
        if x["ferry"]:
            l += [ligne("Traversée (durée estimée)", hms(x["ferry"]["sec"]), ""), ligne("Durée totale du trajet", hms(x["total_sec"]), "")]
        l += [ligne("Péages", eur(x["peage"]), ""), ligne("Électricité" if ev else "Carburant", eur(x["carb"]), "")]
        if x["ferry"]:
            l.append(ligne("Traversée en ferry (estimation)", eur(x["trav"]), ""))
        l.append(ligne("Total route", eur(x["route"]), ""))
        return "".join(l)

    jours_html = []
    pts_visites, nuits = [], []
    for k, j in enumerate(d["jours"]):
        debut = de["nom"] if k == 0 else d["jours"][k - 1]["fin"]["nom"]
        fin = j["fin"]
        lx = j.get("lieux") or {}
        badges = "".join(f"<span>{badge(ref, kind)} <small>{round(km)} km</small></span>" for ref, kind, km in j["routes"]) or "<small>Numéros de route non indiqués sur ce parcours.</small>"
        bloc_ferry = ""
        if j["ferry_km"]:
            bloc_ferry = (f'<div class="it-bloc"><h3>Traversée en ferry</h3><p class="it-wait" style="color:var(--text)">'
                          f'Traversée d\'environ {round(j["ferry_km"])} km, estimée à {eur(trav(j["ferry_km"]))} pour le véhicule et ses passagers. '
                          "Réservez à l'avance : les traversées longues se font souvent de nuit, avec cabine possible.</p></div>")
        recharge = ""
        if ev:
            aut = 300
            msg = (f"Journée de {round(j['km'])} km : une autonomie de {aut} km suffit sans recharge en route. Une recharge pendant le déjeuner reste un confort."
                   if j["km"] <= aut * 0.8 else
                   f"Journée de {round(j['km'])} km, proche d'une autonomie de {aut} km : prévoyez de recharger pendant le déjeuner."
                   if j["km"] <= aut else
                   f"Journée de {round(j['km'])} km, au-delà d'une autonomie de {aut} km : prévoyez au moins {-(-int(j['km']) // aut) - 1} recharge(s) en route.")
            recharge = (f'<div class="it-bloc"><h3>Recharge</h3><p class="it-wait" style="color:var(--text)">{esc(msg)}</p></div>'
                        + liste("Recharger près du déjeuner", lx.get("bornes_midi"), borne_sous, "Aucune borne trouvée près du milieu de la journée.", None, True)
                        + liste(f"Recharger à {fin['nom']}", lx.get("bornes_nuit"), borne_sous, "Aucune borne trouvée dans cette ville.", None, True))
        corps = (liste("À voir en chemin", lx.get("visites"), lambda x: x.get("genre", ""), "Aucun lieu remarquable trouvé sur ce tronçon.", "v")
                 + liste("Où déjeuner", lx.get("dejeuner"), sous_resto, "Aucun restaurant trouvé près du milieu de la journée.", "r")
                 + liste(f"Où dîner à {fin['nom']}", lx.get("diner"), sous_resto, "Aucun restaurant trouvé dans cette ville.", "r")) if lx else ""
        for v in (lx.get("visites") or []):
            pts_visites.append([v["lat"], v["lon"], v["nom"]])
        nuits.append([fin["lat"], fin["lon"], f"Nuit {k + 1} : {fin['nom']}"])
        jours_html.append(
            f'<section><h2>Jour {k + 1} : {esc(debut)} à {esc(fin["nom"])}</h2>'
            f'<p class="it-wait">{round(j["km"])} km, {hms(j["sec"])} de conduite</p>'
            f'<div class="it-roads">{badges}</div>{bloc_ferry}{recharge}{corps}'
            f'<div class="it-bloc"><h3>Dormir à {esc(fin["nom"])}</h3>'
            f'<a class="btn-booking" style="display:inline-block" href="{esc(lien_booking(fin["nom"], fin.get("pays", "")))}" target="_blank" rel="noopener sponsored nofollow">Chercher un hôtel à {esc(fin["nom"])}</a></div></section>')

    # liens vers d'autres trajets
    autres = [t for t in trajets if t["slug"] != slug and (t["depart"]["nom"] == de["nom"] or t["arrivee"]["nom"] == ar["nom"]
                                                           or (t["depart"]["nom"] == de["nom"] and t["arrivee"]["nom"] == ar["nom"]))][:8]
    liens = "".join(f'<li><a href="{esc(t["slug"])}.html">{esc(t["titre"].split(" : ")[0])}</a></li>' for t in autres)
    autres_html = f'<h2>Autres trajets</h2><ul>{liens}</ul>' if liens else ""

    faq_html = "".join(f"<details><summary><b>{esc(q)}</b></summary><p>{esc(r)}</p></details>" for q, r in faq)
    jsonld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]}, ensure_ascii=False).replace("</", "<\\/")
    carte = json.dumps({"c": [[round(c[1], 4), round(c[0], 4)] for c in d["decouverte"]["coords"]], "n": nuits, "v": pts_visites},
                       ensure_ascii=False).replace("</", "<\\/")
    maj = date_fr(d.get("genere", ""))
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(titre)} | MyHotelCompare</title>
<meta name="description" content="{esc(meta[:158])}">
<link rel="canonical" href="{esc(url)}">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(titre)}">
<meta property="og:description" content="{esc(meta[:158])}">
<meta property="og:url" content="{esc(url)}">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">{jsonld}</script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
{global_style}
<style>{css}
.tj-cmp .glass-box h2{{margin-top:0}}
.tj-fil{{font-size:.9rem;color:var(--muted);margin:0 0 10px}}
</style>
</head>
<body><div class="container">
{menu_html}
<p class="tj-fil"><a href="index.html">Accueil</a> &gt; <a href="{PAGE_INDEX}">Trajets sans autoroute</a> &gt; {esc(de['nom'])} {esc(ar['nom'])}</p>
<div class="hero-banner">
  <h1 style="color:#fff;margin:0 0 10px;font-size:clamp(1.6rem,3.6vw,2.4rem)">{esc(titre)}</h1>
  <p style="margin:0;max-width:760px;line-height:1.7;color:#effcff">{esc(p1)}</p>
</div>
<p style="line-height:1.7">{esc(p2)} {esc(p3)} {esc(nommee)}</p>
<section class="it-cmp tj-cmp" aria-label="Comparatif avec l'autoroute">
  <div class="glass-box"><h2>Par l'autoroute</h2>{colonne(A)}</div>
  <div class="glass-box win"><h2>Parcours découverte</h2>{colonne(D)}</div>
</section>
<p class="it-note">{esc(hyp)}, péage à 0,10 €/km sur les tronçons à péage. Montants indicatifs, mis à jour le {esc(maj)}.</p>
<p><a class="btn-compare" style="display:inline-block;text-decoration:none;width:auto;padding:14px 24px" href="{esc(lien_planificateur(d))}">Calculer avec mon véhicule</a></p>
<div id="itMap"></div>
{''.join(jours_html)}
<section class="glass-box it-seo" style="margin:24px 0"><h2 style="margin-top:0">Questions fréquentes</h2>{faq_html}</section>
{autres_html}
<p class="it-note">Les lieux et restaurants viennent d'OpenStreetMap et de Wikipédia : vérifiez les horaires avant de partir. Itinéraire calculé avec <a href="https://openrouteservice.org/" target="_blank" rel="noopener">OpenRouteService</a>, lieux via <a href="https://www.geoapify.com/" target="_blank" rel="noopener">Geoapify</a>, données &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors.</p>
{footer_html}
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const TR={carte};
const map=L.map("itMap");
L.tileLayer("https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png",{{maxZoom:18,attribution:"&copy; OpenStreetMap"}}).addTo(map);
const ligne=L.polyline(TR.c,{{color:"#075985",weight:5}}).addTo(map);
TR.n.slice(0,-1).forEach(p=>L.marker([p[0],p[1]]).addTo(map).bindPopup(p[2]));
TR.v.forEach(p=>L.circleMarker([p[0],p[1]],{{radius:6,color:"#c8322b",weight:2,fillColor:"#fff",fillOpacity:1}}).addTo(map).bindPopup(p[2]));
map.fitBounds(ligne.getBounds().pad(0.1));
</script>
</body>
</html>
"""


# ---------- Page d'index ----------

def page_index(pages, site_url, global_style, menu_html, footer_html, css):
    lignes = []
    for d, slug in pages:
        A, D, _, _, ev = couts(d)
        lignes.append(
            f'<tr><td><a href="{esc(slug)}.html">{esc(d["depart"]["nom"])} à {esc(d["arrivee"]["nom"])}</a>{" (électrique)" if ev else ""}</td>'
            f'<td>{round(D["km"])} km</td><td>{hms(D["total_sec"])}</td><td>{len(d["jours"])}</td><td>{eur(A["peage"])}</td></tr>')
    url = f"{site_url}/{PAGE_INDEX}"
    desc = ("Trajets sans autoroute en Europe : distance, durée, étapes, visites, restaurants et coût comparé à l'autoroute, "
            "pour une trentaine de trajets populaires.")
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Trajets sans autoroute en Europe : itinéraires et coût | MyHotelCompare</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(url)}">
<meta property="og:type" content="website">
<meta property="og:title" content="Trajets sans autoroute en Europe : itinéraires et coût">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(url)}">
{global_style}
<style>{css}
.tj-table{{width:100%;border-collapse:collapse}}
.tj-table th,.tj-table td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line)}}
.tj-wrap{{overflow-x:auto}}
</style>
</head>
<body><div class="container">
{menu_html}
<div class="hero-banner">
  <h1 style="color:#fff;margin:0 0 10px">Trajets sans autoroute en Europe</h1>
  <p style="margin:0;max-width:760px;line-height:1.7;color:#effcff">Pour chaque trajet : la distance, la durée, les étapes de conduite, des lieux à visiter, des restaurants et le coût comparé à l'autoroute. Votre trajet n'est pas dans la liste ? Calculez-le dans le <a style="color:#fff" href="itineraire-decouverte.html">planificateur d'itinéraires</a>.</p>
</div>
<div class="tj-wrap glass-box" style="margin:20px 0"><table class="tj-table">
<thead><tr><th>Trajet</th><th>Distance sans autoroute</th><th>Durée totale</th><th>Jours</th><th>Péages évités (estimation)</th></tr></thead>
<tbody>{''.join(lignes)}</tbody></table></div>
<p class="it-note">Estimations indicatives pour une conduite d'environ 4 h par jour. Détail et hypothèses sur chaque page.</p>
{footer_html}
</div></body></html>
"""


# ---------- Point d'entrée appelé par generateur.py ----------

def generate_trajets_pages(output_dir, global_style, menu_html, footer_html, site_url):
    if not LISTE.exists():
        print("Trajets : trajets.json introuvable, rien à générer.")
        return
    trajets = json.loads(LISTE.read_text(encoding="utf-8"))
    css = css_planificateur()
    pages, ignores = [], []
    for t in trajets:
        f = DATA / f"{t['slug']}.json"
        if not f.exists():
            ignores.append((t["slug"], "données absentes (lancez trajets_fetch.py)"))
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        if not qualite(d):
            ignores.append((t["slug"], "données insuffisantes"))
            continue
        pages.append((d, t["slug"]))
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for d, slug in pages:
        (out / f"{slug}.html").write_text(page_trajet(d, slug, trajets, site_url, global_style, menu_html, footer_html, css), encoding="utf-8")
    if pages:
        (out / PAGE_INDEX).write_text(page_index(pages, site_url, global_style, menu_html, footer_html, css), encoding="utf-8")
    print(f"Trajets : {len(pages)} page(s) générée(s), {len(ignores)} ignorée(s).")
    for slug, raison in ignores:
        print("  -", slug, ":", raison)