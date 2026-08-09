import streamlit as st
import os
from data.airlines_data import AIRLINES_DATA as airlines

# 1. Configuration unique de la page en premier
st.set_page_config(page_title="Compagnies - HotelCompare", page_icon="✈️", layout="wide")

# 2. Style CSS global (masquage de la sidebar, de l'en-tête et mode sombre unifié)
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
b1, b2, b3, b4 = st.columns(4)
with b1:
    if st.button("🏨 Hôtels", use_container_width=True, key="nav_hotel_cie"):
        st.switch_page("app.py")
with b2:
    if st.button("✈️ Compagnies Aériennes", use_container_width=True, key="nav_cie_cie"):
        st.switch_page("pages/1_Compagnies_Aeriennes.py")
with b3:
    if st.button("🚗 Loueurs de Véhicules", use_container_width=True, key="nav_voiture_cie"):
        st.switch_page("pages/2_Loueurs_Vehicules.py")
with b4:
    if st.button("📖 Blog", use_container_width=True, key="nav_blog_cie"):
        st.switch_page("pages/3_Blog.py")

st.markdown("---")

# 4. Contenu de la page
st.title("✈️ Guide des Compagnies Aériennes")
st.write("Analysez les caractéristiques, les avantages et les points d'attention de chaque compagnie.")

# Sélection
liste_compagnies = sorted(list(airlines.keys()))
choix = st.selectbox("Sélectionnez une compagnie :", liste_compagnies)

if choix:
    data = airlines[choix]
    
    col_titre, col_logo = st.columns([3, 1])
    with col_titre:
        st.header(choix)
    with col_logo:
        logo_path = data.get("logo", "images/airbus_vol.jpg")
        if os.path.exists(logo_path):
            st.image(logo_path, width=100)
        elif os.path.exists("images/airbus_vol.jpg"):
            st.image("images/airbus_vol.jpg", width=100)

    # Infos clés
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Catégorie**\n\n{data.get('categorie', 'N/A')}")
    with c2:
        st.markdown(f"**Alliance**\n\n{data.get('alliance', 'N/A')}")
    with c3:
        st.markdown(f"**Note globale**\n\n⭐ {data.get('note', 'N/A')}")

    st.markdown("---")
    st.subheader("📖 À propos")
    st.write(data.get("resume", ""))
    
    col_g, col_d = st.columns(2)
    with col_g:
        st.write(f"**📜 Histoire :** {data.get('histoire', 'N/A')}")
        st.write(f"**✈️ Flotte :** {data.get('flotte', 'N/A')}")
    with col_d:
        st.write(f"**🧳 Bagages :** {data.get('bagages', 'N/A')}")
        st.write(f"**🛡️ Sécurité :** {data.get('securite', 'N/A')}")

    st.subheader("📍 Liaisons fréquentes")
    st.write(", ".join(data.get("liaisons", [])))

    st.info(f"**🎯 Pour qui ?** {data.get('pour_qui', '')}")

    col_pos, col_neg = st.columns(2)
    with col_pos:
        st.success("✅ Points Positifs")
        for p in data.get("points_positifs", []): st.markdown(f"- {p}")
    with col_neg:
        st.error("⚠️ Points de vigilance")
        for n in data.get("points_negatifs", []): st.markdown(f"- {n}")

    if "lien" in data and data["lien"]:
        st.markdown("---")
        st.markdown(
            f'<a href="{data["lien"]}" target="_blank" style="display: block; width: 100%; background-color: #0066cc; color: white; padding: 12px 20px; text-align: center; text-decoration: none; font-size: 16px; font-weight: bold; border-radius: 6px;">Réserver le vol</a>',
            unsafe_allow_html=True
        )