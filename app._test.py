import streamlit as st
import os
import json
import streamlit.components.v1 as components
import urllib.parse
import base64
import apropos
import confidentialite
import contact

# --- FONCTION DE MISE À JOUR DES LIENS ---
def update_booking_aid(url, new_aid="8012379"):
    if not url:
        return ""
    # Nettoyage automatique du ? en fin de lien
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
    # Nettoyage automatique du ? en fin de lien
    url = url.rstrip('?')
    if "anrdoezrs.net" in url:
        return url
    encoded_url = urllib.parse.quote(url, safe='')
    return f"https://www.anrdoezrs.net/click-8012379-13854902?url={encoded_url}"

# --- Configuration de la page ---
st.set_page_config(page_title="HotelCompare", page_icon="images/favicon_io/favicon.ico", layout="wide")
# Configuration de la page
st.set_page_config(page_title="HotelCompare", page_icon="images/favicon_io/favicon.ico", layout="wide")

import streamlit as st

# Injection des balises Open Graph pour l'aperçu Facebook
st.markdown("""
    <script>
        function setMetaTag(property, content) {
            let element = document.querySelector(`meta[property='${property}']`) || document.querySelector(`meta[name='${property}']`);
            if (!element) {
                element = document.createElement('meta');
                if (property.startsWith('og:')) {
                    element.setAttribute('property', property);
                } else {
                    element.setAttribute('name', property);
                }
                document.head.appendChild(element);
            }
            element.setAttribute('content', content);
        }

        // Personnalise ces informations selon ton site
        setMetaTag('og:title', 'HotelCompare - Comparateur d’hôtels');
        setMetaTag('og:description', 'Trouve et compare les meilleures offres d’hôtels facilement.');
        setMetaTag('og:image', 'https://myhotelcompare.com/media/c139095b96abe4e5e4fc4ea931714e10.png'); // Mets le lien direct vers une image JPG/PNG
        setMetaTag('og:url', 'https://myhotelcompare.com/Blog');
        setMetaTag('og:type', 'website');
    </script>
""", unsafe_allow_html=True)

# Le style CSS global (masquage de la sidebar, de l'en-tête et mode sombre)
st.markdown("""
    <style>
    /* Masquer tous les types d'en-têtes et barres Streamlit possibles */
    header, [data-testid="stHeader"], [data-testid="stDecoration"], .stApp > header {
        display: none !important;
        height: 0px !important;
    }
    
    /* Cacher le menu latéral */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Fond général sombre et suppression de tout espace en haut */
    .stApp { 
        background-color: #0B132B !important; 
        color: #FFFFFF !important;
    }
    
    .block-container { 
        padding-top: 0rem !important; 
        margin-top: 0px !important;
    }
    
    iframe { 
        width: 100% !important; 
    }
    
    /* Textes généraux et libellés en blanc */
    p, span, label, h1, h2, h3, h4, h5, h6, 
    .stMarkdown, div[data-baseweb="select"] span {
        color: #FFFFFF !important;
    }

    /* --- REDUCTION DES ESPACES ENTRE LES ELEMENTS --- */
    div.stMarkdown {
        margin-bottom: -10px !important; /* Rapproche les éléments textuels les uns des autres */
    }

    /* Texte des boutons du haut en NOIR */
    .stButton button, .stButton button p, .stButton button span {
        color: #0B132B !important;
        font-weight: 600 !important;
    }

    /* Bouton "Comparer" (primary) en vert */
    button[kind="primary"] {
        background-color: #10B981 !important;
        border-color: #10B981 !important;
    }
    button[kind="primary"]:hover {
        background-color: #0d9668 !important;
        border-color: #0d9668 !important;
    }
    button[kind="primary"] p, 
    button[kind="primary"] span {
        color: #FFFFFF !important;
    }

    /* Cartes d'hôtels adaptées au fond sombre */
    .hotel-card { 
        background-color: #1C2541 !important; 
        border: 1px solid #3A506B;
        border-radius: 12px;
        padding: 20px;
        color: #FFFFFF !important;
    }

    /* --- CORRECTION POUR LES AVIS (TEXTE EN NOIR SUR FOND CLAIR) --- */
    div[data-testid="column"] div.stMarkdown p, 
    div[data-testid="column"] div.stMarkdown span {
        color: #0B132B !important;
    }
    </style>
""", unsafe_allow_html=True)

# Votre code de vérification Google Search Console
google_verification_content = "UFPNwmAw5bpc..."

# Script JS pour remonter et insérer la balise dans le <head> principal
google_tag_script = f"""
<script>
    const parentHead = window.parent.document.head;
    
    // Vérifie si la balise n'existe pas déjà pour éviter les doublons
    if (!parentHead.querySelector('meta[name="google-site-verification"]')) {{
        const metaTag = document.createElement('meta');
        metaTag.name = 'google-site-verification';
        metaTag.content = '{google_verification_content}';
        parentHead.appendChild(metaTag);
    }}
</script>
"""

# Exécution du composant (dimensions à 0 car il n'y a rien d'affiché visuellement)
components.html(google_tag_script, height=0, width=0)
# --- AJOUTEZ CE BLOC ICI ---
canonical_url = "https://www.myhotelcompare.com/"
canonical_script = f"""
<script>
    const parentHead = window.parent.document.head;
    // Supprime une ancienne balise canonical pour éviter les doublons
    const existingCanonical = parentHead.querySelector('link[rel="canonical"]');
    if (existingCanonical) {{ existingCanonical.remove(); }}
    // Ajoute la nouvelle
    const linkTag = document.createElement('link');
    linkTag.rel = 'canonical';
    linkTag.href = '{canonical_url}';
    parentHead.appendChild(linkTag);
</script>
"""
components.html(canonical_script, height=0, width=0)
# ---------------------------
# --- GOOGLE ANALYTICS (gtag.js) ---
google_analytics_script = """
<script>
    const parentHead = window.parent.document.head;
    if (!parentHead.querySelector('script[data-ga-injected]')) {
        const gtagScript = document.createElement('script');
        gtagScript.async = true;
        gtagScript.src = 'https://www.googletagmanager.com/gtag/js?id=G-RKPRX66Z4N';
        gtagScript.setAttribute('data-ga-injected', 'true');
        parentHead.appendChild(gtagScript);

        const inlineScript = document.createElement('script');
        inlineScript.text = `
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-RKPRX66Z4N');
        `;
        parentHead.appendChild(inlineScript);
    }
</script>
"""
components.html(google_analytics_script, height=0, width=0)

# --- AJOUT DU SCRIPT DE TRACKING CJ AFFILIATE ---
st.markdown(
    '<script src="https://www.anrdoezrs.net/am/10182501/include/allCJ/impressions/page/am.js"></script>',
    unsafe_allow_html=True
)

# Passerelle pour lier les liens HTML du footer sombre à la session
query_params = st.query_params
if "page" in query_params:
    p = query_params["page"]
    if p == "apropos":
        st.session_state.page = "À propos"
    elif p == "confidentialite":
        st.session_state.page = "Politique de confidentialité"
    elif p == "contact":
        st.session_state.page = "Contact"
    elif p == "accueil":
        st.session_state.page = "Comparateur Hôtels"

# Gestion de l'état de navigation
if 'page' not in st.session_state:
    st.session_state.page = "Comparateur Hôtels"

# --- Chargement dynamique de tous les hôtels depuis le dossier data/ ---
HOTELS_DATA = {}
data_dir = "data"

if os.path.exists(data_dir):
    for fichier in os.listdir(data_dir):
        if fichier.endswith(".json") or fichier.endswith(".geojson"):
            chemin_fichier = os.path.join(data_dir, fichier)
            try:
                with open(chemin_fichier, "r", encoding="utf-8") as f:
                    donnees_pays = json.load(f)
                    if isinstance(donnees_pays, dict):
                        HOTELS_DATA.update(donnees_pays)
            except Exception as e:
                print(f"Erreur lors du chargement de {fichier}: {e}")

# --- En-tête Global ---
col_logo, col_titre = st.columns([1, 8])
with col_logo:
    if os.path.exists("logo_4.png"):
        st.image("logo_4.png", width=90)
with col_titre:
    st.markdown("<h1 style='text-align: center;'>Comparateur intelligent d'hôtels</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.2em;'><b>Nomad</b> : L'IA qui analyse les avis pour dénicher votre hôtel idéal.</p>", unsafe_allow_html=True)

st.markdown("---")

# --- Boutons de Navigation (Redirection vers les pages multipages) ---
b1, b2, b3, b4, b5 = st.columns(5)

with b1:
    if st.button("Hôtels", icon=":material/hotel:", use_container_width=True):
        st.session_state.page = "Comparateur Hôtels"
        st.rerun()
with b2:
    if st.button("Compagnies Aériennes", icon=":material/flight:", use_container_width=True):
        st.switch_page("pages/1_Compagnies_Aeriennes.py")
with b3:
    if st.button("Location de Véhicules", icon=":material/directions_car:", use_container_width=True):
        st.switch_page("pages/2_Loueurs_Vehicules.py")
with b4:
    if st.button("Croisières", icon=":material/directions_boat:", use_container_width=True):
        st.switch_page("pages/3_Cruises.py")

with b5:
    if st.button("Blog", icon=":material/article:", use_container_width=True):
        st.switch_page("pages/4_Blog.py")

st.markdown("---")

# ==============================================================================
# GESTION DE L'AFFICHAGE DES PAGES SECONDAIRES (Footer links)
# ==============================================================================

if st.session_state.page == "À propos":
    apropos.afficher_page()

elif st.session_state.page == "Politique de confidentialité":
    confidentialite.afficher_page()

elif st.session_state.page == "Contact":
    contact.afficher_page()

else:
    # ==============================================================================
    # SECTION 1 : COMPARATEUR D'HÔTELS & RECHERCHE MULTICRITÈRES (ACCUEIL)
    # ==============================================================================
    
    # --- Style CSS pour les badges et images ---
    st.markdown(
    """
    <style>
    /* Cible spécifiquement le bouton de lien st.link_button */
    [data-testid="stLinkButton"] a {
        background-color: #003580 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    /* Force le texte interne du lien en blanc */
    [data-testid="stLinkButton"] a div, 
    [data-testid="stLinkButton"] a p, 
    [data-testid="stLinkButton"] a span {
        color: #FFFFFF !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# SECTION 1 : CAROUSEL & PROMO CÔTE À CÔTE (HAUT DE PAGE)
# ==============================================================================
col_caroussel, col_promo = st.columns([1, 1], gap="medium")

with col_caroussel:
    def get_img_as_base64(path):
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""

    img_paths = ["images/image caroussel 2.png", "images/image_afrique.jpg", "images/image_astuce.jpg", "images/image_hotel.jpg", "images/image_tunisie.jpg"]
    imgs_base64 = [get_img_as_base64(p) for p in img_paths]

    carousel_html = f"""
    <div style="width: 100%; height: 350px; position: relative; overflow: hidden; border-radius: 8px; background: #0e1117;">
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
    st.markdown(carousel_html, unsafe_allow_html=True)

with col_promo:
    with st.container(border=True):
        chemin_promo = "data/promo_semaine.json"
        if os.path.exists(chemin_promo):
            try:
                with open(chemin_promo, "r", encoding="utf-8") as f:
                    promo = json.load(f)
                    if isinstance(promo, dict):
                        # 1. Image
                        if promo.get("image"):
                            st.markdown(f'<img src="{promo["image"]}" style="width: 100%; height: 160px; object-fit: cover; border-radius: 6px; margin-bottom: 8px;">', unsafe_allow_html=True)
                        
                        # 2. Titre
                        st.markdown(f"**{promo.get('titre', '')}**")
                        
                        # 3. Ligne Pays et Ville
                        ville = promo.get("ville", "")
                        pays = promo.get("pays", "")
                        if ville or pays:
                            st.markdown(f"<p style='color: #94a3b8; font-size: 0.85em; margin-top: -8px; margin-bottom: 6px;'>📍 {ville}{', ' if ville and pays else ''}{pays}</p>", unsafe_allow_html=True)
                        
                        # 4. Description
                        st.write(promo.get("description", ""))
                        
                        # 5. Bouton
                        if promo.get("lien"):
                            lien_final = update_booking_aid(promo["lien"])
                            st.markdown(f"""
                                <a href="{lien_final}" target="_blank" rel="nofollow sponsored" rel="nofollow sponsored" rel="nofollow sponsored" rel="nofollow sponsored" rel="nofollow sponsored" rel="nofollow sponsored" 
                                   style="display: block; background-color: #003580; color: white; 
                                   padding: 10px; text-align: center; text-decoration: none; 
                                   border-radius: 6px; font-weight: bold; font-family: sans-serif;">
                                   J'en profite
                                </a>
                            """, unsafe_allow_html=True)
            except Exception as e:
                print(f"Erreur chargement promo : {e}")

# ==============================================================================
# SECTION 2 : COMPARATEUR D'HÔTELS (PLEINE LARGEUR EN DESSOUS)
# ==============================================================================
st.markdown("---")
st.subheader("💡 Comment comparer vos hôtels")
st.markdown(
    "1. Sélectionnez pays et ville. 2. Choisissez deux hôtels. 3. Cliquez sur"
    " Comparer."
)

# --- Menus de sélection du Comparateur ---
pays_disponibles = sorted(
    list(
        set(
            str(d.get("pays", "Autre")).strip()
            for d in HOTELS_DATA.values()
            if isinstance(d, dict)
        )
    )
)
c_pays, c_ville, c1, c2, c_btn1, c_btn2 = st.columns(
    [2, 2, 2.5, 2.5, 1.8, 1.2]
)

choix_pays = c_pays.selectbox(
    "Pays",
    pays_disponibles,
    index=None,
    placeholder="Choisissez un pays",
    key="comp_pays",
)

villes_disponibles_comp = sorted(
    list(
        set(
            str(d.get("ville", "Autre")).strip()
            for d in HOTELS_DATA.values()
            if isinstance(d, dict)
            and (not choix_pays or str(d.get("pays", "")).strip() == choix_pays)
        )
    )
)
choix_ville = c_ville.selectbox(
    "Ville",
    villes_disponibles_comp,
    index=None,
    placeholder="Choisissez une ville",
    key="comp_ville",
)

hotels_filtres_comp = [
    nom
    for nom, d in HOTELS_DATA.items()
    if isinstance(d, dict)
    and (not choix_pays or str(d.get("pays", "")).strip() == choix_pays)
    and (not choix_ville or str(d.get("ville", "")).strip() == choix_ville)
]

choix1 = c1.selectbox(
    "Premier hôtel",
    hotels_filtres_comp,
    index=None,
    placeholder="Choisissez un 1er hébergement",
)
hotels_restants = [h for h in hotels_filtres_comp if h != choix1]
choix2 = c2.selectbox(
    "Deuxième hôtel",
    hotels_restants,
    index=None,
    placeholder="Choisissez un 2nd hébergement",
)

valider = c_btn1.button("Comparer", type="primary", use_container_width=True)
if c_btn2.button("Reset", use_container_width=True):
  st.rerun()
# --- Affichage des résultats du Comparateur ---
if valider:
    comparaison = [c for c in [choix1, choix2] if c != ""]
    if not comparaison:
        st.warning("Veuillez sélectionner au moins un hôtel.")
    else:
        cols = st.columns(len(comparaison))
        for i, nom in enumerate(comparaison):
            d = HOTELS_DATA.get(nom)
            if not d:
                continue
            with cols[i]:
                st.markdown('<div class="hotel-card">', unsafe_allow_html=True)
                
                # --- STRUCTURE EN 2 COLONNES ---
                col_gauche, col_droite = st.columns([1.2, 1], gap="medium")
                
                with col_gauche:
                    img_src = d.get("image")
                    if img_src and img_src != "...":
                        st.image(img_src, use_container_width=True)
                        
                    st.subheader(nom)
                    ville_hotel = d.get("ville", "")
                    pays_hotel = d.get("pays", "")
                    if ville_hotel or pays_hotel:
                        st.markdown(f"<p style='color: #94a3b8; font-size: 0.9em; margin-top: -10px; margin-bottom: 10px;'>📍 {ville_hotel}, {pays_hotel}</p>", unsafe_allow_html=True)
                    
                    if d.get("avis"):
                        st.markdown(f"Note : <span class='badge-note'>{d['avis']}</span>", unsafe_allow_html=True)
                    
                    st.write("")
                    if d.get("etoiles"): st.write(f"⭐ **{d['etoiles']}**")
                    if d.get("prix_moyen"): st.write(f"💰 {d['prix_moyen']}")
                
                with col_droite:
                    st.markdown("<p style='font-weight: bold; margin-bottom: 8px;'>Réserver avec :</p>", unsafe_allow_html=True)
                    
                    prix_affiche = d.get("prix_moyen", "Meilleurs prix")

                    lien_brut = d.get("lien_booking") or d.get("lien", "https://www.booking.com/index.fr.html")
                    lien_booking = update_booking_aid(lien_brut)

                    st.markdown(f"""
                        <a href='{lien_booking}' target='_blank' rel='nofollow sponsored' rel='nofollow sponsored' rel='nofollow sponsored' rel='nofollow sponsored' rel='nofollow sponsored' 
                        style='display: block; background-color: #003580; color: white; padding: 12px 10px; text-align: center; text-decoration: none; border-radius: 6px; font-weight: bold; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                            Réserver sur Booking<br>
                            <span style='font-size: 13px; font-weight: normal; opacity: 0.9;'>À partir de {prix_affiche}</span>
                        </a>
                    """, unsafe_allow_html=True)

                    lien_expedia = d.get("lien_expedia", "https://www.anrdoezrs.net/click-8012379-13854902?url=https://www.expedia.fr/")

                    st.markdown(f"""
                        <a href='{lien_expedia}' target='_blank' rel='nofollow sponsored' rel='nofollow sponsored' rel='nofollow sponsored' 
                        style='display: block; background-color: #ffcc00; color: #000000; padding: 12px 10px; text-align: center; text-decoration: none; border-radius: 6px; font-weight: bold; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                            Réserver sur Expedia<br>
                            <span style='font-size: 13px; font-weight: normal; opacity: 0.8;'>À partir de {prix_affiche}</span>
                        </a>
                    """, unsafe_allow_html=True)

                    # 3. Carte géographique
                    lieu_recherche = f"{nom}, {ville_hotel}, {pays_hotel}"
                    lieu_encode = urllib.parse.quote(lieu_recherche)
                    map_html = f"""
                    <iframe width="100%" height="180" style="border:0; border-radius: 8px; margin-top: 10px;" loading="lazy" src="https://maps.google.com/maps?q={lieu_encode}&t=&z=13&ie=UTF8&iwloc=&output=embed"></iframe>
                    """
                    components.html(map_html, height=190)

                # --- PARTIE BASSE ---
                st.write("---")
                # ... (reste de votre code pour la description, équipements, etc.)

                # --- PARTIE BASSE : Description, équipements et avis (reste inchangée) ---
                st.write("---")
                desc_finale = d.get("description_ia") or d.get("description")
                if desc_finale:
                     st.write(f"**✨ Description :** {desc_finale}")
                
                if d.get("equipements"):
                    with st.expander("🛠️ Équipements"):
                        st.write(", ".join(d['equipements']))

                if d.get("points_positifs"):
                    with st.expander("✅ Points Positifs"):
                        for p in d.get("points_positifs"): st.write(f"• {p}")
                if d.get("points_negatifs"):
                    with st.expander("⚠️ Points Négatifs"):
                        for n in d.get("points_negatifs"): st.write(f"• {n}")
                
                if d.get("Nomad, vous en dit plus"):
                    st.markdown("---")
                    st.success(f"🗣️ **Nomad, vous en dit plus :** {d['Nomad, vous en dit plus']}")

                if d.get("pour_qui") and isinstance(d.get("pour_qui"), dict):
                    st.markdown("---")
                    st.info(f"**Verdict :** {d['pour_qui'].get('verdict', '')}")
                    with st.expander("🤔 Pour qui ?"):
                        for cle, val in d['pour_qui'].items():
                           if cle != 'verdict':
                            st.write(f"**{cle.capitalize()} :** {val}")
                
                if d.get("meta_avis"):
                    st.caption(d['meta_avis'])
                                
                    st.markdown('</div>', unsafe_allow_html=True)
# SECTION 2 : RECHERCHE D'HÔTEL PAR CRITÈRES (SÉCURISÉE)
# ==============================================================================
st.markdown(
    """
    <style>
    /* Correction pour les tags sélectionnés dans le multiselect */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #ff4b4b !important; /* Fond rouge */
    }
    .stMultiSelect [data-baseweb="tag"] span {
        color: #ffffff !important; /* Texte blanc */
    }
    /* Garde le texte de la zone de saisie visible */
    .stMultiSelect div[data-baseweb="select"] span {
        color: #ffffff !important; 
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")
st.subheader("🎯 Recherche d'hôtel par critères")
st.write("Filtrez précisément selon vos envies ci-dessous 👇")

col_c1, col_c2, col_c3 = st.columns(3)

with col_c1:
    pays_disponibles_crit = sorted(list(set(str(info.get("pays", "")).strip() for info in HOTELS_DATA.values() if isinstance(info, dict) and info.get("pays"))))
    filtre_pays_crit = st.selectbox("🌍 Pays :", ["Tous"] + pays_disponibles_crit, key="crit_pays")

with col_c2:
    if filtre_pays_crit == "Tous":
        villes_disponibles_crit = sorted(list(set(info.get("ville", "") for info in HOTELS_DATA.values() if isinstance(info, dict) and info.get("ville"))))
    else:
        villes_disponibles_crit = sorted(list(set(info.get("ville", "") for info in HOTELS_DATA.values() if isinstance(info, dict) and str(info.get("pays", "")).strip() == filtre_pays_crit and info.get("ville"))))
        
    filtre_ville_crit = st.selectbox("📍 Ville :", ["Toutes"] + villes_disponibles_crit, key="crit_ville")

with col_c3:
    filtre_etoiles_crit = st.selectbox("⭐ Standing :", ["Tous", "3 étoiles", "4 étoiles", "5 étoiles", "Maison d'hôtes"], key="crit_etoiles")

# Multiselect pour les équipements
filtre_equipements_multi = st.multiselect(
    "🏊 Équipements spécifiques (choix multiples) :", 
    [
        "Piscine", 
        "Centre-ville", 
        "Parc aquatique / Toboggans", 
        "Spa / Bien-être", 
        "Climatisation", 
        "Vue mer", 
        "Parking", 
        "Petit-déjeuner inclus"
    ],
    placeholder="Choisissez un ou plusieurs équipements",
    key="crit_equip_multi"
)

# --- SÉCURITÉ : Vérification si l'utilisateur a fait au moins un choix ---
aucun_filtre_actif = (
    filtre_pays_crit == "Tous"
    and filtre_ville_crit == "Toutes"
    and filtre_etoiles_crit == "Tous"
    and not filtre_equipements_multi
)

if aucun_filtre_actif:
    st.info(
        "👆 Veuillez sélectionner au moins un critère ci-dessus (Pays, Ville, Standing ou Équipement) pour afficher les hôtels correspondants."
    )
else:
    hotels_filtres_crit = []

    # --- Filtrage combiné (ET strict pour les équipements) ---
    for nom, info in HOTELS_DATA.items():
        if not isinstance(info, dict):
            continue

        pays_hotel = str(info.get("pays", "")).strip().lower()
        ville_hotel = str(info.get("ville", "")).strip().lower()
        etoiles_hotel = str(info.get("etoiles", "")).strip().lower()

        equipements_str = " ".join(info.get("equipements", []))
        texte_complet = (
            f"{nom} {pays_hotel} {ville_hotel} {info.get('description', '')}"
            f" {' '.join(info.get('points_positifs', []))} {equipements_str}"
        ).lower()

        # Filtre Pays (ignoré si "Tous" ou vide)
        if filtre_pays_crit and filtre_pays_crit != "Tous" and filtre_pays_crit.strip().lower() not in pays_hotel:
            continue
            
        # Filtre Ville (ignoré si "Toutes" ou vide)
        if filtre_ville_crit and filtre_ville_crit != "Toutes" and filtre_ville_crit.strip().lower() not in ville_hotel:
            continue
            
        # Filtre Étoiles / Standing (ignoré si "Tous" ou vide)
        if filtre_etoiles_crit and filtre_etoiles_crit != "Tous" and filtre_etoiles_crit.strip().lower() not in etoiles_hotel:
            continue

        if filtre_equipements_multi:
            tous_les_criteres_sont_presents = True
            for eq in filtre_equipements_multi:
                match_cet_equipement = False
                if eq == "Piscine" and any(m in texte_complet for m in ["piscine", "bassin"]):
                    match_cet_equipement = True
                elif eq == "Centre-ville" and any(m in texte_complet for m in ["centre", "habib", "bourguiba", "emplacement"]):
                    match_cet_equipement = True
                elif eq == "Parc aquatique / Toboggans" and any(m in texte_complet for m in ["aquatique", "toboggan"]):
                    match_cet_equipement = True
                elif eq == "Spa / Bien-être" and any(m in texte_complet for m in ["spa", "bien-être", "thalasso"]):
                    match_cet_equipement = True
                elif eq == "Climatisation" and any(m in texte_complet for m in ["climatisation", "climatisé"]):
                    match_cet_equipement = True
                elif eq == "Vue mer" and any(m in texte_complet for m in ["vue mer", "front de mer", "mer", "plage"]):
                    match_cet_equipement = True
                elif eq == "Parking" and any(m in texte_complet for m in ["parking", "stationnement"]):
                    match_cet_equipement = True
                elif eq == "Petit-déjeuner inclus" and any(m in texte_complet for m in ["petit-déjeuner", "petit déjeuner", "inclus"]):
                    match_cet_equipement = True

                if not match_cet_equipement:
                    tous_les_criteres_sont_presents = False
                    break

            if not tous_les_criteres_sont_presents:
                continue

        hotels_filtres_crit.append((nom, info))

    # --- Affichage des résultats des critères ---
    st.markdown("---")
    if not hotels_filtres_crit:
        st.warning("⚠️ Aucun hôtel ne correspond à cette combinaison de critères.")
    else:
        st.success(f"🔍 **{len(hotels_filtres_crit)} hôtel(s) correspondant(s)**")

        for nom, info in hotels_filtres_crit:
            col1, col2 = st.columns([1, 2])
            with col1:
                image_url = info.get("image", "")
                if image_url:
                    st.image(image_url, use_container_width=True)
            with col2:
                st.subheader(nom)
                st.write(
                    f"📍 **{info.get('ville', '')}, {info.get('pays', '')}** | ⭐"
                    f" {info.get('etoiles', 'N/C')}"
                )
                st.write(f"💰 **{info.get('prix_moyen', 'Sur demande')}**")
                points = info.get("points_positifs", [])
                if points:
                    st.markdown(f"**Points forts :** {', '.join(points)}")

                lien_booking = update_booking_aid(info.get("lien_booking", "#"))
                if not lien_booking:
                    lien_booking = "#"
                lien_expedia = info.get("lien_expedia", "#")
                if not lien_expedia:
                    lien_expedia = "#"

                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    st.markdown(
                        f'<a href="{lien_booking}" target="_blank" rel="nofollow sponsored" style="display: flex;'
                        ' justify-content: center; align-items: center; background-color:'
                        ' #003580; text-align: center; padding: 0.38rem 1rem;'
                        ' border-radius: 0.5rem; font-weight: 600; text-decoration:'
                        ' none; height: 38px; box-sizing: border-box; width: 100%;"><span'
                        ' style="color: #ffffff !important;">Réserver sur'
                        ' Booking</span></a>',
                        unsafe_allow_html=True,
                    )
                with col_b2:
                    st.markdown(
                        f'<a href="{lien_expedia}" target="_blank" rel="nofollow sponsored" style="display: flex;'
                        ' justify-content: center; align-items: center; background-color:'
                        ' #FFC107; text-align: center; padding: 0.38rem 1rem;'
                        ' border-radius: 0.5rem; font-weight: 600; text-decoration:'
                        ' none; height: 38px; box-sizing: border-box; width: 100%;"><span'
                        ' style="color: #000000 !important;">Réserver sur'
                        ' Expedia</span></a>',
                        unsafe_allow_html=True,
                    )

            st.markdown("---")

# ==============================================================================
# SECTION EXTÉRIEURE (HORS DE LA BOUCLE DES HÔTELS)
# ==============================================================================
st.subheader("💬 Ce que pensent nos voyageurs")

col_a1, col_a2, col_a3 = st.columns(3)

with col_a1:
    st.markdown(
        """
        <div class="hotel-card" style="background-color: #1C2541 !important;">
            <p style="color: #f59e0b; font-size: 1.1em; margin-bottom: 5px;">⭐⭐⭐⭐⭐</p>
            <p style="font-style: italic; font-size: 0.95em;">"Grâce au comparateur, j'ai trouvé l'hôtel idéal pour mes vacances en un clin d'œil !"</p>
            <div style="display: flex; align-items: center; margin-top: 12px;">
                <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop&crop=faces" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover; margin-right: 10px;">
                <div>
                    <p style="font-weight: bold; font-size: 0.85em; margin: 0;">Marc D.</p>
                    <p style="font-size: 0.75em; color: #94a3b8; margin: 0;">Voyageur solo</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
        
with col_a2:
    st.markdown(
        """
        <div class="hotel-card" style="background-color: #1C2541 !important;">
            <p style="color: #f59e0b; font-size: 1.1em; margin-bottom: 5px;">⭐⭐⭐⭐⭐</p>
            <p style="font-style: italic; font-size: 0.95em;">"Super application, très pratique pour comparer les hôtels rapidement. Je recommande !"</p>
            <div style="display: flex; align-items: center; margin-top: 12px;">
                <img src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=faces" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover; margin-right: 10px;">
                <div>
                    <p style="font-weight: bold; font-size: 0.85em; margin: 0;">Sarah L.</p>
                    <p style="font-size: 0.75em; color: #94a3b8; margin: 0;">Voyage en famille</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )        
with col_a3:
    st.markdown(
        """
        <div class="hotel-card" style="background-color: #1C2541 !important;">
            <p style="color: #f59e0b; font-size: 1.1em; margin-bottom: 5px;">⭐⭐⭐⭐⭐</p>
            <p style="font-style: italic; font-size: 0.95em;">"Le comparateur m'a permis d'économiser pas mal sur mon séjour. Interface fluide et propre."</p>
            <div style="display: flex; align-items: center; margin-top: 12px;">
                <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=faces" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover; margin-right: 10px;">
                <div>
                    <p style="font-weight: bold; font-size: 0.85em; margin: 0;">Karim B.</p>
                    <p style="font-size: 0.75em; color: #94a3b8; margin: 0;">Voyageur régulier</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
st.markdown("---")
st.markdown("<p style='text-align: center; color: white; font-size: 15px; font-weight: bold; margin-bottom: 10px;'>APPROUVÉ PAR LES VOYAGEURS QUI RÉSERVENT SUR</p>", unsafe_allow_html=True)

html_partenaires = """
<div style="text-align: center; margin-bottom: 15px; display: flex; justify-content: center; align-items: center; gap: 30px;">
    <span style="background-color: #003580; color: white; padding: 8px 20px; border-radius: 6px; font-weight: 900; font-size: 18px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">Booking.com</span>
    <a href="https://www.tkqlhce.com/click-101825091-14521545" target="_blank" rel="nofollow sponsored" style="background-color: white; padding: 6px 14px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); display: inline-flex; align-items: center; text-decoration: none;">
        <img src="https://www.awltovhc.com/image-101825091-14521545" alt="Expedia" style="height: 52px; display: block;">
    </a>
</div>
"""
st.markdown(html_partenaires, unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #888; font-size: 11px;'>Comparaison de plus de 1000 hôtels &nbsp;&bull;&nbsp; 10 destinations incontournables &nbsp;&bull;&nbsp; 2 sites de réservation vérifiés</p>", unsafe_allow_html=True)
st.markdown("---")

# ==============================================================================
# PIED DE PAGE ET FORMULAIRE DE FEEDBACK
# ==============================================================================
footer_html = """
<style>
.footer-bg {
    background-color: #1e293b;
    color: #f8fafc;
    padding: 30px;
    border-radius: 10px;
    text-align: center;
    margin-top: 40px;
}
.footer-links {
    margin-bottom: 15px;
}
.footer-links a {
    color: #38bdf8;
    text-decoration: none;
    margin: 0 15px;
    font-weight: 500;
    font-size: 0.95em;
}
.footer-links a:hover {
    text-decoration: underline;
    color: #ffffff;
}
.footer-copy {
    color: #94a3b8;
    font-size: 0.85em;
    margin: 0;
}
</style>

<div class="footer-bg">
    <div class="footer-links">
        <a href="/?page=accueil" target="_self">Accueil</a>
        <a href="/?page=apropos" target="_self">À propos</a>
        <a href="/?page=confidentialite" target="_self">Politique de confidentialité</a>
        <a href="/?page=contact" target="_self">Contact</a>
    </div>
    <p class="footer-copy">© 2026 MyHotelCompare. Tous droits réservés. Propulsé par l'IA.</p>
</div>
"""

st.markdown(footer_html, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<h3 style='text-align: center; color: white;'>💬 Votre avis nous intéresse</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.9em;'>Le site est en cours de construction. Aidez-nous à l'améliorer !</p>", unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
with col_f2:
    formspree_url = "https://formspree.io/f/xaewjazy"
    st.markdown(f"""
        <form action="{formspree_url}" method="POST" style="display: flex; flex-direction: column; gap: 10px;">
            <input type="text" name="nom" placeholder="Votre nom ou prénom (facultatif)" style="padding: 10px; border-radius: 5px; border: 1px solid #ccc; color: #000;">
            <textarea name="message" placeholder="Vos remarques, bugs ou conseils..." rows="4" style="padding: 10px; border-radius: 5px; border: 1px solid #ccc; color: #000;" required></textarea>
            <button type="submit" style="background-color: #10B981; color: white; padding: 10px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">Envoyer mon avis</button>
        </form>
    """, unsafe_allow_html=True)