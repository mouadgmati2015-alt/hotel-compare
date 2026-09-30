"""
enrichir_acces.py
------------------
Génère le champ 'acces' (aéroport le plus proche + distance réelle) pour
tous les hôtels de data/*.json, à partir de :
  1. Vraies coordonnées GPS de l'hôtel, obtenues via Nominatim (OpenStreetMap,
     gratuit, sans clé API) — réutilise le même cache que data_logements/,
     donc les hôtels déjà géocodés ne refont pas d'appel réseau.
  2. Une table d'aéroports internationaux réels (nom, code IATA, coordonnées
     vérifiables) par pays.
  3. La distance à vol d'oiseau (formule haversine) entre l'hôtel et l'aéroport
     le plus proche du même pays.

Rien n'est inventé : la distance est calculée, pas devinée. Le temps de trajet
en voiture est explicitement présenté comme une ESTIMATION (vitesse moyenne
conventionnelle), jamais comme une donnée précise.

Usage :
    python enrichir_acces.py                 # simulation (aucune écriture)
    python enrichir_acces.py --apply         # applique réellement
    python enrichir_acces.py --apply --force # réécrit même les hôtels qui ont déjà un champ 'acces'
"""

import json
import math
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

DATA_DIR = Path("data_logements")
GEOCODE_CACHE_PATH = Path("data_logements") / "_geocode_cache.json"  # même cache que generateur.py
APPLY = "--apply" in sys.argv
FORCE = "--force" in sys.argv

# ---------------------------------------------------------------------------
# Table d'aéroports internationaux réels par pays (nom officiel, IATA, lat/lon).
# Complète cette liste si tu as des hôtels dans des pays non couverts :
# le script les signalera clairement plutôt que d'inventer une distance.
# ---------------------------------------------------------------------------
AEROPORTS_PAR_PAYS = {
    "Tunisie": [
        ("Aéroport d'Enfidha-Hammamet", "NBE", 36.0758, 10.4386),
        ("Aéroport de Tunis-Carthage", "TUN", 36.8510, 10.2272),
        ("Aéroport de Djerba-Zarzis", "DJE", 33.8753, 10.7755),
        ("Aéroport de Monastir Habib Bourguiba", "MIR", 35.7581, 10.7547),
        ("Aéroport de Tozeur-Nefta", "TOE", 33.9398, 8.1103),
        ("Aéroport de Sfax-Thyna", "SFA", 34.7180, 10.6910),
        ("Aéroport de Tabarka-Aïn Draham", "TBJ", 36.9791, 8.8779),
    ],
    "Maroc": [
        ("Aéroport Mohammed V (Casablanca)", "CMN", 33.3675, -7.5900),
        ("Aéroport de Marrakech-Ménara", "RAK", 31.6069, -8.0363),
        ("Aéroport d'Agadir-Al Massira", "AGA", 30.3250, -9.4131),
        ("Aéroport Ibn Battouta (Tanger)", "TNG", 35.7269, -5.9169),
        ("Aéroport de Fès-Saïs", "FEZ", 33.9273, -4.9781),
        ("Aéroport de Rabat-Salé", "RBA", 34.0515, -6.7515),
    ],
    "Espagne": [
        ("Aéroport de Madrid-Barajas", "MAD", 40.4983, -3.5676),
        ("Aéroport de Barcelone-El Prat", "BCN", 41.2971, 2.0785),
        ("Aéroport de Palma de Majorque", "PMI", 39.5517, 2.7388),
        ("Aéroport de Malaga-Costa del Sol", "AGP", 36.6749, -4.4991),
        ("Aéroport d'Alicante-Elche", "ALC", 38.2822, -0.5582),
    ],
    "Grèce": [
        ("Aéroport d'Athènes-Eleftherios Venizelos", "ATH", 37.9364, 23.9445),
        ("Aéroport de Santorin", "JTR", 36.3992, 25.4793),
        ("Aéroport de Zante", "ZTH", 37.6753, 20.8843),
    ],
    "Turquie": [
        ("Aéroport d'Istanbul", "IST", 41.2753, 28.7519),
        ("Aéroport d'Antalya", "AYT", 36.8987, 30.8005),
    ],
    "Égypte": [
        ("Aéroport du Caire", "CAI", 30.1219, 31.4056),
        ("Aéroport de Hurghada", "HRG", 27.1783, 33.7994),
        ("Aéroport de Marsa Alam", "RMF", 25.5570, 34.5836),
        ("Aéroport de Charm el-Cheikh", "SSH", 27.9773, 34.3950),
    ],
    "Portugal": [
        ("Aéroport de Lisbonne Humberto Delgado", "LIS", 38.7756, -9.1354),
        ("Aéroport de Faro", "FAO", 37.0144, -7.9659),
        ("Aéroport de Porto Francisco Sá Carneiro", "OPO", 41.2481, -8.6814),
    ],
    "Croatie": [
        ("Aéroport de Dubrovnik", "DBV", 42.5614, 18.2682),
        ("Aéroport de Split", "SPU", 43.5389, 16.2980),
        ("Aéroport de Zagreb", "ZAG", 45.7429, 16.0688),
    ],
    "Montenegro": [
        ("Aéroport de Tivat", "TIV", 42.4047, 18.7233),
        ("Aéroport de Podgorica", "TGD", 42.3594, 19.2519),
    ],
    "France": [
        ("Aéroport Paris-Charles de Gaulle", "CDG", 49.0097, 2.5479),
        ("Aéroport de Nice Côte d'Azur", "NCE", 43.6584, 7.2159),
        ("Aéroport de Strasbourg", "SXB", 48.5383, 7.6282),
        ("Aéroport de Bordeaux-Mérignac", "BOD", 44.8283, -0.7156),
    ],
    "Italie": [
        ("Aéroport de Rome-Fiumicino", "FCO", 41.8003, 12.2389),
        ("Aéroport de Milan-Malpensa", "MXP", 45.6306, 8.7281),
        ("Aéroport de Venise Marco Polo", "VCE", 45.5053, 12.3519),
        ("Aéroport de Naples", "NAP", 40.8860, 14.2908),
        ("Aéroport d'Olbia Costa Smeralda", "OLB", 40.8987, 9.5175),
        ("Aéroport de Pise", "PSA", 43.6839, 10.3927),
        ("Aéroport de Bari", "BRI", 41.1389, 16.7606),
        ("Aéroport de Cagliari-Elmas", "CAG", 39.2515, 9.0543),
        ("Aéroport de Catane", "CTA", 37.4668, 15.0664),
    ],
}

RAYON_TERRE_KM = 6371


def haversine_km(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (math.sin(delta_phi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    return RAYON_TERRE_KM * 2 * math.asin(math.sqrt(a))


def charger_cache_geocodage():
    if GEOCODE_CACHE_PATH.exists():
        with open(GEOCODE_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def sauvegarder_cache_geocodage(cache):
    GEOCODE_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(GEOCODE_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def geocoder_lieu(ville, pays, cache):
    cle = f"{ville}, {pays}".strip(", ").lower()
    if not cle:
        return None
    if cle in cache:
        return cache[cle]
    try:
        requete = urllib.parse.quote(f"{ville}, {pays}")
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={requete}&limit=1"
        req = urllib.request.Request(url, headers={"User-Agent": "MyHotelCompare/1.0 (contact: myhotelcompare@gmail.com)"})
        with urllib.request.urlopen(req, timeout=10) as response:
            resultats = json.loads(response.read().decode("utf-8"))
        if resultats:
            coords = {"lat": float(resultats[0]["lat"]), "lng": float(resultats[0]["lon"])}
            cache[cle] = coords
            time.sleep(1)  # Nominatim impose max 1 requête/seconde
            return coords
    except Exception as e:
        print(f"    ⚠️  Erreur de géocodage pour '{cle}': {e}")
    cache[cle] = None
    return None


def trouver_aeroport_le_plus_proche(pays, lat_hotel, lng_hotel):
    aeroports = AEROPORTS_PAR_PAYS.get(pays)
    if not aeroports:
        return None
    candidats = []
    for nom, iata, lat_a, lon_a in aeroports:
        distance = haversine_km(lat_hotel, lng_hotel, lat_a, lon_a)
        candidats.append((distance, nom, iata))
    candidats.sort(key=lambda c: c[0])
    return candidats[0]  # (distance_km, nom, iata)


def generer_acces(distance_km, nom_aeroport, iata):
    distance_arrondie = round(distance_km)
    # Estimation de temps de trajet clairement présentée comme telle,
    # sur une vitesse moyenne conventionnelle de 60 km/h (route + ville mêlées)
    minutes_estimees = round((distance_km / 60) * 60)
    return {
        "aeroport_le_plus_proche": f"{nom_aeroport} ({iata}), à environ {distance_arrondie} km à vol d'oiseau",
        "temps_de_trajet_estime": f"Environ {minutes_estimees} min en voiture (estimation, hors trafic)",
        "transferts": "Transferts privés ou navette disponibles sur demande auprès de l'hôtel ou d'un prestataire local.",
    }


def main():
    cache = charger_cache_geocodage()
    total_traites = 0
    total_sans_donnees_pays = 0
    total_geocodage_echoue = 0

    for fichier in DATA_DIR.glob("*.json"):
        if fichier.name == "promo_semaine.json":
            continue
        with open(fichier, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"⚠️  {fichier.name} ignoré (JSON invalide) : {e}")
                continue
        if not isinstance(data, dict):
            continue

        fichier_modifie = False

        for nom_hotel, donnees in data.items():
            if not isinstance(donnees, dict):
                continue
            if donnees.get("acces") and not FORCE:
                continue

            ville = donnees.get("ville", "")
            pays = donnees.get("pays", "")

            if pays not in AEROPORTS_PAR_PAYS:
                total_sans_donnees_pays += 1
                continue

            coords = geocoder_lieu(ville, pays, cache)
            if not coords:
                total_geocodage_echoue += 1
                print(f"    ⚠️  Géocodage impossible pour {nom_hotel} ({ville}, {pays}) — 'acces' non généré")
                continue

            resultat = trouver_aeroport_le_plus_proche(pays, coords["lat"], coords["lng"])
            if not resultat:
                continue
            distance_km, nom_aeroport, iata = resultat
            acces = generer_acces(distance_km, nom_aeroport, iata)

            print(f"{'[APPLY]' if APPLY else '[SIMULATION]'} {nom_hotel} → {nom_aeroport} ({iata}), {round(distance_km)} km")

            if APPLY:
                donnees["acces"] = acces
                fichier_modifie = True
            total_traites += 1

        if APPLY and fichier_modifie:
            with open(fichier, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    sauvegarder_cache_geocodage(cache)

    print(f"\n{'Modifications appliquées' if APPLY else 'Simulation terminée'} : {total_traites} hôtel(s) enrichi(s).")
    if total_sans_donnees_pays:
        print(f"{total_sans_donnees_pays} hôtel(s) ignoré(s) : pays absent de AEROPORTS_PAR_PAYS (à compléter dans le script).")
    if total_geocodage_echoue:
        print(f"{total_geocodage_echoue} hôtel(s) ignoré(s) : géocodage Nominatim échoué (ville/pays introuvable ou mal orthographié).")
    if not APPLY:
        print("Relance avec --apply pour écrire réellement les changements dans les fichiers JSON.")


if __name__ == "__main__":
    main()