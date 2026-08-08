import streamlit as st
import streamlit.components.v1 as components

def afficher_page():
    st.title("📞 Contactez-nous")
    st.markdown("---")

    # Composant HTML totalement indépendant pour forcer le design du bloc et du bouton
    html_code = """
    <div style="background-color: #1C2541; border: 1px solid #3A506B; border-radius: 12px; padding: 40px; text-align: center; font-family: sans-serif;">
        <h3 style="color: #FFFFFF; margin-bottom: 15px; font-size: 24px;">💬 Un besoin, une question ou une suggestion ?</h3>
        <p style="font-size: 16px; color: #FFFFFF; margin-bottom: 10px; line-height: 1.5;">
            Pour mieux vous répondre et assurer un suivi personnalisé, nous communiquons exclusivement par <b>message privé sur notre page Facebook</b>.
        </p>
        <p style="color: #94a3b8; font-size: 14px; margin-bottom: 30px;">Notre équipe vous répondra dans les plus brefs délais !</p>
        
        <a href="https://www.facebook.com/profile.php?id=61591545557027" target="_blank" style="background-color: #1877f2; color: #ffffff !important; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            💬 Envoyer un message sur Facebook
        </a>
    </div>
    """
    
    components.html(html_code, height=280, scrolling=False)