"""
enrichir_fiches.py
-------------------
Ajoute automatiquement les champs 'faq', 'environs' et 'hotels_similaires'
à tous les hôtels de data/*.json qui ne les ont pas encore.

Ne génère QUE du contenu basé sur des données déjà réelles dans le JSON
(ville, pays, équipements, autres hôtels du même endroit) — aucune donnée
inventée (pas de distance d'aéroport, pas de prix fictif).

v2 : corrige deux problèmes identifiés en simulation :
  - hotels_similaires ne fait plus de repli "même pays" (qui suggérait des
    hôtels à 300-500 km sans rapport géographique réel) : si aucun hôtel de
    la même ville n'existe, la liste reste vide plutôt que trompeuse.
  - faq et environs piochent parmi plusieurs formulations (choisies de façon
    stable via un hash du nom d'hôtel) pour limiter le contenu quasi-dupliqué
    d'une fiche à l'autre, qui pourrait être pénalisé par Google.

Usage :
    python enrichir_fiches.py                # mode simulation (aucune écriture)
    python enrichir_fiches.py --apply         # applique réellement les changements
    python enrichir_fiches.py --apply --force # réécrit même les hôtels qui ont déjà une faq
"""

import hashlib
import json
import sys
from pathlib import Path

DATA_DIR = Path("data_logements")
APPLY = "--apply" in sys.argv
FORCE = "--force" in sys.argv


def index_stable(cle, nb_variantes):
    """Choisit un index de façon stable (toujours le même pour un même hôtel),
    pour varier les formulations sans que ça change à chaque exécution."""
    if nb_variantes <= 1:
        return 0
    h = int(hashlib.sha256(cle.encode("utf-8")).hexdigest(), 16)
    return h % nb_variantes


def charger_tous_les_hotels():
    hotels_par_fichier = {}
    for fichier in DATA_DIR.glob("*.json"):
        if fichier.name == "promo_semaine.json":
            continue
        with open(fichier, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"⚠️  {fichier.name} ignoré (JSON invalide) : {e}")
                continue
        if isinstance(data, dict):
            hotels_par_fichier[fichier] = data
    return hotels_par_fichier


def generer_hotels_similaires(nom_hotel, donnees, tous_les_hotels_plats):
    """Uniquement des hôtels réels de la MÊME VILLE. Pas de repli par pays :
    un hôtel à 400 km n'est pas un hôtel 'similaire' pertinent."""
    ville = donnees.get("ville", "")
    if not ville:
        return []
    memes_villes = [
        nom for nom, d in tous_les_hotels_plats.items()
        if nom != nom_hotel and d.get("ville") == ville
    ]
    return memes_villes[:3]


ENVIRONS_TEMPLATES = [
    "L'hôtel est situé à {lieu}, une destination qui propose ses propres attractions, commerces et lieux de restauration à proximité.",
    "Implanté à {lieu}, l'établissement permet de rayonner facilement vers les attractions, commerces et restaurants du secteur.",
    "{lieu} accueille cet établissement et offre à proximité un choix de commerces, de restaurants et de points d'intérêt à explorer.",
    "Cet hôtel se trouve à {lieu}, où l'on trouve à proximité diverses attractions locales, commerces et adresses de restauration.",
]


def generer_environs(nom_hotel, donnees):
    ville = donnees.get("ville", "")
    pays = donnees.get("pays", "")
    if not ville and not pays:
        return ""
    lieu = f"{ville}, {pays}".strip(", ")
    template = ENVIRONS_TEMPLATES[index_stable(nom_hotel + "|environs", len(ENVIRONS_TEMPLATES))]
    return template.format(lieu=lieu)


FAQ_PERIODE_TEMPLATES = [
    "Cela dépend de la saison touristique locale ; consultez les tendances climatiques de la destination avant de réserver.",
    "Le climat varie selon les mois ; il est conseillé de vérifier la météo saisonnière de {ville} avant de fixer vos dates.",
    "La période idéale dépend de vos préférences climatiques ; renseignez-vous sur les moyennes saisonnières de {ville}.",
]

FAQ_INCLUSIVE_TEMPLATES = [
    "L'établissement propose une formule All Inclusive ; le détail exact des prestations incluses est à vérifier directement lors de la réservation.",
    "Une formule tout compris est proposée par l'hôtel ; les prestations précises incluses peuvent varier, à confirmer au moment de la réservation.",
]


def generer_faq(nom_hotel, donnees):
    equipements = [str(e).lower() for e in (donnees.get("equipements") or [])]
    ville = donnees.get("ville", "cette destination")
    faq = []

    if any("all inclusive" in e or "tout compris" in e for e in equipements):
        idx = index_stable(nom_hotel + "|inclusive", len(FAQ_INCLUSIVE_TEMPLATES))
        faq.append({
            "question": "La formule est-elle vraiment tout compris ?",
            "reponse": FAQ_INCLUSIVE_TEMPLATES[idx]
        })
    if any("piscine" in e for e in equipements):
        faq.append({
            "question": "L'hôtel dispose-t-il d'une piscine ?",
            "reponse": f"Oui, {nom_hotel} dispose d'une piscine parmi ses équipements."
        })
    if any("plage" in e for e in equipements):
        faq.append({
            "question": "L'hôtel est-il en bord de mer ?",
            "reponse": f"Oui, {nom_hotel} propose un accès plage parmi ses équipements."
        })
    if any("spa" in e for e in equipements):
        faq.append({
            "question": "Y a-t-il un spa sur place ?",
            "reponse": f"Oui, un spa fait partie des équipements de {nom_hotel}."
        })

    idx_periode = index_stable(nom_hotel + "|periode", len(FAQ_PERIODE_TEMPLATES))
    faq.append({
        "question": f"Quelle est la meilleure période pour séjourner à {ville} ?",
        "reponse": FAQ_PERIODE_TEMPLATES[idx_periode].format(ville=ville)
    })

    return faq[:4]


def main():
    hotels_par_fichier = charger_tous_les_hotels()

    tous_les_hotels_plats = {}
    for data in hotels_par_fichier.values():
        for nom, d in data.items():
            if isinstance(d, dict):
                tous_les_hotels_plats[nom] = d

    total_modifies = 0
    total_fichiers_modifies = 0
    total_sans_similaires = 0

    for fichier, data in hotels_par_fichier.items():
        fichier_modifie = False

        for nom_hotel, donnees in data.items():
            if not isinstance(donnees, dict):
                continue

            deja_enrichi = donnees.get("faq") or donnees.get("environs") or donnees.get("hotels_similaires")
            if deja_enrichi and not FORCE:
                continue

            similaires = generer_hotels_similaires(nom_hotel, donnees, tous_les_hotels_plats)
            if not similaires:
                total_sans_similaires += 1

            nouvelles_valeurs = {
                "faq": generer_faq(nom_hotel, donnees),
                "environs": generer_environs(nom_hotel, donnees),
                "hotels_similaires": similaires,
            }

            print(f"{'[APPLY]' if APPLY else '[SIMULATION]'} {nom_hotel} ({fichier.name})")
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

    print(f"\n{'Modifications appliquées' if APPLY else 'Simulation terminée'} : {total_modifies} hôtel(s) concerné(s).")
    print(f"  dont {total_sans_similaires} hôtel(s) sans aucun hôtel similaire réel dans la même ville (hotels_similaires laissé vide, c'est normal).")
    if APPLY:
        print(f"{total_fichiers_modifies} fichier(s) réécrit(s) dans data/.")
    else:
        print("Relance avec --apply pour écrire réellement les changements dans les fichiers JSON.")


if __name__ == "__main__":
    main()