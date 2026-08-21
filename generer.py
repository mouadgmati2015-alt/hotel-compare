import json
import os
import re
import base64
import shutil

import urllib

output_dir = "mon_site_final"
data_dir = "data"

if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir, exist_ok=True)

# --- CONFIGURATION ---
output_dir = "mon_site_final"
data_dir = "data"

if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir, exist_ok=True)

# --- FONCTIONS DE MISE À JOUR DES LIENS AFFILIÉS ---
def update_booking_aid(url, new_aid="8012379"):
    if not url:
        return "#"
    url = url.rstrip('?')
    clean_url = url.replace("??", "?")
    parsed = urllib.parse.urlparse(clean_url)
    query_params = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    query_params["aid"] = new_aid
    new_query = urllib.parse.urlencode(query_params)
    return urllib.parse.urlunparse(parsed._replace(query=new_query))
 
def update_expedia_link(url):
    if not url:
        return "https://www.anrdoezrs.net/click-8012379-13854902?url=https://www.expedia.fr/"
    url = url.rstrip('?')
    if "anrdoezrs.net" in url:
        return url
    encoded_url = urllib.parse.quote(url, safe='')
    return f"https://www.anrdoezrs.net/click-8012379-13854902?url={encoded_url}"

def slugify(texte):
    if not texte: return ""
    texte = texte.lower().strip()
    texte = re.sub(r'[^a-z0-9]+', '-', texte)
    return texte.strip('-')

# --- FONCTIONS UTILITAIRES ---
def get_logo_base64():
    return "logo_4.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return ""

def get_img_as_base64(path):
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def markdown_to_html(texte):
    if not texte: 
        return ""
    if isinstance(texte, dict):
        texte = "<br>".join([f"<b>{str(k).capitalize()}</b> : {v}" for k, v in texte.items()])
    elif isinstance(texte, list):
        texte = "<br>".join([f"• {str(item)}" for item in texte])
    else:
        texte = str(texte)

    texte = re.sub(r'\n\n+', '</p><p>', texte)
    texte = texte.replace('\n', '<br>')
    texte = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', texte)
    texte = re.sub(r'### (.*?)<br>', r'<h3>\1</h3>', texte)
    texte = re.sub(r'\* (.*?)<br>', r'<li>\1</li>', texte)
    return f"<p>{texte}</p>"

def nettoyer_slug(texte):
    return re.sub(r'[^a-z0-9]+', '-', texte.lower().strip()).strip('-')

def get_img_as_base64(path):
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# 1. Chargement des articles (Blog)
articles_blog = []
json_paths = ["data/blog_data.json", "blog_data.json", "data/articles.json", "articles.json"]
path_trouve = None

for p in json_paths:
    if os.path.exists(p):
        path_trouve = p
        break

if path_trouve:
    try:
        with open(path_trouve, "r", encoding="utf-8") as f:
            articles_blog = json.load(f)
    except: pass

# 2. Chargement des hôtels
all_hotels = []
if os.path.exists(data_dir):
    for filename in os.listdir(data_dir):
        if filename.endswith(".json") and filename not in ["blog_data.json", "articles.json", "cruises_data.json", "airlines_data.json", "promo_semaine.json"]:
            filepath = os.path.join(data_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict):
                        for nom, d in data.items():
                            if not isinstance(d, dict): continue
                            slug = nettoyer_slug(nom)
                            if slug:
                                desc_complete = (
                                    d.get('description_longue') or 
                                    d.get('description_ia') or 
                                    d.get('description') or 
                                    d.get('texte') or 
                                    ""
                                )
                                all_hotels.append({
                                    'nom': nom,
                                    'slug': slug,
                                    'ville': d.get('ville', ''),
                                    'pays': d.get('pays', ''),
                                    'etoiles': d.get('etoiles', 'N/C'),
                                    'prix': d.get('prix_moyen', 'Sur demande'),
                                    'image': d.get('image', ''),
                                    'description': desc_complete,
                                    'equipements': d.get('equipements', []),
                                    'avis': d.get('avis', ''),
                                    'points_positifs': d.get('points_positifs', []),
                                    'points_negatifs': d.get('points_negatifs', []),
                                    'nomad': d.get('Nomad, vous en dit plus', ''),
                                    'pour_qui': d.get('pour_qui', {}),
                                    'meta_avis': d.get('meta_avis', ''),
                                    'lien_booking': d.get('lien_booking', '#'),
                                    'lien_expedia': d.get('lien_expedia', '#')
                                })
                except Exception as e:
                    print(f"Erreur lecture hôtel {filename}: {e}")

# 3. Chargement des croisières
cruises_data = {}
cruise_paths = ["data/cruises_data.json", "cruises_data.json"]
for cp in cruise_paths:
    if os.path.exists(cp):
        try:
            with open(cp, "r", encoding="utf-8") as f:
                cruises_data = json.load(f)
            break
        except: pass

# 4. Chargement des compagnies aériennes
airlines_data = {}
try:
    from data.airlines_data import AIRLINES_DATA as airlines_data
except:
    for ap in ["data/airlines_data.json", "airlines_data.json"]:
        if os.path.exists(ap):
            try:
                with open(ap, "r", encoding="utf-8") as f:
                    airlines_data = json.load(f)
                break
            except: pass

# Footer HTML réutilisable
footer_html_shared = """
<div class="footer-bg">
    <div class="footer-links">
        <a onclick="showSection('accueil')">Accueil</a>
        <a onclick="showSection('apropos')">À propos</a>
        <a onclick="showSection('confidentialite')">Politique de confidentialité</a>
        <a onclick="showSection('contact')">Contact</a>
    </div>
    <p class="footer-copy">© 2026 MyHotelCompare. Tous droits réservés. Propulsé par l'IA.</p>
</div>
"""

# Préparation des images du caroussel en base64
img_paths = ["images/image caroussel 2.png", "images/image_afrique.jpg", "images/image_astuce.jpg", "images/image_hotel.jpg", "images/image_tunisie.jpg"]
imgs_base64 = [get_img_as_base64(p) for p in img_paths]

carousel_html_content = f"""
<div style="width: 100%; height: 260px; position: relative; overflow: hidden; border-radius: 8px; background: #0e1117;">
    <style>
    @keyframes customFade {{
        0% {{ opacity: 0; }}
        6% {{ opacity: 1; }}
        20% {{ opacity: 1; }}
        26% {{ opacity: 0; }}
        100% {{ opacity: 0; }}
    }}
    .hotel-slide-item {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 8px;
        opacity: 0;
        animation: customFade 15s infinite;
    }}
    </style>
    <img class="hotel-slide-item" src="data:image/png;base64,{imgs_base64[0]}" style="animation-delay: 0s;">
    <img class="hotel-slide-item" src="data:image/jpeg;base64,{imgs_base64[1]}" style="animation-delay: 3s;">
    <img class="hotel-slide-item" src="data:image/jpeg;base64,{imgs_base64[2]}" style="animation-delay: 6s;">
    <img class="hotel-slide-item" src="data:image/jpeg;base64,{imgs_base64[3]}" style="animation-delay: 9s;">
    <img class="hotel-slide-item" src="data:image/jpeg;base64,{imgs_base64[4]}" style="animation-delay: 12s;">
</div>
"""

# 5. Génération du blog
blog_cards_html = ""
blog_sections_html = ""

for i, art in enumerate(articles_blog):
    titre = art.get("titre", "Article")
    resume = art.get("resume", "")
    details_html = markdown_to_html(art.get("details", ""))
    
    img_path = art.get("image")
    if not img_path and "images" in art and isinstance(art["images"], list) and len(art["images"]) > 0:
        img_path = art["images"][0]
    if not img_path:
        img_path = "images/test.jpg"

    b64_img = get_img_as_base64(img_path)
    img_src = f"data:image/jpeg;base64,{b64_img}" if b64_img else "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=600&q=80"

    blog_cards_html += f"""
    <div style="background-color: #1C2541; border: 1px solid #3A506B; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column;">
        <img src="{img_src}" style="width: 100%; height: 180px; object-fit: cover;">
        <div style="padding: 20px; display: flex; flex-direction: column; flex-grow: 1; justify-content: space-between;">
            <h3 style="color: white; margin-top: 0; font-size: 1.15em;">{titre}</h3>
            <p style="color: #94a3b8; font-size: 0.88em; margin-bottom: 20px;">{resume}</p>
            <button onclick="showSection('blog-detail-{i}')" style="background-color: #3A506B; color: white; padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold;">Lire l'article</button>
        </div>
    </div>
    """

    blog_sections_html += f"""
    <div id="section-blog-detail-{i}" class="page-section" style="display:none;">
        <button onclick="showSection('blog')" style="background:none; border:none; color:#38bdf8; cursor:pointer; font-size:1em; margin-bottom:15px;">← Retour au blog</button>
        <div style="background-color: #1C2541; border: 1px solid #3A506B; border-radius: 12px; padding: 30px; line-height: 1.7; margin-bottom: 20px;">
            <h1>{titre}</h1>
            <img src="{img_src}" style="width: 100%; max-height: 400px; object-fit: cover; border-radius: 8px; margin-bottom: 20px;">
            <div style="font-size: 1.1em; color: #e2e8f0;">{details_html}</div>
        </div>
        {footer_html_shared}
    </div>
    """

# 6. Génération des détails hôtels
hotel_details_sections_html = ""
for h in all_hotels:
    equipements_html = ", ".join(h['equipements']) if h['equipements'] else "Non spécifiés"
    desc_html = markdown_to_html(h['description'])
    
    avis_html = markdown_to_html(h['avis']) if h['avis'] else ""
    positifs_html = markdown_to_html(h['points_positifs']) if h['points_positifs'] else ""
    negatifs_html = markdown_to_html(h['points_negatifs']) if h['points_negatifs'] else ""
    nomad_html = markdown_to_html(h['nomad']) if h['nomad'] else ""
    pour_qui_html = markdown_to_html(h['pour_qui']) if h['pour_qui'] else ""
    meta_avis = f"<p style='font-size: 0.9em; color: #94a3b8; font-style: italic;'>{h['meta_avis']}</p>" if h['meta_avis'] else ""
    
    hotel_details_sections_html += f"""
    <div id="section-hotel-detail-{h['slug']}" class="page-section" style="display:none;">
        <button onclick="showSection('hotels')" style="background:none; border:none; color:#38bdf8; cursor:pointer; font-size:1em; margin-bottom:15px;">← Retour au comparateur</button>
        <div style="background-color: #1C2541; border: 1px solid #3A506B; border-radius: 12px; padding: 40px; box-sizing: border-box; line-height: 1.7; margin-bottom: 20px;">
            <h1>{h['nom']}</h1>
            <p style="color: #94a3b8;">📍 {h['ville']}, {h['pays']} | ⭐ {h['etoiles']}</p>
            {f'<img src="{h["image"]}" style="width:100%; max-height:350px; object-fit:cover; border-radius:8px; margin:15px 0;">' if h['image'] else ''}
            
            <h3>✨ Description</h3>
            <div style="color: #e2e8f0; word-break: break-word;">{desc_html}</div>
            
            {f'<h3>⭐ Avis</h3><div style="color: #e2e8f0; word-break: break-word;">{avis_html}</div>' if avis_html else ''}
            {f'<h3>👍 Points forts</h3><div style="color: #e2e8f0; word-break: break-word;">{positifs_html}</div>' if positifs_html else ''}
            {f'<h3>👎 Points faibles</h3><div style="color: #e2e8f0; word-break: break-word;">{negatifs_html}</div>' if negatifs_html else ''}
            {f'<h3>🧭 Nomad, vous en dit plus</h3><div style="color: #e2e8f0; word-break: break-word;">{nomad_html}</div>' if nomad_html else ''}
            {f'<h3>🎯 Pour qui & Verdict</h3><div style="color: #e2e8f0; word-break: break-word;">{pour_qui_html}</div>' if pour_qui_html else ''}
            {meta_avis}

            <h3>🛠️ Équipements</h3>
            <p style="color: #e2e8f0;">{equipements_html}</p>
            
            <div style="margin-top: 20px; display: flex; gap: 10px; flex-wrap: wrap;">
                <a href="{h['lien_booking']}" target="_blank" style="background: #003580; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold;">Réserver sur Booking</a>
                <a href="{h['lien_expedia']}" target="_blank" style="background: #ffcc00; color: #000; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold;">Réserver sur Expedia</a>
            </div>
        </div>
        {footer_html_shared}
    </div>
    """

hotels_js_data = json.dumps(all_hotels, ensure_ascii=False)
loueurs_data = {
    "Enterprise": {"rang": "#1 Mondial", "note": "4.4 / 5", "resume": "Leader mondial de la location, excellent service client, très présent dans les aéroports et les centres-villes."},
    "Hertz": {"rang": "#2 Mondial", "note": "4.0 / 5", "resume": "Présent dans le monde entier, grand choix de véhicules récents et service client fiable."},
    "Avis": {"rang": "#3 Mondial", "note": "4.1 / 5", "resume": "L'un des pionniers de la location, reconnu pour son service professionnel et ses programmes de fidélité."},
    "Sixt": {"rang": "#4 Mondial", "note": "4.3 / 5", "resume": "Flotte moderne, véhicules haut de gamme souvent disponibles et agences très bien placées."},
    "Europcar": {"rang": "#5 Mondial", "note": "3.9 / 5", "resume": "Réseau très étendu en Europe et formules de location flexibles adaptées aux voyageurs internationaux."},
    "Alamo": {"rang": "#6 Mondial", "note": "4.2 / 5", "resume": "Très populaire auprès des vacanciers, notamment pour ses options de choix de véhicule sur place."},
    "Budget": {"rang": "#7 Mondial", "note": "3.8 / 5", "resume": "Idéal pour les petits budgets, offre un très bon rapport qualité-prix sur une large gamme de véhicules."},
    "Dollar": {"rang": "#8 Mondial", "note": "3.7 / 5", "resume": "Tarifs souvent très compétitifs pour les locations de vacances en famille."},
    "Thrifty": {"rang": "#9 Mondial", "note": "3.7 / 5", "resume": "Solutions économiques et pratiques pour les voyageurs à la recherche de bons plans."}
}
loueurs_js_data = json.dumps(loueurs_data, ensure_ascii=False)
cruises_js_data = json.dumps(cruises_data, ensure_ascii=False)
airlines_js_data = json.dumps(airlines_data, ensure_ascii=False)

# 7. Template HTML global
html_monolithique = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>MyHotelCompare - Comparateur Intelligent d'Hôtels</title>
    <style>
        body {{ background-color: #0B132B; color: #FFFFFF; font-family: sans-serif; margin: 0; padding: 20px; }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        .top-nav {{ display: flex; gap: 10px; background-color: #1C2541; padding: 15px; border-radius: 10px; margin-bottom: 25px; border: 1px solid #3A506B; flex-wrap: wrap; }}
        .top-nav button {{ color: white; background-color: #3A506B; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; }}
        .top-nav button:hover {{ background-color: #38bdf8; color: #0B132B; }}
        .filters-box {{ background-color: #1C2541; border: 1px solid #3A506B; border-radius: 10px; padding: 20px; margin-bottom: 25px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .filters-box select {{ width: 100%; padding: 10px; border-radius: 6px; border: 1px solid #3A506B; background-color: #0B132B; color: white; }}
        .btn-compare {{ background-color: #10B981; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; }}
        .comparison-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }}
        @media (max-width: 768px) {{ .comparison-grid {{ grid-template-columns: 1fr; }} }}
        .hotel-card {{ background-color: #1C2541; border: 1px solid #3A506B; border-radius: 12px; padding: 20px; box-sizing: border-box; }}
        .btn-booking {{ display: block; background-color: #003580; color: white; padding: 10px; text-align: center; text-decoration: none; border-radius: 6px; font-weight: bold; margin-bottom: 8px; }}
        .btn-expedia {{ display: block; background-color: #ffcc00; color: #000; padding: 10px; text-align: center; text-decoration: none; border-radius: 6px; font-weight: bold; margin-bottom: 8px; }}
        .blog-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; }}
        .content-box {{ background-color: #0B132B; border-radius: 12px; padding: 20px 0; }}
        .cruise-card {{ background-color: #1C2541; border: 1px solid #3A506B; border-radius: 12px; padding: 20px; margin-bottom: 20px; display: grid; grid-template-columns: 220px 1fr 200px; gap: 20px; align-items: start; }}
        @media (max-width: 768px) {{ .cruise-card {{ grid-template-columns: 1fr; }} }}
        
        /* Styles d'accueil */
        .hero-title {{ text-align: center; font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }}
        .hero-subtitle {{ text-align: center; color: #94a3b8; font-size: 1.1em; margin-bottom: 30px; }}
        .cards-grid-3 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0; }}
        .feature-card {{ background-color: #1C2541; border: 1px solid #3A506B; border-radius: 12px; padding: 25px; }}
        .btn-action-green {{ display: block; background-color: #10B981; color: white; padding: 14px; text-align: center; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 1.1em; margin: 30px auto; max-width: 400px; cursor: pointer; border: none; }}
        .form-box {{ background-color: #1C2541; border: 1px solid #3A506B; border-radius: 12px; padding: 30px; max-width: 700px; margin: 0 auto; }}
        .form-input {{ width: 100%; padding: 12px; border-radius: 6px; border: 1px solid #3A506B; background-color: #0B132B; color: white; margin-bottom: 15px; box-sizing: border-box; }}
        
        /* Footer */
        .footer-bg {{ background-color: #1e293b; color: #f8fafc; padding: 30px; border-radius: 10px; text-align: center; margin-top: 40px; }}
        .footer-links {{ display: flex; justify-content: center; gap: 20px; margin-bottom: 10px; flex-wrap: wrap; }}
        .footer-links a {{ color: #38bdf8; text-decoration: none; margin: 0 15px; font-weight: 500; font-size: 0.95em; cursor: pointer; }}
        .footer-links a:hover {{ text-decoration: underline; color: #ffffff; }}
        .footer-copy {{ color: #94a3b8; font-size: 0.85em; margin: 0; }}
        
        .page-content-card {{ background-color: #1C2541; border: 1px solid #3A506B; border-radius: 12px; padding: 40px; line-height: 1.7; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <!-- BARRE DE NAVIGATION -->
        <div class="top-nav">
            <button onclick="showSection('accueil')">Accueil</button>
            <button onclick="showSection('hotels')">Hôtels</button>
            <button onclick="showSection('compagnies')">Compagnies Aériennes</button>
            <button onclick="showSection('vehicules')">Location de Véhicules</button>
            <button onclick="showSection('croisieres')">Croisières</button>
            <button onclick="showSection('blog')">Blog Voyage</button>
        </div>

        <!-- PAGE D'ACCUEIL (AVEC CAROUSSEL À GAUCHE) -->
        <div id="section-accueil" class="page-section content-box" style="display:block;">
            <div class="hero-title">Comparateur intelligent d'hôtels</div>
            <div class="hero-subtitle">Nomad : L'IA qui analyse les avis pour dénicher votre hôtel idéal.</div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 20px; margin-bottom: 40px;">
                <!-- Caroussel d'images à gauche -->
                <div style="background:#1C2541; border:1px solid #3A506B; border-radius:12px; overflow:hidden; padding: 10px;">
                    {carousel_html_content}
                    <div style="padding: 10px 5px 0 5px;">
                        <h3 style="margin:0 0 5px 0;">Évasion & Découverte</h3>
                        <p style="color:#94a3b8; margin:0; font-size:0.9em;">Trouvez les plus beaux panoramas du monde entier au meilleur prix.</p>
                    </div>
                </div>
                <!-- Carte promo à droite -->
                <div style="background:#1C2541; border:1px solid #3A506B; border-radius:12px; overflow:hidden; padding: 10px;">
                    <img src="https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=800&q=80" style="width:100%; height:260px; object-fit:cover; border-radius: 8px;">
                    <div style="padding: 10px 5px 0 5px;">
                        <h3 style="margin:0 0 5px 0;">Naama Bay Promenade Beach Resort</h3>
                        <p style="color:#94a3b8; margin:0 0 5px 0; font-size:0.9em;">📍 Sharm el-Sheikh, Égypte</p>
                        <p style="color:#10B981; margin:0; font-size:0.9em; font-weight:bold;">Séjour du 12 au 19 sept. 2026 (2 adultes) • Vue Jardin • Petit-déjeuner inclus : 469 €</p>
                    </div>
                </div>
            </div>

            <h2 style="text-align: center; margin-top: 40px;">Pourquoi choisir MyHotelCompare ?</h2>
            
            <div class="cards-grid-3">
                <div class="feature-card">
                    <h3 style="margin-top: 0; color: #38bdf8;">🤖 IA Nomad</h3>
                    <p style="color: #94a3b8; font-size: 0.95em; margin-bottom: 0;">Analyse automatique des vrais avis clients pour éviter les pièges.</p>
                </div>
                <div class="feature-card">
                    <h3 style="margin-top: 0; color: #38bdf8;">🎯 Sur-Mesure</h3>
                    <p style="color: #94a3b8; font-size: 0.95em; margin-bottom: 0;">Trouvez l'hôtel idéal selon vos critères (parc aquatique, spa, plage privée).</p>
                </div>
                <div class="feature-card">
                    <h3 style="margin-top: 0; color: #38bdf8;">🛡️ Zéro Stress</h3>
                    <p style="color: #94a3b8; font-size: 0.95em; margin-bottom: 0;">Maîtrisez votre budget et profitez d'un séjour en toute sérénité.</p>
                </div>
            </div>

            <button class="btn-action-green" onclick="showSection('hotels')">🚀 Accéder au comparateur d'hôtels</button>

            <div style="text-align: center; margin: 50px 0 20px 0;">
                <h2 style="margin-bottom: 5px;">💬 Votre avis nous intéresse</h2>
                <p style="color: #94a3b8;">Le site est en cours de construction. Aide-nous à l'améliorer !</p>
            </div>

            <div class="form-box">
                <form onsubmit="event.preventDefault(); alert('Merci pour votre message ! Votre avis a bien été pris en compte.');">
                    <input type="text" placeholder="Votre nom ou pseudo (ex: Jean D.)" class="form-input" required>
                    <textarea placeholder="Votre avis, une suggestion ou un retour d'expérience..." class="form-input" rows="4" required></textarea>
                    <button type="submit" class="btn-action-green" style="margin: 0 auto; width: 100%;">Envoyer mon avis</button>
                </form>
            </div>

            {footer_html_shared}
        </div>

        <!-- HOTELS -->
        <div id="section-hotels" class="page-section" style="display:none;">
            <h2>💡 Comparateur d'hôtels</h2>
            <div class="filters-box">
                <div><label style="color:#94a3b8; display:block; margin-bottom:5px;">Pays</label><select id="selectPays" onchange="updateVilles()"><option value="">Tous les pays</option></select></div>
                <div><label style="color:#94a3b8; display:block; margin-bottom:5px;">Ville</label><select id="selectVille" onchange="updateHotels()"><option value="">Toutes les villes</option></select></div>
                <div><label style="color:#94a3b8; display:block; margin-bottom:5px;">Premier hôtel</label><select id="selectHotel1"><option value="">Choisissez...</option></select></div>
                <div><label style="color:#94a3b8; display:block; margin-bottom:5px;">Deuxième hôtel</label><select id="selectHotel2"><option value="">Choisissez...</option></select></div>
            </div>
            <button class="btn-compare" onclick="lancerComparaison()">🚀 Lancer la comparaison</button>
            <div id="resultatComparaison" class="comparison-grid"></div>
            {footer_html_shared}
        </div>

        <!-- COMPAGNIES AERIENNES -->
        <div id="section-compagnies" class="page-section content-box" style="display:none;">
            <h1>✈️ Guide des Compagnies Aériennes</h1>
            <p style="color:#94a3b8; margin-bottom:20px;">Analysez les caractéristiques, les avantages et les points d'attention de chaque compagnie.</p>
            
            <div style="margin-bottom: 25px;">
                <label style="color:#94a3b8; display:block; margin-bottom:8px;">Sélectionnez une compagnie :</label>
                <select id="selectAirline" onchange="afficherAirline()" style="width: 100%; max-width: 400px; padding: 10px; border-radius: 6px; border: 1px solid #3A506B; background-color: #0B132B; color: white;">
                    <option value="">Sélectionnez...</option>
                </select>
            </div>

            <div id="detailAirline" style="margin-bottom: 30px;"></div>
            {footer_html_shared}
        </div>

        <!-- VEHICULES -->
        <div id="section-vehicules" class="page-section content-box" style="display:none;">
            <h1>🚗 Comparateur & Agences de Location de Véhicules</h1>
            <p style="color:#94a3b8; margin-bottom:20px;">Recherchez et comparez les meilleurs loueurs de voitures à travers le monde.</p>
            <div style="margin-bottom: 25px;">
                <label style="color:#94a3b8; display:block; margin-bottom:8px;">Choisissez un loueur de véhicules :</label>
                <select id="selectLoueur" onchange="afficherLoueur()" style="width: 100%; max-width: 400px; padding: 10px; border-radius: 6px; border: 1px solid #3A506B; background-color: #0B132B; color: white;">
                    <option value="">Sélectionnez un loueur...</option>
                </select>
            </div>
            <div id="detailLoueur" style="margin-bottom: 30px;"></div>
            <hr style="border-color: #3A506B; margin: 30px 0;">
            <h3>Trouvez votre véhicule partout dans le monde</h3>
            <div style="width: 100%; min-height: 400px; margin-top: 15px; margin-bottom: 30px;">
                <script async src="https://tpemd.com/content?trs=552839&shmarker=751055&locale=fr&powered_by=true&border_radius=4&plain=true&show_logo=false&color_background=%23ffca28&color_button=%2355a539&color_text=%23000000&color_input_text=%23000000&color_button_text=%23ffffff&promo_id=4480&campaign_id=10" charset="utf-8"></script>
            </div>
            {footer_html_shared}
        </div>

        <!-- CROISIERES -->
        <div id="section-croisieres" class="page-section" style="display:none;">
            <h1>🚢 Comparateur de Croisières Sereines</h1>
            <p style="color:#94a3b8; margin-bottom:20px;">Découvrez et comparez notre sélection de croisières axées sur la détente, le calme et l'évasion.</p>
            
            <div class="filters-box">
                <div><label style="color:#94a3b8; display:block; margin-bottom:5px;">Région / Type</label><select id="selectRegionCruise" onchange="filtrerCroisieres()"><option value="Toutes">Toutes</option></select></div>
                <div><label style="color:#94a3b8; display:block; margin-bottom:5px;">Compagnie</label><select id="selectCompagnieCruise" onchange="filtrerCroisieres()"><option value="Toutes">Toutes</option></select></div>
            </div>

            <div id="listeCroisieres" style="margin-bottom: 30px;"></div>
            {footer_html_shared}
        </div>

        <!-- BLOG -->
        <div id="section-blog" class="page-section" style="display:none;">
            <h1>📖 Notre Blog Voyage</h1>
            <div class="blog-grid" style="margin-bottom: 30px;">
                {blog_cards_html}
            </div>
            {footer_html_shared}
        </div>

        <!-- PAGE À PROPOS -->
        <div id="section-apropos" class="page-section" style="display:none;">
            <div class="page-content-card">
                <h1>ℹ️ À propos de MyHotelCompare</h1>
                <p style="color: #94a3b8; font-size: 1.1em;">Votre assistant intelligent pour trouver et comparer les meilleurs séjours au meilleur prix.</p>
                <hr style="border-color: #3A506B; margin: 25px 0;">
                
                <h3>🎯 Notre Mission</h3>
                <p><b>MyHotelCompare</b> est né d'un constat simple : comparer des centaines d'hôtels et de plateformes prend un temps précieux. Notre mission est de vous simplifier la vie grâce à une interface claire, rapide et propulsée par des technologies intelligentes pour résumer l'essentiel en un clin d'œil.</p>
                
                <h3>💡 Ce que nous proposons</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0;">
                    <div style="background: #0B132B; padding: 20px; border-radius: 8px; border: 1px solid #3A506B;">
                        <h4 style="color: #38bdf8; margin-top:0;">🏨 Comparaison</h4>
                        <p style="color: #cbd5e1; margin-bottom:0;">Comparez côte à côte les équipements, les notes, les prix et les photos de vos hôtels favoris.</p>
                    </div>
                    <div style="background: #0B132B; padding: 20px; border-radius: 8px; border: 1px solid #3A506B;">
                        <h4 style="color: #38bdf8; margin-top:0;">🤖 Analyse IA</h4>
                        <p style="color: #cbd5e1; margin-bottom:0;">Bénéficiez de résumés automatiques et d'avis synthétisés pour savoir instantanément quel hôtel vous correspond.</p>
                    </div>
                    <div style="background: #0B132B; padding: 20px; border-radius: 8px; border: 1px solid #3A506B;">
                        <h4 style="color: #38bdf8; margin-top:0;">✈️ Multidiscipline</h4>
                        <p style="color: #cbd5e1; margin-bottom:0;">Retrouvez également des outils pour comparer les compagnies aériennes et planifier vos voyages plus sereinement.</p>
                    </div>
                </div>

                <hr style="border-color: #3A506B; margin: 25px 0;">
                <h3>🔒 Notre Engagement</h3>
                <div style="background: rgba(56, 189, 248, 0.1); border-left: 4px solid #38bdf8; padding: 15px; border-radius: 0 8px 8px 0; color: #e2e8f0;">
                    Nous mettons un point d'honneur à vous offrir une information transparente et neutre. Toutes les données affichées ont pour but de vous aider à faire le meilleur choix pour vos vacances ou vos déplacements professionnels.
                </div>
            </div>
            {footer_html_shared}
        </div>

        <!-- PAGE POLITIQUE DE CONFIDENTIALITE -->
        <div id="section-confidentialite" class="page-section" style="display:none;">
            <div class="page-content-card">
                <h1>🔒 Politique de confidentialité</h1>
                <p style="color: #94a3b8;">Dernière mise à jour : Août 2026</p>
                <hr style="border-color: #3A506B; margin: 25px 0;">

                <h3>1. Introduction</h3>
                <p>Bienvenue sur <b>MyHotelCompare</b>. Nous accordons une importance majeure à la protection de votre vie privée et de vos données personnelles. Cette politique de confidentialité vous informe sur la manière dont nous traitons vos informations lors de l'utilisation de notre comparateur.</p>

                <h3>2. Données collectées</h3>
                <p>Dans le cadre de votre navigation sur notre site, nous pouvons collecter les types de données suivants :</p>
                <ul style="color: #e2e8f0; line-height: 1.8;">
                    <li><b>Préférences de recherche :</b> Les pays, villes et hôtels que vous sélectionnez pour effectuer vos comparaisons.</li>
                    <li><b>Données de contact :</b> Votre nom, votre adresse e-mail et vos messages si vous utilisez notre formulaire de contact.</li>
                    <li><b>Données techniques :</b> Informations de session nécessaires au bon fonctionnement de l'interface.</li>
                </ul>

                <h3>3. Utilisation des données</h3>
                <p>Les informations que vous nous transmettez sont utilisées exclusivement pour :</p>
                <ul style="color: #e2e8f0; line-height: 1.8;">
                    <li>Vous fournir les résultats de comparaison d'hôtels et de vols.</li>
                    <li>Améliorer l'ergonomie et les fonctionnalités de l'application.</li>
                    <li>Répondre à vos demandes ou suggestions.</li>
                </ul>

                <h3>4. Protection des données</h3>
                <p>Nous mettons en œuvre des mesures de sécurité techniques et organisationnelles appropriées pour protéger vos données contre tout accès, modification, divulgation ou destruction non autorisée.</p>

                <h3>5. Vos droits</h3>
                <p>Conformément à la réglementation applicable en matière de protection des données, vous disposez d'un droit d'accès, de rectification et de suppression des informations vous concernant.</p>
            </div>
            {footer_html_shared}
        </div>

        <!-- PAGE CONTACT -->
        <div id="section-contact" class="page-section" style="display:none;">
            <div class="page-content-card" style="text-align: center; max-width: 700px; margin: 0 auto;">
                <h1 style="margin-bottom: 10px;">📞 Contactez-nous</h1>
                <hr style="border-color: #3A506B; margin: 25px 0;">
                
                <div style="background-color: #0B132B; border: 1px solid #3A506B; border-radius: 12px; padding: 40px; text-align: center;">
                    <h3 style="color: #FFFFFF; margin-bottom: 15px; font-size: 24px;">💬 Un besoin, une question ou une suggestion ?</h3>
                    <p style="font-size: 16px; color: #FFFFFF; margin-bottom: 10px; line-height: 1.5;">
                        Pour mieux vous répondre et assurer un suivi personnalisé, nous communiquons exclusivement par <b>message privé sur notre page Facebook</b>.
                    </p>
                    <p style="color: #94a3b8; font-size: 14px; margin-bottom: 30px;">Notre équipe vous répondra dans les plus brefs délais !</p>
                    
                    <a href="https://www.facebook.com/profile.php?id=61591545557027" target="_blank" style="background-color: #1877f2; color: #ffffff !important; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                        💬 Envoyer un message sur Facebook
                    </a>
                </div>
            </div>
            {footer_html_shared}
        </div>

        <!-- DETAILS -->
        {blog_sections_html}
        {hotel_details_sections_html}
    </div>

    <script>
        const hotelsData = {hotels_js_data};
        const loueursData = {loueurs_js_data};
        const cruisesData = {cruises_js_data};
        const airlinesData = {airlines_js_data};

        function showSection(id) {{
            document.querySelectorAll('.page-section').forEach(el => el.style.display = 'none');
            const target = document.getElementById('section-' + id);
            if (target) {{
                target.style.display = 'block';
                window.scrollTo(0, 0);
            }}
        }}

        function initFiltres() {{
            const selectPays = document.getElementById('selectPays');
            if (selectPays) {{
                const paysSet = [...new Set(hotelsData.map(h => h.pays).filter(Boolean))].sort();
                selectPays.innerHTML = '<option value="">Tous les pays</option>';
                paysSet.forEach(p => {{ 
                    let opt = document.createElement('option'); 
                    opt.value = p; 
                    opt.textContent = p; 
                    selectPays.appendChild(opt); 
                }});
                updateVilles();
            }}

            const selectLoueur = document.getElementById('selectLoueur');
            if (selectLoueur) {{
                selectLoueur.innerHTML = '<option value="">Sélectionnez un loueur...</option>';
                Object.keys(loueursData).forEach(nom => {{
                    let opt = document.createElement('option');
                    opt.value = nom;
                    opt.textContent = nom;
                    selectLoueur.appendChild(opt);
                }});
            }}

            const selectAirline = document.getElementById('selectAirline');
            if (selectAirline) {{
                selectAirline.innerHTML = '<option value="">Sélectionnez...</option>';
                Object.keys(airlinesData).sort().forEach(nom => {{
                    let opt = document.createElement('option');
                    opt.value = nom;
                    opt.textContent = nom;
                    selectAirline.appendChild(opt);
                }});
            }}

            initCroisieres();
        }}

        function updateVilles() {{
            const pays = document.getElementById('selectPays').value;
            const selectVille = document.getElementById('selectVille');
            if (!selectVille) return;
            selectVille.innerHTML = '<option value="">Toutes les villes</option>';
            const villesSet = [...new Set(hotelsData.filter(h => !pays || h.pays === pays).map(h => h.ville).filter(Boolean))].sort();
            villesSet.forEach(v => {{ 
                let opt = document.createElement('option'); 
                opt.value = v; 
                opt.textContent = v; 
                selectVille.appendChild(opt); 
            }});
            updateHotels();
        }}

        function updateHotels() {{
            const pays = document.getElementById('selectPays').value;
            const ville = document.getElementById('selectVille').value;
            const filtered = hotelsData.filter(h => (!pays || h.pays === pays) && (!ville || h.ville === ville));
            const s1 = document.getElementById('selectHotel1'); 
            const s2 = document.getElementById('selectHotel2');
            if (!s1 || !s2) return;
            s1.innerHTML = '<option value="">1er hébergement</option>'; 
            s2.innerHTML = '<option value="">2nd hébergement</option>';
            filtered.forEach(h => {{
                s1.appendChild(new Option(h.nom, h.slug));
                s2.appendChild(new Option(h.nom, h.slug));
            }});
        }}

        function lancerComparaison() {{
            const h1Val = document.getElementById('selectHotel1').value;
            const h2Val = document.getElementById('selectHotel2').value;
            const h1 = hotelsData.find(h => h.slug === h1Val);
            const h2 = hotelsData.find(h => h.slug === h2Val);
            let html = '';
            if (h1) html += renderCard(h1);
            if (h2) html += renderCard(h2);
            document.getElementById('resultatComparaison').innerHTML = html || '<p style="color:#94a3b8; grid-column:span 2; text-align:center;">Veuillez sélectionner au moins un hôtel.</p>';
        }}

        function renderCard(h) {{
            const mapQuery = encodeURIComponent(h.nom + ", " + h.ville + ", " + h.pays);
            return `<div class="hotel-card">
                ${{h.image ? '<img src="' + h.image + '" style="width:100%; height:180px; object-fit:cover; border-radius:8px; margin-bottom:10px;">' : ''}}
                <h3>${{h.nom}}</h3>
                <p style="color:#94a3b8;">📍 ${{h.ville}}, ${{h.pays}} | ⭐ ${{h.etoiles}}</p>
                <p style="color:#10B981; font-weight:bold;">💰 ${{h.prix}}</p>
                <button onclick="showSection('hotel-detail-${{h.slug}}')" style="display:block; background:#3A506B; color:white; border:none; width:100%; padding:8px; text-align:center; border-radius:6px; margin-bottom:10px; cursor:pointer; font-weight:bold;">📄 Voir la fiche détaillée</button>
                <a href="${{h.lien_booking}}" target="_blank" class="btn-booking">Réserver sur Booking</a>
                <a href="${{h.lien_expedia}}" target="_blank" class="btn-expedia">Réserver sur Expedia</a>
                <iframe width="100%" height="150" style="border:0; border-radius:6px; margin-top:10px;" src="https://maps.google.com/maps?q=${{mapQuery}}&output=embed"></iframe>
            </div>`;
        }}

        function afficherLoueur() {{
            const nom = document.getElementById('selectLoueur').value;
            const container = document.getElementById('detailLoueur');
            if (!nom || !loueursData[nom]) {{
                container.innerHTML = '';
                return;
            }}
            const l = loueursData[nom];
            container.innerHTML = `
                <hr style="border-color: #3A506B; margin: 20px 0;">
                <div style="display: flex; gap: 20px; align-items: center; flex-wrap: wrap;">
                    <div style="background-color: #3b82f6; color: white; padding: 12px 20px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 16px;">
                        ${{l.rang}}
                    </div>
                    <div>
                        <h2 style="margin: 0 0 5px 0;">${{nom}}</h2>
                        <p style="margin: 0; color: #94a3b8;"><b>Note globale :</b> ⭐ ${{l.note}}</p>
                    </div>
                </div>
                <p style="margin-top: 15px; color: #e2e8f0; font-size: 1.1em;"><b>Résumé des avis :</b> ${{l.resume}}</p>
            `;
        }}

        function afficherAirline() {{
            const nom = document.getElementById('selectAirline').value;
            const container = document.getElementById('detailAirline');
            if (!nom || !airlinesData[nom]) {{
                container.innerHTML = '';
                return;
            }}
            const d = airlinesData[nom];
            
            let positifs = (d.points_positifs || []).map(p => `<li>${{p}}</li>`).join('');
            let negatifs = (d.points_negatifs || []).map(n => `<li>${{n}}</li>`).join('');
            let liaisons = (d.liaisons || []).join(', ');

            container.innerHTML = `
                <hr style="border-color: #3A506B; margin: 20px 0;">
                <h2>${{nom}}</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                    <div style="background:#1C2541; padding:15px; border-radius:8px; border:1px solid #3A506B;"><b>Catégorie</b><br>${{d.categorie || 'N/A'}}</div>
                    <div style="background:#1C2541; padding:15px; border-radius:8px; border:1px solid #3A506B;"><b>Alliance</b><br>${{d.alliance || 'N/A'}}</div>
                    <div style="background:#1C2541; padding:15px; border-radius:8px; border:1px solid #3A506B;"><b>Note globale</b><br>⭐ ${{d.note || 'N/A'}}</div>
                </div>
                <h3>📖 À propos</h3>
                <p style="color:#e2e8f0;">${{d.resume || ''}}</p>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; margin:20px 0;">
                    <div><b>📜 Histoire :</b> ${{d.histoire || 'N/A'}}<br><br><b>✈️ Flotte :</b> ${{d.flotte || 'N/A'}}</div>
                    <div><b>🧳 Bagages :</b> ${{d.bagages || 'N/A'}}<br><br><b>🛡️ Sécurité :</b> ${{d.securite || 'N/A'}}</div>
                </div>
                <p><b>📍 Liaisons fréquentes :</b> ${{liaisons}}</p>
                <p style="background:#1C2541; padding:15px; border-radius:8px; border-left:4px solid #38bdf8;"><b>🎯 Pour qui ?</b> ${{d.pour_qui || ''}}</p>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-top:20px;">
                    <div style="background:rgba(16,185,129,0.1); padding:15px; border-radius:8px; border:1px solid #10B981;"><h4 style="color:#10B981; margin-top:0;">✅ Points Positifs</h4><ul>${{positifs}}</ul></div>
                    <div style="background:rgba(239,68,68,0.1); padding:15px; border-radius:8px; border:1px solid #EF4444;"><h4 style="color:#EF4444; margin-top:0;">⚠️ Points de vigilance</h4><ul>${{negatifs}}</ul></div>
                </div>
                ${{d.lien ? `<a href="${{d.lien}}" target="_blank" style="display:block; background:#0066cc; color:white; padding:12px; text-align:center; text-decoration:none; border-radius:6px; font-weight:bold; margin-top:25px;">Réserver le vol</a>` : ''}}
            `;
        }}

        function initCroisieres() {{
            const sReg = document.getElementById('selectRegionCruise');
            const sComp = document.getElementById('selectCompagnieCruise');
            if (!sReg || !sComp) return;

            let regions = new Set();
            let compagnies = new Set();
            Object.values(cruisesData).forEach(c => {{
                if (c.region) regions.add(c.region);
                if (c.compagnie) compagnies.add(c.compagnie);
            }});

            sReg.innerHTML = '<option value="Toutes">Toutes</option>';
            [...regions].sort().forEach(r => sReg.innerHTML += `<option value="${{r}}">${{r}}</option>`);

            sComp.innerHTML = '<option value="Toutes">Toutes</option>';
            [...compagnies].sort().forEach(cp => sComp.innerHTML += `<option value="${{cp}}">${{cp}}</option>`);

            filtrerCroisieres();
        }}

        function filtrerCroisieres() {{
            const reg = document.getElementById('selectRegionCruise').value;
            const comp = document.getElementById('selectCompagnieCruise').value;
            const container = document.getElementById('listeCroisieres');
            
            let html = '';
            let count = 0;

            Object.entries(cruisesData).forEach(([nom, data]) => {{
                if (reg !== 'Toutes' && data.region !== reg) return;
                if (comp !== 'Toutes' && data.compagnie !== comp) return;
                count++;

                let itineraireHtml = '';
                if (data.itineraire_detaille && data.itineraire_detaille.length > 0) {{
                    itineraireHtml = `<details style="margin-top:10px; color:#94a3b8; cursor:pointer;"><summary style="font-weight:bold; color:#38bdf8;">🗺️ Voir l'itinéraire détaillé jour par jour</summary><ul style="margin:5px 0 0 20px; padding:0;">`;
                    data.itineraire_detaille.length && data.itineraire_detaille.forEach(j => {{ itineraireHtml += `<li>${{j}}</li>`; }});
                    itineraireHtml += `</ul></details>`;
                }}

                html += `
                <div class="cruise-card">
                    <div>
                        ${{data.image ? `<img src="${{data.image}}" style="width:100%; height:160px; object-fit:cover; border-radius:6px;">` : ''}}
                    </div>
                    <div>
                        <h3 style="margin-top:0; color:white;">${{nom}}</h3>
                        <p style="margin:5px 0; color:#94a3b8;"><b>Compagnie :</b> ${{data.compagnie || ''}} | <b>Région :</b> ${{data.region || ''}} | <b>Durée :</b> ${{data.duree || ''}}</p>
                        <p style="color:#e2e8f0; margin-top:10px;">${{data.description || ''}}</p>
                        ${{itineraireHtml}}
                    </div>
                    <div style="display:flex; flex-direction:column; justify-content:space-between; text-align:right;">
                        <div>
                            <span style="font-size:1.2em; font-weight:bold; color:#10B981;">${{data.prix_moyen || 'Sur demande'}}</span>
                        </div>
                        ${{data.lien_reservation ? `<a href="${{data.lien_reservation}}" target="_blank" style="display:block; background:#003580; color:white; padding:10px; text-align:center; text-decoration:none; border-radius:6px; font-weight:bold; margin-top:15px;">Réserver</a>` : ''}}
                    </div>
                </div>`;
            }});

            if (count === 0) {{
                html = '<p style="color:#94a3b8; text-align:center; padding:20px;">Aucune croisière ne correspond à vos critères.</p>';
            }}

            container.innerHTML = `<h3 style="margin-bottom:20px;">📋 Résultats (${{count}} croisières trouvées)</h3>` + html;
        }}

        window.onload = initFiltres;
    </script>
</body>
</html>
"""

with open(f"{output_dir}/index.html", "w", encoding="utf-8") as f:
    f.write(html_monolithique)

print("Génération réussie : le caroussel est intégré et tout le site est assemblé !")