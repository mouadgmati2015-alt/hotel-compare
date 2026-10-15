"""Récupère les données de chaque trajet de trajets.json auprès du Worker et les enregistre dans data_trajets/.

À lancer en local, une fois (puis environ une fois par mois) :
    python trajets_fetch.py --limit 2        # essai sur 2 trajets
    python trajets_fetch.py                  # tous les trajets manquants
    python trajets_fetch.py --force          # tout recalculer
    python trajets_fetch.py --only paris-nice-sans-autoroute,lyon-milan-sans-autoroute

Le script reprend là où il s'est arrêté : un trajet déjà enregistré n'est pas recalculé.
"""
import datetime
import json
import math
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from itineraire import WORKER_URL  # même adresse que la page du planificateur

BASE = Path(__file__).resolve().parent
DATA = BASE / "data_trajets"
LISTE = BASE / "trajets.json"
ORIGINE = "https://myhotelcompare.com"  # origine autorisée par le Worker (ALLOWED_ORIGINS)
RYTHME_H = 4        # heures de conduite par jour, comme dans le planificateur
PAUSE = 1.0         # secondes entre deux appels (le Worker limite à 90 requêtes par minute et par adresse)


# ---------- Appels au Worker ----------

def appel(corps, essais=4):
    donnees = json.dumps(corps).encode("utf-8")
    for n in range(essais):
        req = urllib.request.Request(
            WORKER_URL, data=donnees, method="POST",
            headers={"Content-Type": "application/json", "Origin": ORIGINE, "User-Agent": "MyHotelCompare-generateur/1.0"},
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                res = json.loads(r.read().decode("utf-8"))
            time.sleep(PAUSE)
            return res
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "ignore")[:200]
            if e.code in (429, 502, 503, 504) and n < essais - 1:
                time.sleep(6 * (n + 1))
                continue
            raise RuntimeError(f"Worker {e.code} : {detail}")
        except (urllib.error.URLError, TimeoutError) as e:
            if n < essais - 1:
                time.sleep(6 * (n + 1))
                continue
            raise RuntimeError(f"Réseau : {e}")


# ---------- Même logique que la page du planificateur (itineraire.py) ----------

def km2(a, b):
    t = math.pi / 180
    x = math.sin((b[1] - a[1]) * t / 2) ** 2 + math.cos(a[1] * t) * math.cos(b[1] * t) * math.sin((b[0] - a[0]) * t / 2) ** 2
    return 12742 * math.asin(math.sqrt(x))


REF = re.compile(r"^\s*(RN|RD|SS|SP|SR|N|D|B|A|L|K|S|C)\s*[-.]?\s*(\d{1,4})\s*[A-Za-z]*\s*$", re.I)


def road_ref(nom):
    """Numéro de route lu dans le nom d'un tronçon : (type, libellé) ou None."""
    for part in re.split(r"[,;/]", str(nom)):
        m = REF.match(part)
        if m:
            kind = "N" if re.fullmatch(r"RN|SS|N|B|A", m.group(1), re.I) else "D"
            pref = re.sub(r"^R([ND])$", r"\1", m.group(1).upper())
            return kind, pref + m.group(2)
    return None


def ville_etape(steps, cum, cible, prev):
    idx0 = next((i for i, x in enumerate(cum) if x >= cible), len(steps) - 2)
    idx0 = max(idx0, prev + 1)
    while idx0 > prev + 1 and idx0 < len(steps) and steps[idx0].get("f"):
        idx0 -= 1
    try:
        v = appel({"action": "etape", "pt": steps[min(idx0, len(steps) - 1)]["c"]})
    except RuntimeError as e:
        print("    ville d'étape introuvable :", e)
        return None
    best, bd = -1, 1e9
    for i, s in enumerate(steps):
        if prev < i < len(steps) - 1 and not s.get("f") and abs(cum[i] - cible) <= 2400:
            d = km2(s["c"], [v["lon"], v["lat"]])
            if d < bd:
                bd, best = d, i
    return {"idx": best if best >= 0 else idx0, "nom": v["nom"], "pays": v.get("pays", ""), "c": [v["lon"], v["lat"]]}


def decouper_villes(steps, nb, fin_nom, fin_pays, arr_c):
    total = sum(s["s"] for s in steps)
    cum, t = [], 0
    for s in steps:
        t += s["s"]
        cum.append(t)
    coupes, villes, prev = [], [], -1
    for k in range(1, nb):
        cible = k * total / nb
        r = ville_etape(steps, cum, cible, prev)
        if not r:
            idx = next((i for i, x in enumerate(cum) if x >= cible), len(steps) - 2)
            if idx <= prev:
                idx = prev + 1
            idx = min(idx, len(steps) - 2)
            r = {"idx": idx, "nom": f"Étape {k}", "pays": "", "c": steps[idx]["c"]}
        coupes.append(r["idx"])
        villes.append({"nom": r["nom"], "pays": r["pays"], "lon": r["c"][0], "lat": r["c"][1]})
        prev = r["idx"]
    jours, a = [], 0
    for i in coupes:
        jours.append(steps[a:i + 1])
        a = i + 1
    jours.append(steps[a:])
    villes.append({"nom": fin_nom, "pays": fin_pays, "lon": arr_c[0], "lat": arr_c[1]})
    return jours, villes


# ---------- Construction des données d'un trajet ----------

def construire(t):
    d, a = t["depart"], t["arrivee"]
    ev = t["vehicule"] == "electrique"
    route = appel({"depart": [d["lon"], d["lat"]], "arrivee": [a["lon"], a["lat"]]})
    time.sleep(2)  # OpenRouteService limite le nombre de calculs par minute
    dec, aut = route["decouverte"], route["autoroute"]
    steps = dec.get("steps") or []
    if not steps:
        raise RuntimeError("aucune étape renvoyée")
    nb = max(1, math.ceil(dec["sec"] / (RYTHME_H * 3600)))
    jours, villes = decouper_villes(steps, nb, a["nom"], a["pays"], [a["lon"], a["lat"]])

    sortie = []
    for k, st in enumerate(jours):
        print(f"    jour {k + 1}/{len(jours)} : {villes[k]['nom']}")
        rt = [s for s in st if not s.get("f")]
        debut = [d["lon"], d["lat"]] if k == 0 else jours[k - 1][-1]["c"]
        pas = max(1, math.ceil(len(rt) / 25))
        poly = [debut] + [s["c"] for i, s in enumerate(rt) if i % pas == 0]
        tot = sum(s["s"] for s in rt)
        cumul, midi = 0, (rt[0] if rt else st[0])["c"]
        for s in rt:
            cumul += s["s"]
            if cumul >= tot / 2:
                midi = s["c"]
                break
        lieux = None
        if len(poly) >= 2:
            try:
                lieux = appel({"action": "lieux", "poly": poly, "midi": midi, "fin": st[-1]["c"], "ev": ev})
            except RuntimeError as e:
                print("    lieux indisponibles :", e)
        routes = {}
        for s in st:
            r = road_ref(s["n"])
            if r:
                routes[r] = routes.get(r, 0) + s["d"]
        top = sorted(routes.items(), key=lambda kv: -kv[1])[:6]
        sortie.append({
            "fin": villes[k],
            "km": round(sum(s["d"] for s in rt) / 1000, 1),
            "sec": sum(s["s"] for s in st),
            "ferry_km": round(sum(s["d"] for s in st if s.get("f")) / 1000, 1),
            "routes": [[ref, kind, round(m / 1000, 1)] for (kind, ref), m in top],
            "lieux": lieux,
        })
    coords = dec.get("coords") or []
    pas = max(1, math.ceil(len(coords) / 400))
    return {
        "slug": t["slug"], "titre": t["titre"], "vehicule": t["vehicule"],
        "depart": d, "arrivee": a,
        "autoroute": aut,
        "decouverte": {"km": dec["km"], "sec": dec["sec"], "ferry": dec.get("ferry"), "coords": coords[::pas] + ([coords[-1]] if coords and (len(coords) - 1) % pas else [])},
        "jours": sortie,
        "genere": datetime.date.today().isoformat(),
    }


def main():
    args = sys.argv[1:]
    force = "--force" in args
    limite = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    only = set(args[args.index("--only") + 1].split(",")) if "--only" in args else None
    DATA.mkdir(exist_ok=True)
    trajets = json.loads(LISTE.read_text(encoding="utf-8"))
    if only:
        trajets = [t for t in trajets if t["slug"] in only]
    faits, echecs, deja = 0, [], 0
    for t in trajets:
        fichier = DATA / f"{t['slug']}.json"
        if fichier.exists() and not force:
            deja += 1
            continue
        if limite is not None and faits >= limite:
            break
        print(f"[{faits + 1}] {t['titre']}")
        try:
            donnees = construire(t)
            fichier.write_text(json.dumps(donnees, ensure_ascii=False), encoding="utf-8")
            faits += 1
        except Exception as e:  # on continue avec le trajet suivant
            print("    ÉCHEC :", e)
            echecs.append((t["slug"], str(e)))
    print(f"\nTerminé : {faits} trajet(s) enregistré(s), {deja} déjà présent(s), {len(echecs)} échec(s).")
    for slug, e in echecs:
        print("  -", slug, ":", e)
    if echecs:
        print("Relancez la même commande pour retenter les trajets en échec.")


if __name__ == "__main__":
    main()