import streamlit as st

def afficher_page():
    # En-tête de la page
    st.title("ℹ️ À propos de MyHotelCompare")
    st.write("Votre assistant intelligent pour trouver et comparer les meilleurs séjours au meilleur prix.")
    
    st.markdown("---")
    
    # Section Mission
    st.subheader("🎯 Notre Mission")
    st.write(
        "**MyHotelCompare** est né d'un constat simple : comparer des centaines d'hôtels et de plateformes "
        "prend un temps précieux. Notre mission est de vous simplifier la vie grâce à une interface claire, "
        "rapide et propulsée par des technologies intelligentes pour résumer l'essentiel en un clin d'œil."
    )
    
    # Section Fonctionnalités clés sous forme de colonnes
    st.subheader("💡 Ce que nous proposons")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🏨 Comparaison")
        st.write("Comparez côte à côte les équipements, les notes, les prix et les photos de vos hôtels favoris.")
        
    with col2:
        st.markdown("### 🤖 Analyse IA")
        st.write("Bénéficiez de résumés automatiques et d'avis synthétisés pour savoir instantanément quel hôtel vous correspond.")
        
    with col3:
        st.markdown("### ✈️ Multidiscipline")
        st.write("Retrouvez également des outils pour comparer les compagnies aériennes et planifier vos voyages plus sereinement.")

    st.markdown("---")
    
    # Section Engagement
    st.subheader("🔒 Notre Engagement")
    st.info(
        "Nous mettons un point d'honneur à vous offrir une information transparente et neutre. "
        "Toutes les données affichées ont pour but de vous aider à faire le meilleur choix pour vos vacances ou vos déplacements professionnels."
    )
    
    # Petit message de bas de page pour la page À propos
    st.write("")
    st.caption("© 2026 MyHotelCompare — Tous droits réservés.")