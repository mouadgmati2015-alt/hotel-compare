import json

# 1. Charger votre fichier JSON d'origine
with open("tunisie.json", "r", encoding="utf-8") as f:
    hotels_data = json.load(f)

# 2. Parcourir chaque hôtel pour automatiser la structure
for nom_hotel, d in hotels_data.items():
    # Si l'hôtel n'a pas encore la structure 'tarifs_operateurs'
    if "tarifs_operateurs" not in d:
        ancien_lien = d.get("lien", "#")
        prix_actuel = d.get("prix_moyen", "")
        
        # Détecter si c'est Expedia ou Booking/Autre selon le lien
        if "expedia" in ancien_lien.lower():
            operateur = "Expedia"
        else:
            operateur = "Booking"
            
        # Créer la structure propre
        d["tarifs_operateurs"] = {
            operateur: {
                "prix": prix_actuel,
                "lien": ancien_lien
            }
        }
        
        # Optionnel : supprimer l'ancienne clé "lien" si vous ne la voulez plus
        if "lien" in d:
            del d["lien"]

# 3. Sauvegarder le fichier mis à jour proprement
with open("tunisie_modifie.json", "w", encoding="utf-8") as f:
    json.dump(hotels_data, f, ensure_ascii=False, indent=4)

print("Migration automatique terminée avec succès !")