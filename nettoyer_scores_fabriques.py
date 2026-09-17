"""
Script de nettoyage : retire les scores/notes fabriqués par IA insérés directement
dans le texte des descriptions (pas dans points_positifs/negatifs, déjà traités ailleurs).

Exemples de texte visé :
- "une note fabuleuse de 9,3"
- "un confort exceptionnel de 9,4"
- "noté 9.2/10"
- "perle (8,7/10)"
- "standing supérieur, confort exceptionnel noté 9..."

Usage :
    python nettoyer_scores_fabriques.py            -> mode simulation (aucune modification écrite)
    python nettoyer_scores_fabriques.py --apply     -> applique réellement les corrections

Le script affiche un rapport détaillé AVANT/APRÈS pour chaque modification,
pour que tu puisses vérifier manuellement que rien n'est cassé grammaticalement
avant de lancer en mode --apply.
"""
import json
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv[1:]
BASE_DIR = Path(__file__).resolve().parent
DOSSIERS_A_SCANNER = [BASE_DIR / "data", BASE_DIR / "data_logements"]
# Champs techniques à ne jamais toucher : URLs, coordonnées, identifiants — un nettoyage
# de texte n'a pas de sens dessus et pourrait les casser.
CHAMPS_A_EXCLURE = {
    "lien_booking", "lien_expedia", "lien_site_officiel", "lien",
    "image", "images", "galerieImages", "image_alt_source",
    "pays", "ville", "type", "slug", "id",
    "lat", "lng", "lat_manuel", "lng_manuel",
    "@context", "@type", "url",
}

# Liste de motifs regex → remplacement. Ordre important : du plus spécifique au plus général.
PATTERNS = [
    # "(superbe/une) note (fabuleuse/exceptionnelle/...) de 9,3" → toute la locution "note ... de X" supprimée,
    # que l'adjectif soit placé avant "note" ("une superbe note de X") ou après ("une note fabuleuse de X"),
    # avec ou sans "une" devant (cas fréquent en meta_description)
    (r"\b(?:une\s+)?(?:superbe\s+|belle\s+|excellente\s+|magnifique\s+)?note\s+(?:fabuleuse\s+|exceptionnelle\s+|globale\s+|remarquable\s+)?de\s+\d+[.,]\d+(?:/10)?\b", ""),
    # "confort élevé de 8,8/10" / "confort exceptionnel de 9,3" / "confort quasi parfait de 9,9" / "confort de 9.2/10" →
    # on garde "confort" + l'éventuel adjectif (jusqu'à 3 mots, ex: "quasi parfait"), on ne retire que "de X,X(/10)"
    (r"\bconfort((?:\s+[^\s,;.()]+){0,3})\s+de\s+\d+[.,]\d+(?:/10)?\b", r"confort\1"),
    # "noté 9.2/10" / "notée à 8,7/10" → supprimé
    (r"\bnoté[e]?\s*(à\s*)?\d+[.,]\d+(/10)?\b", ""),
    # "(8,7/10)" ou "(9.3)" en parenthèses après un mot → supprimé
    (r"\s*\(\d+[.,]\d+(/10)?\)", ""),
    # "8,7/10" ou "9.3/10" isolé restant → supprimé
    (r"\b\d+[.,]\d+/10\b", ""),
    # Connecteurs devenus bancals une fois le score retiré :
    # "affiche avec" / "propose avec" / "offre avec" → juste le verbe, sans "avec" orphelin
    (r"\b(affiche|propose|offre)\s+avec\b", r"\1"),
    # "affiche et" / "propose et" / "offre et" → même chose quand c'est "et" (pas "avec") qui suit directement le verbe
    (r"\b(affiche|propose|offre)\s+et\b", r"\1"),
    # "avec et" → la phrase supprimée entre "avec" et "et" laisse les deux mots collés : on retire "et"
    (r"\bavec\s+et\b", "avec"),
    # "couronné par." ou "couronné par," → le complément a disparu, on retire la locution entière
    (r"\bcouronné par\s*([.,;:])", r"\1"),
    # "notée ." / "noté ," → même chose, locution qui ne pointe plus vers rien
    (r"\bnoté[e]?\s*([.,;:])", r"\1"),
    # Nettoyage des espaces doubles, doubles virgules, et séquences ": ," laissées par les suppressions
    (r"\s{2,}", " "),
    (r"\(\s*\)", ""),
    (r":\s*,\s*", ": "),
    (r",\s*,\s*", ", "),
    # "de." / "de," qui traîne quand toute la fin de la locution a été supprimée
    # (ex: "note de localisation de 9,5/10" → "de." orphelin)
    (r"\bde\s+([.,;:])", r"\1"),
    (r"\s+([,.;!?])", r"\1"),
]


def nettoyer_texte(texte):
    original = texte
    # Trois passes : la 1re fait les suppressions principales, les suivantes nettoient les résidus
    # en cascade (connecteurs orphelins, espaces, parenthèses vides) qu'une seule passe ne peut pas tous rattraper.
    for _ in range(3):
        for motif, remplacement in PATTERNS:
            texte = re.sub(motif, remplacement, texte, flags=re.IGNORECASE)
    texte = texte.strip()
    # Si le texte d'origine commençait par une majuscule (début de phrase) mais que le résultat
    # commence maintenant par une minuscule — soit parce qu'on a supprimé le premier mot, soit parce
    # qu'un remplacement a forcé une casse fixe — on remet la majuscule initiale.
    if original and texte and original[0].isupper() and texte[0].islower():
        texte = texte[0].upper() + texte[1:]
    return texte, texte != original


def nettoyer_recursif(valeur, chemin=""):
    """Parcourt récursivement dicts/listes/chaînes et nettoie chaque texte trouvé,
    sauf les champs techniques listés dans CHAMPS_A_EXCLURE (URLs, coordonnées, etc.).
    Retourne (valeur_nettoyée, liste_de_modifications)."""
    modifications = []

    if isinstance(valeur, dict):
        for cle, sous_valeur in list(valeur.items()):
            if cle in CHAMPS_A_EXCLURE:
                continue
            nouveau_chemin = f"{chemin}.{cle}" if chemin else cle
            resultat, mods = nettoyer_recursif(sous_valeur, nouveau_chemin)
            valeur[cle] = resultat
            modifications.extend(mods)
        return valeur, modifications

    if isinstance(valeur, list):
        nouvelle_liste = []
        for i, item in enumerate(valeur):
            resultat, mods = nettoyer_recursif(item, f"{chemin}[{i}]")
            nouvelle_liste.append(resultat)
            modifications.extend(mods)
        return nouvelle_liste, modifications

    if isinstance(valeur, str):
        nouvelle_valeur, a_change = nettoyer_texte(valeur)
        if a_change:
            modifications.append((chemin, valeur, nouvelle_valeur))
        return nouvelle_valeur, modifications

    # nombres, booléens, None : rien à nettoyer
    return valeur, modifications


def traiter_fichier(chemin_fichier):
    modifications = []
    with open(chemin_fichier, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        return modifications

    fichier_modifie = False
    for nom_entite, contenu in data.items():
        if not isinstance(contenu, dict):
            continue
        contenu_nettoye, mods_entite = nettoyer_recursif(contenu, "")
        if mods_entite:
            fichier_modifie = True
            data[nom_entite] = contenu_nettoye
            for chemin, avant, apres in mods_entite:
                modifications.append({
                    "fichier": chemin_fichier.name,
                    "entite": nom_entite,
                    "champ": chemin,
                    "avant": avant,
                    "apres": apres,
                })

    if APPLY and fichier_modifie:
        with open(chemin_fichier, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    return modifications


def main():
    toutes_modifications = []
    for dossier in DOSSIERS_A_SCANNER:
        if not dossier.exists():
            continue
        for fichier in dossier.glob("*.json"):
            if fichier.name == "_geocode_cache.json":
                continue
            toutes_modifications.extend(traiter_fichier(fichier))

    print(f"\n{'='*70}")
    print(f"Mode : {'APPLICATION RÉELLE' if APPLY else 'SIMULATION (rien n’est écrit)'}")
    print(f"{'='*70}\n")

    if not toutes_modifications:
        print("Aucun score fabriqué détecté dans les champs scannés. ✅")
        return

    for mod in toutes_modifications:
        print(f"📄 {mod['fichier']} — {mod['entite']} — champ: {mod['champ']}")
        print(f"   AVANT : {mod['avant'][:200]}")
        print(f"   APRÈS : {mod['apres'][:200]}")
        print()

    print(f"{'='*70}")
    print(f"Total : {len(toutes_modifications)} modification(s) {'appliquée(s)' if APPLY else 'détectée(s) (simulation)'}")
    if not APPLY:
        print("Relance avec --apply pour écrire réellement les corrections dans les fichiers JSON.")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()