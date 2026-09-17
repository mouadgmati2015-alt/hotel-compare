import os
import json

dossier_data = "data"

def nettoyer_valeur(val):
    if isinstance(val, str) and val.startswith("[") and "](" in val:
        # Extrait l'URL entre les parenthèses
        return val.split("](")[1].rstrip(")")
    return val

# Parcourt tous les fichiers du dossier data
for filename in os.listdir(dossier_data):
    if filename.endswith(".json"):
        chemin = os.path.join(dossier_data, filename)
        with open(chemin, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"Erreur lecture {filename}: {e}")
                continue

        # Nettoyage récursif des dictionnaires d'hôtels
        modifie = False
        for hotel, details in data.items():
            if isinstance(details, dict):
                for k, v in details.items():
                    val_propre = nettoyer_valeur(v)
                    if val_propre != v:
                        details[k] = val_propre
                        modifie = True

        # Sauvegarde le fichier nettoyé
        if modifie:
            with open(chemin, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Fichier nettoyé et sauvegardé : {filename}")

print("Nettoyage de tous les fichiers JSON terminé !")