"""
compresser_images.py
----------------------
Redimensionne et compresse les images du dossier images/ (et ses sous-dossiers,
comme les photos de logements atypiques) pour réduire le poids des pages.

- Ne touche jamais aux .svg, .ico, ni au dossier favicon_io/
- Redimensionne toute image dont la largeur dépasse LARGEUR_MAX
- Recompresse en JPEG qualité 82 (bon compromis visuel/poids) ou PNG optimisé
- Saute les fichiers déjà sous SEUIL_KO (pas la peine d'y toucher)

Usage :
    python compresser_images.py                  # simulation (aucune écriture)
    python compresser_images.py --apply           # applique réellement
"""

import sys
from pathlib import Path
from PIL import Image

DOSSIER_IMAGES = Path("images")
LARGEUR_MAX = 1920
SEUIL_KO = 200  # en dessous, on ne touche pas au fichier
QUALITE_JPEG = 82
APPLY = "--apply" in sys.argv

EXTENSIONS = {".jpg", ".jpeg", ".png"}
DOSSIERS_EXCLUS = {"favicon_io"}


def traiter_image(chemin):
    taille_avant_ko = chemin.stat().st_size / 1024
    if taille_avant_ko < SEUIL_KO:
        return None  # déjà léger, on ne touche pas

    try:
        img = Image.open(chemin)
    except Exception as e:
        print(f"    ⚠️  Impossible d'ouvrir {chemin.name} : {e}")
        return None

    img_originale_mode = img.mode
    largeur, hauteur = img.size
    redimensionnee = False
    if largeur > LARGEUR_MAX:
        ratio = LARGEUR_MAX / largeur
        img = img.resize((LARGEUR_MAX, int(hauteur * ratio)), Image.LANCZOS)
        redimensionnee = True

    if APPLY:
        if chemin.suffix.lower() in (".jpg", ".jpeg"):
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(chemin, "JPEG", quality=QUALITE_JPEG, optimize=True)
        else:  # .png
            img.save(chemin, "PNG", optimize=True)

    taille_apres_ko = chemin.stat().st_size / 1024 if APPLY else None
    return {
        "redimensionnee": redimensionnee,
        "avant_ko": taille_avant_ko,
        "apres_ko": taille_apres_ko,
    }


def main():
    if not DOSSIER_IMAGES.exists():
        print("Dossier images/ introuvable — lance ce script depuis la racine du projet.")
        sys.exit(1)

    total_avant = 0
    total_apres = 0
    total_traitees = 0

    for chemin in DOSSIER_IMAGES.rglob("*"):
        if chemin.is_dir():
            continue
        if any(dossier_exclu in chemin.parts for dossier_exclu in DOSSIERS_EXCLUS):
            continue
        if chemin.suffix.lower() not in EXTENSIONS:
            continue

        resultat = traiter_image(chemin)
        if resultat is None:
            continue

        total_traitees += 1
        total_avant += resultat["avant_ko"]
        info = f"{resultat['avant_ko']:.0f} Ko"
        if resultat["redimensionnee"]:
            info += " (redimensionnée)"
        if APPLY:
            total_apres += resultat["apres_ko"]
            info += f" → {resultat['apres_ko']:.0f} Ko"
        print(f"{'[APPLY]' if APPLY else '[SIMULATION]'} {chemin.relative_to(DOSSIER_IMAGES)} : {info}")

    print(f"\n{total_traitees} image(s) {'compressée(s)' if APPLY else 'à compresser'}.")
    print(f"Poids total avant : {total_avant/1024:.1f} Mo")
    if APPLY:
        print(f"Poids total après : {total_apres/1024:.1f} Mo")
        if total_avant > 0:
            print(f"Économie : {(total_avant - total_apres)/1024:.1f} Mo ({(1 - total_apres/total_avant)*100:.0f}%)")
    else:
        print("Relance avec --apply pour compresser réellement les fichiers.")


if __name__ == "__main__":
    main()