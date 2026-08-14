import streamlit as st
import streamlit.components.v1 as components

# 1. Configuration unique de la page en premier
st.set_page_config(page_title="Loueurs - HotelCompare", page_icon="🚗", layout="wide")

# 2. Style CSS global unifié (masquage de la sidebar, de l'en-tête et mode sombre)
st.markdown("""
    <style>
    /* Supprimer la bande blanche du haut et le menu de gauche */
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    
    /* Fond général sombre et remontée du contenu */
    .stApp { 
        background-color: #0B132B !important; 
        color: #FFFFFF !important;
    }
    .block-container { 
        padding-top: 0rem !important; 
        margin-top: -10px !important;
    }
    iframe { 
        width: 100% !important; 
    }
    
    /* Textes généraux en blanc */
    p, span, label, h1, h2, h3, h4, h5, h6, 
    .stMarkdown, div[data-baseweb="select"] span {
        color: #FFFFFF !important;
    }

    /* Couleur du texte à l'intérieur des boutons du haut */
    .stButton button, .stButton button p, .stButton button span {
        color: #0B132B !important;
        font-weight: 700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Barre de navigation par onglets (en haut)
b1, b2, b3, b4, b5 = st.columns(5)

with b1:
    if st.button("🏨 Hôtels", use_container_width=True):
        st.session_state.page = "Comparateur Hôtels"
        st.switch_page("app.py")
with b2:
    if st.button("✈️ Compagnies Aériennes", use_container_width=True):
        st.switch_page("pages/1_Compagnies_Aeriennes.py")
with b3:
    if st.button("🚗 Loueurs de Véhicules", use_container_width=True):
        st.switch_page("pages/2_Loueurs_Vehicules.py")
with b4:
    # --- CHANGEMENT ICI : Nom "Croisières" et redirection vers cruises.py ---
    if st.button("🚢 Croisières", use_container_width=True):
        st.switch_page("pages/3_Cruises.py")
with b5:
    if st.button("📖 Blog", use_container_width=True):
        st.switch_page("pages/4_Blog.py")
st.markdown("---")

# 4. Contenu de la page
st.title("🚗 Comparateur & Agences de Location de Véhicules")
st.write("Recherchez et comparez les meilleurs loueurs de voitures à travers le monde.")

LOUEURS_DATA = {
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

liste_options = ["Sélectionnez un loueur..."] + list(LOUEURS_DATA.keys())
choix_loueur = st.selectbox("Choisissez un loueur de véhicules :", liste_options)

if choix_loueur != "Sélectionnez un loueur...":
    infos_l = LOUEURS_DATA[choix_loueur]
    st.markdown("---")
    col_l1, col_l2 = st.columns([1, 4])
    with col_l1:
        st.markdown(f"""
        <div style="background-color: #3b82f6; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 16px;">
            {infos_l['rang']}
        </div>
        """, unsafe_allow_html=True)
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