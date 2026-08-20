import os
import json
import re

def slugify(texte):
    texte = texte.lower().strip()
    texte = re.sub(r'[^a-z0-9]+', '-', texte)
    return texte.strip('-')

BASE_URL = "https://myhotelcompare.com"

urls = []

# Page d'accueil
urls.append((f"{BASE_URL}/", "daily", "1.0"))

# Pages via query params (structure réelle confirmée : ?page=...)
urls.append((f"{BASE_URL}/?page=accueil", "daily", "0.9"))
urls.append((f"{BASE_URL}/?page=hotels", "daily", "0.9"))
urls.append((f"{BASE_URL}/?page=apropos", "monthly", "0.5"))
urls.append((f"{BASE_URL}/?page=contact", "monthly", "0.5"))
urls.append((f"{BASE_URL}/?page=confidentialite", "yearly", "0.3"))

# Pages multipage Streamlit (vérifiez ces URLs dans le navigateur avant envoi)
urls.append((f"{BASE_URL}/Compagnies_Aeriennes", "weekly", "0.7"))
urls.append((f"{BASE_URL}/Loueurs_Vehicules", "weekly", "0.7"))
urls.append((f"{BASE_URL}/Blog", "weekly", "0.7"))

# Chargement des hôtels depuis data/
HOTELS_DATA = {}
data_dir = "data"
if os.path.exists(data_dir):
    for fichier in os.listdir(data_dir):
        if fichier.endswith(".json") or fichier.endswith(".geojson"):
            chemin = os.path.join(data_dir, fichier)
            try:
                with open(chemin, "r", encoding="utf-8") as f:
                    donnees = json.load(f)
                    if isinstance(donnees, dict):
                        HOTELS_DATA.update(donnees)
            except Exception as e:
                print(f"Erreur chargement {fichier}: {e}")

for nom in HOTELS_DATA.keys():
    slug = slugify(nom)
    urls.append((f"{BASE_URL}/?hotel={slug}", "weekly", "0.8"))

# Génération XML
xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
xml_lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
for url, changefreq, priority in urls:
    xml_lines.append("    <url>")
    xml_lines.append(f"        <loc>{url}</loc>")
    xml_lines.append(f"        <changefreq>{changefreq}</changefreq>")
    xml_lines.append(f"        <priority>{priority}</priority>")
    xml_lines.append("    </url>")
xml_lines.append("</urlset>")

# Avant
os.makedirs("static_root", exist_ok=True)
with open("static_root/sitemap.xml", "w", encoding="utf-8") as f:
    f.write("\n".join(xml_lines))

# Après
os.makedirs("static", exist_ok=True)
with open("static/sitemap.xml", "w", encoding="utf-8") as f:
    f.write("\n".join(xml_lines))
