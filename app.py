import streamlit as st
import os
import json
from data.hotels_data import HOTELS_DATA
from data.airlines_data import AIRLINES_DATA
import streamlit.components.v1 as components

# --- Configuration de la page ---
st.set_page_config(page_title="HotelCompare", layout="wide")

# Injection de la balise de vérification Google Search Console
google_tag = '<meta name="google-site-verification" content="UFPNwmAw5bpc..." />'
components.html(google_tag, height=0, width=0)

# --- Style CSS ---
st.markdown("""
    <style>
    .stApp {
        background-color: #F8F9FA;
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
    [data-testid="collapsedControl"]::after {
        content: " Menu";
        font-size: 14px;
        font-weight: bold;
        color: #333;
        vertical-align: middle;
        margin-left: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Gestion de l'état de navigation ---
if 'page' not in st.session_state:
    st.session_state.page = "Comparateur Hôtels"

# --- En-tête Global : Logo et Titre sur la même ligne ---
col_logo, col_titre = st.columns([1, 8])
with col_logo:
    if os.path.exists("logo_4.png"):
        st.image("logo_4.png", width=90)
with col_titre:
    st.markdown("<h2 style='padding-top: 10px;'>Comparez les hôtels, les compagnies aériennes, les loueurs avec notre IA</h2>", unsafe_allow_html=True)

st.markdown("---")

# --- 4 Boutons de Navigation ---
b1, b2, b3, b4 = st.columns(4)
with b1:
    if st.button("🏨 Hôtels", use_container_width=True):
        st.session_state.page = "Comparateur Hôtels"
        st.rerun()
with b2:
    if st.button("✈️ Compagnies Aériennes", use_container_width=True):
        st.session_state.page = "Compagnies Aériennes"
        st.rerun()
with b3:
    if st.button("🚗 Loueurs de Véhicules", use_container_width=True):
        st.session_state.page = "Loueurs Véhicules"
        st.rerun()
with b4:
    if st.button("📖 Blog", use_container_width=True):
        st.session_state.page = "Blog"
        st.rerun()

st.markdown("---")

# ==============================================================================
# SECTION 1 : COMPARATEUR D'HÔTELS
# ==============================================================================
if st.session_state.page == "Comparateur Hôtels":
    st.image("images/image caroussel 2.png", use_container_width=True)

    st.subheader("💡 Comment comparer vos hôtels")
    st.markdown("""
    1. **Sélectionnez** vos deux hôtels dans les menus déroulants ci-dessous.
    2. **Cliquez** sur le bouton rouge **Comparer**.
    3. **Découvrez** les points forts et points faibles pour faire votre choix !
    """)
    st.markdown("---")
    
   # Recherche avec 4 colonnes : Premier hôtel, Deuxième hôtel, Bouton Comparer, Bouton Reset
    noms_hotels = list(HOTELS_DATA.keys())
    c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
    choix1 = c1.selectbox("Premier hôtel", [""] + noms_hotels)
    choix2 = c2.selectbox("Deuxième hôtel", [""] + noms_hotels)
    valider = c3.button("Comparer", type="primary", use_container_width=True)
    
    # Bouton Reset pour effacer la sélection (en bleu via HTML/CSS ou simple bouton)
    reset = c4.button("Reset", use_container_width=True)

    if reset:
        st.rerun()
    if valider:
        comparaison = [c for c in [choix1, choix2] if c != ""]
        if not comparaison:
            st.warning("Veuillez sélectionner au moins un hôtel.")
        else:
            cols = st.columns(len(comparaison))
            for i, nom in enumerate(comparaison):
                d = HOTELS_DATA.get(nom)
                with cols[i]:
                    st.subheader(nom)
                    if d.get("image"): 
                        st.image(d["image"], use_container_width=True)
                    
                    lien = d.get("lien", "")
                    for cle, valeur in d.items():
                        if cle in ["nom", "image", "points_positifs", "points_negatifs", "pour_qui", "lien"]:
                            continue
                        st.write(f"**{cle.replace('_', ' ').capitalize()} :** {valeur}")
                    
                    # Lien universel propre vers l'accueil général de Booking avec ton ID CJ
                    lien_booking_cj = "https://www.kqzyfj.com/click-10182501-12677526?url=https%3A%2F%2Fwww.booking.com%2Findex.fr.html"
                    
                    st.markdown(f'<a href="{lien_booking_cj}" target="_blank" style="text-decoration:none;"><button style="width:100%; padding:10px; background-color:#FF4B4B; color:white; border:none; border-radius:5px; cursor:pointer;">Réserver sur Booking</button></a>', unsafe_allow_html=True)
                    st.write("") 
                    
                    st.info(f"**Verdict :** {d.get('pour_qui', {}).get('verdict', 'N/A')}")
                    
                    with st.expander("✅ Points Positifs"):
                        for p in d.get("points_positifs", []):
                            st.write(f"- {p}")
                    with st.expander("⚠️ Points Négatifs"):
                        for n in d.get("points_negatifs", []):
                            st.write(f"- {n}")

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
        
        # En-tête de la compagnie
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
        
        # Affichage complet des informations
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
            
        st.markdown("---")
        st.link_button(f"Réserver un vol avec {choix_cie}", infos.get('lien', 'https://www.travelpayouts.com/'))
# ==============================================================================
# SECTION 3 : LOUEURS DE VÉHICULES
# ==============================================================================
elif st.session_state.page == "Loueurs Véhicules":
    st.title("🚗 Comparateur & Agences de Location de Véhicules")
    st.write("Recherchez et comparez les meilleurs loueurs de voitures à travers le monde.")
    
    # Dictionnaire complet avec classement mondial (rang)
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

    # --- MENU DÉROULANT ---
    # On ajoute une option par défaut "Sélectionnez un loueur..."
    liste_options = ["Sélectionnez un loueur..."] + list(LOUEURS_DATA.keys())
    choix_loueur = st.selectbox("Choisissez un loueur de véhicules :", liste_options)

    # Si l'utilisateur choisit un vrai loueur (différent de l'option par défaut)
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

    # --- INTÉGRATION DU WIDGET DE RECHERCHE MONDIAL ---
    st.markdown("---")
    st.subheader("Trouvez votre véhicule partout dans le monde")
    
    import streamlit.components.v1 as components
    
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

    import json
    import os

    # 1. On charge d'abord les articles en haut de la page Blog
    try:
        with open("blog_data.json", "r", encoding="utf-8") as f:
            articles = json.load(f)
    except Exception as e:
        articles = []
        st.error(f"Erreur de chargement du JSON : {e}")

    # 2. On initialise l'état de l'article ouvert s'il n'existe pas
    if 'article_ouvert' not in st.session_state:
        st.session_state.article_ouvert = None

    # 3. On affiche soit l'article en détail, soit la liste complète
    if st.session_state.article_ouvert:
        art = st.session_state.article_ouvert
        st.header(art.get('titre', ''))
        if 'image' in art and os.path.exists(art['image']):
            st.image(art['image'], use_container_width=True)
        st.markdown(art.get('details', "Contenu de l'article..."))
        
        if st.button("⬅️ Retour au blog"):
            st.session_state.article_ouvert = None
            st.rerun()
            
    else:
        # Affichage de la grille des articles
        for i in range(0, len(articles), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(articles):
                    art = articles[i + j]
                    with cols[j]:
                        if 'image' in art and os.path.exists(art['image']):
                            st.image(art['image'], use_container_width=True)
                        st.subheader(art.get('titre', ''))
                        st.write(art.get('resume', ''))
                        if st.button("Lire la suite", key=f"art_{i}_{j}"):
                            st.session_state.article_ouvert = art
                            st.rerun()