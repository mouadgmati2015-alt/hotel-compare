import json
import time
import google.generativeai as genai

# 1. Configurer ta clé API
genai.configure(api_key="VOTRE_CLE")
model = genai.GenerativeModel('gemini-2.0-flash')

# 2. Charger le fichier
with open("data/tunisie.json", "r", encoding="utf-8") as f:
    hotels_dict = json.load(f)

# 3. Boucle avec sauvegarde immédiate
for nom_hotel, hotel_data in hotels_dict.items():
    # On vérifie si la description IA est déjà présente pour ne pas refaire les hôtels déjà faits
    if "description_ia" in hotel_data and len(hotel_data["description_ia"]) > 100:
        print(f"Déjà fait : {nom_hotel}, je passe au suivant.")
        continue

    print(f"Génération pour : {nom_hotel}...")
    try:
        points = ", ".join(hotel_data.get('points_positifs', []))
        prompt = f"""
        Rédige une description marketing très riche et immersive (en français) pour cet hôtel. 
        Tu DOIS rédiger un texte dense d'au moins 6 lignes.
        Nom: {nom_hotel}
        Ville: {hotel_data.get('ville', 'Tunisie')}
        Standing: {hotel_data.get('etoiles', '4')}
        Atouts: {points}
        Le texte doit être élégant, inspirant et donner envie de réserver.
        """
        
        response = model.generate_content(prompt)
        hotel_data["description_ia"] = response.text
        
        # SAUVEGARDE IMMÉDIATE après chaque hôtel
        with open("data/tunisie.json", "w", encoding="utf-8") as f:
            json.dump(hotels_dict, f, ensure_ascii=False, indent=4)
        print(f"Succès pour {nom_hotel} et sauvegarde effectuée.")
        
        time.sleep(5) # On augmente la pause à 5s pour être plus sûr
        
    except Exception as e:
        print(f"Erreur sur {nom_hotel} : {e}")
        time.sleep(10) # Pause plus longue en cas d'erreur
        continue

print("--- Travail terminé ! ---")