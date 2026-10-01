"""
Détecte les liens d'images cassés dans les fichiers JSON du projet.
Pour chaque image, envoie une requête HTTP pour vérifier qu'elle répond
correctement (code 200) et signale les erreurs (404, timeout, URL vide
ou malformée, etc.).

Usage :
    pip install requests
    python check_liens_casses.py

À lancer depuis la racine du projet (là où se trouvent les dossiers
"data" et "data_logements").
"""
import json
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Le module 'requests' n'est pas installé.")
    print("Lance d'abord : pip install requests")
    raise SystemExit(1)

BASE_DIR = Path(__file__).resolve().parent
DOSSIERS_A_SCANNER = ["data", "data_logements"]
TIMEOUT = 8  # secondes, avant d'abandonner une image trop lente
DELAI_ENTRE_REQUETES = 0.15  # petite pause pour ne pas spammer les serveurs

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def verifier_url(url):
    """Retourne (ok: bool, raison: str) pour une URL d'image donnée."""
    if not url or not url.strip():
        return False, "URL vide"
    if not url.startswith(("http://", "https://")):
        return None, "locale (non vérifiée par ce script)"
    try:
        # HEAD d'abord (plus rapide) ; certains serveurs le refusent, on bascule sur GET
        resp = requests.head(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if resp.status_code >= 400:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True)
        if resp.status_code == 200:
            return True, "OK"
        return False, f"Code HTTP {resp.status_code}"
    except requests.exceptions.Timeout:
        return False, "Timeout (trop lent ou ne répond pas)"
    except requests.exceptions.SSLError:
        return False, "Erreur SSL/certificat"
    except requests.exceptions.ConnectionError:
        return False, "Erreur de connexion (serveur injoignable)"
    except Exception as e:
        return False, f"Erreur : {e}"


def main():
    etablissements = []  # (fichier, nom, url)

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
                etablissements.append((f"{dossier_nom}/{fichier.name}", nom_etab, url_image))

    total = len(etablissements)
    print(f"Vérification de {total} image(s)... (ça peut prendre plusieurs minutes)\n")

    casses = []
    locales_ignorees = 0
    ok_count = 0

    for i, (fichier, nom, url) in enumerate(etablissements, 1):
        ok, raison = verifier_url(url)
        if ok is None:
            locales_ignorees += 1
        elif ok:
            ok_count += 1
        else:
            casses.append((fichier, nom, url, raison))
            print(f"❌ [{i}/{total}] {nom} ({fichier}) — {raison}")
        if i % 25 == 0:
            print(f"   ... {i}/{total} vérifiées")
        time.sleep(DELAI_ENTRE_REQUETES)

    print(f"\n{'='*70}")
    print("RÉSUMÉ")
    print(f"{'='*70}")
    print(f"  Images fonctionnelles      : {ok_count}")
    print(f"  Images locales (ignorées)  : {locales_ignorees}")
    print(f"  Images CASSÉES             : {len(casses)}")

    if casses:
        print(f"\n{'='*70}")
        print("DÉTAIL DES LIENS CASSÉS")
        print(f"{'='*70}")
        for fichier, nom, url, raison in casses:
            print(f"\n• {nom}")
            print(f"  Fichier : {fichier}")
            print(f"  Raison  : {raison}")
            print(f"  URL     : {url}")

        rapport_path = BASE_DIR / "liens_casses_rapport.json"
        rapport_path.write_text(
            json.dumps(
                [{"fichier": f, "nom": n, "url": u, "raison": r} for f, n, u, r in casses],
                ensure_ascii=False, indent=2
            ),
            encoding="utf-8"
        )
        print(f"\n📄 Rapport détaillé sauvegardé dans : {rapport_path.name}")
    else:
        print("\n✅ Aucun lien cassé détecté !")


if __name__ == "__main__":
    main()