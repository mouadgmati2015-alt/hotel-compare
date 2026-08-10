import streamlit as st
import json

st.set_page_config(page_title="Assistant Voyageur", layout="wide")

# Ton thème graphique global
st.markdown("""
    <style>
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    
    .stApp { 
        background-color: #0B132B !important; 
        color: #FFFFFF !important;
    }
    .block-container { 
        padding-top: 0rem !important; 
        margin-top: -10px !important;
    }
    
    p, span, label, h1, h2, h3, h4, h5, h6, .stMarkdown {
        color: #FFFFFF !important;
    }

    .stLinkButton a, .stLinkButton a p, .stLinkButton a div {
        color: #0B132B !important;
        font-weight: 700 !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_hotels():
    with open("data/tunisie.json", "r", encoding="utf-8") as f:
        return json.load(f)

hotels_data = load_hotels()

st.title("🤖 Assistant Voyageur")
st.write("Trouvez l'hôtel idéal via la recherche ou les filtres par critères ci-dessous 👇")

# --- 1. BARRE DE RECHERCHE PRINCIPALE ---
query = st.text_input("Recherche rapide :", placeholder="Ex: un hôtel à Tunis ou à Djerba...", key="recherche_input")

st.markdown("---")

# --- 2. SECTION DE RECHERCHE PAR CRITÈRES (EN DESSOUS) ---
st.subheader("🎯 Recherche avancée par critères")

col_c1, col_c2, col_c3 = st.columns(3)

with col_c1:
    villes_disponibles = sorted(list(set(info.get("ville", "") for info in hotels_data.values() if info.get("ville"))))
    filtre_ville = st.selectbox("📍 Choisir une ville :", ["Toutes"] + villes_disponibles)

with col_c2:
    filtre_etoiles = st.selectbox("⭐ Standing / Étoiles :", ["Tous", "3 étoiles", "4 étoiles", "5 étoiles", "Maison d'hôtes"])

with col_c3:
    filtre_equipement = st.selectbox("🏊 Équipement spécifique :", ["Tous", "Piscine", "Centre-ville", "Parc aquatique / Toboggans"])

st.markdown("---")

# --- 3. LOGIQUE DE FILTRAGE COMBINÉE ---
hotels_filtres = []

for nom, info in hotels_data.items():
    ville_hotel = str(info.get("ville", ""))
    etoiles_hotel = str(info.get("etoiles", ""))
    
    equipements_str = " ".join(info.get('equipements', []))
    texte_complet = f"{nom} {ville_hotel} {info.get('description', '')} {' '.join(info.get('points_positifs', []))} {equipements_str}".lower()
    
    # Si l'utilisateur utilise la barre de recherche textuelle du haut
    if query:
        query_lower = query.lower()
        mots_requete = [m for m in query_lower.split() if len(m) > 2]
        # Vérification si les mots de la recherche correspondent à l'hôtel
        correspond_texte = any(mot in texte_complet for mot in mots_requete)
        if not correspond_texte:
            continue
    
    # Si l'utilisateur utilise les filtres par critères du bas
    if filtre_ville != "Toutes" and filtre_ville.lower() not in ville_hotel.lower():
        continue
        
    if filtre_etoiles != "Tous" and filtre_etoiles.lower() not in etoiles_hotel.lower():
        continue
        
    if filtre_equipement == "Piscine" and not any(m in texte_complet for m in ["piscine", "bassin"]):
        continue
    if filtre_equipement == "Centre-ville" and not any(m in texte_complet for m in ["centre", "habib", "bourguiba", "emplacement"]):
        continue
    if filtre_equipement == "Parc aquatique / Toboggans" and not any(m in texte_complet for m in ["aquatique", "toboggan"]):
        continue

    hotels_filtres.append((nom, info))

# --- 4. AFFICHAGE DES RÉSULTATS ---
if not hotels_filtres:
    st.warning("⚠️ Aucun hôtel ne correspond à vos critères de recherche.")
else:
    st.success(f"🔍 **{len(hotels_filtres)} hôtel(s) trouvé(s)**")

    for nom, info in hotels_filtres:
        col1, col2 = st.columns([1, 2])
        with col1:
            image_url = info.get("image", "")
            if image_url:
                st.image(image_url, use_container_width=True)
        with col2:
            st.subheader(nom)
            st.write(f"📍 **{info.get('ville', '')}** | ⭐ {info.get('etoiles', 'N/C')}")
            st.write(f"💰 **{info.get('prix_moyen', 'Sur demande')}**")
            points = info.get('points_positifs', [])
            if points:
                st.markdown(f"**Points forts :** {', '.join(points)}")
            
            lien = info.get('lien', '#')
            st.link_button("Réserver sur Booking", lien)
            
        st.markdown("---")