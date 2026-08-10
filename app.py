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
    if not url: return ""
    clean_url = url.replace("??", "?")
    parsed = urllib.parse.urlparse(clean_url)
    query_params = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    query_params["aid"] = new_aid
    new_query = urllib.parse.urlencode(query_params)
    return urllib.parse.urlunparse(parsed._replace(query=new_query))

# Configuration de la page
st.set_page_config(page_title="HotelCompare", page_icon="images/favicon_io/favicon.ico", layout="wide")

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

    /* Texte des boutons du haut en NOIR */
    .stButton button, .stButton button p, .stButton button span {
        color: #0B132B !important;
        font-weight: 600 !important;
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

# Injection de la balise de vérification Google Search Console
google_tag = '<meta name="google-site-verification" content="UFPNwmAw5bpc..." />'
components.html(google_tag, height=0, width=0)

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
    st.markdown("<h2 style='padding-top: 10px;'>Comparez les hôtels, les compagnies aériennes, les loueurs avec notre IA</h2>", unsafe_allow_html=True)

st.markdown("---")

# --- Boutons de Navigation (Redirection vers les pages multipages) ---
b1, b2, b3, b4 = st.columns(4)
with b1:
    if st.button("🏨 Hôtels", use_container_width=True):
        st.session_state.page = "Comparateur Hôtels"
        st.rerun()
with b2:
    if st.button("✈️ Compagnies Aériennes", use_container_width=True):
        st.switch_page("pages/1_Compagnies_Aeriennes.py")
with b3:
    if st.button("🚗 Loueurs de Véhicules", use_container_width=True):
        st.switch_page("pages/2_Loueurs_Vehicules.py")
with b4:
    if st.button("📖 Blog", use_container_width=True):
        st.switch_page("pages/3_Blog.py")

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
    st.markdown("""
    <style>
        .badge-note {
            background-color: #003580;
            color: white;
            padding: 5px 10px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 1.1em;
        }
        .hotel-card div[data-testid="stImage"] img {
            height: 150px !important;
            object-fit: cover !important;
            width: 100% !important;
            border-radius: 8px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Carrousel ---
    def get_img_as_base64(path):
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""

    img_paths = ["images/image caroussel 2.png", "images/image_afrique.jpg", "images/image_astuce.jpg", "images/image_hotel.jpg", "images/image_tunisie.jpg"]
    imgs_base64 = [get_img_as_base64(p) for p in img_paths]

    carousel_html = f"""
    <div style="width: 100%; height: 280px; position: relative; overflow: hidden; border-radius: 8px; margin-bottom: 20px;">
        <style>
        .slide {{ position: absolute; width: 100%; height: 100%; opacity: 0; animation: fade 15s infinite; object-fit: cover; }}
        @keyframes fade {{ 0% {{ opacity: 0; }} 6% {{ opacity: 1; }} 20% {{ opacity: 1; }} 26% {{ opacity: 0; }} 100% {{ opacity: 0; }} }}
        </style>
        <img class="slide" src="data:image/png;base64,{imgs_base64[0]}" style="animation-delay: 0s;">
        <img class="slide" src="data:image/jpeg;base64,{imgs_base64[1]}" style="animation-delay: 3s;">
        <img class="slide" src="data:image/jpeg;base64,{imgs_base64[2]}" style="animation-delay: 6s;">
        <img class="slide" src="data:image/jpeg;base64,{imgs_base64[3]}" style="animation-delay: 9s;">
        <img class="slide" src="data:image/jpeg;base64,{imgs_base64[4]}" style="animation-delay: 12s;">
    </div>
    """
    st.markdown(carousel_html, unsafe_allow_html=True)

    st.subheader("💡 Comment comparer vos hôtels")
    st.markdown("1. Sélectionnez pays et ville. 2. Choisissez deux hôtels. 3. Cliquez sur Comparer.")
    
    # --- Menus de sélection du Comparateur ---
    pays_disponibles = sorted(list(set(str(d.get("pays", "Autre")).strip() for d in HOTELS_DATA.values() if isinstance(d, dict))))
    c_pays, c_ville, c1, c2, c_btn1, c_btn2 = st.columns([2, 2, 2, 2, 1, 1])
    
    choix_pays = c_pays.selectbox("Pays", [""] + pays_disponibles, key="comp_pays")
    villes_disponibles_comp = sorted(list(set(str(d.get("ville", "Autre")).strip() for d in HOTELS_DATA.values() if isinstance(d, dict) and (not choix_pays or str(d.get("pays", "")).strip() == choix_pays))))
    choix_ville = c_ville.selectbox("Ville", [""] + villes_disponibles_comp, key="comp_ville")
    
    hotels_filtres_comp = [nom for nom, d in HOTELS_DATA.items() if isinstance(d, dict) and (not choix_pays or str(d.get("pays", "")).strip() == choix_pays) and (not choix_ville or str(d.get("ville", "")).strip() == choix_ville)]
    
    choix1 = c1.selectbox("Premier hôtel", [""] + hotels_filtres_comp)
    hotels_restants = [h for h in hotels_filtres_comp if h != choix1]
    choix2 = c2.selectbox("Deuxième hôtel", [""] + hotels_restants)
    
    valider = c_btn1.button("Comparer", type="primary", use_container_width=True)
    if c_btn2.button("Reset"):
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
                    
                    img_src = d.get("image")
                    if img_src and img_src != "...":
                        st.image(img_src, width=350)
                        
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
                    
                    if d.get("pour_qui") and isinstance(d.get("pour_qui"), dict):
                        st.markdown("---")
                        st.info(f"**Verdict :** {d['pour_qui'].get('verdict', '')}")
                        with st.expander("🤔 Pour qui ?"):
                            for cle, val in d['pour_qui'].items():
                                if cle != 'verdict':
                                    st.write(f"**{cle.capitalize()} :** {val}")

                    if d.get("meta_avis"):
                        st.caption(d['meta_avis'])
                    
                    st.write("")
                    
                    tarifs = d.get("tarifs_operateurs", {})
                    if tarifs:
                        st.markdown("<h4 style='color: #1e293b !important;'>🏷️ Comparatif des prix</h4>", unsafe_allow_html=True)
                        tarifs_valides = {k: v for k, v in tarifs.items() if isinstance(v, dict) and "prix" in v}
                        
                        if tarifs_valides:
                            meilleur_operateur = min(tarifs_valides, key=lambda k: tarifs_valides[k]["prix"])
                            
                            for operateur, infos in tarifs_valides.items():
                                prix_actuel = infos["prix"]
                                detail_actuel = infos.get("detail", "Séjour standard")
                                lien_actuel = update_booking_aid(infos.get("lien", "https://www.booking.com/index.fr.html"))
                                
                                col_p1, col_p2, col_p3 = st.columns([3, 2, 1])
                                with col_p1:
                                    if operateur == meilleur_operateur:
                                        st.markdown(f"<span style='color: #1e293b !important; font-weight: bold;'>{operateur}</span> 🟢 <span style='background-color:#34a853; color:white; padding:2px 6px; border-radius:4px; font-size:0.8em;'>Meilleur prix</span>", unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"<span style='color: #1e293b !important; font-weight: bold;'>{operateur}</span>", unsafe_allow_html=True)
                                    st.markdown(f"<span style='color: #64748b !important; font-size: 0.85em;'>{detail_actuel}</span>", unsafe_allow_html=True)
                                with col_p2:
                                    st.markdown(f"<div style='text-align: right; font-weight: bold; font-size: 1.1em; color: #1e293b !important;'>{prix_actuel} €</div>", unsafe_allow_html=True)
                                with col_p3:
                                    st.markdown(f"<div style='text-align: right;'><a href='{lien_actuel}' target='_blank' style='background-color:#003580; color:white; padding:5px 10px; text-decoration:none; border-radius:4px; font-size:0.85em; font-weight:bold; display:inline-block;'>Voir</a></div>", unsafe_allow_html=True)
                                
                                st.markdown("<hr style='margin: 5px 0; border: 0; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
                        else:
                            st.warning("Tarifs opérateurs non disponibles.")
                    else:
                        url_hotel = update_booking_aid(d.get("lien", "https://www.booking.com/index.fr.html"))
                        st.markdown(f'<a href="{url_hotel}" target="_blank" style="text-decoration:none;"><div style="background-color:#003580; color:white; padding:12px; text-align:center; border-radius:6px; font-weight:bold;">Voir les offres</div></a>', unsafe_allow_html=True)

    # ==============================================================================
    # SECTION 2 : RECHERCHE D'HÔTEL PAR CRITÈRES (SÉCURISÉE)
    # ==============================================================================
    st.markdown("---")
    st.subheader("🎯 Recherche d'hôtel par critères")
    st.write("Filtrez précisément selon vos envies ci-dessous 👇")

    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        pays_disponibles_crit = sorted(list(set(str(info.get("pays", "")).strip() for info in HOTELS_DATA.values() if info.get("pays"))))
        filtre_pays_crit = st.selectbox("🌍 Pays :", ["Tous"] + pays_disponibles_crit, key="crit_pays")

    with col_c2:
        if filtre_pays_crit == "Tous":
            villes_disponibles_crit = sorted(list(set(info.get("ville", "") for info in HOTELS_DATA.values() if info.get("ville"))))
        else:
            villes_disponibles_crit = sorted(list(set(info.get("ville", "") for info in HOTELS_DATA.values() if str(info.get("pays", "")).strip() == filtre_pays_crit and info.get("ville"))))
            
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
        key="crit_equip_multi"
    )

    # --- SÉCURITÉ : Vériﬁcation si l'utilisateur a fait au moins un choix ---
    aucun_filtre_actif = (
        filtre_pays_crit == "Tous" and 
        filtre_ville_crit == "Toutes" and 
        filtre_etoiles_crit == "Tous" and 
        not filtre_equipements_multi
    )

    if aucun_filtre_actif:
        st.info("👆 Veuillez sélectionner au moins un critère ci-dessus (Pays, Ville, Standing ou Équipement) pour afficher les hôtels correspondants.")
    else:
        # --- Filtrage combiné ---
        hotels_filtres_crit = []

        for nom, info in HOTELS_DATA.items():
            pays_hotel = str(info.get("pays", ""))
            ville_hotel = str(info.get("ville", ""))
            etoiles_hotel = str(info.get("etoiles", ""))
            
            equipements_str = " ".join(info.get('equipements', []))
            texte_complet = f"{nom} {pays_hotel} {ville_hotel} {info.get('description', '')} {' '.join(info.get('points_positifs', []))} {equipements_str}".lower()
            
            # Filtre Pays
            if filtre_pays_crit != "Tous" and filtre_pays_crit.lower() not in pays_hotel.lower():
                continue
                
            # Filtre Ville
            if filtre_ville_crit != "Toutes" and filtre_ville_crit.lower() not in ville_hotel.lower():
                continue
                
            # Filtre Étoiles
            if filtre_etoiles_crit != "Tous" and filtre_etoiles_crit.lower() not in etoiles_hotel.lower():
                continue
                
            # Filtres Équipements
            if filtre_equipements_multi:
                match_un_equipement = False
                for eq in filtre_equipements_multi:
                    if eq == "Piscine" and any(m in texte_complet for m in ["piscine", "bassin"]):
                        match_un_equipement = True
                    elif eq == "Centre-ville" and any(m in texte_complet for m in ["centre", "habib", "bourguiba", "emplacement"]):
                        match_un_equipement = True
                    elif eq == "Parc aquatique / Toboggans" and any(m in texte_complet for m in ["aquatique", "toboggan"]):
                        match_un_equipement = True
                    elif eq == "Spa / Bien-être" and any(m in texte_complet for m in ["spa", "bien-être", "thalasso"]):
                        match_un_equipement = True
                    elif eq == "Climatisation" and any(m in texte_complet for m in ["climatisation", "climatisé"]):
                        match_un_equipement = True
                    elif eq == "Vue mer" and any(m in texte_complet for m in ["vue mer", "front de mer", "mer", "plage"]):
                        match_un_equipement = True
                    elif eq == "Parking" and any(m in texte_complet for m in ["parking", "stationnement"]):
                        match_un_equipement = True
                    elif eq == "Petit-déjeuner inclus" and any(m in texte_complet for m in ["petit-déjeuner", "petit déjeuner", "inclus"]):
                        match_un_equipement = True
                
                if not match_un_equipement:
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
                    st.write(f"📍 **{info.get('ville', '')}, {info.get('pays', '')}** | ⭐ {info.get('etoiles', 'N/C')}")
                    st.write(f"💰 **{info.get('prix_moyen', 'Sur demande')}**")
                    points = info.get('points_positifs', [])
                    if points:
                        st.markdown(f"**Points forts :** {', '.join(points)}")
                    
                    lien = update_booking_aid(info.get('lien', '#'))
                    st.link_button("Réserver sur Booking", lien)
                    
                st.markdown("---")

    # ==============================================================================
    # SECTION 3 : AVIS CLIENTS
    # ==============================================================================
    st.subheader("💬 Ce que pensent nos voyageurs")
    
    col_a1, col_a2, col_a3 = st.columns(3)
    
    with col_a1:
        st.markdown(
            """
            <div class="hotel-card" style="background-color: #1C2541 !important;">
                <p style="color: #f59e0b; font-size: 1.1em; margin-bottom: 5px;">⭐⭐⭐⭐⭐</p>
                <p style="font-style: italic; font-size: 0.95em;">"Grâce au comparateur, j'ai trouvé l'hôtel idéal à Djerba pour notre groupe d'amis au meilleur prix. Super interface !"</p>
                <div style="display: flex; align-items: center; margin-top: 12px;">
                    <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop&crop=faces" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover; margin-right: 10px;">
                    <div>
                        <p style="font-weight: bold; font-size: 0.85em; margin: 0;">Thomas M.</p>
                        <p style="font-size: 0.75em; color: #94a3b8; margin: 0;">Séjour à Djerba</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
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

    # --- BANNIÈRE PARTENAIRE BOOKING SOUS LES AVIS ---
    st.markdown("""
    <div style="text-align: center; padding: 20px; background-color: #1C2541; border: 1px solid #3A506B; border-radius: 10px; margin-top: 20px;">
        <p style="color: #94a3b8; font-size: 14px; margin-bottom: 8px;">En partenariat officiel avec</p>
        <a href="https://www.booking.com" target="_blank" style="color: #38bdf8; font-size: 18px; font-weight: bold; text-decoration: none;">
            Booking.com <span style="font-size: 0.8em;">🔗</span>
        </a>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# PIED DE PAGE SOMBRE ET HARMONIEUX
# ==============================================================================
st.markdown("---")

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