import streamlit as st
import os
import json
from streamlit_carousel import carousel
from data.hotels_data import HOTELS_DATA

# Configuration de la page
st.set_page_config(page_title="HotelCompare", layout="wide")

# --- Style CSS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { min-width: 150px; max-width: 150px; }
    .stApp { margin-top: -60px; }
    .hero-container { text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- Navigation ---
page = st.sidebar.radio("Navigation", ["Comparateur", "Blog"])

if page == "Comparateur":
    # En-tête (Ligne corrigée ici)
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.image("logo_4.png", width=120)
    st.title("Comparez vos hôtels avec l'IA")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Carrousel
    test_items = [
        dict(title="", text="", img="https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?q=80&w=2000"),
        dict(title="", text="", img="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=2000")
    ]
    carousel(items=test_items, width=1)
    
    st.divider()
    
    # Recherche
    noms_hotels = list(HOTELS_DATA.keys())
    c1, c2, c3 = st.columns([2, 2, 1])
    choix1 = c1.selectbox("Premier hôtel", [""] + noms_hotels)
    choix2 = c2.selectbox("Deuxième hôtel", [""] + noms_hotels)
    valider = c3.button("Comparer", type="primary", use_container_width=True)

    # Affichage résultats
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
                    if d.get("image"): st.image(d["image"], use_container_width=True)
                    
                    # Extraction du lien et affichage dynamique des autres infos
                    lien = d.get("lien", "")
                    for cle, valeur in d.items():
                        if cle in ["nom", "image", "points_positifs", "points_negatifs", "pour_qui", "lien"]:
                            continue
                        st.write(f"**{cle.replace('_', ' ').capitalize()} :** {valeur}")
                    
                    # Bouton de réservation propre
                    if lien:
                        st.markdown(f'<a href="{lien}" target="_blank" style="text-decoration:none;"><button style="width:100%; padding:10px; background-color:#FF4B4B; color:white; border:none; border-radius:5px; cursor:pointer;">Réserver sur le site partenaire</button></a>', unsafe_allow_html=True)
                        st.write("") 
                    
                    st.info(f"**Verdict :** {d.get('pour_qui', {}).get('verdict', 'N/A')}")
                    
                    with st.expander("✅ Points Positifs"):
                        for p in d.get("points_positifs", []):
                            st.write(f"- {p}")
                    with st.expander("⚠️ Points Négatifs"):
                        for n in d.get("points_negatifs", []):
                            st.write(f"- {n}")

elif page == "Blog":
    st.title("📖 Notre Blog Voyage")
    
    # Données intégrées pour éviter les problèmes de chemin de fichier
    articles = [
  {
    "titre": "5 astuces d'expert pour voyager moins cher",
    "image": "images/images_astuce.jfif",
    "resume": "Voyager ne signifie pas forcément se ruiner.",
    "details": "Voici mes 5 conseils d'expert : flexibilité, réservation anticipée, hébergement alternatif, cuisine locale et bagage léger."
  },
  {
    "titre": "Le guide ultime pour choisir son hôtel en Tunisie",
    "image": "images/images_hotel.jfif",
    "resume": "Choisir le mauvais hôtel peut gâcher un séjour.",
    "details": "Vérifiez bien l'emplacement, les services inclus et les avis récents."
  },
  {
    "titre": "Découvrir la Tunisie autrement",
    "image": "images/images_tunisie.jfif",
    "resume": "Sortir des sentiers battus.",
    "details": "Sidi Bou Saïd, le désert du Sud et les villages berbères sont des lieux magiques."
  }
]
    for i, art in enumerate(articles):
        with st.expander(art['titre'], expanded=(i == 0)):
            # On tente d'afficher l'image
            if os.path.exists(art['image']):
                st.image(art['image'], use_container_width=True)
            else:
                st.warning(f"Image introuvable à : {art['image']}")
            
            st.write(art['resume'])
            
            if st.button(f"Lire la suite", key=f"btn_{i}"):
                st.success(art['details'])