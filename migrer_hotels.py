import json

# Chemins de vos fichiers
ancien_path = 'data/tunisie_ancien.json'
nouveau_path = 'data/tunisie.json'

# Chargement des données avec 'utf-8-sig' pour éviter les erreurs de BOM
with open(ancien_path, 'r', encoding='utf-8-sig') as f:
    ancien_data = json.load(f)

with open(nouveau_path, 'r', encoding='utf-8-sig') as f:
    nouveau_data = json.load(f)

# Copie des liens (image, expedia, booking) pour chaque hôtel
for nom_hotel, infos in nouveau_data.items():
    # Normalisation de la clé (minuscules et sans espaces superflus)
    nom_trouve = None
    for ancien_nom in ancien_data:
        if ancien_nom.strip().lower() == nom_hotel.strip().lower():
            nom_trouve = ancien_nom
            break
            
    if nom_trouve:
        ancien_hotel = ancien_data[nom_trouve]
        
        # 1. Copie de l'image si elle existe dans l'ancien
        if 'image' in ancien_hotel and ancien_hotel['image']:
            nouveau_data[nom_hotel]['image'] = ancien_hotel['image']
            
        # 2. Copie du lien Expedia s'il existe dans l'ancien
        if 'lien_expedia' in ancien_hotel and ancien_hotel['lien_expedia']:
            nouveau_data[nom_hotel]['lien_expedia'] = ancien_hotel['lien_expedia']
            
        # 3. Copie du lien Booking s'il existe dans l'ancien
        if 'lien_booking' in ancien_hotel and ancien_hotel['lien_booking']:
            nouveau_data[nom_hotel]['lien_booking'] = ancien_hotel['lien_booking']

# Sauvegarde du fichier mis à jour
with open(nouveau_path, 'w', encoding='utf-8') as f:
    json.dump(nouveau_data, f, ensure_ascii=False, indent=4)

print("Migration réussie : les liens images, Expedia et Booking ont été copiés !")
print(f"Nombre total d'hôtels dans le fichier : {len(nouveau_data)}")