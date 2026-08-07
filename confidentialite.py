import streamlit as st

def afficher_page():
    # Petit espace pour éviter que le titre soit collé en haut
    st.write("")
    
    # En-tête de la page
    st.title("🔒 Politique de confidentialité")
    st.write("Dernière mise à jour : Août 2026")
    
    st.markdown("---")
    
    # Section 1
    st.subheader("1. Introduction")
    st.write(
        "Bienvenue sur **MyHotelCompare**. Nous accordons une importance majeure à la protection de votre vie privée "
        "et de vos données personnelles. Cette politique de confidentialité vous informe sur la manière dont nous "
        "traitons vos informations lors de l'utilisation de notre comparateur."
    )
    
    # Section 2
    st.subheader("2. Données collectées")
    st.write("Dans le cadre de votre navigation sur notre site, nous pouvons collecter les types de données suivants :")
    st.markdown(
        """
        - **Préférences de recherche :** Les pays, villes et hôtels que vous sélectionnez pour effectuer vos comparaisons.
        - **Données de contact :** Votre nom, votre adresse e-mail et vos messages si vous utilisez notre formulaire de contact.
        - **Données techniques :** Informations de session nécessaires au bon fonctionnement de l'interface (gérées via Streamlit).
        """
    )
    
    # Section 3
    st.subheader("3. Utilisation des données")
    st.write(
        "Les informations que vous nous transmettez sont utilisées exclusivement pour :"
    )
    st.markdown(
        """
        - Vous fournir les résultats de comparaison d'hôtels et de vols.
        - Améliorer l'ergonomie et les fonctionnalités de l'application.
        - Répondre à vos demandes ou suggestions.
        """
    )
    
    # Section 4
    st.subheader("4. Protection des données")
    st.write(
        "Nous mettons en œuvre des mesures de sécurité techniques et organisationnelles appropriées "
        "pour protéger vos données contre tout accès, modification, divulgation ou destruction non autorisée."
    )
    
    # Section 5
    st.subheader("5. Vos droits")
    st.write(
        "Conformément à la réglementation applicable en matière de protection des données, vous disposez d'un droit "
        "d'accès, de rectification et de suppression des informations vous concernant."
    )
    
    st.markdown("---")
    st.caption("© 2026 MyHotelCompare — Tous droits réservés.")