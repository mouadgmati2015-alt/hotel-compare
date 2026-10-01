"""
Audit des sources d'images dans les fichiers JSON du projet.
Classe chaque image par domaine (Booking, Expedia, site propre de l'hôtel,
image locale, ou autre/inconnu) pour évaluer le risque légal et préparer
une éventuelle migration vers un hébergement local des images.

Usage :
    python audit_images.py

À lancer depuis la racine du projet (là où se trouvent les dossiers
"data" et "data_logements").
"""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent
DOSSIERS_A_SCANNER = ["data", "data_logements"]

# Domaines qu'on reconnaît comme "programme d'affiliation" (risque a priori plus faible,
# sous réserve de respecter les conditions du programme d'affiliation concerné)
DOMAINES_BOOKING = ["bstatic.com", "booking.com"]
DOMAINES_EXPEDIA = ["trvl-media.com", "expedia.fr", "expedia.com", "expediastatic.com"]

def categoriser(url):
    if not url:
        return "vide"
    if not url.startswith(("http://", "https://")):
        return "locale (déjà dans ton dossier images/)"
    domaine = urlparse(url).netloc.lower()
    if any(d in domaine for d in DOMAINES_BOOKING):
        return "Booking.com"
    if any(d in domaine for d in DOMAINES_EXPEDIA):
        return "Expedia"
    return f"AUTRE SOURCE ({domaine})"

def main():
    resultats = {}  # categorie -> liste de (fichier, nom_etablissement, url)

    for dossier_nom in DOSSIERS_A_SCANNER:
        dossier = BASE_DIR / dossier_nom
        if not dossier.exists():
            continue
        for fichier in sorted(dossier.glob("*.json")):
            if fichier.name.startswith("_"):
                continue
            try:
                data = json.loads(fichier.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"⚠️  Impossible de lire {fichier.name} : {e}")
                continue
            if not isinstance(data, dict):
                continue
            for nom_etab, details in data.items():
                if not isinstance(details, dict):
                    continue
                url_image = details.get("image", "")
                categorie = categoriser(url_image)
                resultats.setdefault(categorie, []).append(
                    (f"{dossier_nom}/{fichier.name}", nom_etab, url_image)
                )

    # --- Rapport ---
    total = sum(len(v) for v in resultats.values())
    print(f"\n{'='*70}")
    print(f"AUDIT DES SOURCES D'IMAGES — {total} établissement(s) analysé(s)")
    print(f"{'='*70}\n")

    ordre_affichage = ["Booking.com", "Expedia", "locale (déjà dans ton dossier images/)", "vide"]
    autres = sorted(k for k in resultats if k not in ordre_affichage)

    for categorie in ordre_affichage + autres:
        if categorie not in resultats:
            continue
        entrees = resultats[categorie]
        print(f"\n### {categorie} — {len(entrees)} image(s) ###")
        for fichier, nom, url in entrees[:200]:  # évite un flot infini à l'écran
            print(f"  - [{fichier}] {nom}")
            if categorie.startswith("AUTRE SOURCE"):
                print(f"      {url}")

    print(f"\n{'='*70}")
    print("RÉSUMÉ")
    print(f"{'='*70}")
    for categorie in ordre_affichage + autres:
        if categorie in resultats:
            print(f"  {categorie:45s} : {len(resultats[categorie])}")

    # Sauvegarde aussi un rapport JSON exploitable
    rapport_path = BASE_DIR / "audit_images_rapport.json"
    rapport_json = {
        cat: [{"fichier": f, "nom": n, "url": u} for f, n, u in entrees]
        for cat, entrees in resultats.items()
    }
    rapport_path.write_text(json.dumps(rapport_json, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n📄 Rapport détaillé sauvegardé dans : {rapport_path.name}")

if __name__ == "__main__":
    main()