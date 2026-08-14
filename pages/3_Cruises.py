import json
import os
import streamlit as st

# --- Configuration de la page ---
st.set_page_config(
    page_title="HotelCompare - Croisières",
    page_icon="images/favicon_io/favicon.ico",
    layout="wide",
)

# --- Style CSS global (masquage de la sidebar et thème sombre identique à l'accueil) ---
st.markdown(
    """
    <style>
    /* Masquer les en-têtes et barres Streamlit */
    header, [data-testid="stHeader"], [data-testid="stDecoration"], .stApp > header {
        display: none !important;
        height: 0px !important;
    }
    
    /* Cacher complètement la barre latérale */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Fond général sombre et texte en blanc */
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

    /* Réduction des espaces entre les éléments */
    div.stMarkdown {
        margin-bottom: -10px !important;
    }

    /* Texte des boutons du haut */
    .stButton button, .stButton button p, .stButton button span {
        color: #0B132B !important;
        font-weight: 600 !important;
        font-size: 0.9em !important;
    }

    /* Correction pour les textes à l'intérieur des colonnes */
    div[data-testid="column"] div.stMarkdown p, 
    div[data-testid="column"] div.stMarkdown span {
        color: #0B132B !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- En-tête Global ---
col_logo, col_titre = st.columns([1, 8])
with col_logo:
  if os.path.exists("logo_4.png"):
    st.image("logo_4.png", width=90)
with col_titre:
  st.markdown(
      "<h2 style='padding-top: 10px;'>Comparez les hôtels, les compagnies"
      " aériennes, les loueurs avec notre IA</h2>",
      unsafe_allow_html=True,
  )

st.markdown("---")

# --- Boutons de Navigation Globale ---
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
  if st.button("🚢 Croisières", use_container_width=True):
    pass
with b5:
  if st.button("📖 Blog", use_container_width=True):
    st.switch_page("pages/3_Blog.py")

st.markdown("---")

# --- Contenu de la Page Croisières ---
st.title("🚢 Comparateur de Croisières Sereines")
st.write(
    "Découvrez et comparez notre sélection de croisières axées sur la détente,"
    " le calme et l'évasion."
)
st.markdown("---")


# Chargement des données JSON des croisières
@st.cache_data
def load_cruise_data():
  json_path = "cruises_data.json"
  if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
      return json.load(f)
  return {}


cruises_data = load_cruise_data()

if not cruises_data:
  st.warning(
      "⚠️ Aucun fichier `cruises_data.json` trouvé à la racine du projet. "
      "Veuillez y placer votre fichier de données pour afficher les croisières."
  )
else:
  # --- FILTRES DE RECHERCHE EN LIGNE ---
  st.markdown("### 🔍 Filtrer les croisières")
  f_col1, f_col2 = st.columns(2)

  regions_disponibles = ["Toutes"] + list(
      set(data.get("region", "") for data in cruises_data.values())
  )
  with f_col1:
    region_choisie = st.selectbox("Région / Type", regions_disponibles)

  compagnies_disponibles = ["Toutes"] + list(
      set(data.get("compagnie", "") for data in cruises_data.values())
  )
  with f_col2:
    compagnie_choisie = st.selectbox("Compagnie", compagnies_disponibles)

  # --- APPLICATION DES FILTRES ---
  filtered_cruises = {}
  for nom, data in cruises_data.items():
    if region_choisie != "Toutes" and data.get("region") != region_choisie:
      continue
    if (
        compagnie_choisie != "Toutes"
        and data.get("compagnie") != compagnie_choisie
    ):
      continue
    filtered_cruises[nom] = data

  st.markdown("---")
  st.markdown(f"### 📋 Résultats ({len(filtered_cruises)} croisières trouvées)")

  # --- INITIALISATION DE LA LISTE DE COMPARAISON EN SESSION ---
  if "compare_list" not in st.session_state:
    st.session_state["compare_list"] = []

  # --- AFFICHAGE DES CARTES DE CROISIÈRES ---
  for nom, data in filtered_cruises.items():
    with st.container(border=True):
      col_img, col_info, col_action = st.columns([1, 2, 1])

      with col_img:
        if data.get("image"):
          st.markdown(
              f'<img src="{data["image"]}" style="width: 100%; height: 160px;'
              ' object-fit: cover; border-radius: 6px; margin-bottom: 8px;">',
              unsafe_allow_html=True,
          )

      with col_info:
        st.subheader(nom)
        st.write(f"**Compagnie :** {data.get('compagnie')}")
        st.write(f"**Région :** {data.get('region')}")
        st.write(f"**Durée :** {data.get('duree')}")
        st.write(f"**Prix indicatif :** {data.get('prix_moyen')}")

      with col_action:
        is_checked = nom in st.session_state["compare_list"]
        select_box = st.checkbox(
            "Ajouter au comparateur", value=is_checked, key=f"chk_{nom}"
        )

        if select_box and nom not in st.session_state["compare_list"]:
          st.session_state["compare_list"].append(nom)
          st.rerun()
        elif not select_box and nom in st.session_state["compare_list"]:
          st.session_state["compare_list"].remove(nom)
          st.rerun()

        if data.get("lien_reservation"):
          st.markdown(
              f"""
                    <a href="{data['lien_reservation']}" target="_blank" 
                       style="display: block; background-color: #003580; color: white; 
                       padding: 8px; text-align: center; text-decoration: none; 
                       border-radius: 6px; font-weight: bold; margin-top: 10px;">
                        Réserver
                    </a>
                """,
              unsafe_allow_html=True,
          )

      # Description
      st.info(data.get("description", ""))

      # Itinéraire détaillé jour par jour si disponible
      if data.get("itineraire_detaille"):
        with st.expander("🗺️ Voir l'itinéraire détaillé jour par jour"):
          for jour in data["itineraire_detaille"]:
            st.markdown(f"- {jour}")

  # --- SECTION COMPARATEUR CÔTE À CÔTE ---
  if len(st.session_state["compare_list"]) > 0:
    st.markdown("---")
    st.header("⚖️ Comparatif côte à côte")
    st.write(
        "Voici un face-à-face détaillé des croisières sélectionnées pour vous"
        " aider à faire votre choix :"
    )

    selected_names = st.session_state["compare_list"]

    if len(selected_names) > 3:
      st.warning(
          "⚠️ Pour un meilleur confort de lecture, veuillez sélectionner au"
          " maximum 3 croisières à comparer simultanément."
      )
    else:
      comp_cols = st.columns(len(selected_names))
      for i, name in enumerate(selected_names):
        c_data = cruises_data[name]
        with comp_cols[i]:
          # --- AJOUT DE L'IMAGE DANS LE COMPARATEUR ---
          if c_data.get("image"):
            st.markdown(
                f'<img src="{c_data["image"]}" style="width: 100%; height: 120px;'
                ' object-fit: cover; border-radius: 6px; margin-bottom: 8px;">',
                unsafe_allow_html=True,
            )

          st.markdown(f"### {name}")
          st.metric(label="Prix indicatif", value=c_data.get("prix_moyen"))
          st.write(f"**Compagnie :** {c_data.get('compagnie')}")
          st.write(f"**Durée :** {c_data.get('duree')}")

          st.markdown("#### ✨ Points forts")
          for pf in c_data.get("points_positifs", []):
            st.markdown(f"- {pf}")

          verdict_text = c_data.get("pour_qui", {}).get("verdict", "")
          if verdict_text:
            st.success(f"**Notre avis :** {verdict_text}")

          if st.button(f"Retirer {name}", key=f"btn_remove_comp_{name}"):
            st.session_state["compare_list"].remove(name)
            st.rerun()