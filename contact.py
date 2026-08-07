import streamlit as st

def afficher_page():
    st.write("")  # Petit espace pour ne pas coller en haut
    st.title("📞 Contactez-nous")
    st.write("Une question, une suggestion ou un partenariat ? Nous sommes à votre écoute.")
    
    st.markdown("---")
    
    # Utilisation de colonnes pour séparer les infos et le formulaire
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Nos coordonnées")
        st.write("📧 **Email :** contact@myhotelcompare.com")
        st.write("📍 **Localisation :** France")
        st.write("🕒 **Réponse :** Sous 24h-48h ouvrées")
        
        st.markdown("---")
        st.subheader("Suivez-nous")
        st.write("Restez informé des nouveautés sur nos réseaux sociaux.")
        # Vous pouvez ajouter des liens cliquables ici
        st.markdown("[LinkedIn](https://linkedin.com) | [Instagram](https://instagram.com)")

    with col2:
        st.subheader("Envoyez-nous un message")
        with st.form("form_contact"):
            nom = st.text_input("Nom complet")
            email = st.text_input("Adresse e-mail")
            objet = st.selectbox("Objet de votre message", ["Support technique", "Partenariat", "Suggestion", "Autre"])
            message = st.text_area("Votre message")
            
            envoyer = st.form_submit_button("Envoyer le message")
            
            if envoyer:
                if nom and email and message:
                    st.success("Merci ! Votre message a bien été envoyé. Nous vous répondrons rapidement.")
                    # Note : Dans une vraie application, vous ajouteriez ici 
                    # une fonction pour envoyer réellement l'email (ex: smtplib)
                else:
                    st.error("Veuillez remplir tous les champs obligatoires.")

    st.write("")
    st.caption("© 2026 MyHotelCompare — Tous droits réservés.")