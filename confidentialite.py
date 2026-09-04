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
    st.subheader("2. Responsable du traitement")
    st.write(
        "Le responsable du traitement des données est Mouad Guemati (Entreprise Individuelle), "
        "domicilié à Fegersheim, 67640, France."
    )
    st.write("Contact : myhotelcompare@gmail.com")

    # Section 3
    st.subheader("3. Données collectées")
    st.write("Dans le cadre de votre navigation sur notre site, nous pouvons collecter les types de données suivants :")
    st.markdown(
        """
        - **Préférences de recherche :** les pays, villes et hôtels que vous sélectionnez pour effectuer vos comparaisons.
        - **Données de contact :** votre nom, votre adresse e-mail et vos messages si vous utilisez notre formulaire de contact.
        - **Données techniques de navigation :** adresse IP, type d'appareil, pages visitées, collectées via Google Analytics uniquement si vous avez donné votre consentement.
        - **Données de session :** informations nécessaires au bon fonctionnement de l'interface (gérées via Streamlit).
        """
    )

    # Section 4
    st.subheader("4. Finalités et base légale")
    st.markdown(
        """
        - **Fournir les résultats de comparaison** — base légale : exécution de mesures précontractuelles / intérêt légitime.
        - **Mesure d'audience (Google Analytics)** — base légale : votre consentement, recueilli via le bandeau cookies.
        - **Répondre à vos demandes** envoyées via le formulaire de contact — base légale : intérêt légitime.
        - **Fonctionnement technique du site** — base légale : intérêt légitime.
        """
    )

    # Section 5
    st.subheader("5. Cookies")
    st.write(
        "Ce site utilise Google Analytics (identifiant G-RLVNV2211J) pour mesurer l'audience et comprendre "
        "l'utilisation du site. Ces cookies ne sont déposés qu'après votre consentement explicite via le bandeau "
        "affiché lors de votre première visite. Vous pouvez à tout moment retirer votre consentement en effaçant "
        "les cookies de votre navigateur, ce qui réaffichera le bandeau à votre prochaine visite."
    )

    # Section 6
    st.subheader("6. Durée de conservation")
    st.write(
        "Les données de mesure d'audience sont conservées 13 mois maximum, conformément aux recommandations de "
        "la CNIL. Les données transmises via le formulaire de contact sont conservées le temps nécessaire au "
        "traitement de votre demande."
    )

    # Section 7
    st.subheader("7. Destinataires des données")
    st.write(
        "Vos données techniques de navigation (si consentement donné) sont transmises à Google (Google Analytics), "
        "susceptible de les traiter en dehors de l'Union Européenne (États-Unis), dans le cadre de garanties "
        "contractuelles types approuvées par la Commission européenne. Notre hébergeur, Render Services, Inc. "
        "(États-Unis), traite les données techniques nécessaires à la mise à disposition du site. Aucune donnée "
        "personnelle n'est vendue à des tiers."
    )

    # Section 8
    st.subheader("8. Protection des données")
    st.write(
        "Nous mettons en œuvre des mesures de sécurité techniques et organisationnelles appropriées pour protéger "
        "vos données contre tout accès, modification, divulgation ou destruction non autorisée."
    )

    # Section 9
    st.subheader("9. Vos droits")
    st.write(
        "Conformément au RGPD, vous disposez d'un droit d'accès, de rectification, d'effacement, de limitation, "
        "d'opposition et de portabilité de vos données. Vous pouvez exercer ces droits en nous contactant à "
        "myhotelcompare@gmail.com."
    )
    st.write(
        "Vous disposez également du droit d'introduire une réclamation auprès de la CNIL (www.cnil.fr)."
    )

    st.markdown("---")
    st.caption("© 2026 MyHotelCompare — Tous droits réservés.")