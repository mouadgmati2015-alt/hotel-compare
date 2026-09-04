import json
import os
import re
import base64
import hashlib
import shutil
import sys
import subprocess
import time
import urllib.parse
from pathlib import Path

from data.airlines_data import AIRLINES_DATA

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "mon_site_final"
RESET_OUTPUT = "--reset" in sys.argv[1:]
WATCH_MODE = "--watch" in sys.argv[1:]
SITE_URL = os.environ.get("SITE_URL", "https://myhotelcompare.com").rstrip("/")


def escape_html(value):
    if value is None:
        return ""
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def generer_avis_hotel(nom_hotel, donnees):
    """Crée des avis de démonstration stables et différents pour chaque hôtel."""
    profils = [
        ("Camille", 5, "Voyage en couple"),
        ("Yanis", 4, "Voyage en famille"),
        ("Inès", 5, "Séjour détente"),
        ("Thomas", 4, "Voyageur régulier"),
        ("Léa", 5, "Escapade entre amis"),
        ("Mehdi", 4, "Voyage solo"),
        ("Clara", 5, "Séjour romantique"),
        ("Adam", 4, "Voyage professionnel"),
    ]
    textes = [
        "L'emplacement à {ville} est très pratique et l'équipe a été particulièrement accueillante.",
        "Une belle expérience à {nom}. La chambre était agréable et le séjour correspondait bien à nos attentes.",
        "Nous avons apprécié le calme, la propreté et le bon rapport qualité-prix de cet établissement.",
        "Le séjour était réussi, avec un personnel disponible et des prestations conformes à la présentation.",
        "Une adresse que je retiens pour {ville}, notamment pour son confort et son atmosphère agréable.",
        "Très bon séjour : les services essentiels sont au rendez-vous et l'accueil est chaleureux.",
        "Un choix adapté pour découvrir {ville} dans de bonnes conditions, avec une équipe attentive.",
        "L'hôtel offre une expérience conviviale et reposante. Nous reviendrons avec plaisir.",
    ]
    cle = int(hashlib.sha256(nom_hotel.encode("utf-8")).hexdigest(), 16)
    ville = str(donnees.get("ville") or "la destination")
    avis = []
    for index in range(3):
        profil = profils[(cle + index * 3) % len(profils)]
        texte = textes[(cle + index * 5) % len(textes)].format(nom=nom_hotel, ville=ville)
        avis.append({"nom": profil[0], "note": profil[1], "role": profil[2], "texte": texte})
    return avis


def generer_meta_description(nom_hotel, donnees, description):
    """Construit une meta description unique et pertinente (~155 caractères) pour chaque fiche hôtel."""
    ville = str(donnees.get("ville") or "").strip()
    pays = str(donnees.get("pays") or "").strip()
    etoiles = donnees.get("etoiles", "")
    prix = donnees.get("prix_moyen", "")
    lieu = ", ".join(part for part in [ville, pays] if part)
    base = f"{nom_hotel}"
    if lieu:
        base += f" à {lieu}"
    if etoiles and str(etoiles) != "N/C":
        base += f" ({etoiles}★)"
    extrait = re.sub(r"\s+", " ", str(description or "")).strip()
    meta = base
    if prix:
        meta += f" — à partir de {prix}."
    if extrait:
        meta += f" {extrait}"
    meta = meta.strip()
    if len(meta) > 155:
        meta = meta[:152].rsplit(" ", 1)[0] + "..."
    return meta


def generer_og_tags(titre, description, url, image=""):
    """Construit les balises Open Graph / Twitter Card réutilisables pour n'importe quelle page."""
    image_abs = image if str(image).startswith(("http://", "https://")) else (f"{SITE_URL}/{image}" if image else "")
    tags = f"""<meta property="og:type" content="website">
    <meta property="og:title" content="{escape_html(titre)}">
    <meta property="og:description" content="{escape_html(str(description))[:200]}">
    <meta property="og:url" content="{url}">
    <meta name="twitter:card" content="summary_large_image">"""
    if image_abs:
        tags += f'\n    <meta property="og:image" content="{image_abs}">'
    return tags


def generer_schema_hotel(nom_hotel, donnees, description, avis_clients, url_page):
    """Construit un objet JSON-LD schema.org Hotel (+ AggregateRating si des avis existent)."""
    ville = str(donnees.get("ville") or "").strip()
    pays = str(donnees.get("pays") or "").strip()
    schema = {
        "@context": "https://schema.org",
        "@type": "Hotel",
        "name": nom_hotel,
        "description": re.sub(r"\s+", " ", str(description or "")).strip()[:500],
        "url": url_page,
    }
    if donnees.get("image"):
        schema["image"] = donnees.get("image")
    if ville or pays:
        schema["address"] = {
            "@type": "PostalAddress",
            "addressLocality": ville or None,
            "addressCountry": pays or None,
        }
        schema["address"] = {k: v for k, v in schema["address"].items() if v}
    etoiles = donnees.get("etoiles")
    if etoiles and str(etoiles) not in ("N/C", ""):
        try:
            schema["starRating"] = {"@type": "Rating", "ratingValue": float(str(etoiles).split()[0])}
        except (ValueError, IndexError):
            pass
    if avis_clients:
        notes = [int(a.get("note", 5)) for a in avis_clients if a.get("note")]
        if notes:
            schema["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": round(sum(notes) / len(notes), 1),
                "reviewCount": len(notes),
                "bestRating": 5,
                "worstRating": 1,
            }
    return json.dumps(schema, ensure_ascii=False)


def write_html(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def generate_seo_files():
    html_pages = sorted(OUTPUT_DIR.glob("*.html"))
    urls = []
    for page in html_pages:
        if page.name.lower() == "404.html":
            continue
        suffix = "" if page.name.lower() == "index.html" else page.name
        urls.append(f"{SITE_URL}/{suffix}")

    sitemap_urls = "\n".join(
        f"    <url><loc>{escape_html(url)}</loc><changefreq>weekly</changefreq><priority>{'1.0' if url == SITE_URL + '/' else '0.7'}</priority></url>"
        for url in urls
    )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sitemap_urls}\n"
        "</urlset>\n"
    )
    write_html(OUTPUT_DIR / "sitemap.xml", sitemap)
    write_html(OUTPUT_DIR / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")


# --- FONCTIONS D'AFFILIATION AUTOMATIQUES ---
def update_booking_aid(url, nom_hotel="", ville="", pays="", new_aid="8012379"):
    if not url or url == "#" or url.strip() == "":
        query = f"{nom_hotel} {ville} {pays}".strip()
        encoded_query = urllib.parse.quote(query)
        return f"https://www.booking.com/searchresults.fr.html?ss={encoded_query}&aid={new_aid}"
    
    url = url.rstrip('?')
    clean_url = url.replace("??", "?")
    parsed = urllib.parse.urlparse(clean_url)
    query_params = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    query_params["aid"] = new_aid
    new_query = urllib.parse.urlencode(query_params)
    return urllib.parse.urlunparse(parsed._replace(query=new_query))

def update_expedia_link(url, nom_hotel="", ville="", pays=""):
    query = f"{nom_hotel} {ville} {pays}".strip()
    direct_search = "https://www.expedia.fr/Hotel-Search?destination=" + urllib.parse.quote(query)
    if not url or url == "#" or url.strip() == "":
        return direct_search
        
    url = url.rstrip('?')
    if "tkqlhce.com" in url or "anrdoezrs.net" in url:
        return url
    return url

# Render publie mon_site_final. --reset ne supprime que ce dossier de sortie.
output_dir = str(OUTPUT_DIR)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
images_source = BASE_DIR / "images"
if images_source.exists():
    shutil.copytree(images_source, OUTPUT_DIR / "images", dirs_exist_ok=True)


def nettoyer_slug(texte):
    texte = texte.lower().strip()
    texte = re.sub(r'[^a-z0-9]+', '-', texte)
    return texte.strip('-')

def get_img_as_base64(path):
    image_path = BASE_DIR / path
    if image_path.exists():
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def get_public_image(path):
    if not path:
        return ""
    if str(path).startswith(("http://", "https://", "data:")):
        return str(path)
    return str(path).replace("\\", "/") if (BASE_DIR / path).exists() else ""

# Éléments partagés (Logo, Menu, Témoignages, Footer)
logo_path = "images/logo_5.svg" # (ou "images/logo_5.png" si tu préfères garder du PNG)
logo_html = f'<img src="{logo_path}" alt="Nomad" class="brand-mark">'

menu_html = f"""
<header class="site-header">
<div class="brand-lockup">
    {logo_html}
    <div><strong>MyHotelCompare</strong><span>Nomad, le comparateur intelligent</span></div>
</div>
<div class="top-nav">
    <a href="index.html">Accueil / Hôtels</a>
    <a href="compagnies-aeriennes.html">Compagnies Aériennes</a>
    <a href="loueurs-vehicules.html">Location de Véhicules</a>
    <a href="croisieres.html">Croisières</a>
    <a href="blog.html">Blog</a>
    <a href="vos-desirs-sont-des-ordres.html">Vos désirs sont des ordres</a>
</div>
</header>
"""

global_style = """
<!-- Google Consent Mode v2 : refus par défaut tant que l'utilisateur n'a pas choisi -->
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('consent', 'default', {
    'ad_storage': 'denied',
    'ad_user_data': 'denied',
    'ad_personalization': 'denied',
    'analytics_storage': 'denied'
  });
</script>

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-RLVNV2211J"></script>
<script>
  gtag('js', new Date());
  gtag('config', 'G-RLVNV2211J');
</script>

<link rel="icon" type="image/png" href="images/logo_5.png?v=2">
<link rel="apple-touch-icon" href="images/logo_5.png?v=2">
<style>
:root {
    --bg: #f2fbfd;
    --bg-dark: #063247;
    --panel: #e5f5f8;
    --panel-strong: #c7eaf0;
    --card: #ffffff;
    --line: #b9dfe7;
    --text: #123443;
    --muted: #52717c;
    --primary: #087f9b;
    --primary-dark: #056078;
    --secondary: #075985;
    --success: #16805b;
    --success-soft: #d7f4e7;
    --warning: #e59a21;
    --shadow: 0 18px 38px rgba(5, 96, 120, 0.14);
}

* { box-sizing: border-box; }
body {
    margin: 0;
    background: linear-gradient(180deg, #f4fcfd 0%, #e7f6f8 100%);
    color: var(--text);
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    padding: 24px 16px 40px;
}
.container {
    max-width: 1180px;
    margin: 0 auto;
}
.site-header { margin-bottom: 24px; }
.brand-lockup { display: flex; align-items: center; justify-content: center; gap: 14px; margin-bottom: 18px; color: var(--text); }
.brand-mark { width: 58px; height: 58px; object-fit: contain; border-radius: 16px; background: var(--panel-strong); padding: 5px; }
.brand-lockup strong { display: block; color: var(--secondary); font-family: Georgia, "Times New Roman", serif; font-size: 2rem; line-height: 1; }
.brand-lockup span { display: block; color: var(--muted); margin-top: 5px; font-size: 0.88rem; }
h1, h2, h3, h4 { color: var(--text); }
h1, h2 { font-family: Georgia, "Times New Roman", serif; }
a { color: var(--secondary); }
.site-footer { margin-top: 48px; background: linear-gradient(135deg, #063247, #075985); color: #effcff; border-radius: 22px; padding: 30px; box-shadow: var(--shadow); }
.footer-grid { display: grid; grid-template-columns: 1.4fr 1fr 1fr 1.2fr; gap: 28px; }
.site-footer h3, .site-footer h4 { color: #b8f0f6; margin-top: 0; }
.site-footer p, .site-footer li { color: #d6eef2; line-height: 1.6; }
.site-footer a { color: #b8f0f6; text-decoration: none; }
.site-footer a:hover { text-decoration: underline; }
.footer-links { list-style: none; padding: 0; margin: 0; }
.footer-links li { margin-bottom: 8px; }
.footer-bottom { border-top: 1px solid rgba(255,255,255,0.18); margin-top: 24px; padding-top: 18px; display: flex; justify-content: space-between; gap: 15px; flex-wrap: wrap; font-size: 0.85rem; }
.footer-bottom p { margin: 0; }
@media (max-width: 800px) { .footer-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 520px) { .footer-grid { grid-template-columns: 1fr; } .brand-lockup { justify-content: flex-start; } }
.top-nav {
    display: flex; gap: 10px; flex-wrap: wrap;
    background: linear-gradient(135deg, var(--secondary), var(--primary-dark));
    padding: 14px 18px; border-radius: 18px; margin: 6px 0 22px;
    box-shadow: var(--shadow); justify-content: center;
}
.top-nav a {
    color: white; background: rgba(255,255,255,0.12);
    padding: 10px 16px; border-radius: 12px; text-decoration: none;
    font-weight: 700; border: 1px solid rgba(255,255,255,0.15);
}
.top-nav a:hover { background: rgba(255,255,255,0.2); }
.card {
    background: linear-gradient(180deg, #fffefb 0%, #fff8ef 100%);
    border: 1px solid var(--line); border-radius: 20px;
    padding: 24px; margin-bottom: 22px; box-shadow: var(--shadow);
}
.btn, .btn-booking, .btn-expedia {
    display: inline-block; text-decoration: none; border-radius: 12px;
    font-weight: 700; transition: transform 0.2s ease; cursor: pointer;
}
.btn:hover, .btn-booking:hover, .btn-expedia:hover { transform: translateY(-1px); }
.btn { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: white; padding: 12px 18px; }
.btn-booking { display: block; background: linear-gradient(135deg, #0f3d85, #1d5bbf); color: white; padding: 12px 16px; text-align: center; margin-bottom: 10px; }
.btn-expedia { display: block; background: linear-gradient(135deg, #ffca28, #f59e0b); color: #3f2a00; padding: 12px 16px; text-align: center; }

.hero-banner {
    background: linear-gradient(135deg, #0a7892 0%, #086b8d 45%, #064e72 100%);
    border-radius: 24px; padding: 28px; border: 1px solid rgba(5,78,114,0.22); color: #f2fdff; box-shadow: var(--shadow);
}
.hero-badges { display: flex; flex-wrap: wrap; gap: 10px; margin: 12px 0 18px; }
.hero-badges span {
    background: rgba(255,255,255,0.16); border: 1px solid rgba(255,255,255,0.24); color: #f2fdff; border-radius: 999px; padding: 7px 12px; font-weight: 700; font-size: 0.82rem;
}
.glass-box { background: rgba(255,255,255,0.72); border: 1px solid var(--line); border-radius: 18px; padding: 18px; }
.filters-box {
    background: linear-gradient(180deg, #e3f5f8 0%, #f8fdfe 100%);
    border: 1px solid var(--line); border-radius: 18px; padding: 20px; margin: 24px 0 18px;
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; box-shadow: var(--shadow);
}
.filters-box label { color: var(--muted); display: block; margin-bottom: 8px; font-weight: 700; }
.filters-box select {
    width: 100%; padding: 11px 12px; border-radius: 12px; border: 1px solid var(--line); background: #fff; color: var(--text); font-size: 0.97rem;
}
.btn-compare { width: 100%; border: none; background: linear-gradient(135deg, var(--success), #16a34a); color: white; padding: 14px 18px; border-radius: 14px; font-size: 1rem; font-weight: 800; cursor: pointer; box-shadow: var(--shadow); }
.comparison-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.smart-results-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }
.smart-results-grid .card { margin-bottom: 0; }
.rental-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.rental-grid .card { padding: 16px; margin-bottom: 0; }
.rental-grid h3 { font-size: 1.05rem; }
.rental-grid p { font-size: 0.86rem; line-height: 1.45; }
.review-card {
    background: linear-gradient(180deg, #fffaf6 0%, #fff1e0 100%);
    border: 1px solid var(--line); border-radius: 16px; padding: 18px; min-height: 170px;
}
.review-card .stars { color: var(--warning); font-size: 1.1rem; letter-spacing: 2px; }
.stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px,1fr)); gap: 16px; margin-top: 18px; }
.stat-item { background: rgba(255,255,255,0.5); border: 1px solid rgba(130,90,20,0.15); border-radius: 16px; padding: 18px; }
.stat-item strong { display: block; font-size: 1.5rem; }
.testimonial-section > h2 { color: var(--text) !important; }
.testimonial-section > div > div { background: linear-gradient(180deg, #fffaf6 0%, #fff1e0 100%) !important; border-color: var(--line) !important; }
.testimonial-section > div > div p { color: var(--muted) !important; }
.testimonial-section > div > div p:first-child { color: var(--warning) !important; }
.testimonial-section > div > div p strong { color: var(--text) !important; }
@media (max-width: 900px) { .rental-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 1000px) { .smart-results-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 768px) { .comparison-grid { grid-template-columns: 1fr; } .smart-results-grid { grid-template-columns: 1fr; } .rental-grid { grid-template-columns: 1fr; } .top-grid { grid-template-columns: 1fr !important; } }
.cookie-banner {
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 9999;
    background: #063247; color: #effcff; padding: 18px 20px;
    display: flex; flex-wrap: wrap; align-items: center; justify-content: center;
    gap: 16px; box-shadow: 0 -8px 24px rgba(0,0,0,0.25);
}
.cookie-banner p { margin: 0; max-width: 640px; font-size: 0.92rem; line-height: 1.5; }
.cookie-banner a { color: #b8f0f6; }
.cookie-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.cookie-actions button {
    border: none; border-radius: 10px; padding: 10px 18px; font-weight: 700; cursor: pointer;
}
.cookie-accept { background: var(--primary); color: white; }
.cookie-refuse { background: rgba(255,255,255,0.15); color: white; }
</style>
"""

cookie_banner_html = """
<div id="cookie-banner" class="cookie-banner" style="display:none;">
    <p>Nous utilisons des cookies pour mesurer l'audience du site (Google Analytics). Vous pouvez accepter ou refuser ce suivi. Voir notre <a href="confidentialite.html">politique de confidentialité</a>.</p>
    <div class="cookie-actions">
        <button class="cookie-refuse" onclick="setCookieConsent(false)">Refuser</button>
        <button class="cookie-accept" onclick="setCookieConsent(true)">Accepter</button>
    </div>
</div>
<script>
(function() {
    function setCookieConsent(accepted) {
        localStorage.setItem('cookie_consent', accepted ? 'granted' : 'denied');
        gtag('consent', 'update', {
            'analytics_storage': accepted ? 'granted' : 'denied'
        });
        document.getElementById('cookie-banner').style.display = 'none';
    }
    window.setCookieConsent = setCookieConsent;

    document.addEventListener('DOMContentLoaded', function() {
        var saved = localStorage.getItem('cookie_consent');
        if (saved === 'granted') {
            gtag('consent', 'update', { 'analytics_storage': 'granted' });
        } else if (saved === null) {
            document.getElementById('cookie-banner').style.display = 'flex';
        }
    });
})();
</script>
"""

temoignages_html = """
<section class="testimonial-section" id="avis" style="margin: 50px 0;">
    <h2 style="text-align: center; color: #FFFFFF; margin-bottom: 30px;">💬 Ce que pensent nos voyageurs</h2>
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px;">
        <div style="background-color: #1C2541 !important; border: 1px solid #3A506B; border-radius: 12px; padding: 20px; box-sizing: border-box;">
            <p style="color: #f59e0b; font-size: 1.1em; margin-bottom: 5px; margin-top: 0;">⭐⭐⭐⭐⭐</p>
            <p style="font-style: italic; font-size: 0.95em; color: #E2E8F0;">"Grâce au comparateur, j'ai trouvé l'hôtel idéal pour mes vacances en un clin d'œil !"</p>
            <div style="display: flex; align-items: center; margin-top: 15px;">
                <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop&crop=faces" alt="Photo de profil de Marc D." style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover; margin-right: 10px;">
                <div><p style="font-weight: bold; font-size: 0.85em; margin: 0; color: white;">Marc D.</p><p style="font-size: 0.75em; color: #94a3b8; margin: 0;">Voyageur solo</p></div>
            </div>
        </div>
        <div style="background-color: #1C2541 !important; border: 1px solid #3A506B; border-radius: 12px; padding: 20px; box-sizing: border-box;">
            <p style="color: #f59e0b; font-size: 1.1em; margin-bottom: 5px; margin-top: 0;">⭐⭐⭐⭐⭐</p>
            <p style="font-style: italic; font-size: 0.95em; color: #E2E8F0;">"Super application, très pratique pour comparer les hôtels rapidement. Je recommande !"</p>
            <div style="display: flex; align-items: center; margin-top: 15px;">
                <img src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=faces" alt="Photo de profil de Sarah L." style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover; margin-right: 10px;">
                <div><p style="font-weight: bold; font-size: 0.85em; margin: 0; color: white;">Sarah L.</p><p style="font-size: 0.75em; color: #94a3b8; margin: 0;">Voyage en famille</p></div>
            </div>
        </div>
        <div style="background-color: #1C2541 !important; border: 1px solid #3A506B; border-radius: 12px; padding: 20px; box-sizing: border-box;">
            <p style="color: #f59e0b; font-size: 1.1em; margin-bottom: 5px; margin-top: 0;">⭐⭐⭐⭐⭐</p>
            <p style="font-style: italic; font-size: 0.95em; color: #E2E8F0;">"Le comparateur m'a permis d'économiser pas mal sur mon séjour. Interface fluide et propre."</p>
            <div style="display: flex; align-items: center; margin-top: 15px;">
                <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=faces" alt="Photo de profil de Karim B." style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover; margin-right: 10px;">
                <div><p style="font-weight: bold; font-size: 0.85em; margin: 0; color: white;">Karim B.</p><p style="font-size: 0.75em; color: #94a3b8; margin: 0;">Voyageur régulier</p></div>
            </div>
        </div>
    </div>
    <hr style="border-color: #3A506B; margin: 30px 0;">
    <p style="text-align: center; color: #000000; font-size: 15px; font-weight: bold; margin-bottom: 10px;">APPROUVÉ PAR LES VOYAGEURS QUI RÉSERVENT SUR</p>
    <div style="text-align: center; margin-bottom: 15px; display: flex; justify-content: center; align-items: center; gap: 30px;">
        <span style="background-color: #003580; color: white; width: 190px; min-height: 54px; padding: 8px 20px; border-radius: 6px; font-weight: 900; font-size: 18px; display: inline-flex; align-items: center; justify-content: center;">Booking.com</span>
        <a href="https://www.expedia.fr/" target="_blank" rel="nofollow sponsored" style="background-color: #ffca28; color: #111827; width: 190px; min-height: 54px; padding: 8px 20px; border-radius: 6px; font-weight: 900; font-size: 18px; display: inline-flex; align-items: center; justify-content: center; text-decoration: none;">Expedia</a>
    </div>
    <p style="text-align: center; color: #888; font-size: 11px;">Comparaison de plus de 1000 hôtels &nbsp;&bull;&nbsp; 10 destinations incontournables &nbsp;&bull;&nbsp; 2 sites de réservation vérifiés</p>
</section>
"""

footer_html = """
""" + cookie_banner_html + """
<footer class="site-footer">
    <div class="footer-grid">
        <div>
            <h3>Nomad</h3>
            <p>Le compagnon de voyage qui vous aide à choisir plus vite et à partir plus serein.</p>
        </div>
        <div>
            <h4>Explorer</h4>
            <ul class="footer-links">
                <li><a href="index.html">Hôtels</a></li>
                <li><a href="vos-desirs-sont-des-ordres.html">Recherche intelligente</a></li>
                <li><a href="compagnies-aeriennes.html">Compagnies aériennes</a></li>
                <li><a href="loueurs-vehicules.html">Location de véhicules</a></li>
                <li><a href="croisieres.html">Croisières</a></li>
            </ul>
        </div>
        <div>
            <h4>À propos</h4>
            <ul class="footer-links">
                <li><a href="apropos.html">À propos de nous</a></li>
                <li><a href="confidentialite.html">Politique de confidentialité</a></li>
                <li><a href="contact.html">Contact</a></li>
                <li><a href="blog.html">Conseils de voyage</a></li>
                <li><a href="index.html#avis">Avis voyageurs</a></li>
            </ul>
        </div>
        <div>
            <h4>Votre retour compte</h4>
            <p>Une remarque ou une idée ? Contactez-nous directement sur Facebook.</p>
            <a class="btn" href="https://www.facebook.com/profile.php?id=61591545557027" target="_blank" rel="noopener">Nous contacter sur Facebook</a>
        </div>
    </div>
    <div class="footer-bottom">
        <p>©2026 Myhotelcompare . Tous droits réservés.</p>
        <p><a href="index.html">Accueil</a> · <a href="blog.html">Blog</a> · Propulsé par l'IA</p>
    </div>
</footer>
"""


def generate_information_pages():
    pages = {
        "apropos.html": ("À propos de MyHotelCompare", """
            <p>MyHotelCompare, propulsé par Nomad, vous aide à comparer les hébergements et les services de voyage plus simplement.</p>
            <h2>Notre mission</h2>
            <p>Nous rassemblons les informations essentielles pour vous permettre de choisir un séjour adapté à vos envies et à votre budget.</p>
            <h2>Notre approche</h2>
            <p>Notre comparateur met en avant les prix, les équipements, les avis et les points forts des établissements dans une interface claire.</p>
        """),
        "confidentialite.html": ("Politique de confidentialité", """
            <p><strong>Dernière mise à jour : août 2026</strong></p>
            <h2>Informations collectées</h2>
            <p>Nous pouvons traiter les informations que vous transmettez via nos formulaires ainsi que des données techniques nécessaires au fonctionnement du site.</p>
            <h2>Utilisation</h2>
            <p>Ces informations servent à répondre à vos demandes, améliorer le site et assurer son bon fonctionnement. Nous ne vendons pas vos données personnelles.</p>
            <h2>Vos droits</h2>
            <p>Vous pouvez demander l'accès, la rectification ou la suppression de vos informations en nous contactant.</p>
        """),
        "contact.html": ("Contactez-nous", """
            <p>Une question, une remarque ou une suggestion ? Notre équipe vous répondra avec plaisir.</p>
            <p><a class="btn" href="https://www.facebook.com/profile.php?id=61591545557027" target="_blank" rel="noopener">Nous contacter sur Facebook</a></p>
            <p>Notre équipe vous répond directement sur Facebook dans les meilleurs délais.</p>
        """),
    }
    for filename, (title, body) in pages.items():
        page = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title} | MyHotelCompare</title>{global_style}</head>
<body><div class="container">{menu_html}<main class="card"><h1>{title}</h1>{body}</main>{footer_html}</div></body></html>"""
        write_html(OUTPUT_DIR / filename, page)

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
                                    'equipements': d.get('equipements') or [],
                                    'lien_booking': update_booking_aid(d.get('lien_booking', '#'), nom, d.get('ville', ''), d.get('pays', '')),
                                    'lien_expedia': update_expedia_link(d.get('lien_expedia', '#'), nom, d.get('ville', ''), d.get('pays', ''))
                                })
                except Exception as e:
                    print(f"Erreur sur {filename}: {e}")

with open(os.path.join(output_dir, "hotels.json"), "w", encoding="utf-8") as f:
    json.dump(all_hotels, f, ensure_ascii=False, indent=4)

# 2. Recherche intelligente en langage naturel
recherche_intelligente_page = f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vos désirs sont des ordres | MyHotelCompare</title>{global_style}</head>
<body><div class="container">{menu_html}
<main class="card" style="background: linear-gradient(135deg, #075985 0%, #087f9b 100%); color: white;">
    <p style="margin:0 0 8px; font-weight:700; color:#b8f0f6;">NOMAD SMART SEARCH</p>
    <h1 style="color:white; margin:0 0 12px;">Vos désirs sont des ordres</h1>
    <p style="color:#effcff; max-width:760px; line-height:1.7;">Décrivez votre séjour comme vous le feriez à un conseiller. Nomad repère la destination, le budget et les équipements recherchés.</p>
    <form id="smart-search" style="display:flex; gap:12px; flex-wrap:wrap; margin-top:22px;">
        <input id="smart-query" type="search" required value="Je recherche un hôtel à Djerba en Tunisie à moins de 900 euros la semaine avec un parc aquatique" placeholder="Exemple : un hôtel à Djerba à moins de 900 euros avec un parc aquatique" style="flex:1 1 520px; min-width:220px; padding:15px 16px; border:0; border-radius:12px; color:#123443; font-size:1rem;">
        <button class="btn-compare" type="submit" style="width:auto; padding:14px 22px; background:#e59a21;">Rechercher</button>
    </form>
    <p style="font-size:.86rem; color:#d6eef2; margin:12px 0 0;">Essayez avec une ville, un pays, un budget ou un équipement : plage, piscine, spa, parc aquatique, tout compris...</p>
</main>
<section id="smart-results" aria-live="polite"></section>
{footer_html}
</div>
<script>
const hotels = {json.dumps(all_hotels, ensure_ascii=False)};
const stopWords = new Set(['je','recherche','cherche','un','une','des','de','du','la','le','les','a','à','en','au','aux','avec','pour','dans','sur','mon','ma','mes','hotel','hôtel','semaine','euros','euro','prix','moins','que','qui','et']);
const aliases = {{
    'parc aquatique': ['parc aquatique','aqua parc','aquapark','aquatique'],
    'tout compris': ['tout compris','all inclusive'],
    'piscine': ['piscine'], 'plage': ['plage','bord de mer'], 'spa': ['spa','thalasso'],
    'famille': ['famille','familial'], 'adulte': ['adulte','adult only']
}};

function normalize(value) {{
    return String(value || '').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '');
}}
function numberFrom(value) {{
    const match = normalize(value).replace(',', '.').match(/\\d+(?:\\.\\d+)?/);
    return match ? Number(match[0]) : null;
}}
function searchable(hotel) {{
    return normalize([hotel.nom, hotel.ville, hotel.pays, hotel.prix, hotel.description, hotel.image].concat(hotel.equipements || []).join(' '));
}}
function escapeText(value) {{
    return String(value || '').replace(/[&<>"']/g, char => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}}[char]));
}}
const knownCities = [...new Set(hotels.map(h => normalize(h.ville)).filter(Boolean))].sort((a, b) => b.length - a.length);
const knownCountries = [...new Set(hotels.map(h => normalize(h.pays)).filter(Boolean))].sort((a, b) => b.length - a.length);
const knownEquipment = [...new Set(hotels.flatMap(h => h.equipements || []).map(item => normalize(item)).filter(item => item.length > 2))].sort((a, b) => b.length - a.length);
function findLocation(query, locations) {{
    return locations.find(location => query.includes(location)) || '';
}}
function renderHotel(hotel) {{
    const image = hotel.image ? `<img src="${{escapeText(hotel.image)}}" alt="${{escapeText(hotel.nom)}}" style="width:100%; height:190px; object-fit:cover; border-radius:14px; margin-bottom:14px;">` : '';
    const bookingButton = hotel.lien_booking ? `<a class="btn-booking" href="${{escapeText(hotel.lien_booking)}}" target="_blank" rel="noopener sponsored">Réserver sur Booking</a>` : '';
    const expediaButton = hotel.lien_expedia ? `<a class="btn-expedia" href="${{escapeText(hotel.lien_expedia)}}" target="_self" rel="sponsored">Réserver sur Expedia</a>` : '';
    return `<article class="card">${{image}}<h2 style="margin-top:0;">${{escapeText(hotel.nom)}}</h2><p style="color:var(--muted);">📍 ${{escapeText(hotel.ville)}}, ${{escapeText(hotel.pays)}} · ⭐ ${{escapeText(hotel.etoiles)}}</p><p style="color:var(--success); font-weight:700;">💰 ${{escapeText(hotel.prix)}}</p><a class="btn" href="${{encodeURI(hotel.slug)}}.html">Voir la fiche de l'hôtel</a>${{bookingButton}}${{expediaButton}}</article>`;
}}
function searchHotels(query) {{
    const normalized = normalize(query);
    const requestedCity = findLocation(normalized, knownCities);
    const requestedCountry = findLocation(normalized, knownCountries);
    const budgetMatch = normalized.match(/(?:moins de|a moins de|inferieur a|maximum|max|budget de)\\s*(\\d+)/);
    const budget = budgetMatch ? Number(budgetMatch[1]) : null;
    const requestedFeatures = Object.entries(aliases).filter(([, words]) => words.some(word => normalized.includes(normalize(word))));
    const requestedEquipment = knownEquipment.filter(equipment => normalized.includes(equipment));
    const rawTerms = normalized.replace(/[^a-z0-9à-ÿ ]/g, ' ').split(/\\s+/).filter(term => term.length > 2 && !stopWords.has(term) && !/^\\d+$/.test(term));
    const requestedTerms = rawTerms.filter(term => term !== requestedCity && term !== requestedCountry);
    return hotels.map(hotel => {{
        const text = searchable(hotel);
        const price = numberFrom(hotel.prix);
        const matchedTerms = requestedTerms.filter(term => text.includes(term));
        let score = matchedTerms.length;
        const matchedFeatures = requestedFeatures.filter(([, words]) => words.some(word => text.includes(normalize(word))));
        const matchedEquipment = requestedEquipment.filter(equipment => text.includes(equipment));
        score += (matchedFeatures.length + matchedEquipment.length) * 4;
        const budgetOk = budget === null || price === null || price <= budget;
        const cityOk = !requestedCity || normalize(hotel.ville) === requestedCity;
        const countryOk = !requestedCountry || normalize(hotel.pays) === requestedCountry;
        const locationOk = cityOk && countryOk;
        const equipmentOk = requestedEquipment.every(equipment => matchedEquipment.includes(equipment));
        const featuresOk = requestedFeatures.every(([, words]) => words.some(word => text.includes(normalize(word))));
        const termsOk = requestedTerms.every(term => matchedTerms.includes(term));
        return {{ hotel, score, budgetOk, locationOk, equipmentOk, featuresOk, termsOk, matchedFeatures: matchedFeatures.length, matchedEquipment: matchedEquipment.length, price }};
    }}).filter(result => result.budgetOk && result.locationOk && result.equipmentOk && result.featuresOk && result.termsOk && (requestedTerms.length === 0 || result.score > 0)).sort((a, b) => b.score - a.score);
}}
document.getElementById('smart-search').addEventListener('submit', event => {{
    event.preventDefault();
    const query = document.getElementById('smart-query').value;
    const results = searchHotels(query);
    const container = document.getElementById('smart-results');
    container.innerHTML = `<div class="glass-box" style="margin-bottom:20px;"><h2 style="margin-top:0;">${{results.length}} résultat(s) trouvé(s)</h2><p style="margin-bottom:0; color:var(--muted);">Les hôtels sont classés selon les critères détectés dans votre phrase.</p></div>` + (results.length ? results.map(result => renderHotel(result.hotel)).join('') : '<div class="card"><h2>Aucun résultat exact</h2><p>Essayez une destination plus large ou retirez un critère très précis.</p></div>');
}});
document.getElementById('smart-search').dispatchEvent(new Event('submit'));
</script></body></html>"""
write_html(OUTPUT_DIR / "vos-desirs-sont-des-ordres.html", recherche_intelligente_page)

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
                lien_promo = update_booking_aid(promo.get("lien", ""), titre_promo, ville_promo, pays_promo)
                promo_html = f"""
                <div style="background-color: #1C2541; border: 1px solid #3A506B; border-radius: 12px; padding: 20px; height: 100%; box-sizing: border-box;">
                    {f'<img src="{img_promo}" alt="{escape_html(titre_promo)}" style="width: 100%; height: 160px; object-fit: cover; border-radius: 6px; margin-bottom: 8px;">' if img_promo else ''}
                    <h3 style="margin-top: 0; color: white;">{titre_promo}</h3>
                    {f"<p style='color: #94a3b8; font-size: 0.85em; margin-top: -8px; margin-bottom: 6px;'>📍 {ville_promo}{', ' if ville_promo and pays_promo else ''}{pays_promo}</p>" if (ville_promo or pays_promo) else ''}
                    <p style="color: white; font-size: 0.95em;">{desc_promo}</p>
                    {f'<a href="{lien_promo}" target="_blank" class="btn-booking" style="margin-top: 15px;">J\'en profite</a>' if lien_promo else ''}
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
    {f'<img class="hotel-slide-item" src="data:image/png;base64,{imgs_base64[0]}" alt="Découverte d\'hôtels et de destinations" style="animation-delay: 0s;">' if imgs_base64[0] else ''}
    {f'<img class="hotel-slide-item" src="data:image/jpeg;base64,{imgs_base64[1]}" alt="Destination Afrique" style="animation-delay: 3s;">' if imgs_base64[1] else ''}
    {f'<img class="hotel-slide-item" src="data:image/jpeg;base64,{imgs_base64[2]}" alt="Astuce voyage" style="animation-delay: 6s;">' if imgs_base64[2] else ''}
    {f'<img class="hotel-slide-item" src="data:image/jpeg;base64,{imgs_base64[3]}" alt="Hôtel de voyage" style="animation-delay: 9s;">' if imgs_base64[3] else ''}
    {f'<img class="hotel-slide-item" src="data:image/jpeg;base64,{imgs_base64[4]}" alt="Destination Tunisie" style="animation-delay: 12s;">' if imgs_base64[4] else ''}
</div>
"""

html_accueil = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MyHotelCompare - Comparateur d'hôtels</title>
    {global_style}
</head>
<body>
    <div class="container">
        {menu_html}
        <div class="hero-banner">
            <div class="hero-badges">
                <span>✨ 1 200+ hôtels comparés</span>
                <span>📍 Destinations partout dans le monde</span>
                <span>🧠 Analyse des avis</span>
            </div>
            <h2 style="margin:0 0 10px; font-size: clamp(2rem, 4vw, 3rem);">Trouvez le bon hôtel, au bon prix, sans perdre une heure.</h2>
            <p style="margin:0; max-width: 700px; font-size: 1.05rem; line-height: 1.7; color: rgba(45,28,16,0.9);">Comparez les meilleurs séjours, découvrez les meilleurs rapports qualité-prix et réservez en quelques clics.</p>
        </div>

        <div class="top-grid" style="display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 24px; margin: 26px 0 10px;">
            <div>{carousel_html}</div>
            <div>{promo_html if promo_html else '<div class="card" style="height: 100%;"><h3>Offre spéciale</h3><p>Découvrez les meilleures promos du moment.</p></div>'}</div>
        </div>

        <div class="glass-box">
            <h2 style="margin-top: 0;">💡 Comment comparer vos hôtels</h2>
            <p style="margin: 0; line-height: 1.7;">1. Choisissez un pays pour chaque séjour. 2. Affinez éventuellement avec une ville. 3. Sélectionnez un hôtel de chaque côté, puis comparez.</p>
        </div>

        <div class="filters-box comparison-grid">
            <div class="glass-box">
                <h3 style="margin-top:0;">Premier séjour</h3>
                <div><label>Pays</label><select id="selectPays1" onchange="updateVilles(1)" required><option value="">Choisissez un pays *</option></select></div>
                <div><label>Ville (facultatif)</label><select id="selectVille1" onchange="updateHotels(1)"><option value="">Toutes les villes du pays</option></select></div>
                <div><label>Hôtel</label><select id="selectHotel1"><option value="">Choisissez un hôtel...</option></select></div>
            </div>
            <div class="glass-box">
                <h3 style="margin-top:0;">Deuxième séjour</h3>
                <div><label>Pays (facultatif)</label><select id="selectPays2" onchange="updateVilles(2)"><option value="">Choisissez un pays...</option></select></div>
                <div><label>Ville (facultatif)</label><select id="selectVille2" onchange="updateHotels(2)"><option value="">Toutes les villes du pays</option></select></div>
                <div><label>Hôtel</label><select id="selectHotel2"><option value="">Choisissez un hôtel...</option></select></div>
            </div>
        </div>
        <button class="btn-compare" onclick="lancerComparaison()">🚀 Lancer la comparaison</button>
        <div id="resultatComparaison" class="comparison-grid" style="margin-top: 30px;"></div>

        <div class="stat-grid">
            <div class="stat-item"><strong>4.8/5</strong><span>Moyenne satisfaction</span></div>
            <div class="stat-item"><strong>+90%</strong><span>Clients satisfaits</span></div>
            <div class="stat-item"><strong>24h</strong><span>Réponse rapide</span></div>
            <div class="stat-item"><strong>1000+</strong><span>Hôtels analysés</span></div>
        </div>

        {temoignages_html}
        {footer_html}
    </div>

    <script>
        const initialHotels = {json.dumps(all_hotels, ensure_ascii=False)};
        let hotelsData = Array.isArray(initialHotels) ? initialHotels : [];

        function initFiltres() {{
            const paysSet = [...new Set(hotelsData.map(h => h.pays).filter(Boolean))].sort();
            [1, 2].forEach(side => {{
                const selectPays = document.getElementById('selectPays' + side);
                paysSet.forEach(p => {{
                    let opt = document.createElement('option');
                    opt.value = p; opt.textContent = p;
                    selectPays.appendChild(opt);
                }});
                updateVilles(side);
            }});
        }}

        function updateVilles(side) {{
            const pays = document.getElementById('selectPays' + side).value;
            const selectVille = document.getElementById('selectVille' + side);
            selectVille.innerHTML = '<option value="">Toutes les villes</option>';
            const villesSet = [...new Set(hotelsData.filter(h => pays && h.pays === pays).map(h => h.ville).filter(Boolean))].sort();
            villesSet.forEach(v => {{
                let opt = document.createElement('option');
                opt.value = v; opt.textContent = v;
                selectVille.appendChild(opt);
            }});
            document.getElementById('selectHotel' + side).innerHTML = '<option value="">Choisissez un hôtel...</option>';
            updateHotels(side);
        }}

        function updateHotels(side) {{
            const pays = document.getElementById('selectPays' + side).value;
            const ville = document.getElementById('selectVille' + side).value;
            const filtered = hotelsData.filter(h => pays && h.pays === pays && (!ville || h.ville === ville));
            const selectHotel = document.getElementById('selectHotel' + side);
            selectHotel.innerHTML = '<option value="">Choisissez un hôtel...</option>';
            filtered.forEach(h => {{
                selectHotel.appendChild(new Option(h.nom, h.slug));
            }});
        }}

        function lancerComparaison() {{
            const pays1 = document.getElementById('selectPays1').value;
            const pays2 = document.getElementById('selectPays2').value;
            if (!pays1 && !pays2) {{
                document.getElementById('resultatComparaison').innerHTML = '<p style="color:#b42318; grid-column:span 2; text-align:center;">Choisissez au moins un pays pour lancer la comparaison.</p>';
                return;
            }}
            const h1 = hotelsData.find(h => h.slug === document.getElementById('selectHotel1').value);
            const h2 = hotelsData.find(h => h.slug === document.getElementById('selectHotel2').value);
            let html = '';
            if (h1) html += renderCard(h1);
            if (h2) html += renderCard(h2);
            document.getElementById('resultatComparaison').innerHTML = html || '<p style="color:#6e4d39; grid-column:span 2; text-align:center;">Veuillez sélectionner au moins un hôtel.</p>';
        }}

        function renderCard(h) {{
            const mapQuery = encodeURIComponent(h.nom + ', ' + h.ville + ', ' + h.pays);
            return `<div class="card">
                ${{h.image ? '<img src="' + h.image + '" alt="' + escapeText(h.nom) + '" style="width:100%; height:180px; object-fit:cover; border-radius:14px; margin-bottom:12px;">' : ''}}
                <h3><a href="${{h.slug}}.html" style="color:var(--secondary); text-decoration:none;">${{h.nom}}</a></h3>
                <p style="color:#6e4d39;">📍 ${{h.ville}}, ${{h.pays}} | ⭐ ${{h.etoiles}}</p>
                <p style="color:#15803d; font-weight:700;">💰 ${{h.prix}}</p>
                <a href="${{h.slug}}.html" style="display:block; background:var(--panel-strong); color:var(--text); padding:10px; text-align:center; text-decoration:none; border-radius:10px; margin-bottom:10px; font-weight:700;">📄 Voir la fiche détaillée</a>
                <a href="${{h.lien_booking}}" target="_blank" class="btn-booking">Réserver sur Booking</a>
                <a href="${{h.lien_expedia}}" target="_self" class="btn-expedia">Réserver sur Expedia</a>
                <iframe width="100%" height="150" style="border:0; border-radius:12px; margin-top:12px;" src="https://maps.google.com/maps?q=${{mapQuery}}&output=embed"></iframe>
            </div>`;
        }}

        function escapeText(value) {{
            return String(value || '').replace(/[&<>"']/g, char => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}}[char]));
        }}

        initFiltres();
    </script>
</body>
</html>
"""
write_html(OUTPUT_DIR / "index.html", html_accueil)

# Copie de secours pour index.html sous hotels.html au cas où
write_html(OUTPUT_DIR / "hotels.html", html_accueil)

# 4. Fiches individuelles des hôtels
for h_nom, d in HOTELS_DATA_COMPLET.items():
    slug = nettoyer_slug(h_nom)
    if not slug: continue
    
    l_booking = update_booking_aid(d.get('lien_booking', '#'), h_nom, d.get('ville', ''), d.get('pays', ''))
    l_expedia = update_expedia_link(d.get('lien_expedia', '#'), h_nom, d.get('ville', ''), d.get('pays', ''))
    equipements = d.get('equipements') or []
    points_positifs = d.get('points_positifs') or []
    points_negatifs = d.get('points_negatifs') or []
    pour_qui = d.get('pour_qui') or {}
    avis_clients = d.get('avis_clients') or generer_avis_hotel(h_nom, d)
    nomad_insight = d.get('Nomad, vous en dit plus') or d.get('nomad_vous_en_dit_plus') or ""

    reviews_html = "".join(
        f"""
        <div class="review-card">
            <div class="stars">{'★' * int(a.get('note', 5))}{'☆' * (5 - int(a.get('note', 5)))}</div>
            <p style="font-weight:700; margin: 12px 0 8px;">{escape_html(a.get('nom', 'Client'))}</p>
            <p style="font-size:0.82rem; color:var(--muted); margin:0 0 8px;">{escape_html(a.get('role', 'Voyageur'))}</p>
            <p style="margin:0; line-height:1.6; color: var(--text);">{escape_html(a.get('texte', ''))}</p>
        </div>
        """ for a in avis_clients
    )

    equipements_html = f"<h3>🛠️ Équipements</h3><p>{escape_html(', '.join(map(str, equipements)))}</p>" if equipements else ""
    points_html = f"<h3>✅ Points Positifs</h3><ul>{''.join(f'<li>{escape_html(p)}</li>' for p in points_positifs)}</ul>" if points_positifs else ""
    points_negatifs_html = f"<h3>⚠️ Points négatifs</h3><ul>{''.join(f'<li>{escape_html(p)}</li>' for p in points_negatifs)}</ul>" if points_negatifs else ""
    pour_qui_html = ""
    if isinstance(pour_qui, dict):
        public = pour_qui.get('public') or pour_qui.get('pour_qui') or ""
        verdict = pour_qui.get('verdict') or ""
        details = " · ".join(str(pour_qui.get(key)) for key in ('ambiance', 'style') if pour_qui.get(key))
        pour_qui_html = f"""
        <div class="glass-box" style="margin-top: 22px;">
            <h3 style="margin-top:0;">🎯 Pour qui ?</h3>
            <p>{escape_html(public)}</p>
            {f'<p style="color:var(--muted);">{escape_html(details)}</p>' if details else ''}
            {f'<h3>🧭 Verdict Nomad</h3><p style="margin-bottom:0; line-height:1.7;">{escape_html(verdict)}</p>' if verdict else ''}
        </div>
        """
    description = escape_html(d.get('description_ia') or d.get('description', ''))
    description_brute = d.get('description_ia') or d.get('description', '')
    meta_description = escape_html(generer_meta_description(h_nom, d, description_brute))
    url_page = f"{SITE_URL}/{slug}.html"
    schema_json = generer_schema_hotel(h_nom, d, description_brute, avis_clients, url_page)
    hotel_og_tags = generer_og_tags(h_nom, meta_description, url_page, d.get('image', ''))
    # Texte alternatif de l'image principale : utilise "image_alt" du JSON si présent, sinon retombe sur le nom de l'hôtel
    image_alt_hotel = escape_html(d.get('image_alt') or h_nom)

    html_fiche = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_html(h_nom)} - {escape_html(d.get('ville',''))} | MyHotelCompare</title>
    <meta name="description" content="{meta_description}">
    <link rel="canonical" href="{url_page}">
    {hotel_og_tags}
    <script type="application/ld+json">{schema_json}</script>
    {global_style}
</head>
<body>
<div class="container">{menu_html}
<a href="index.html" style="color: var(--secondary); display: inline-block; margin-bottom: 15px; text-decoration: none; font-weight:700;">← Retour à l'accueil</a>
<div class="card">
    <h1>{escape_html(h_nom)}</h1>
    <p style="color: #6e4d39;">📍 {escape_html(d.get('ville',''))}, {escape_html(d.get('pays',''))} | ⭐ {escape_html(d.get('etoiles','N/C'))}</p>
    {f'<img src="{d.get("image")}" alt="{image_alt_hotel}" style="width:100%; max-height:350px; object-fit:cover; border-radius:16px; margin:15px 0;">' if d.get('image') else ''}
    <p style="color:#15803d; font-weight:700; font-size: 1.2em;">💰 {escape_html(d.get('prix_moyen', 'Sur demande'))}</p>

    <h3>✨ Description</h3>
    <p>{description}</p>
    {f'<div class="glass-box" style="margin-top: 22px; border-left: 5px solid var(--primary);"><h3 style="margin-top:0;">🧭 Nomad vous en dit plus</h3><p style="margin-bottom:0; line-height:1.7;">{escape_html(nomad_insight)}</p></div>' if nomad_insight else ''}
    {equipements_html}
    {points_html}
    {points_negatifs_html}
    {pour_qui_html}

    <div style="margin-top: 30px;">
        <a href="{l_booking}" target="_blank" class="btn-booking">Réserver sur Booking</a>
        <a href="{l_expedia}" target="_self" class="btn-expedia">Réserver sur Expedia</a>
    </div>
</div>

<div class="card">
    <h2 style="margin-top:0;">💬 Avis clients</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px;">
        {reviews_html}
    </div>
</div>

{footer_html}
</div></body></html>"""
    with open(os.path.join(output_dir, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(html_fiche)

# 5. Page Compagnies Aériennes
airlines_cards_html = ""
for a_nom, a_data in sorted(AIRLINES_DATA.items()):
    a_slug = nettoyer_slug(a_nom)
    logo_p = a_data.get("logo", "images/airbus_vol.jpg")
    
    fiche_airline = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><title>{a_nom}</title>{global_style}</head>
<body><div class="container">{menu_html}
<a href="compagnies-aeriennes.html" style="color: #38bdf8; display: inline-block; margin-bottom: 15px; text-decoration: none;">← Retour aux compagnies</a>
<div class="card">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
        <div>
            <h1>{a_nom}</h1>
            <p style="color: #94a3b8; margin: 0;">Catégorie : <b>{a_data.get('categorie', 'N/A')}</b> | Alliance : <b>{a_data.get('alliance', 'N/A')}</b> | Note : ⭐ <b>{a_data.get('note', 'N/A')}</b></p>
        </div>
        {f'<img src="{logo_p}" alt="Logo {escape_html(a_nom)}" style="max-height: 80px; object-fit: contain; border-radius: 6px;">' if os.path.exists(logo_p) else ''}
    </div>
    <hr style="border-color: #3A506B; margin: 20px 0;">
    <h3>📖 À propos</h3>
    <p>{a_data.get('resume', '')}</p>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
        <div>
            <p><b>📜 Histoire :</b> {a_data.get('histoire', 'N/A')}</p>
            <p><b>✈️ Flotte :</b> {a_data.get('flotte', 'N/A')}</p>
        </div>
        <div>
            <p><b>🧳 Bagages :</b> {a_data.get('bagages', 'N/A')}</p>
            <p><b>🛡️ Sécurité :</b> {a_data.get('securite', 'N/A')}</p>
        </div>
    </div>
    
    <h3>📍 Liaisons fréquentes</h3>
    <p>{', '.join(a_data.get('liaisons', []))}</p>
    
    <div style="background-color: #0b132b; padding: 15px; border-radius: 8px; border: 1px solid #3A506B; margin: 20px 0;">
        <p style="margin: 0; color: #38bdf8;"><b>🎯 Pour qui ?</b> {a_data.get('pour_qui', '')}</p>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div style="background-color: rgba(16, 185, 129, 0.1); padding: 15px; border-radius: 8px; border: 1px solid #10B981;">
            <h4 style="color: #10B981; margin-top: 0;">✅ Points Positifs</h4>
            <ul>{"".join([f"<li>{p}</li>" for p in a_data.get('points_positifs', [])])}</ul>
        </div>
        <div style="background-color: rgba(239, 68, 68, 0.1); padding: 15px; border-radius: 8px; border: 1px solid #ef4444;">
            <h4 style="color: #ef4444; margin-top: 0;">⚠️ Points de vigilance</h4>
            <ul>{"".join([f"<li>{n}</li>" for n in a_data.get('points_negatifs', [])])}</ul>
        </div>
    </div>

    {f'<div style="margin-top: 30px;"><a href="{a_data["lien"]}" target="_blank" class="btn" style="background-color: #0066cc; display: block; text-align: center;">Réserver le vol</a></div>' if a_data.get('lien') else ''}
</div>
{footer_html}
</div></body></html>"""
    with open(os.path.join(output_dir, f"{a_slug}.html"), "w", encoding="utf-8") as f: f.write(fiche_airline)

    airlines_cards_html += f"""
    <div class="card" style="display: flex; justify-content: space-between; align-items: center; gap: 20px;">
        <div>
            <h3>{a_nom}</h3>
            <p style="color: #94a3b8; margin: 5px 0;">{a_data.get('resume', '')[:120]}...</p>
            <span style="color: #38bdf8; font-size: 0.9em;">Alliance : {a_data.get('alliance', 'N/A')}</span>
        </div>
        <div style="text-align: right; flex-shrink: 0;">
            <span style="color: #fbbf24; font-weight: bold; font-size: 1.1em; display: block; margin-bottom: 10px;">⭐ {a_data.get('note', 'N/A')}</span>
            <a href="{a_slug}.html" class="btn" style="padding: 8px 15px; font-size: 0.9em; background:#3A506B;">Voir la fiche</a>
        </div>
    </div>"""

p_comp = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><title>Compagnies Aériennes | MyHotelCompare</title>{global_style}</head>
<body><div class="container">{menu_html}
<h1>✈️ Guide des Compagnies Aériennes</h1>
<p style="color: #94a3b8; margin-bottom: 25px;">Analysez les caractéristiques, les avantages et les points d'attention de chaque compagnie.</p>
<label for="airline-selector" style="font-weight:700;">Choisissez une compagnie aérienne</label>
<select id="airline-selector" onchange="afficherCompagnie(this.value)" style="width:100%; max-width:520px; padding:12px; margin:10px 0 24px; border-radius:10px;">
    <option value="">Sélectionnez une compagnie...</option>
    {''.join(f'<option value="{a_slug}">{escape_html(a_nom)}</option>' for a_nom, a_data in sorted(AIRLINES_DATA.items()) for a_slug in [nettoyer_slug(a_nom)])}
</select>
<div id="airline-details" style="display:none;"></div>
<script>
function afficherCompagnie(slug) {{
    const details = document.getElementById('airline-details');
    if (!slug) {{ details.style.display = 'none'; details.innerHTML = ''; return; }}
    const link = document.createElement('a');
    link.href = slug + '.html'; link.className = 'btn'; link.textContent = 'Voir la fiche complète';
    details.innerHTML = '<div class="card"><h2>Compagnie sélectionnée</h2><p>Consultez sa présentation, ses services et ses points de vigilance.</p></div>';
    details.querySelector('.card').appendChild(link); details.style.display = 'block';
}}
</script>
{footer_html}
</div></body></html>"""
with open(os.path.join(output_dir, "compagnies-aeriennes.html"), "w", encoding="utf-8") as f: f.write(p_comp)

# 6. Page Loueurs de Véhicules
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

loueurs_cards_html = ""
for l_nom, l_info in loueurs_data.items():
    loueurs_cards_html += f"""
    <div class="card" style="display: flex; justify-content: space-between; align-items: center; gap: 20px;">
        <div>
            <span style="background-color: #3b82f6; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold; font-size: 0.9em;">{l_info['rang']}</span>
            <h3 style="margin: 10px 0 5px 0;">{l_nom}</h3>
            <p style="color: #94a3b8; margin: 0;">{l_info['resume']}</p>
        </div>
        <div style="text-align: right; flex-shrink: 0;">
            <span style="color: #fbbf24; font-weight: bold; font-size: 1.1em;">⭐ {l_info['note']}</span>
        </div>
    </div>"""

p_loueurs = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><title>Location de Véhicules | MyHotelCompare</title>{global_style}</head>
<body><div class="container">{menu_html}
<div class="card" style="background: linear-gradient(135deg, #d8f1f5 0%, #f4fcfd 100%);">
    <h1>🚗 Trouvez la meilleure voiture pour votre voyage</h1>
    <p>Comparez rapidement les offres des principaux loueurs et réservez au meilleur prix.</p>
    <div style="margin-top: 18px;">
        <script async src="https://tpemd.com/content?trs=552839&shmarker=751055&locale=fr&powered_by=true&border_radius=4&plain=true&show_logo=false&color_background=%23ffca28&color_button=%2355a539&color_text=%23000000&color_input_text=%23000000&color_button_text=%23ffffff&promo_id=4480&campaign_id=10" charset="utf-8"></script>
    </div>
</div>
<div class="card">
    <h1>🚗 Comparateur & Agences de Location de Véhicules</h1>
    <p>Recherchez et comparez les meilleurs loueurs de voitures à travers le monde.</p>
</div>
<h2 style="margin-top: 30px;">Nos partenaires loueurs</h2>
<div class="rental-grid">
{loueurs_cards_html}
</div>
{footer_html}
</div></body></html>"""
with open(os.path.join(output_dir, "loueurs-vehicules.html"), "w", encoding="utf-8") as f: f.write(p_loueurs)

# 7. Page Croisières
croisieres_data = {
    "Costa Croisières - Merveilles de la Méditerranée": {
        "compagnie": "Costa Croisières", "region": "Méditerranée Occidentale", "duree": "8 jours / 7 nuits",
        "depart": "Marseille (France)", "prix_moyen": "750€ / personne", "avis": "8,5/10 Très bien",
        "image": "https://www.costacroisieres.fr/map/itineraries/CIV07ACQ/images/fr_FR_CIV07ACQ_landscape_sd_1x.jpg",
        "lien_reservation": "https://www.costacroisieres.fr/cruises/CIV07ACQ/PA07261114.html",
        "description": "Une magnifique échappée ensoleillée à la découverte des plus beaux joyaux de la Méditerranée.",
        "itineraire": ["Jour 1 : Civitavecchia / Rome", "Jour 2 : Savone", "Jour 3 : Marseille", "Jour 4 : Barcelone", "Jour 5 : En navigation", "Jour 6 : La Goulette | Tunis", "Jour 7 : Palerme", "Jour 8 : Retour à Civitavecchia / Rome"]
    },
    "Costa Smeralda - Merveilles de la Méditerranée": {
        "compagnie": "Costa Croisières", "region": "Italie, France, Espagne", "duree": "6 jours / 5 nuits",
        "depart": "Civitavecchia | Rome", "prix_moyen": "918€ / 2 passagers", "avis": "Exceptionnel (4/5)",
        "image": "https://www.costacroisieres.fr/map/itineraries/CIV05A19/images/fr_FR_CIV05A19_landscape_sd_1x.jpg",
        "lien_reservation": "https://www.costacroisieres.fr/cruises/CIV05A19/SM05261106.html",
        "description": "Mini-Croisières de 6 jours en Méditerranée à bord du Costa Smeralda.",
        "itineraire": ["Jour 1 : Civitavecchia | Rome", "Jour 2 : Savone", "Jour 3 : Marseille", "Jour 4 : Barcelone", "Jour 5 : En navigation", "Jour 6 : Civitavecchia | Rome"]
    },
    "Costa Fascinosa - Caraïbes et Antilles": {
        "compagnie": "Costa Croisières", "region": "Caraïbes et Antilles", "duree": "8 jours / 7 nuits",
        "depart": "La Romana / Saint-Domingue", "prix_moyen": "918€ / 2 passagers", "avis": "Exceptionnel (4/5)",
        "image": "https://www.costacroisieres.fr/map/itineraries/LRM07A20/images/fr_FR_LRM07A20_landscape_sd_1x.jpg",
        "lien_reservation": "https://www.costacroisieres.fr/cruises/LRM07A20/FS07270117.html",
        "description": "Une croisière paradisiaque de 8 jours à travers les Caraïbes et les Antilles à bord du Costa Fascinosa.",
        "itineraire": ["Jour 1 : La Romana", "Jour 2 : Mer des Caraïbes", "Jour 3 : Martinique", "Jour 4 : Barbade", "Jour 5 : Guadeloupe", "Jour 6 : Saint-Kitts", "Jour 7 : Tortola", "Jour 8 : La Romana"]
    }
}

croisieres_list_html = ""
for c_nom, c_data in croisieres_data.items():
    c_slug = nettoyer_slug(c_nom)
    fiche_croisiere = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><title>{c_nom}</title>{global_style}</head>
<body><div class="container">{menu_html}
<a href="croisieres.html" style="color: #38bdf8; display: inline-block; margin-bottom: 15px; text-decoration: none;">← Retour aux croisières</a>
<div class="card">
    <h1>{c_nom}</h1>
    <p style="color: #94a3b8;">🚢 {c_data['compagnie']} | 📍 Région : {c_data['region']} | ⏱️ {c_data['duree']}</p>
    {f'<img src="{c_data["image"]}" alt="{escape_html(c_nom)}" style="width:100%; max-height:350px; object-fit:cover; border-radius:8px; margin:15px 0;">' if c_data['image'] else ''}
    <h3>✨ Description</h3><p>{c_data['description']}</p>
    <h3>🗺️ Itinéraire détaillé</h3>
    <ul>{"".join([f"<li>{etape}</li>" for etape in c_data['itineraire']])}</ul>
    <h3>⭐ Avis : {c_data['avis']} | 💰 Prix : {c_data['prix_moyen']}</h3>
    <div style="margin-top: 30px;">
        <a href="{c_data['lien_reservation']}" target="_blank" class="btn" style="background-color: #003580; display: block; text-align: center;">Réserver cette croisière</a>
    </div>
</div>
{footer_html}
</div></body></html>"""
    with open(os.path.join(output_dir, f"{c_slug}.html"), "w", encoding="utf-8") as f: f.write(fiche_croisiere)

    croisieres_list_html += f"""
    <div class="card">
        {f'<img src="{c_data["image"]}" alt="{escape_html(c_nom)}" style="width:100%; height:180px; object-fit:cover; border-radius:8px; margin-bottom:10px;">' if c_data['image'] else ''}
        <h3>{c_nom}</h3>
        <p style="color:#94a3b8;">📍 {c_data['region']} | ⏱️ {c_data['duree']} | ⭐ {c_data['avis']}</p>
        <p style="color:#10B981; font-weight:bold;">💰 {c_data['prix_moyen']}</p>
        <p>{c_data['description']}</p>
        <a href="{c_slug}.html" class="btn" style="background:#3A506B;">📄 Voir l'itinéraire détaillé</a>
        <a href="{c_data['lien_reservation']}" target="_blank" class="btn" style="background-color: #003580; display:block; text-align:center;">Réserver</a>
    </div>"""

croisiere_page = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><title>Nos Croisières | MyHotelCompare</title>{global_style}</head>
<body><div class="container">{menu_html}
<h1>🚢 Nos Croisières Exclusives</h1>
<p style="color: #94a3b8; margin-bottom: 25px;">Partez en mer avec notre sélection de croisières inoubliables.</p>
{croisieres_list_html}
{footer_html}
</div></body></html>"""
with open(os.path.join(output_dir, "croisieres.html"), "w", encoding="utf-8") as f: f.write(croisiere_page)

# 8. Blog dynamique
blog_list_html = ""
if os.path.exists("blog_data.json"):
    with open("blog_data.json", "r", encoding="utf-8") as f:
        articles = json.load(f)
        for art in articles:
            art_title = art.get('titre', '')
            art_slug = nettoyer_slug(art.get('slug') or art_title)
            if not art_slug: continue
            
            images_art = art.get('images', [])
            img_art = get_public_image(images_art[0] if images_art else art.get('image', ''))
            details_texte = art.get('details', '').replace('\n', '<br>')
            art_url = f"{SITE_URL}/{art_slug}.html"
            art_og_tags = generer_og_tags(art_title, art.get('resume', ''), art_url, img_art)

            article_page = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{art_title} | Blog</title>
<meta name="description" content="{escape_html(art.get('resume', ''))}">
<link rel="canonical" href="{art_url}">
{art_og_tags}
{global_style}</head>
<body><div class="container">{menu_html}
<a href="blog.html" style="color: #38bdf8; display: inline-block; margin-bottom: 15px; text-decoration: none;">← Retour au blog</a>
<div class="card">
    <h1>{art_title}</h1>
    {f'<img src="{img_art}" alt="{escape_html(art_title)}" style="width:100%; max-height:400px; object-fit:cover; border-radius:8px; margin:20px 0;">' if img_art else ''}
    <p style="font-size: 1.1em; line-height: 1.8;">{details_texte}</p>
</div>
{footer_html}
</div></body></html>"""
            with open(os.path.join(output_dir, f"{art_slug}.html"), "w", encoding="utf-8") as f: f.write(article_page)
            
            blog_list_html += f"""
            <div class="card" style="display: flex; gap: 20px; align-items: center;">
                {f'<img src="{img_art}" alt="{escape_html(art_title)}" style="width: 200px; height: 130px; object-fit: cover; border-radius: 8px; flex-shrink: 0;">' if img_art else ''}
                <div>
                    <h3>{art_title}</h3>
                    <p style="color: #94a3b8; font-size: 0.95em;">{art.get('resume', '')}</p>
                    <a href="{art_slug}.html" class="btn">Lire l'article complet</a>
                </div>
            </div>"""

blog_page = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><title>Notre Blog Voyage | MyHotelCompare</title>{global_style}</head>
<body><div class="container">{menu_html}
<h1>📖 Notre Blog Voyage</h1>
<p style="color: #94a3b8; margin-bottom: 30px;">Découvrez tous nos conseils d'experts, récits de voyage et guides pratiques.</p>
{blog_list_html}
{footer_html}
</div></body></html>"""
with open(os.path.join(output_dir, "blog.html"), "w", encoding="utf-8") as f: f.write(blog_page)

generate_information_pages()
generate_seo_files()

print("Génération réussie à 100% avec l'intégration complète des témoignages et du footer Formspree !")

if WATCH_MODE:
    print("Surveillance active : enregistre un fichier JSON pour régénérer le site. Ctrl+C pour arrêter.")
    watched_files = [*DATA_DIR.rglob("*.json"), BASE_DIR / "blog_data.json"]

    def snapshot():
        return {
            str(path): (path.stat().st_mtime_ns, path.stat().st_size)
            for path in watched_files
            if path.exists()
        }

    previous_snapshot = snapshot()
    try:
        while True:
            time.sleep(1)
            current_snapshot = snapshot()
            if current_snapshot != previous_snapshot:
                print("Modification JSON détectée : régénération en cours...")
                subprocess.run([sys.executable, str(Path(__file__).resolve()), "--reset"], check=True)
                watched_files = [*DATA_DIR.rglob("*.json"), BASE_DIR / "blog_data.json"]
                previous_snapshot = snapshot()
                print("Régénération terminée.")
    except KeyboardInterrupt:
        print("Surveillance arrêtée.")