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
    [data-testid="column"] {
        background-color: #f9f9f9;
        border: 1px solid #e0e0e0;
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Navigation ---
page = st.sidebar.radio("Navigation", ["Comparateur", "Blog"])

if page == "Comparateur":
    # En-tête
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
    
    # --- Mode d'emploi ---
    st.markdown("---")
    st.subheader("💡 Comment comparer vos hôtels")
    st.markdown("""
    1. **Sélectionnez** vos deux hôtels dans les menus déroulants ci-dessous.
    2. **Cliquez** sur le bouton rouge **Comparer**.
    3. **Découvrez** les points forts et points faibles pour faire votre choix !
    """)
    st.markdown("---")
    
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
    
    articles = [
        {"titre": "5 astuces d'expert pour voyager moins cher", "image": "images/image_astuce.jpg", "resume": "Voyager ne signifie pas forcément se ruiner.", "details": """
Vous rêvez de vacances inoubliables sans pour autant faire exploser votre budget ? En tant qu'experts chez **HotelCompare**, nous analysons quotidiennement les tendances tarifaires. Voici nos 5 astuces imparables.

### 1. La règle d'or : La flexibilité des dates
C’est le facteur n°1 qui influence le prix. Décaler vos dates de départ de seulement 48 heures peut vous faire économiser jusqu'à 30 %.

*   **Conseil d'expert** : Privilégiez les départs en milieu de semaine, souvent moins demandés que les week-ends.

### 2. Anticipez ou profitez des "Last Minute"
Il existe deux écoles pour économiser :

*   **Early Booking** : Idéal pour les familles aux dates précises, avec des réductions pour les réservations effectuées des mois à l'avance.
*   **Dernière minute** : Pour les aventuriers, la dernière semaine permet parfois de dénicher des offres incroyables sur les chambres invendues.

### 3. Comparez intelligemment sur HotelCompare
Un tarif bas n'est pas toujours une économie s'il exclut les services essentiels (petit-déjeuner, Wi-Fi, etc.).

*   **Notre astuce** : Utilisez nos filtres avancés pour comparer le rapport qualité-prix global plutôt que le prix facial.

### 4. Visez la "basse saison" ou l'entre-deux
Si les mois de juillet et août sont les plus coûteux, les périodes de **mai-juin** ou **septembre-octobre** offrent un climat idéal avec des tarifs nettement plus attractifs.

### 5. Abonnez-vous aux alertes prix
La tarification hôtelière est dynamique. Sur **HotelCompare**, créez une alerte sur votre destination préférée pour être notifié dès que les prix baissent.

**Ne payez plus jamais trop cher pour vos vacances.** Grâce à HotelCompare, comparez en toute transparence et trouvez l'offre qui respecte votre budget.
"""},
        {"titre": "Le guide ultime pour choisir son hôtel en Tunisie", "image": "images/image_hotel.jpg", "resume": "Choisir le mauvais hôtel peut gâcher un séjour.", "details": """
Choisir l'hébergement idéal pour ses vacances peut parfois ressembler à un casse-tête, surtout face à la richesse des destinations tunisiennes. Que vous soyez attiré par le charme historique de Djerba, l'effervescence de Sousse, ou la douceur de vivre à Hammamet et Nabeul, le choix de votre pied-à-terre est décisif.

Sur **HotelCompare**, nous avons simplifié cette étape cruciale.

### 1. Définissez votre priorité géographique
La Tunisie offre des ambiances radicalement différentes :

*   **Djerba** : Idéal pour une immersion totale dans le calme, les plages de sable fin et l'architecture traditionnelle des menzels.
*   **Hammamet & Nabeul** : Le compromis parfait entre vie nocturne, culture et stations balnéaires.
*   **Sousse** : Parfait si vous cherchez le dynamisme, les activités nautiques et la proximité avec la Médina.

### 2. Analysez les points forts et points faibles en un coup d'œil
Chaque voyageur a ses exigences. Sur HotelCompare, nous mettons en avant :

*   **Les points forts** : Proximité de la plage, qualité des services, animations ou calme recherché.
*   **Les points faibles** : Nous jouons la carte de la franchise, qu'il s'agisse d'un éloignement des centres d'intérêt ou d'une infrastructure vieillissante.

### 3. Pourquoi utiliser HotelCompare ?
Plutôt que de perdre des heures, notre moteur automatise l'analyse pour vous grâce à une architecture intégrant des données géo-localisées :

*   Informations mises à jour en temps réel.
*   Affichage clair pour comparer les prestations côte à côte.
*   Aide à la décision basée sur des critères objectifs.

**Prêt à organiser votre prochaine escapade en Tunisie ?**
Explorez dès maintenant nos listings sur et trouvez l'hôtel qui correspond exactement à vos envies.
"""},
        {"titre": "Découvrir la Tunisie autrement", "image": "images/image_tunisie.jpg", "resume": "Sortir des sentiers battus.", "details": """
La Tunisie est souvent associée à ses magnifiques stations balnéaires. Pourtant, au-delà des piscines, se cache une terre de contrastes saisissants, d'histoire millénaire et d'hospitalité légendaire.

### 1. Changez de décor : Cap sur le Sud
Pour découvrir la Tunisie autrement, il faut savoir s'éloigner du rivage. Le désert du Sahara, avec ses étendues infinies de dunes, offre un silence rare.

*   **L'expérience** : Passez une nuit dans un campement sous les étoiles à Douz ou explorez les maisons troglodytes de Matmata.

### 2. Le charme des maisons d'hôtes
Pour une immersion totale, rien ne vaut les **Dar** ou les **Menzels**. Ces maisons traditionnelles offrent un confort moderne tout en préservant l'âme architecturale locale.

*   **Pourquoi essayer ?** Vous bénéficierez d'un accueil personnalisé et d'une cuisine faite maison aux saveurs authentiques.

### 3. Vivez au rythme des traditions
La Tunisie se découvre par ses sens :

*   **Gastronomie** : Partez à la découverte des marchés locaux pour goûter à une brik artisanale, une ojja épicée ou un couscous traditionnel.
*   **Artisanat** : Visitez les ateliers de tissage à Kairouan ou de poterie à Guellala (Djerba).

### 4. Comment HotelCompare vous accompagne
Sur **HotelCompare**, nous filtrons pour vous ces hébergements atypiques :

*   **Filtres avancés** : Recherchez par style (maison d'hôtes, boutique-hôtel, éco-lodge).
*   **Localisation optimisée** : Accédez à des lieux moins touristiques, au plus près de la vie locale.

**La Tunisie est une destination à multiples facettes.** Explorez nos sélections spéciales sur [HotelCompare](http://ton-lien-ici.com) et commencez à planifier votre voyage hors des sentiers battus.
"""},
        {"titre": "Voyager en AFRIQUE : Conseils et Astuces", "image": "images/image_afrique.jpg", "resume": "Guide essentiel pour une préparation sereine.", "details": """
Préparer un voyage en Afrique demande une organisation rigoureuse. Voici un guide pour aborder votre préparation en toute sérénité.

### 1. Aspect Sanitaire : Anticiper pour voyager serein
La santé est une priorité. Consultez un médecin ou un centre de vaccination au moins 4 à 8 semaines avant le départ.

*   **Vaccinations** : La **Fièvre jaune** est souvent obligatoire (carnet jaune). Assurez-vous d'être à jour pour les vaccins universels (DTP, etc.). D'autres vaccins (Hépatite A/B, typhoïde, rage) peuvent être conseillés selon votre destination.
*   **Paludisme (Malaria)** : La prévention repose sur la **protection antivectorielle** (vêtements longs, répulsifs, moustiquaire) et la **chimioprophylaxie** (traitement préventif sur avis médical).
*   **Hygiène** : Ne buvez que de l'eau en bouteille capsulée, privilégiez les aliments bien cuits et évitez les glaçons.

### 2. Formalités d'entrée
Les règles varient drastiquement. Consultez toujours les sites officiels des Affaires étrangères.

*   **Passeport** : Validité d'au moins 6 mois après la date de retour et au moins deux pages vierges.
*   **Visa** : Vérifiez si vous êtes dispensé, si un **e-visa** est requis ou si le visa à l'arrivée est possible.
*   **Assurance voyage** : Une nécessité absolue pour couvrir les frais médicaux et le rapatriement sanitaire.

### 3. Conseils d'experts pour vos préparatifs
*   **Numérisation** : Scannez vos documents (passeport, visa, assurance) sur un Cloud sécurisé.
*   **Inscription consulaire** : Si vous êtes français, inscrivez-vous sur le portail **"Fil d'Ariane"**.
*   **Trousse à pharmacie** : Prévoyez une trousse complète (pansements, antidiarrhéiques, paracétamol, antibiotiques).

**Dernier rappel** : Les conditions évoluent rapidement. Vérifiez les sites des ambassades quelques semaines avant votre départ !
"""},
        {"titre": "Calendrier des bons plans", "image": "images/test.jpg", "resume": "Les meilleures périodes pour voyager à moindre coût.", "details": """
Pour voyager à moindre coût, la règle d'or est de privilégier le "hors-saison" ou les périodes d'intersaison. Voici une tendance générale des destinations abordables mois par mois :

### Calendrier des destinations économiques

*   **Janvier & Février** : Idéal pour les escapades citadines européennes. *Destinations : Londres, New York, Copenhague, Marrakech.*
*   **Mars** : Tarifs compétitifs avant le renouveau printanier. *Destinations : Afrique du Sud, Maghreb, Europe de l'Est.*
*   **Avril & Mai** : Excellent rapport qualité-prix en Europe. *Destinations : Bulgarie, Roumanie, Croatie, Maghreb.*
*   **Juin & Septembre** : Les mois les plus favorables financièrement. *Destinations : Grèce, Espagne, Italie, Bali.*
*   **Juillet & Août** : Haute saison. Privilégiez des lieux moins prisés ou réservez très longtemps à l'avance. *Destinations : Grèce (Cyclades), Portugal, Turquie, Albanie.*
*   **Octobre & Novembre** : Arrière-saison méditerranéenne idéale. *Destinations : Espagne, Italie, Croatie.*
*   **Décembre** : Prix bas hors période de fêtes, sauf pour les destinations hivernales.

### Conseils d'expert pour réduire vos coûts

1.  **Flexibilité** : Utilisez les outils de recherche "mois le moins cher" sur les comparateurs pour identifier les fluctuations.
2.  **Destinations "Budget"** : Certains pays comme la **Bulgarie**, le **Vietnam**, le **Cambodge** ou l'**Albanie** permettent un coût de vie très faible (parfois moins de 30€/jour).
3.  **Réservation** : Pour les destinations estivales prisées, l'anticipation reste votre meilleure arme pour maîtriser votre budget.

**Voyagez intelligemment en choisissant la bonne période pour votre destination !**
"""},
    ]

    if 'page_ouverte' not in st.session_state:
        st.session_state.page_ouverte = None

    if st.session_state.page_ouverte:
        art = st.session_state.page_ouverte
        st.header(art['titre'])
        st.image(art['image'], use_container_width=True)
        st.markdown(art['details'])
        if st.button("⬅️ Retour au blog"):
            st.session_state.page_ouverte = None
            st.rerun()
    else:
        for i in range(0, len(articles), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(articles):
                    art = articles[i + j]
                    with cols[j]:
                        st.image(art['image'], use_container_width=True)
                        st.subheader(art['titre'])
                        st.write(art['resume'])
                        if st.button("Lire la suite", key=art['titre']):
                            st.session_state.page_ouverte = art
                            st.rerun()