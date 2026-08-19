import os
import json
import urllib.parse

def generate_sitemap():
    base_url = "https://www.myhotelcompare.com"
    
    # 1. Vos pages statiques de base
    urls = [
        f"{base_url}/",
        f"{base_url}/contact",
        f"{base_url}/apropos",
        f"{base_url}/confidentialite",
        f"{base_url}/Compagnies_Aeriennes",
        f"{base_url}/Loueurs_Vehicules"
    ]
    
    data_dir = "data"
    
    # 2. Lecture automatique du dossier data/
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(data_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        
                        # Si le fichier utilise le format dictionnaire d'hôtels (comme votre exemple)
                        if isinstance(data, dict):
                            for hotel_name in data.keys():
                                # On transforme le nom de l'hôtel en slug propre pour l'URL 
                                # (ex: "Verginia Sharm Resort & Aqua Park" -> "Verginia-Sharm-Resort-Aqua-Park")
                                slug = hotel_name.strip().replace(" ", "-").replace("&", "et")
                                # Nettoyage des caractères spéciaux potentiels
                                slug = urllib.parse.quote(slug)
                                urls.append(f"{base_url}/{slug}")
                                
                        # Si c'est une liste classique (pour les articles de blog par exemple)
                        elif isinstance(data, list):
                            for item in data:
                                slug = item.get("slug") or item.get("id")
                                if slug:
                                    urls.append(f"{base_url}/{slug}")
                                    
                except Exception as e:
                    print(f"Erreur lors de la lecture de {filename}: {e}")

    # 3. Création du fichier sitemap.xml final sans doublons
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in sorted(set(urls)):
        xml_content += f"    <url>\n"
        xml_content += f"        <loc>{url}</loc>\n"
        xml_content += f"        <changefreq>weekly</changefreq>\n"
        xml_content += f"        <priority>0.8</priority>\n"
        xml_content += f"    </url>\n"
        
    xml_content += '</urlset>'

    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(xml_content)
    
    print(f"Sitemap généré avec succès ! Total : {len(urls)} URLs incluses.")

if __name__ == "__main__":
    generate_sitemap()