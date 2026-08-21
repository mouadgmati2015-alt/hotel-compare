import json
import os
import re
import base64
import shutil

# On utilise un nouveau dossier propre pour éviter les vieux fichiers en cache
output_dir = "mon_site_final"
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir, exist_ok=True)

def nettoyer_slug(texte):
    texte = texte.lower().strip()
    texte = re.sub(r'[^a-z0-9]+', '-', texte)
    return texte.strip('-')

def get_img_as_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# 1. Chargement des données d'hôtels depuis data/
HOTELS_DATA_COMPLET = {}
all_hotels = []
data_dir = "data"

if os.path.exists(data_dir):
    for filename in os.listdir(data_dir):
        if filename.endswith(".json") and filename != "promo_semaine.json":
            chemin_fichier = os.path.join(data_dir, filename)
            with open(chemin_fichier, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict):
                        for nom, d in data.items():
                            if not isinstance(d, dict): continue
                            slug = nettoyer_slug(nom)
                            if slug:
                                HOTELS_DATA_COMPLET[nom] = d
                                all_hotels.append({
                                    'nom': nom, 'slug': slug, 'ville': d.get('ville', ''), 'pays': d.get('pays', ''),
                                    'etoiles': d.get('etoiles', 'N/C'), 'prix': d.get('prix_moyen', 'Sur demande'),
                                    'image': d.get('image', ''), 'description': d.get('description_ia') or d.get('description', ''),
                                    'lien_booking': d.get('lien_booking', '#'), 'lien_expedia': d.get('lien_expedia', '#')
                                })
                except Exception as e:
                    print(f"Erreur sur {filename}: {e}")

# 2. Promo de la semaine
promo_html = ""
chemin_promo = os.path.join(data_dir, "promo_semaine.json")
if os.path.exists(chemin_promo):
    try:
        with open(chemin_promo, "r", encoding="utf-8") as f:
            promo = json.load(f)
            if isinstance(promo, dict):
                img_promo = promo.get("image", "")
                titre_promo = promo.get("titre", "")
                ville_promo = promo.get("ville", "")
                pays_promo = promo.get("pays", "")
                desc_promo = promo.get("description", "")
                promo_html = f"""
                <div style="background-color: #1C2541; border: 1px solid #3A506B; border-radius: 12px; padding: 20px; height: 100%; box-sizing: border-box;">
                    {f'<img src="{img_promo}" style="width: 100%; height: 160px; object-fit: cover; border-radius: 6px; margin-bottom: 8px;">' if img_promo else ''}
                    <h3 style="margin-top: 0; color: white;">{titre_promo}</h3>
                    {f"<p style='color: #94a3b8; font-size: 0.85em; margin-top: -8px; margin-bottom: 6px;'>📍 {ville_promo}{', ' if ville_promo and pays_promo else ''}{pays_promo}</p>" if (ville_promo or pays_promo) else ''}
                    <p style="color: white; font-size: 0.95em;">{desc_promo}</p>
                </div>
                """
    except Exception as e:
        print(f"Erreur promo : {e}")

# Carrousel
img_paths = ["images/image caroussel 2.png", "images/image_afrique.jpg", "images/image_astuce.jpg", "images/image_hotel.jpg", "images/image_tunisie.jpg"]
imgs_base64 = [get_img_as_base64(p) for p in img_paths]

carousel_html = f"""
<div style="width: 100%; height: 350px; position: relative; overflow: hidden; border-radius: 12px; background: #0e1117; border: 1px solid #3A506B;">
    <style>
    @keyframes customFade {{ 0% {{ opacity: 0; }} 6% {{ opacity: 1; }} 20% {{ opacity: 1; }} 26% {{ opacity: 0; }} 100% {{ opacity: 0; }} }}
    .hotel-slide-item {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; border-radius: 12px; opacity: 0; animation: customFade 15s infinite; }}
    </style>
    {f'<img class="hotel-slide-item" src="data:image/png;base64,{imgs_base64[0]}" style="animation-delay: 0s;">' if imgs_base64[0] else ''}
    {f'<img class="hotel-slide-item" src="data:image/jpeg;base64,{imgs_base64[1]}" style="animation-delay: 3s;">' if imgs_base64[1] else ''}
    {f'<img class="hotel-slide-item" src="data:image/jpeg;base64,{imgs_base64[2]}" style="animation-delay: 6s;">' if imgs_base64[2] else ''}
    {f'<img class="hotel-slide-item" src="data:image/jpeg;base64,{imgs_base64[3]}" style="animation-delay: 9s;">' if imgs_base64[3] else ''}
    {f'<img class="hotel-slide-item" src="data:image/jpeg;base64,{imgs_base64[4]}" style="animation-delay: 12s;">' if imgs_base64[4] else ''}
</div>
"""

logo_b64 = get_img_as_base64("logo_4.png")
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="width: 70px; height: 70px; object-fit: contain; border-radius: 8px;">' if logo_b64 else ''

menu_html = """
<div class="top-nav">
    <a href="index.html">Accueil</a>
    <a href="hotels.html">Hôtels</a>
    <a href="compagnies-aeriennes.html">Compagnies Aériennes</a>
    <a href="loueurs-vehicules.html">Location de Véhicules</a>
    <a href="croisieres.html">Croisières</a>
    <a href="blog.html">Blog</a>
</div>
"""

# 3. Page d'accueil
html_accueil = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>MyHotelCompare - Comparateur d'hôtels</title>
    <style>
        body {{ background-color: #0B132B !important; color: #FFFFFF !important; font-family: sans-serif; margin: 0; padding: 20px; }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        .top-nav {{ display: flex; gap: 10px; background-color: #1C2541; padding: 15px; border-radius: 10px; margin-bottom: 25px; border: 1px solid #3A506B; overflow-x: auto; }}
        .top-nav a {{ color: white; background-color: #3A506B; padding: 8px 16px; border-radius: 6px; text-decoration: none; }}
        .header-box {{ display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 10px; }}
        .top-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }}
        @media (max-width: 768px) {{ .top-grid {{ grid-template-columns: 1fr; }} }}
        .features-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }}
        @media (max-width: 768px) {{ .features-grid {{ grid-template-columns: 1fr; }} }}
        .feature-box {{ background-color: #1C2541; border: 1px solid #3A506B; border-radius: 10px; padding: 20px; }}
        .feature-box h4 {{ color: #38bdf8; margin-top: 0; }}
        .btn-cta {{ background-color: #10B981; color: white; padding: 14px 30px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; }}
    </style>
</head>
<body>
    <div class="container">
        {menu_html}
        <div class="header-box">{logo_html}<h1 style="margin:0;">Comparateur intelligent d'hôtels</h1></div>
        <p style="text-align: center; color: #94a3b8; font-size: 1.2em; margin-bottom: 30px;"><b>Nomad</b> : L'IA qui analyse les avis pour dénicher votre hôtel idéal.</p>
        <div class="top-grid"><div>{carousel_html}</div><div>{promo_html}</div></div>
        <h2 style="text-align: center; margin: 40px 0 20px 0;">Pourquoi choisir MyHotelCompare ?</h2>
        <div class="features-grid">
            <div class="feature-box"><h4>🤖 IA Nomad</h4><p>Analyse automatique des vrais avis clients pour éviter les pièges.</p></div>
            <div class="feature-box"><h4>🎯 Sur-Mesure</h4><p>Trouvez l'hôtel idéal selon vos critères (spa, plage privée...).</p></div>
            <div class="feature-box"><h4>💼 Zéro Stress</h4><p>Maîtrisez votre budget et profitez d'un séjour en toute sérénité.</p></div>
        </div>
        <div style="text-align: center; margin: 40px 0;"><a href="hotels.html" class="btn-cta">🚀 Accéder au comparateur d'hôtels</a></div>
    </div>
</body>
</html>
"""
with open(f"{output_dir}/index.html", "w", encoding="utf-8") as f:
    f.write(html_accueil)

# 4. Page hotels.html (Comparateur)
hotels_js_data = json.dumps(all_hotels, ensure_ascii=False)
html_hotels = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Comparateur d'hôtels | MyHotelCompare</title>
    <style>
        body {{ background-color: #0B132B; color: #FFFFFF; font-family: sans-serif; padding: 20px; margin: 0; }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        .top-nav {{ display: flex; gap: 10px; background-color: #1C2541; padding: 15px; border-radius: 10px; margin-bottom: 25px; border: 1px solid #3A506B; overflow-x: auto; }}
        .top-nav a {{ color: white; background-color: #3A506B; padding: 8px 16px; border-radius: 6px; text-decoration: none; }}
        .filters-box {{ background-color: #1C2541; border: 1px solid #3A506B; border-radius: 10px; padding: 20px; margin-bottom: 25px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .filters-box select {{ width: 100%; padding: 10px; border-radius: 6px; border: 1px solid #3A506B; background-color: #0B132B; color: white; }}
        .btn-compare {{ background-color: #10B981; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; }}
        .comparison-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        @media (max-width: 768px) {{ .comparison-grid {{ grid-template-columns: 1fr; }} }}
        .hotel-card {{ background-color: #1C2541; border: 1px solid #3A506B; border-radius: 12px; padding: 20px; box-sizing: border-box; }}
        .btn-booking {{ display: block; background-color: #003580; color: white; padding: 10px; text-align: center; text-decoration: none; border-radius: 6px; font-weight: bold; margin-bottom: 8px; }}
        .btn-expedia {{ display: block; background-color: #ffcc00; color: #000; padding: 10px; text-align: center; text-decoration: none; border-radius: 6px; font-weight: bold; margin-bottom: 8px; }}
    </style>
</head>
<body>
    <div class="container">
        {menu_html}
        <h2>💡 Comparateur d'hôtels</h2>
        <div class="filters-box">
            <div><label style="color:#94a3b8; display:block; margin-bottom:5px;">Pays</label><select id="selectPays" onchange="updateVilles()"><option value="">Tous les pays</option></select></div>
            <div><label style="color:#94a3b8; display:block; margin-bottom:5px;">Ville</label><select id="selectVille" onchange="updateHotels()"><option value="">Toutes les villes</option></select></div>
            <div><label style="color:#94a3b8; display:block; margin-bottom:5px;">Premier hôtel</label><select id="selectHotel1"><option value="">Choisissez...</option></select></div>
            <div><label style="color:#94a3b8; display:block; margin-bottom:5px;">Deuxième hôtel</label><select id="selectHotel2"><option value="">Choisissez...</option></select></div>
        </div>
        <button class="btn-compare" onclick="lancerComparaison()">🚀 Lancer la comparaison</button>
        <div id="resultatComparaison" class="comparison-grid" style="margin-top: 30px;"></div>
    </div>
    <script>
        const hotelsData = {hotels_js_data};
        function initFiltres() {{
            const paysSet = [...new Set(hotelsData.map(h => h.pays).filter(Boolean))].sort();
            const selectPays = document.getElementById('selectPays');
            paysSet.forEach(p => {{ let opt = document.createElement('option'); opt.value = p; opt.textContent = p; selectPays.appendChild(opt); }});
            updateVilles();
        }}
        function updateVilles() {{
            const pays = document.getElementById('selectPays').value;
            const selectVille = document.getElementById('selectVille');
            selectVille.innerHTML = '<option value="">Toutes les villes</option>';
            const villesSet = [...new Set(hotelsData.filter(h => !pays || h.pays === pays).map(h => h.ville).filter(Boolean))].sort();
            villesSet.forEach(v => {{ let opt = document.createElement('option'); opt.value = v; opt.textContent = v; selectVille.appendChild(opt); }});
            updateHotels();
        }}
        function updateHotels() {{
            const pays = document.getElementById('selectPays').value;
            const ville = document.getElementById('selectVille').value;
            const filtered = hotelsData.filter(h => (!pays || h.pays === pays) && (!ville || h.ville === ville));
            const s1 = document.getElementById('selectHotel1'); const s2 = document.getElementById('selectHotel2');
            s1.innerHTML = '<option value="">1er hébergement</option>'; s2.innerHTML = '<option value="">2nd hébergement</option>';
            filtered.forEach(h => {{
                s1.appendChild(new Option(h.nom, h.slug));
                s2.appendChild(new Option(h.nom, h.slug));
            }});
        }}
        function lancerComparaison() {{
            const h1 = hotelsData.find(h => h.slug === document.getElementById('selectHotel1').value);
            const h2 = hotelsData.find(h => h.slug === document.getElementById('selectHotel2').value);
            let html = '';
            if (h1) html += renderCard(h1);
            if (h2) html += renderCard(h2);
            document.getElementById('resultatComparaison').innerHTML = html || '<p style="color:#94a3b8; grid-column:span 2; text-align:center;">Veuillez sélectionner au moins un hôtel.</p>';
        }}
        function renderCard(h) {{
            const mapQuery = encodeURIComponent(h.nom + ", " + h.ville + ", " + h.pays);
            return `<div class="hotel-card">
                ${{h.image ? '<img src="' + h.image + '" style="width:100%; height:180px; object-fit:cover; border-radius:8px; margin-bottom:10px;">' : ''}}
                <h3><a href="${{h.slug}}.html" style="color:#38bdf8; text-decoration:none;">${{h.nom}}</a></h3>
                <p style="color:#94a3b8;">📍 ${{h.ville}}, ${{h.pays}} | ⭐ ${{h.etoiles}}</p>
                <p style="color:#10B981; font-weight:bold;">💰 ${{h.prix}}</p>
                <a href="${{h.slug}}.html" style="display:block; background:#3A506B; color:white; padding:8px; text-align:center; text-decoration:none; border-radius:6px; margin-bottom:10px;">📄 Voir la fiche détaillée</a>
                <a href="${{h.lien_booking}}" target="_blank" class="btn-booking">Réserver sur Booking</a>
                <a href="${{h.lien_expedia}}" target="_blank" class="btn-expedia">Réserver sur Expedia</a>
                <iframe width="100%" height="150" style="border:0; border-radius:6px; margin-top:10px;" src="https://maps.google.com/maps?q=${{mapQuery}}&output=embed"></iframe>
            </div>`;
        }}
        window.onload = initFiltres;
    </script>
</body>
</html>
"""
with open(f"{output_dir}/hotels.html", "w", encoding="utf-8") as f:
    f.write(html_hotels)

# 5. Fiches individuelles des hôtels
for h_nom, d in HOTELS_DATA_COMPLET.items():
    slug = nettoyer_slug(h_nom)
    if not slug: continue
    html_fiche = f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><title>{h_nom}</title>
<style>
body {{ background-color: #0B132B; color: #FFFFFF; font-family: sans-serif; padding: 20px; margin: 0; }}
.container {{ max-width: 900px; margin: 0 auto; }}
.top-nav {{ display: flex; gap: 10px; background-color: #1C2541; padding: 15px; border-radius: 10px; margin-bottom: 25px; border: 1px solid #3A506B; overflow-x: auto; }}
.top-nav a {{ color: white; background-color: #3A506B; padding: 8px 16px; border-radius: 6px; text-decoration: none; }}
.hotel-box {{ background-color: #1C2541; border: 1px solid #3A506B; border-radius: 12px; padding: 25px; }}
</style></head>
<body><div class="container">{menu_html}
<a href="hotels.html" style="color: #38bdf8; display: inline-block; margin-bottom: 15px;">← Retour</a>
<div class="hotel-box">
    <h1>{h_nom}</h1>
    <p style="color: #94a3b8;">📍 {d.get('ville','')}, {d.get('pays','')} | ⭐ {d.get('etoiles','N/C')}</p>
    {f'<img src="{d.get("image")}" style="width:100%; max-height:350px; object-fit:cover; border-radius:8px; margin:15px 0;">' if d.get('image') else ''}
    <h3>✨ Description</h3><p>{d.get('description_ia') or d.get('description', '')}</p>
    <h3>🛠️ Équipements</h3><p>{', '.join(d.get('equipements', []))}</p>
</div></div></body></html>"""
    with open(f"{output_dir}/{slug}.html", "w", encoding="utf-8") as f:
        f.write(html_fiche)

# 6. Vos 11 articles de blog complets avec leurs textes détaillés
articles_blog = [
    {
        "titre": "5 astuces d'expert pour voyager moins cher",
        "slug": "5-astuces-d-expert-pour-voyager-moins-cher",
        "image": "images/image_astuce.jpg",
        "resume": "Voyager ne signifie pas forcément se ruiner.",
        "details": "Vous rêvez de vacances inoubliables sans pour autant faire exploser votre budget ? En tant qu'experts chez HotelCompare, nous analysons quotidiennement les tendances tarifaires. Voici nos 5 astuces imparables.<br><br><b>1. La flexibilité des dates</b><br>Décaler vos dates de départ de seulement 48 heures peut vous faire économiser jusqu'à 30 %.<br><br><b>2. Anticipez ou profitez des Last Minute</b><br>Early Booking ou dernière minute selon votre profil d'aventurier."
    },
    {
        "titre": "Le guide ultime pour choisir son hôtel en Tunisie",
        "slug": "le-guide-ultime-pour-choisir-son-hotel-en-tunisie",
        "image": "images/image_hotel.jpg",
        "resume": "Choisir le mauvais hôtel peut gâcher un séjour.",
        "details": "Choisir l'hébergement idéal pour ses vacances peut parfois ressembler à un casse-tête, surtout face à la richesse des destinations tunisiennes (Djerba, Sousse, Hammamet)."
    },
    {
        "titre": "Découvrir la Tunisie autrement : mes coups de cœur",
        "slug": "decouvrir-la-tunisie-autrement",
        "image": "images/image_tunisie.jpg",
        "resume": "Loin des circuits classiques, la Tunisie regorge de pépites.",
        "details": "La Tunisie est souvent associée à ses magnifiques stations balnéaires. Pourtant, au-delà des piscines, se cache une terre de contrastes saisissants, du désert du Sud aux maisons d'hôtes traditionnelles."
    },
    {
        "titre": "Préparer son voyage en Afrique : Le guide indispensable",
        "slug": "preparer-son-voyage-en-afrique",
        "image": "images/image_afrique.jpg",
        "resume": "Préparer un voyage en Afrique demande une organisation rigoureuse.",
        "details": "La santé, les vaccinations (fièvre jaune, paludisme), les formalités de passeport et l'assurance voyage sont des piliers incontournables pour un séjour en toute sérénité."
    },
    {
        "titre": "Quand partir et où ? Le calendrier des voyageurs malins",
        "slug": "quand-partir-et-ou",
        "image": "images/test.jpg",
        "resume": "Pour voyager à moindre coût, la règle d'or est de privilégier le hors-saison.",
        "details": "Découvrez le calendrier des destinations économiques mois par mois pour fuir la haute saison et profiter de tarifs exceptionnels."
    },
    {
        "titre": "Comprendre les algorithmes de prix des hôtels",
        "slug": "comprendre-les-algorithmes-de-prix",
        "image": "images/algorythme.jpg",
        "resume": "Pourquoi les prix des hôtels changent constamment ? Décryptage des algorithmes.",
        "details": "Le *Revenue Management* fait varier les prix en fonction du taux d'occupation, de la vitesse de réservation et de la saisonnalité."
    },
    {
        "titre": "Avis Hôtel Virginia Resort Sharm El Sheikh : Mon séjour cauchemardesque de 7 nuits",
        "slug": "avis-hotel-virginia-resort",
        "image": "images/virginia.png",
        "resume": "Un séjour de 7 nuits qui a tourné au cauchemar. Cet établissement ne mérite pas ses 4 étoiles.",
        "details": "Chambres vétustes, restauration répétitive (poulet en boucle, absence de fruits variés), formule All-Inclusive s'arrêtant à 22h00... Un récit sans filtre."
    },
    {
        "titre": "Des excursions inoubliables : À la découverte des trésors cachés",
        "slug": "des-excursions-inoubliables",
        "image": "images/im1.jpg",
        "resume": "Récit de voyage, découvertes extraordinaires et un grand merci à notre super guide Mister Heni !",
        "details": "Old Market, Soho Square, Île Blanche en mer Rouge, Farsha Café et virée en quad dans le désert du Sinaï : un séjour inoubliable à Charm el-Cheikh."
    },
    {
        "titre": "L'Avenir du Voyage : Comment le Changement Climatique Redéfinit nos Vacances",
        "slug": "l-avenir-du-voyage",
        "image": "images/avenir_voyage.png",
        "resume": "Découvrez pourquoi et comment nos habitudes de vacances évoluent face au changement climatique.",
        "details": "Entre recherche de fraîcheur dans le Nord, essor du slow tourism et prise de conscience écologique, nos manières de voyager se réinventent."
    },
    {
        "titre": "Comment trouver un hôtel moins cher : 7 astuces infaillibles",
        "slug": "comment-trouver-un-hotel-moins-cher",
        "image": "images/astuces_hotels.png",
        "resume": "Réserver un hébergement au meilleur prix demande quelques astuces. Découvrez 7 conseils d'experts.",
        "details": "Comparateurs indépendants, navigation privée, flexibilité des dates : toutes les clés pour alléger la facture de votre prochain séjour."
    },
    {
        "titre": "Enquête exclusive : All-Inclusive vs. Petit-Déjeuner, les vacanciers ont tranché",
        "slug": "enquete-all-inclusive-vs-petit-dejeuner",
        "image": "images/enquete_exclusive.jpg",
        "resume": "Pourquoi le All-Inclusive triomphe-t-il auprès des familles ? Découvrez notre enquête.",
        "details": "Analyse de la disparition de la pension complète traditionnelle et décryptage des attentes des vacanciers entre liberté et maîtrise du budget."
    }
]

# Génération des cartes et pages d'articles individuelles
blog_cards_html = ""
for art in articles_blog:
    blog_cards_html += f"""
    <div class="blog-card">
        <img src="{art['image']}" alt="{art['titre']}" onerror="this.src='https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=600&q=80'">
        <div class="blog-content">
            <h3>{art['titre']}</h3>
            <p>{art['resume']}</p>
            <a href="{art['slug']}.html" class="btn-article">Lire l'article</a>
        </div>
    </div>
    """
    
    html_article_seul = f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><title>{art['titre']} | MyHotelCompare</title>
<style>
body {{ background-color: #0B132B; color: #FFFFFF; font-family: sans-serif; padding: 20px; margin: 0; }}
.container {{ max-width: 800px; margin: 0 auto; }}
.top-nav {{ display: flex; gap: 10px; background-color: #1C2541; padding: 15px; border-radius: 10px; margin-bottom: 25px; border: 1px solid #3A506B; overflow-x: auto; }}
.top-nav a {{ color: white; background-color: #3A506B; padding: 8px 16px; border-radius: 6px; text-decoration: none; }}
.article-box {{ background-color: #1C2541; border: 1px solid #3A506B; border-radius: 12px; padding: 30px; line-height: 1.7; }}
.article-box img {{ width: 100%; max-height: 400px; object-fit: cover; border-radius: 8px; margin-bottom: 20px; }}
</style></head>
<body>
<div class="container">
    {menu_html}
    <a href="blog.html" style="color: #38bdf8; display: inline-block; margin-bottom: 15px; text-decoration: none;">← Retour au blog</a>
    <div class="article-box">
        <h1>{art['titre']}</h1>
        <img src="{art['image']}" alt="{art['titre']}" onerror="this.src='https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=800&q=80'">
        <div style="font-size: 1.1em; color: #e2e8f0;">{art['details']}</div>
    </div>
</div>
</body>
</html>
"""
    with open(f"{output_dir}/{art['slug']}.html", "w", encoding="utf-8") as f:
        f.write(html_article_seul)

# Génération de la page principale blog.html
html_blog = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Notre Blog Voyage | MyHotelCompare</title>
    <style>
        body {{ background-color: #0B132B; color: #FFFFFF; font-family: sans-serif; margin: 0; padding: 20px; }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        .top-nav {{ display: flex; gap: 10px; background-color: #1C2541; padding: 15px; border-radius: 10px; margin-bottom: 25px; border: 1px solid #3A506B; overflow-x: auto; }}
        .top-nav a {{ color: white; background-color: #3A506B; padding: 8px 16px; border-radius: 6px; text-decoration: none; }}
        h1 {{ font-size: 2em; margin-bottom: 30px; }}
        .blog-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; }}
        .blog-card {{ background-color: #1C2541; border: 1px solid #3A506B; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; }}
        .blog-card img {{ width: 100%; height: 180px; object-fit: cover; }}
        .blog-content {{ padding: 20px; display: flex; flex-direction: column; flex-grow: 1; justify-content: space-between; }}
        .blog-content h3 {{ color: white; margin-top: 0; font-size: 1.15em; margin-bottom: 10px; }}
        .blog-content p {{ color: #94a3b8; font-size: 0.88em; margin-bottom: 20px; line-height: 1.4; }}
        .btn-article {{ display: inline-block; background-color: #3A506B; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 0.9em; font-weight: bold; text-align: center; }}
        .btn-article:hover {{ background-color: #38bdf8; color: #0B132B; }}
    </style>
</head>
<body>
    <div class="container">
        {menu_html}
        <h1>📖 Notre Blog Voyage</h1>
        <div class="blog-grid">
            {blog_cards_html}
        </div>
    </div>
</body>
</html>
"""
with open(f"{output_dir}/blog.html", "w", encoding="utf-8") as f:
    f.write(html_blog)

# 7. Pages annexes
for p in ["compagnies-aeriennes.html", "loueurs-vehicules.html", "croisieres.html"]:
    nom_propre = p.replace('.html', '').replace('-', ' ').capitalize()
    html_annexe = f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><title>{nom_propre} | MyHotelCompare</title>
<style>
body {{ background-color: #0B132B; color: #FFFFFF; font-family: sans-serif; margin: 0; padding: 20px; }}
.container {{ max-width: 1100px; margin: 0 auto; }}
.top-nav {{ display: flex; gap: 10px; background-color: #1C2541; padding: 15px; border-radius: 10px; margin-bottom: 25px; border: 1px solid #3A506B; overflow-x: auto; }}
.top-nav a {{ color: white; background-color: #3A506B; padding: 8px 16px; border-radius: 6px; text-decoration: none; }}
.content {{ background-color: #1C2541; border: 1px solid #3A506B; border-radius: 12px; padding: 30px; }}
</style></head>
<body><div class="container">{menu_html}
<div class="content"><h1>{nom_propre}</h1><p style="color:#94a3b8;">Comparatifs et sélections en cours de chargement...</p></div>
</div></body></html>"""
    with open(f"{output_dir}/{p}", "w", encoding="utf-8") as f:
        f.write(html_annexe)

print(f"Génération réussie ! Ouvrez le dossier '{output_dir}' pour voir votre site complet avec ses 11 articles et textes détaillés.")