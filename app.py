import streamlit as st
import os
import json
import re
import streamlit.components.v1 as components
import urllib.parse
import base64
import apropos
import confidentialite
import contact

# 1. Configuration globale de la page (Doit être la première commande Streamlit)
st.set_page_config(
    page_title="MyHotelCompare - Comparateur d'hôtels",
    page_icon="logo_4.png",  # Remplace "🏨" par le fichier de votre logo
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# --- FONCTION DE MISE À JOUR DES LIENS ---
def update_booking_aid(url, new_aid="8012379"):
    if not url:
        return ""
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
 
# --- FONCTION DE SLUGIFICATION ---
def slugify(texte):
    texte = texte.lower().strip()
    texte = re.sub(r'[^a-z0-9]+', '-', texte)
    return texte.strip('-')

# Injection propre de la méta description et Open Graph pour Google
st.markdown("""
    <script>
        function setMetaTag(name, content) {
            let element = document.querySelector(`meta[name='${name}']`) || document.querySelector(`meta[property='${name}']`);
            if (!element) {
                element = document.createElement('meta');
                if (name.startsWith('og:')) {
                    element.setAttribute('property', name);
                } else {
                    element.setAttribute('name', name);
                }
                document.head.appendChild(element);
            }
            element.setAttribute('content', content);
        }
        
        setMetaTag('description', 'Comparez les meilleurs hôtels, tarifs et destinations sur MyHotelCompare. Trouvez votre séjour idéal au meilleur prix.');
        setMetaTag('og:title', 'HotelCompare - Comparateur d’hôtels');
        setMetaTag('og:description', 'Trouve et compare les meilleures offres d’hôtels facilement.');
        setMetaTag('og:image', 'https://myhotelcompare.com/media/c139095b96abe4e5e4fc4ea931714e10.png');
        setMetaTag('og:url', 'https://myhotelcompare.com/');
        setMetaTag('og:type', 'website');
    </script>
""", unsafe_allow_html=True)
 
# Le style CSS global
st.markdown("""
    <style>
    header, [data-testid="stHeader"], [data-testid="stDecoration"], .stApp > header {
        display: none !important;
        height: 0px !important;
    }
    [data-testid="stSidebar"] {
        display: none !important;
    }
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
    p, span, label, h1, h2, h3, h4, h5, h6, 
    .stMarkdown, div[data-baseweb="select"] span {
        color: #FFFFFF !important;
    }
    div.stMarkdown {
        margin-bottom: -10px !important;
    }
    .stButton button, .stButton button p, .stButton button span {
        color: #0B132B !important;
        font-weight: 600 !important;
    }
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
    .hotel-card { 
        background-color: #1C2541 !important; 
        border: 1px solid #3A506B;
        border-radius: 12px;
        padding: 20px;
        color: #FFFFFF !important;
    }
    div[data-testid="column"] div.stMarkdown p, 
    div[data-testid="column"] div.stMarkdown span {
        color: #0B132B !important;
    }
    .badge-note {
        background-color: #10B981;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)
 
# Vérification Google Search Console & Canonical & Analytics
google_verification_content = "UFPNwmAw5bpc..."
google_tag_script = f"""
<script>
    const parentHead = window.parent.document.head;
    if (!parentHead.querySelector('meta[name="google-site-verification"]')) {{
        const metaTag = document.createElement('meta');
        metaTag.name = 'google-site-verification';
        metaTag.content = '{google_verification_content}';
        parentHead.appendChild(metaTag);
    }}
</script>
"""
components.html(google_tag_script, height=0, width=0)

hotel_param = st.query_params.get("hotel", None)
canonical_url = f"https://www.myhotelcompare.com/?hotel={hotel_param}" if hotel_param else "https://www.myhotelcompare.com/"
canonical_script = f"""
<script>
    const parentHead = window.parent.document.head;
    const existingCanonical = parentHead.querySelector('link[rel="canonical"]');
    if (existingCanonical) {{ existingCanonical.remove(); }}
    const linkTag = document.createElement('link');
    linkTag.rel = 'canonical';
    linkTag.href = '{canonical_url}';
    parentHead.appendChild(linkTag);
</script>
"""
components.html(canonical_script, height=0, width=0)

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

st.markdown('<script src="https://www.anrdoezrs.net/am/10182501/include/allCJ/impressions/page/am.js"></script>', unsafe_allow_html=True)
 
# --- GESTION DE LA NAVIGATION PAR L'URL ET LA SESSION ---
query_params = st.query_params
page_url = query_params.get("page", "accueil")

if page_url == "accueil":
    st.session_state.page = "Accueil"
elif page_url == "hotels":
    st.session_state.page = "Comparateur Hôtels"
elif page_url == "apropos":
    st.session_state.page = "À propos"
elif page_url == "confidentialite":
    st.session_state.page = "Politique de confidentialité"
elif page_url == "contact":
    st.session_state.page = "Contact"

if 'page' not in st.session_state:
    st.session_state.page = "Accueil"
 
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
 
# --- PAGE DÉDIÉE PAR HÔTEL ---
slug_vers_nom = {slugify(nom): nom for nom in HOTELS_DATA.keys()}
if hotel_param and hotel_param in slug_vers_nom:
    nom_hotel = slug_vers_nom[hotel_param]
    d = HOTELS_DATA[nom_hotel]
    st.markdown('<a href="/" target="_self">← Retour à l\'accueil</a>', unsafe_allow_html=True)
    st.title(nom_hotel)
    img_src = d.get("image")
    if img_src:
        st.image(img_src, use_container_width=True)
    st.write(f"📍 **{d.get('ville','')}, {d.get('pays','')}** | ⭐ {d.get('etoiles','N/C')}")
    st.write(f"💰 **{d.get('prix_moyen','Sur demande')}**")
    desc = d.get("description_ia") or d.get("description")
    if desc:
        st.write(f"**✨ Description :** {desc}")
    if d.get("equipements"):
        with st.expander("🛠️ Équipements"):
            st.write(", ".join(d["equipements"]))
    if d.get("points_positifs"):
        with st.expander("✅ Points Positifs"):
            for p in d["points_positifs"]:
                st.write(f"• {p}")
    if d.get("points_negatifs"):
        with st.expander("⚠️ Points Négatifs"):
            for n in d["points_negatifs"]:
                st.write(f"• {n}")
    if d.get("Nomad, vous en dit plus"):
        st.success(f"🗣️ **Nomad, vous en dit plus :** {d['Nomad, vous en dit plus']}")

    lien_booking_detail = update_booking_aid(d.get("lien_booking", "#"))
    lien_expedia_detail = d.get("lien_expedia", "#")
    cb1, cb2 = st.columns(2)
    with cb1:
        st.markdown(f'<a href="{lien_booking_detail}" target="_blank" rel="nofollow sponsored">Réserver sur Booking</a>', unsafe_allow_html=True)
    with cb2:
        st.markdown(f'<a href="{lien_expedia_detail}" target="_blank" rel="nofollow sponsored">Réserver sur Expedia</a>', unsafe_allow_html=True)
    st.stop()
 
# --- En-tête Global ---
col_logo, col_titre = st.columns([1, 8])
with col_logo:
    if os.path.exists("logo_4.png"):
        st.image("logo_4.png", width=90)
with col_titre:
    st.markdown("<h1 style='text-align: center;'>Comparateur intelligent d'hôtels</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.2em;'><b>Nomad</b> : L'IA qui analyse les avis pour dénicher votre hôtel idéal.</p>", unsafe_allow_html=True)
 
st.markdown("---")
 
# --- Boutons de Navigation avec mise à jour propre de l'URL ---
b1, b2, b3, b4, b5 = st.columns(5)
 
with b1:
    if st.button("Accueil", icon=":material/home:", use_container_width=True):
        st.query_params["page"] = "accueil"
        st.session_state.page = "Accueil"
        st.rerun()
with b2:
    if st.button("Hôtels", icon=":material/hotel:", use_container_width=True):
        st.query_params["page"] = "hotels"
        st.session_state.page = "Comparateur Hôtels"
        st.rerun()
with b3:
    if st.button("Compagnies Aériennes", icon=":material/flight:", use_container_width=True):
        st.switch_page("pages/1_Compagnies_Aeriennes.py")
with b4:
    if st.button("Location de Véhicules", icon=":material/directions_car:", use_container_width=True):
        st.switch_page("pages/2_Loueurs_Vehicules.py")
with b5:
    if st.button("Blog", icon=":material/article:", use_container_width=True):
        st.switch_page("pages/4_Blog.py")
 
st.markdown("---")
 
# ==============================================================================
# GESTION DES PAGES ET DE L'ACCUEIL
# ==============================================================================
 
if st.session_state.page == "À propos":
    apropos.afficher_page()
 
elif st.session_state.page == "Politique de confidentialité":
    confidentialite.afficher_page()
 
elif st.session_state.page == "Contact":
    contact.afficher_page()

# 1. PAGE D'ACCUEIL
elif st.session_state.page == "Accueil":
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
                            if promo.get("image"):
                                st.markdown(f'<img src="{promo["image"]}" style="width: 100%; height: 160px; object-fit: cover; border-radius: 6px; margin-bottom: 8px;">', unsafe_allow_html=True)
                            st.markdown(f"**{promo.get('titre', '')}**")
                            ville = promo.get("ville", "")
                            pays = promo.get("pays", "")
                            if ville or pays:
                                st.markdown(f"<p style='color: #94a3b8; font-size: 0.85em; margin-top: -8px; margin-bottom: 6px;'>📍 {ville}{', ' if ville and pays else ''}{pays}</p>", unsafe_allow_html=True)
                            st.write(promo.get("description", ""))
                except Exception as e:
                    print(f"Erreur chargement promo : {e}")

    st.markdown("---")
    st.markdown("<h2 style='text-align: center;'>Pourquoi choisir MyHotelCompare ?</h2>", unsafe_allow_html=True)
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        st.info("🤖 **IA Nomad**\n\nAnalyse automatique des vrais avis clients pour éviter les pièges.")
    with col_a2:
        st.info("🎯 **Sur-Mesure**\n\nTrouvez l'hôtel idéal selon vos critères (parc aquatique, spa, plage privée).")
    with col_a3:
        st.info("💼 **Zéro Stress**\n\nMaîtrisez votre budget et profitez d'un séjour en toute sérénité.")

    st.write("")
    c_btn_c1, c_btn_c2, c_btn_c3 = st.columns([1, 2, 1])
    with c_btn_c2:
        if st.button("🚀 Accéder au comparateur d'hôtels", type="primary", use_container_width=True):
            st.query_params["page"] = "hotels"
            st.session_state.page = "Comparateur Hôtels"
            st.rerun()

    # --- FORMULAIRE DE FEEDBACK (Formspree) ---
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

# 2. PAGE COMPARATEUR HÔTELS
else:
    st.subheader("💡 Comment comparer vos hôtels")
    st.markdown(
        "1. Sélectionnez pays et ville. 2. Choisissez deux hôtels. 3. Cliquez sur Comparer."
    )
    
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
                            <a href='{lien_booking}' target='_blank' rel='nofollow sponsored' 
                            style='display: block; background-color: #003580; color: white; padding: 12px 10px; text-align: center; text-decoration: none; border-radius: 6px; font-weight: bold; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                                Réserver sur Booking<br><span style='font-size: 13px; font-weight: normal; opacity: 0.9;'>À partir de {prix_affiche}</span>
                            </a>
                        """, unsafe_allow_html=True)
                        
                        lien_expedia = d.get("lien_expedia", "https://www.anrdoezrs.net/click-8012379-13854902?url=https://www.expedia.fr/")
                        st.markdown(f"""
                            <a href='{lien_expedia}' target='_blank' rel='nofollow sponsored' 
                            style='display: block; background-color: #ffcc00; color: #000000; padding: 12px 10px; text-align: center; text-decoration: none; border-radius: 6px; font-weight: bold; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                                Réserver sur Expedia<br><span style='font-size: 13px; font-weight: normal; opacity: 0.8;'>À partir de {prix_affiche}</span>
                            </a>
                        """, unsafe_allow_html=True)

                        lieu_recherche = f"{nom}, {ville_hotel}, {pays_hotel}"
                        lieu_encode = urllib.parse.quote(lieu_recherche)
                        map_html = f"""
                        <iframe width="100%" height="180" style="border:0; border-radius: 8px; margin-top: 10px;" loading="lazy" src="https://maps.google.com/maps?q={lieu_encode}&t=&z=13&ie=UTF8&iwloc=&output=embed"></iframe>
                        """
                        components.html(map_html, height=190)

                    # Partie basse intégrée à la carte
                    st.write("---")
                    desc_finale = d.get("description_ia") or d.get("description")
                    if desc_finale:
                        st.write(f"**✨ Description :** {desc_finale}")
                    
                    if d.get("equipements"):
                        with st.expander("🛠️ Équipements"):
                            st.write(", ".join(d['equipements']))

                    if d.get("points_positifs"):
                        with st.expander("✅ Points Positifs"):
                            for p in d.get("points_positifs"): 
                                st.write(f"• {p}")
                                
                    if d.get("points_negatifs"):
                        with st.expander("⚠️ Points Négatifs"):
                            for n in d.get("points_negatifs"): 
                                st.write(f"• {n}")
                    
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

    # Section multicritères
    st.markdown("---")
    st.subheader("🎯 Recherche d'hôtel par critères")
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

    filtre_equipements_multi = st.multiselect(
        "🏊 Équipements spécifiques :", 
        ["Piscine", "Centre-ville", "Parc aquatique / Toboggans", "Spa / Bien-être", "Climatisation", "Vue mer", "Parking", "Petit-déjeuner inclus"],
        key="crit_equip_multi"
    )

    aucun_filtre_actif = (filtre_pays_crit == "Tous" and filtre_ville_crit == "Toutes" and filtre_etoiles_crit == "Tous" and not filtre_equipements_multi)
    
    if aucun_filtre_actif:
        st.info("👆 Veuillez sélectionner au moins un critère ci-dessus pour afficher les hôtels correspondants.")
    else:
        hotels_filtres_crit = []
        for nom, info in HOTELS_DATA.items():
            if not isinstance(info, dict): continue
            pays_hotel = str(info.get("pays", "")).strip().lower()
            ville_hotel = str(info.get("ville", "")).strip().lower()
            etoiles_hotel = str(info.get("etoiles", "")).strip().lower()
            equipements_str = " ".join(info.get("equipements", []))
            texte_complet = f"{nom} {pays_hotel} {ville_hotel} {info.get('description', '')} {equipements_str}".lower()

            if filtre_pays_crit and filtre_pays_crit != "Tous" and filtre_pays_crit.strip().lower() not in pays_hotel: continue
            if filtre_ville_crit and filtre_ville_crit != "Toutes" and filtre_ville_crit.strip().lower() not in ville_hotel: continue
            if filtre_etoiles_crit and filtre_etoiles_crit != "Tous" and filtre_etoiles_crit.strip().lower() not in etoiles_hotel: continue

            if filtre_equipements_multi:
                tous_les_criteres_sont_presents = True
                for eq in filtre_equipements_multi:
                    match_cet_equipement = False
                    if eq == "Piscine" and any(m in texte_complet for m in ["piscine", "bassin"]): match_cet_equipement = True
                    elif eq == "Parc aquatique / Toboggans" and any(m in texte_complet for m in ["aquatique", "toboggan"]): match_cet_equipement = True
                    elif eq == "Spa / Bien-être" and any(m in texte_complet for m in ["spa", "bien-être", "thalasso"]): match_cet_equipement = True
                    elif eq == "Vue mer" and any(m in texte_complet for m in ["vue mer", "front de mer", "mer", "plage"]): match_cet_equipement = True
                    elif eq == "Parking" and any(m in texte_complet for m in ["parking", "stationnement"]): match_cet_equipement = True
                    elif eq == "Petit-déjeuner inclus" and any(m in texte_complet for m in ["petit-déjeuner", "petit déjeuner", "inclus"]): match_cet_equipement = True
                    else: match_cet_equipement = True
                    if not match_cet_equipement:
                        tous_les_criteres_sont_presents = False
                        break
                if not tous_les_criteres_sont_presents: continue
            hotels_filtres_crit.append((nom, info))

        st.markdown("---")
        if not hotels_filtres_crit:
            st.warning("⚠️ Aucun hôtel ne correspond à cette combinaison de critères.")
        else:
            st.success(f"🔍 **{len(hotels_filtres_crit)} hôtel(s) correspondant(s)**")
            for nom, info in hotels_filtres_crit:
                col1, col2 = st.columns([1, 2])
                with col1:
                    if info.get("image"): st.image(info.get("image"), use_container_width=True)
                with col2:
                    slug_hotel = slugify(nom)
                    st.markdown(f'<a href="/?hotel={slug_hotel}" target="_self" style="color:#38bdf8;">🔗 Voir la fiche complète</a>', unsafe_allow_html=True)
                    st.subheader(nom)
                    st.write(f"📍 **{info.get('ville', '')}, {info.get('pays', '')}** | ⭐ {info.get('etoiles', 'N/C')}")
                    st.write(f"💰 **{info.get('prix_moyen', 'Sur demande')}**")

# --- Footer ---
st.markdown("---")
footer_html = """
<style>
.footer-bg { background-color: #1e293b; color: #f8fafc; padding: 30px; border-radius: 10px; text-align: center; margin-top: 40px; }
.footer-links a { color: #38bdf8; text-decoration: none; margin: 0 15px; font-weight: 500; font-size: 0.95em; }
.footer-links a:hover { text-decoration: underline; color: #ffffff; }
.footer-copy { color: #94a3b8; font-size: 0.85em; margin: 0; }
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

import os
import json
import urllib.parse

def generate_sitemap():
    # Force le chemin absolu à la racine du projet
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    sitemap_path = os.path.join(base_dir, "sitemap.xml")
    
    base_url = "https://www.myhotelcompare.com"
    urls = [
        f"{base_url}/",
        f"{base_url}/contact",
        f"{base_url}/apropos",
        f"{base_url}/confidentialite",
        f"{base_url}/Compagnies_Aeriennes",
        f"{base_url}/Loueurs_Vehicules"
    ]
    
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(data_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            for hotel_name in data.keys():
                                slug = urllib.parse.quote(hotel_name.strip().replace(" ", "-").replace("&", "et"))
                                urls.append(f"{base_url}/{slug}")
                        elif isinstance(data, list):
                            for item in data:
                                slug = item.get("slug") or item.get("id")
                                if slug:
                                    urls.append(f"{base_url}/{slug}")
                except Exception as e:
                    print(f"Erreur sur {filename}: {e}")

    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in sorted(set(urls)):
        xml_content += f"    <url>\n        <loc>{url}</loc>\n        <changefreq>weekly</changefreq>\n        <priority>0.8</priority>\n    </url>\n"
    xml_content += '</urlset>'

    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    
    print(f"SUCCÈS : Sitemap généré à la racine avec {len(urls)} URLs !")

# Exécution immédiate
generate_sitemap()