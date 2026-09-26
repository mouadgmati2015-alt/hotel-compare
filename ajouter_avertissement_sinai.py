"""
ajouter_avertissement_sinai.py
--------------------------------
Ajoute un avertissement spécial sur le tampon gratuit "Sinaï uniquement"
à tous les hôtels dont l'aéroport le plus proche est Charm el-Cheikh (SSH),
c'est-à-dire les hôtels du Sud-Sinaï (Charm el-Cheikh, Dahab, Nuweiba, Taba,
Sainte-Catherine).

Usage :
    python ajouter_avertissement_sinai.py                 # simulation
    python ajouter_avertissement_sinai.py --apply          # applique réellement
"""

import json
import sys
from pathlib import Path

DATA_DIR = Path("data")
APPLY = "--apply" in sys.argv

TEXTE_AVERTISSEMENT = (
    "Bon à savoir : si vous restez uniquement dans le Sud-Sinaï (Charm el-Cheikh, "
    "Dahab, Nuweiba, Taba ou Sainte-Catherine) sans vous rendre au Caire, à Louxor, "
    "à Hurghada ou même au parc national de Ras Mohammed, vous pouvez recevoir "
    "gratuitement à l'arrivée un tampon « Sinaï uniquement », valable environ 14 jours "
    "— même si votre nationalité nécessite normalement un visa pour l'Égypte. "
    "Si vous quittez cette zone ou dépassez cette durée, un visa complet est obligatoire. "
    "Les règles ayant été resserrées en 2025, confirmez ce point avant de partir."
)

def main():
    total = 0
    for fichier in DATA_DIR.glob("*.json"):
        if fichier.name == "promo_semaine.json":
            continue
        with open(fichier, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue
        if not isinstance(data, dict):
            continue

        modifie = False
        for nom_hotel, donnees in data.items():
            if not isinstance(donnees, dict):
                continue
            acces = donnees.get("acces") or {}
            aeroport = str(acces.get("aeroport_le_plus_proche", ""))
            if "Charm el-Cheikh" in aeroport or "SSH" in aeroport:
                print(f"{'[APPLY]' if APPLY else '[SIMULATION]'} {nom_hotel} ({fichier.name})")
                if APPLY:
                    donnees["avertissement_visa_sinai"] = TEXTE_AVERTISSEMENT
                    modifie = True
                total += 1

        if APPLY and modifie:
            with open(fichier, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"\n{total} hôtel(s) du Sud-Sinaï concerné(s).")
    if not APPLY:
        print("Relance avec --apply pour écrire réellement les changements.")

if __name__ == "__main__":
    main()