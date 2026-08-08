import streamlit as st
import os
import json
from data.airlines_data import AIRLINES_DATA
import streamlit.components.v1 as components
import urllib.parse
import base64
import apropos
import confidentialite
import contact

# Configuration de la page
st.set_page_config(page_title="HotelCompare", page_icon="images/favicon_io/favicon.ico", layout="wide")

# Injection de la balise de vérification Google Search Console
google_tag = '<meta name="google-site-verification" content="UFPNwmAw5bpc..." />'
components.html(google_tag, height=0, width=0)

# --- AJOUT DU SCRIPT DE TRACKING CJ AFFILIATE ---
st.markdown(
    '<script src="https://www.anrdoezrs.net/am/10182501/include/allCJ/impressions/page/am.js"></script>',
    unsafe_allow_html=True
)

# --- Style CSS Global pour le mode sombre ---
st.markdown("""
    <style>
    /* 1. Fond général sombre */
    .stApp { 
        background-color: #0B132B !important; 
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] { 
        min-width: 150px; 
        max-width: 150px; 
    }
    .block-container { 
        padding-top: 1rem !important; 
    }
    iframe { 
        width: 100% !important; 
    }
    
    /* 2. Textes généraux et libellés en blanc */
    p, span, label, h1, h2, h3, h4, h5, h6, 
    .stMarkdown, div[data-baseweb="select"] span {
        color: #FFFFFF !important;
    }

    /* 3. Texte des boutons du haut en NOIR */
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

# Gestion de l'affichage des pages du menu
if st.session_state.page == "À propos":
    apropos.afficher_page()

elif st.session_state.page == "Politique de confidentialité":
    confidentialite.afficher_page()

elif st.session_state.page == "Contact":
    contact.afficher_page()

else:
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

    # --- Boutons de Navigation ---
    b1, b2, b3, b4 = st.columns(4)
    if b1.button("🏨 Hôtels", use_container_width=True):
        st.session_state.page = "Comparateur Hôtels"
        st.rerun()
    if b2.button("✈️ Compagnies Aériennes", use_container_width=True):
        st.session_state.page = "Compagnies Aériennes"
        st.rerun()
    if b3.button("🚗 Loueurs de Véhicules", use_container_width=True):
        st.session_state.page = "Loueurs Véhicules"
        st.rerun()
    if b4.button("📖 Blog", use_container_width=True):
        st.session_state.page = "Blog"
        st.rerun()

    st.markdown("---")

    # ==============================================================================
    # SECTION 1 : COMPARATEUR D'HÔTELS
    # ==============================================================================
    if st.session_state.page == "Comparateur Hôtels":
        
        # --- Style CSS pour les cartes et images ---
        st.markdown("""
        <style>
            .hotel-card {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                margin-bottom: 20px;
            }
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
        
        # --- Menus de sélection ---
        pays_disponibles = sorted(list(set(str(d.get("pays", "Autre")).strip() for d in HOTELS_DATA.values() if isinstance(d, dict))))
        c_pays, c_ville, c1, c2, c_btn1, c_btn2 = st.columns([2, 2, 2, 2, 1, 1])
        
        choix_pays = c_pays.selectbox("Pays", [""] + pays_disponibles)
        villes_disponibles = sorted(list(set(str(d.get("ville", "Autre")).strip() for d in HOTELS_DATA.values() if isinstance(d, dict) and (not choix_pays or str(d.get("pays", "")).strip() == choix_pays))))
        choix_ville = c_ville.selectbox("Ville", [""] + villes_disponibles)
        
        hotels_filtres = [nom for nom, d in HOTELS_DATA.items() if isinstance(d, dict) and (not choix_pays or str(d.get("pays", "")).strip() == choix_pays) and (not choix_ville or str(d.get("ville", "")).strip() == choix_ville)]
        
        choix1 = c1.selectbox("Premier hôtel", [""] + hotels_filtres)
        hotels_restants = [h for h in hotels_filtres if h != choix1]
        choix2 = c2.selectbox("Deuxième hôtel", [""] + hotels_restants)
        
        valider = c_btn1.button("Comparer", type="primary", use_container_width=True)
        if c_btn2.button("Reset"): st.rerun()

        # --- Affichage des résultats ---
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
                        
                        # Image
                        img_src = d.get("image")
                        if img_src and img_src != "...":
                            st.image(img_src, width=350)
                            
                        # Nom de l'hôtel
                        st.subheader(nom)
                        
                        # Ville et pays sous le nom de l'hôtel
                        ville_hotel = d.get("ville", "")
                        pays_hotel = d.get("pays", "")
                        if ville_hotel or pays_hotel:
                            st.markdown(f"<p style='color: #94a3b8; font-size: 0.9em; margin-top: -10px; margin-bottom: 10px;'>📍 {ville_hotel}, {pays_hotel}</p>", unsafe_allow_html=True)
                        
                        # Note
                        if d.get("avis"):
                            st.markdown(f"Note : <span class='badge-note'>{d['avis']}</span>", unsafe_allow_html=True)
                        
                        st.write("")
                        if d.get("etoiles"): st.write(f"⭐ **{d['etoiles']}**")
                        if d.get("prix_moyen"): st.write(f"💰 {d['prix_moyen']}")
                        
                        st.write("---")
                        
                        # Description
                        if d.get("description"):
                            st.write(f"**Description :** {d['description']}")
                        
                        # Équipements
                        if d.get("equipements"):
                            with st.expander("🛠️ Équipements"):
                                st.write(", ".join(d['equipements']))

                        # Points Positifs / Négatifs
                        if d.get("points_positifs"):
                            with st.expander("✅ Points Positifs"):
                                for p in d.get("points_positifs"): st.write(f"• {p}")
                        if d.get("points_negatifs"):
                            with st.expander("⚠️ Points Négatifs"):
                                for n in d.get("points_negatifs"): st.write(f"• {n}")
                        
                        # Verdict (pour_qui)
                        if d.get("pour_qui") and isinstance(d.get("pour_qui"), dict):
                            st.markdown("---")
                            st.info(f"**Verdict :** {d['pour_qui'].get('verdict', '')}")
                            with st.expander("🤔 Pour qui ?"):
                                for cle, val in d['pour_qui'].items():
                                    if cle != 'verdict':
                                        st.write(f"**{cle.capitalize()} :** {val}")

                        # Meta Avis
                        if d.get("meta_avis"):
                            st.caption(d['meta_avis'])
                        
                        st.write("")
                        
                        # --- COMPARATIF DES PRIX PAR TOUR-OPÉRATEUR ---
                        tarifs = d.get("tarifs_operateurs", {})
                        if tarifs:
                            st.markdown("<h4 style='color: #1e293b !important;'>🏷️ Comparatif des prix</h4>", unsafe_allow_html=True)
                            tarifs_valides = {k: v for k, v in tarifs.items() if isinstance(v, dict) and "prix" in v}
                            
                            if tarifs_valides:
                                meilleur_operateur = min(tarifs_valides, key=lambda k: tarifs_valides[k]["prix"])
                                
                                for operateur, infos in tarifs_valides.items():
                                    prix_actuel = infos["prix"]
                                    detail_actuel = infos.get("detail", "Séjour standard")
                                    lien_actuel = infos.get("lien", "https://www.booking.com/index.fr.html")
                                    
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
                            url_hotel = d.get("lien", "https://www.booking.com/index.fr.html")
                            st.markdown(f'<a href="{url_hotel}" target="_blank" style="text-decoration:none;"><div style="background-color:#003580; color:white; padding:12px; text-align:center; border-radius:6px; font-weight:bold;">Voir les offres</div></a>', unsafe_allow_html=True)

        # ==============================================================================
        # SECTION 5 : AVIS CLIENTS
        # ==============================================================================
        st.markdown("---")
        st.subheader("💬 Ce que pensent nos voyageurs")
        
        col_a1, col_a2, col_a3 = st.columns(3)
        
        with col_a1:
            st.markdown(
            """
            <div class="review-card">
                <p style="color: #f59e0b; font-size: 1.1em; margin-bottom: 5px;">⭐⭐⭐⭐⭐</p>
                <p style="font-style: italic; font-size: 0.95em;">"Grâce au comparateur, j'ai trouvé l'hôtel idéal à Djerba pour notre groupe d'amis au meilleur prix. Super interface !"</p>
                <div style="display: flex; align-items: center; margin-top: 12px;">
                    <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop&crop=faces" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover; margin-right: 10px;">
                    <div>
                        <p style="font-weight: bold; font-size: 0.85em; margin: 0;">Thomas M.</p>
                        <p style="font-size: 0.75em; color: #555555; margin: 0;">Séjour à Djerba</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
            
        with col_a2:
            st.markdown(
            """
            <div class="review-card">
                <p style="color: #f59e0b; font-size: 1.1em; margin-bottom: 5px;">⭐⭐⭐⭐⭐</p>
                <p style="font-style: italic; font-size: 0.95em;">"Super application, très pratique pour comparer les hôtels rapidement. Je recommande !"</p>
                <div style="display: flex; align-items: center; margin-top: 12px;">
                    <img src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=faces" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover; margin-right: 10px;">
                    <div>
                        <p style="font-weight: bold; font-size: 0.85em; margin: 0;">Sarah L.</p>
                        <p style="font-size: 0.75em; color: #555555; margin: 0;">Voyage en famille</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )           
        with col_a3:
            st.markdown(
            """
            <div class="review-card">
                <p style="color: #f59e0b; font-size: 1.1em; margin-bottom: 5px;">⭐⭐⭐⭐⭐</p>
                <p style="font-style: italic; font-size: 0.95em;">"Le comparateur m'a permis d'économiser pas mal sur mon séjour. Interface fluide et propre."</p>
                <div style="display: flex; align-items: center; margin-top: 12px;">
                    <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=faces" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover; margin-right: 10px;">
                    <div>
                        <p style="font-weight: bold; font-size: 0.85em; margin: 0;">Karim B.</p>
                        <p style="font-size: 0.75em; color: #555555; margin: 0;">Voyageur régulier</p>
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
    # SECTION 2 : COMPAGNIES AÉRIENNES
    # ==============================================================================
    elif st.session_state.page == "Compagnies Aériennes":
        st.title("✈️ Comparateur & Avis - Compagnies Aériennes")
        st.write("Sélectionnez ou recherchez une compagnie aérienne pour consulter son résumé, ses avis et réserver au meilleur prix.")
        
        st.markdown("---")
        
        noms_compagnies = sorted(AIRLINES_DATA.keys())
        
        col_s1, col_s2 = st.columns([2, 1])
        choix_cie = col_s1.selectbox("Choisissez une compagnie aérienne", noms_compagnies)
        
        if choix_cie:
            infos = AIRLINES_DATA[choix_cie]
            st.markdown("---")
            
            col_c1, col_c2 = st.columns([1, 4])
            with col_c1:
                try:
                    st.image("images/airbus_vol.jpg", width=120)
                except:
                    st.write("✈️")
            with col_c2:
                st.subheader(choix_cie)
                st.markdown(f"**Catégorie :** {infos['categorie']} | **Alliance :** {infos['alliance']}")
                st.markdown(f"**Note globale :** ⭐ {infos['note']}")
            
            st.write(f"**Résumé :** {infos['resume']}")
            st.write(f"**Politique bagages :** {infos['bagages']}")
            st.write(f"**Flotte :** {infos.get('flotte', 'Flotte moderne et variée')}")
            
            st.markdown("### Principales liaisons :")
            for liaison in infos.get("liaisons", []):
                st.write(f"- ✈️ {liaison}")
                
            with st.expander("📖 Histoire de la compagnie"):
                st.write(infos['histoire'])
                
            with st.expander("🛡️ Sécurité et normes"):
                st.write(infos.get('securite', 'Normes de sécurité internationales respectées.'))
                
            if infos.get("points_positifs"):
                with st.expander("✅ Points Positifs"):
                    for p in infos.get("points_positifs"):
                        st.write(f"- {p}")
                    
            if infos.get("points_negatifs"):
                with st.expander("⚠️ Points Négatifs"):
                    for n in infos.get("points_negatifs"):
                        st.write(f"- {n}")

            if infos.get("pour_qui"):
                st.info(f"**Verdict :** {infos.get('pour_qui')}")

            st.markdown(
                '<a href="https://www.anrdoezrs.net/click-10182501-17053227" target="_blank" style="display: block; width: 100%; background-color: #0066cc; color: white; padding: 12px 20px; text-align: center; text-decoration: none; font-size: 16px; font-weight: bold; border-radius: 6px; box-shadow: 0px 2px 5px rgba(0,0,0,0.2);">Réserver le vol</a>',
                unsafe_allow_html=True
            )

    # ==============================================================================
    # SECTION 3 : LOUEURS DE VÉHICULES
    # ==============================================================================
    elif st.session_state.page == "Loueurs Véhicules":
        st.title("🚗 Comparateur & Agences de Location de Véhicules")
        st.write("Recherchez et comparez les meilleurs loueurs de voitures à travers le monde.")
        
        LOUEURS_DATA = {
            "Enterprise": {
                "rang": "#1 Mondial",
                "note": "4.4 / 5",
                "resume": "Leader mondial de la location, excellent service client, très présent dans les aéroports et les centres-villes."
            },
            "Hertz": {
                "rang": "#2 Mondial",
                "note": "4.0 / 5",
                "resume": "Présent dans le monde entier, grand choix de véhicules récents et service client fiable."
            },
            "Avis": {
                "rang": "#3 Mondial",
                "note": "4.1 / 5",
                "resume": "L'un des pionniers de la location, reconnu pour son service professionnel et ses programmes de fidélité."
            },
            "Sixt": {
                "rang": "#4 Mondial",
                "note": "4.3 / 5",
                "resume": "Flotte moderne, véhicules haut de gamme souvent disponibles et agences très bien placées."
            },
            "Europcar": {
                "rang": "#5 Mondial",
                "note": "3.9 / 5",
                "resume": "Réseau très étendu en Europe et formules de location flexibles adaptées aux voyageurs internationaux."
            },
            "Alamo": {
                "rang": "#6 Mondial",
                "note": "4.2 / 5",
                "resume": "Très populaire auprès des vacanciers, notamment pour ses options de choix de véhicule sur place."
            },
            "Budget": {
                "rang": "#7 Mondial",
                "note": "3.8 / 5",
                "resume": "Idéal pour les petits budgets, offre un très bon rapport qualité-prix sur une large gamme de véhicules."
            },
            "Dollar": {
                "rang": "#8 Mondial",
                "note": "3.7 / 5",
                "resume": "Tarifs souvent très compétitifs pour les locations de vacances en famille."
            },
            "Thrifty": {
                "rang": "#9 Mondial",
                "note": "3.7 / 5",
                "resume": "Solutions économiques et pratiques pour les voyageurs à la recherche de bons plans."
            }
        }

        liste_options = ["Sélectionnez un loueur..."] + list(LOUEURS_DATA.keys())
        choix_loueur = st.selectbox("Choisissez un loueur de véhicules :", liste_options)

        if choix_loueur != "Sélectionnez un loueur...":
            infos_l = LOUEURS_DATA[choix_loueur]
            st.markdown("---")
            col_l1, col_l2 = st.columns([1, 4])
            with col_l1:
                st.markdown(
                    f"""
                    <div style="background-color: #3b82f6; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 16px;">
                        {infos_l['rang']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col_l2:
                st.subheader(choix_loueur)
                st.markdown(f"**Note globale :** ⭐ {infos_l['note']}")
            st.write(f"**Résumé des avis :** {infos_l['resume']}")
            st.markdown("---")

        st.markdown("---")
        st.subheader("Trouvez votre véhicule partout dans le monde")
        
        widget_html = """
        <div style="width: 100%; min-height: 400px;">
            <script async src="https://tpemd.com/content?trs=552839&shmarker=751055&locale=fr&powered_by=true&border_radius=4&plain=true&show_logo=false&color_background=%23ffca28&color_button=%2355a539&color_text=%23000000&color_input_text=%23000000&color_button_text=%23ffffff&promo_id=4480&campaign_id=10" charset="utf-8"></script>
        </div>
        """
        
        components.html(widget_html, height=450, scrolling=True)

    # ==============================================================================
    # SECTION 4 : BLOG
    # ==============================================================================
    elif st.session_state.page == "Blog":
        st.title("📖 Notre Blog Voyage")

        def get_corrected_image(img_path):
            try:
                from PIL import Image, ImageOps
                img = Image.open(img_path)
                img = ImageOps.exif_transpose(img)
                return img
            except Exception:
                return img_path

        try:
            with open("blog_data.json", "r", encoding="utf-8") as f:
                articles = json.load(f)
        except Exception as e:
            articles = []
            st.error(f"Erreur de chargement du JSON : {e}")

        if 'article_ouvert' not in st.session_state:
            st.session_state.article_ouvert = None

        if st.session_state.article_ouvert:
            art = st.session_state.article_ouvert
            st.header(art.get('titre', ''))
            
            onglet_texte, onglet_galerie = st.tabs(["📖 Lire l'article", "📸 Galerie photos"])
            
            with onglet_texte:
                st.markdown(art.get('details', "Contenu de l'article..."))
                
            with onglet_galerie:
                st.write("### 🖼️ Toutes les photos du voyage")
                if 'images' in art and art['images']:
                    images_list = art['images']
                    valid_images = [img for img in images_list if os.path.exists(img)]
                    
                    if valid_images:
                        for i in range(0, len(valid_images), 3):
                            cols = st.columns(3)
                            for j in range(3):
                                idx = i + j
                                if idx < len(valid_images):
                                    with cols[j]:
                                        corrected_img = get_corrected_image(valid_images[idx])
                                        st.image(corrected_img, use_container_width=True)
                                else:
                                    with cols[j]:
                                        st.write("")
                    else:
                        st.info("Aucune image valide trouvée.")
                else:
                    st.info("Aucune galerie photo disponible pour cet article.")
                
            st.markdown("---")
            if st.button("⬅️ Retour au blog"):
                st.session_state.article_ouvert = None
                st.rerun()
                
        else:
            for i in range(0, len(articles), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(articles):
                        art = articles[i + j]
                        with cols[j]:
                            images_art = art.get('images', [])
                            first_img = images_art[0] if images_art and os.path.exists(images_art[0]) else art.get('image', '')
                            
                            if first_img and os.path.exists(first_img):
                                corrected_img = get_corrected_image(first_img)
                                st.image(corrected_img, use_container_width=True)
                                
                            st.subheader(art.get('titre', ''))
                            st.write(art.get('resume', ''))
                            if st.button("Lire la suite", key=f"art_{i}_{j}"):
                                st.session_state.article_ouvert = art
                                st.rerun()

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