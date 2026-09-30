"""
enrichir_fiches_logements.py
------------------------------
Version de enrichir_fiches.py pointée sur data_logements/ au lieu de data/.
Ajoute automatiquement 'faq', 'environs' et 'hotels_similaires' à tous les
logements atypiques qui ne les ont pas encore.

Usage :
    python enrichir_fiches_logements.py                 # simulation
    python enrichir_fiches_logements.py --apply          # applique réellement
    python enrichir_fiches_logements.py --apply --force  # réécrit même l'existant
"""

import hashlib
import json
import sys
from pathlib import Path

DATA_DIR = Path("data_logements")
APPLY = "--apply" in sys.argv
FORCE = "--force" in sys.argv


def index_stable(cle, nb_variantes):
    if nb_variantes <= 1:
        return 0
    h = int(hashlib.sha256(cle.encode("utf-8")).hexdigest(), 16)
    return h % nb_variantes


def charger_tous_les_logements():
    logements_par_fichier = {}
    for fichier in DATA_DIR.glob("*.json"):
        if fichier.name == "_geocode_cache.json":
            continue
        with open(fichier, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"⚠️  {fichier.name} ignoré (JSON invalide) : {e}")
                continue
        if isinstance(data, dict):
            logements_par_fichier[fichier] = data
    return logements_par_fichier


def generer_logements_similaires(nom_logement, donnees, tous_les_logements_plats):
    """Uniquement des logements réels de la MÊME VILLE."""
    ville = donnees.get("ville", "")
    if not ville:
        return []
    memes_villes = [
        nom for nom, d in tous_les_logements_plats.items()
        if nom != nom_logement and d.get("ville") == ville
    ]
    return memes_villes[:3]


ENVIRONS_TEMPLATES = [
    "Ce logement est situé à {lieu}, une destination qui propose ses propres attractions, commerces et lieux de restauration à proximité.",
    "Implanté à {lieu}, l'établissement permet de rayonner facilement vers les attractions, commerces et restaurants du secteur.",
    "{lieu} accueille ce logement et offre à proximité un choix de commerces, de restaurants et de points d'intérêt à explorer.",
    "Ce logement se trouve à {lieu}, où l'on trouve à proximité diverses attractions locales, commerces et adresses de restauration.",
]


def generer_environs(nom_logement, donnees):
    ville = donnees.get("ville", "")
    pays = donnees.get("pays", "")
    if not ville and not pays:
        return ""
    lieu = f"{ville}, {pays}".strip(", ")
    template = ENVIRONS_TEMPLATES[index_stable(nom_logement + "|environs", len(ENVIRONS_TEMPLATES))]
    return template.format(lieu=lieu)


FAQ_PERIODE_TEMPLATES = [
    "Cela dépend de la saison touristique locale ; consultez les tendances climatiques de la destination avant de réserver.",
    "Le climat varie selon les mois ; il est conseillé de vérifier la météo saisonnière de {ville} avant de fixer vos dates.",
    "La période idéale dépend de vos préférences climatiques ; renseignez-vous sur les moyennes saisonnières de {ville}.",
]


def generer_faq(nom_logement, donnees):
    equipements = [str(e).lower() for e in (donnees.get("equipements") or [])]
    ville = donnees.get("ville", "cette destination")
    faq = []

    if any("piscine" in e for e in equipements):
        faq.append({
            "question": "Le logement dispose-t-il d'une piscine ?",
            "reponse": f"Oui, {nom_logement} dispose d'une piscine parmi ses équipements."
        })
    if any("plage" in e for e in equipements):
        faq.append({
            "question": "Le logement est-il en bord de mer ?",
            "reponse": f"Oui, {nom_logement} propose un accès plage parmi ses équipements."
        })
    if any("spa" in e for e in equipements):
        faq.append({
            "question": "Y a-t-il un spa sur place ?",
            "reponse": f"Oui, un spa fait partie des équipements de {nom_logement}."
        })

    idx_periode = index_stable(nom_logement + "|periode", len(FAQ_PERIODE_TEMPLATES))
    faq.append({
        "question": f"Quelle est la meilleure période pour séjourner à {ville} ?",
        "reponse": FAQ_PERIODE_TEMPLATES[idx_periode].format(ville=ville)
    })

    return faq[:4]


def main():
    logements_par_fichier = charger_tous_les_logements()

    tous_les_logements_plats = {}
    for data in logements_par_fichier.values():
        for nom, d in data.items():
            if isinstance(d, dict):
                tous_les_logements_plats[nom] = d

    total_modifies = 0
    total_fichiers_modifies = 0
    total_sans_similaires = 0

    for fichier, data in logements_par_fichier.items():
        fichier_modifie = False

        for nom_logement, donnees in data.items():
            if not isinstance(donnees, dict):
                continue

            deja_enrichi = donnees.get("faq") or donnees.get("environs") or donnees.get("hotels_similaires")
            if deja_enrichi and not FORCE:
                continue

            similaires = generer_logements_similaires(nom_logement, donnees, tous_les_logements_plats)
            if not similaires:
                total_sans_similaires += 1

            nouvelles_valeurs = {
                "faq": generer_faq(nom_logement, donnees),
                "environs": generer_environs(nom_logement, donnees),
                "hotels_similaires": similaires,
            }

            print(f"{'[APPLY]' if APPLY else '[SIMULATION]'} {nom_logement} ({fichier.name})")
            for cle, valeur in nouvelles_valeurs.items():
                apercu = json.dumps(valeur, ensure_ascii=False)
                print(f"    + {cle}: {apercu[:120]}{'...' if len(apercu) > 120 else ''}")

            if APPLY:
                donnees.update(nouvelles_valeurs)
                fichier_modifie = True
            total_modifies += 1

        if APPLY and fichier_modifie:
            with open(fichier, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            total_fichiers_modifies += 1

    print(f"\n{'Modifications appliquées' if APPLY else 'Simulation terminée'} : {total_modifies} logement(s) concerné(s).")
    print(f"  dont {total_sans_similaires} logement(s) sans logement similaire réel dans la même ville (laissé vide, c'est normal).")
    if APPLY:
        print(f"{total_fichiers_modifies} fichier(s) réécrit(s) dans data_logements/.")
    else:
        print("Relance avec --apply pour écrire réellement les changements.")


if __name__ == "__main__":
    main()