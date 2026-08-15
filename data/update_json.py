import glob
import json
import os

# 1. Parcourir tous les fichiers .json du dossier data
dossier_data = "data"
fichiers_json = glob.glob(os.path.join(dossier_data, "*.json"))

for fichier in fichiers_json:
  try:
    with open(fichier, "r", encoding="utf-8") as f:
      data = json.load(f)

    if not isinstance(data, dict):
      continue

    modifie = False
    for nom, info in data.items():
      if isinstance(info, dict):
        equipements = info.get("equipements", [])

        if not isinstance(equipements, list):
          equipements = []

        # Vérifier si "Climatisation" est déjà présente (peu importe la casse)
        deja_present = any(
            str(eq).strip().lower() == "climatisation" for eq in equipements
        )

        if not deja_present:
          equipements.append("Climatisation")
          info["equipements"] = equipements
          modifie = True

    # 2. Sauvegarder uniquement si le fichier a été modifié
    if modifie:
      with open(fichier, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
      print(f"✅ Mis à jour : {os.path.basename(fichier)}")

  except Exception as e:
    print(f"❌ Erreur avec {fichier} : {e}")

print("Traitement de tous les hôtels terminé avec succès !")