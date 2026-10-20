import json
import os

import streamlit as st

from moteur_site import MODELE_DEFAUT, charger_index, repondre

st.set_page_config(page_title="Assistant Voyageur", layout="wide")

# --- Thème graphique (inchangé) ---
st.markdown("""
    <style>
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    .stApp { background-color: #0B132B !important; color: #FFFFFF !important; }
    .block-container { padding-top: 0rem !important; margin-top: -10px !important; }
    p, span, label, h1, h2, h3, h4, h5, h6, .stMarkdown { color: #FFFFFF !important; }
    .stLinkButton a, .stLinkButton a p, .stLinkButton a div { color: #0B132B !important; font-weight: 700 !important; }
    </style>
""", unsafe_allow_html=True)

MAX_QUESTIONS_PAR_SESSION = 20


def secret(nom, defaut=None):
    try:
        return st.secrets.get(nom, os.environ.get(nom, defaut))
    except Exception:               # pas de fichier secrets.toml
        return os.environ.get(nom, defaut)


@st.cache_resource(show_spinner="Chargement du site…")
def index_du_site():
    return charger_index()


@st.cache_data(ttl=3600, show_spinner=False)
def reponse_cachee(question, cle, modele, _index):
    return repondre(question, _index, cle, modele)


def afficher_source(d, i):
    if d["type"] == "hotel":
        m = d["meta"]
        c1, c2 = st.columns([1, 2])
        with c1:
            if m.get("image"):
                st.image(m["image"], use_container_width=True)
        with c2:
            st.subheader(d["titre"])
            st.write(f"📍 **{m.get('ville', '')}** | ⭐ {m.get('etoiles') or 'N/C'}")
            st.write(f"💰 **{m.get('prix') or 'Sur demande'}**")
            if m.get("points"):
                st.markdown(f"**Points forts :** {', '.join(m['points'])}")
            if d["url"]:
                st.link_button("Réserver sur Booking", d["url"], key=f"src_{i}")
    elif d["type"] == "faq":
        st.markdown(f"**✈️ {d['meta']['compagnie']}**")
        st.info(d["meta"]["reponse"])
    else:
        st.markdown(f"**{d['titre']}**")
        st.caption(d["texte"][:220] + "…")
        if d["url"]:
            st.link_button("Voir la page", d["url"], key=f"src_{i}")


# =====================================================================
st.title("🤖 Assistant Voyageur")
st.write("Posez votre question en vos propres mots : je cherche la réponse dans tout le site "
         "(hôtels, compagnies aériennes, trajets sans autoroute).")

index = index_du_site()
cle = secret("ANTHROPIC_API_KEY")
modele = secret("MODELE", MODELE_DEFAUT)

with st.form("demande"):
    question = st.text_input(
        "Votre demande :", max_chars=400,
        placeholder="Ex. un hôtel avec piscine à Djerba, les bagages avec Ethiopian Airlines, Strasbourg Nice sans péage…")
    envoye = st.form_submit_button("Chercher")

if envoye and question.strip():
    st.session_state["nb_q"] = st.session_state.get("nb_q", 0) + 1
    if st.session_state["nb_q"] > MAX_QUESTIONS_PAR_SESSION:
        st.warning("Vous avez atteint la limite de questions pour cette session. Revenez un peu plus tard.")
    else:
        with st.spinner("Je cherche dans le site…"):
            r = reponse_cachee(question.strip(), cle, modele, index)
        for avant, apres in r["corrections"]:
            st.caption(f"J'ai lu « {apres} » à la place de « {avant} ».")
        if r["erreur"]:
            st.caption("L'assistant IA est momentanément indisponible : voici les résultats de la recherche.")
        if r["trouve"]:
            st.success(r["texte"])
        else:
            st.warning(r["texte"])
        if r["lien"]:
            st.link_button(r["lien"][0], r["lien"][1], key="lien_reponse")
        if r["sources"]:
            st.markdown("---")
            st.subheader("📌 Sur le site")
            for i, d in enumerate(r["sources"]):
                afficher_source(d, i)
                st.markdown("---")

st.caption("Les demandes restées sans réponse sont enregistrées (texte seul, sans donnée personnelle) "
           "pour améliorer le site.")

# --- Espace gestion : questions sans réponse (visible seulement si ADMIN_CODE est défini dans les secrets) ---
code_admin = secret("ADMIN_CODE")
if code_admin:
    with st.expander("🔒 Gestion"):
        if st.text_input("Code", type="password", key="code_admin") == code_admin:
            from moteur_site import FICHIER_LOG
            if FICHIER_LOG.exists():
                st.download_button("Télécharger les questions sans réponse", FICHIER_LOG.read_bytes(),
                                   file_name="questions_sans_reponse.jsonl")
                st.code(FICHIER_LOG.read_text(encoding="utf-8")[-3000:] or "(vide)")
            else:
                st.write("Aucune question sans réponse pour l'instant.")

# --- Recherche par critères (logique d'origine, conservée) ---
with st.expander("🎯 Recherche avancée par critères (Tunisie)"):
    @st.cache_data
    def load_hotels():
        with open("data/tunisie.json", "r", encoding="utf-8") as f:
            return json.load(f)

    hotels_data = load_hotels()
    c1, c2, c3 = st.columns(3)
    with c1:
        villes = sorted({i.get("ville", "") for i in hotels_data.values() if i.get("ville")})
        f_ville = st.selectbox("📍 Choisir une ville :", ["Toutes"] + villes)
    with c2:
        f_etoiles = st.selectbox("⭐ Standing / Étoiles :", ["Tous", "3 étoiles", "4 étoiles", "5 étoiles", "Maison d'hôtes"])
    with c3:
        f_equip = st.selectbox("🏊 Équipement spécifique :", ["Tous", "Piscine", "Centre-ville", "Parc aquatique / Toboggans"])

    for nom, info in hotels_data.items():
        ville = str(info.get("ville", ""))
        txt = f"{nom} {ville} {info.get('description', '')} {' '.join(info.get('points_positifs', []))} {' '.join(info.get('equipements', []))}".lower()
        if f_ville != "Toutes" and f_ville.lower() not in ville.lower():
            continue
        if f_etoiles != "Tous" and f_etoiles.lower() not in str(info.get("etoiles", "")).lower():
            continue
        if f_equip == "Piscine" and not any(m in txt for m in ["piscine", "bassin"]):
            continue
        if f_equip == "Centre-ville" and not any(m in txt for m in ["centre", "habib", "bourguiba", "emplacement"]):
            continue
        if f_equip == "Parc aquatique / Toboggans" and not any(m in txt for m in ["aquatique", "toboggan"]):
            continue
        a, b = st.columns([1, 2])
        with a:
            if info.get("image"):
                st.image(info["image"], use_container_width=True)
        with b:
            st.subheader(nom)
            st.write(f"📍 **{ville}** | ⭐ {info.get('etoiles', 'N/C')} | 💰 {info.get('prix_moyen', 'Sur demande')}")
            if info.get("points_positifs"):
                st.markdown(f"**Points forts :** {', '.join(info['points_positifs'])}")
            st.link_button("Réserver sur Booking", info.get("lien", "#"), key=f"crit_{nom}")