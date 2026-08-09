import streamlit as st
import os
import json
from PIL import Image, ImageOps

# 1. Configuration unique de la page en premier
st.set_page_config(page_title="Blog - HotelCompare", page_icon="📖", layout="wide")

# 2. Style CSS global (masquage de la sidebar, de l'en-tête et mode sombre)
st.markdown("""
    <style>
    /* Supprimer la bande blanche du haut et le menu de gauche */
    header, [data-testid="stHeader"], [data-testid="stDecoration"], [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Fond général sombre et remontée du contenu */
    .stApp { 
        background-color: #0B132B !important; 
        color: #FFFFFF !important;
    }
    .block-container { 
        padding-top: 0rem !important; 
        margin-top: 0px !important;
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
    if st.button("🏨 Hôtels", use_container_width=True, key="nav_hotel_blog"):
        st.switch_page("app.py")
with b2:
    if st.button("✈️ Compagnies Aériennes", use_container_width=True, key="nav_cie_blog"):
        st.switch_page("pages/1_Compagnies_Aeriennes.py")
with b3:
    if st.button("🚗 Loueurs de Véhicules", use_container_width=True, key="nav_voiture_blog"):
        st.switch_page("pages/2_Loueurs_Vehicules.py")
with b4:
    if st.button("📖 Blog", use_container_width=True, key="nav_blog_blog"):
        st.switch_page("pages/3_Blog.py")

st.markdown("---")

# 4. Contenu du Blog
st.title("📖 Notre Blog Voyage")

def get_corrected_image(img_path):
    try:
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