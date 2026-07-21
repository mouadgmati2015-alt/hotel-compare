import streamlit as st
import os
import json
from streamlit_carousel import carousel
from data.hotels_data import HOTELS_DATA
import streamlit as st
import streamlit.components.v1 as components


# Injection de la balise de vérification Google Search Console
google_tag = '<meta name="google-site-verification" content="UFPNwmAw5bpc..." />'
components.html(google_tag, height=0, width=0)
# Configuration de la page
st.set_page_config(page_title="HotelCompare", layout="wide")

# --- Style CSS ---
st.markdown("""
    <style>
    .stApp {
        background-color: #F8F9FA;
    }
    [data-testid="stSidebar"] { 
        min-width: 150px; 
        max-width: 150px; 
    }
    .block-container {
        padding-top: 1rem !important;
    }
    iframe {
        width: 100% !important;
    }
    [data-testid="collapsedControl"]::after {
        content: " Menu";
        font-size: 14px;
        font-weight: bold;
        color: #333;
        vertical-align: middle;
        margin-left: 5px;
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
    st.markdown("""
    <style>
    iframe {
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)
    # Carrousel
    test_items = [
        dict(title="", text="", img="https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?q=80&w=2000"),
        dict(title="", text="", img="https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1200&q=80"),
        dict(title="", text="", img="https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&q=80"),
        dict(title="", text="", img="https://images.unsplash.com/photo-1571896349842-33c89424de2d?auto=format&fit=crop&w=1200&q=80"),
        dict(title="", text="", img="https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=1200&q=80"),
        dict(title="", text="", img="https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=1200&q=80"),
        dict(title="", text="", img="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=2000")
    ]
    carousel(items=test_items, width=1)
   
    # --- Mode d'emploi ---
    
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
        {"titre": "Calendrier des bons plans pour voyager", "image": "images/test.jpg", "resume": "Les meilleures périodes pour voyager à moindre coût.", "details": """
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
    {
    "titre": "Comment fonctionnent les algorithmes de prix des hôtels",
    "image": "images/test2.jpg",  # Tu pourras changer l'image si tu en as une spécifique
    "resume": "Comprenez les mécanismes du pricing dynamique pour déjouer les hausses de tarifs et savoir exactement quand réserver au meilleur prix.",
    "details": """
Vous avez sûrement déjà remarqué ce phénomène frustrant : vous consultez le prix d'une chambre d'hôtel le lundi, vous y retournez le mercredi, et le tarif a augmenté de 20 %. Est-ce un hasard ? **Absolument pas.**

Derrière chaque écran de réservation se cachent des algorithmes complexes de *pricing dynamique*, conçus pour faire varier les prix en temps réel. En tant qu'utilisateurs de **HotelCompare**, comprendre ces mécanismes est votre meilleure arme pour payer le juste prix.

Voici comment ces systèmes fonctionnent et, surtout, quand vous devez réserver pour faire de vraies économies.

### 1. Comment les hôtels fixent (et font varier) leurs prix ?

Contrairement aux billets d'avion, les prix des hôtels ne dépendent pas uniquement de la date de votre départ. Les algorithmes de gestion des revenus (*Revenue Management*) intègrent une multitude de variables en continu :

*   **Le taux d'occupation en temps réel** : Plus un hôtel se remplit, plus l'algorithme augmente automatiquement les tarifs des chambres restantes pour maximiser le chiffre d'affaires.
*   **L'effet de saisonnalité et du calendrier** : Les week-ends, les vacances scolaires, les jours fériés mais aussi les événements locaux (concerts, salons professionnels, matchs) déclenchent des hausses automatiques.
*   **La vitesse de réservation (Booking Pace)** : Si un établissement se met à se remplir beaucoup plus vite que d'habitude à une date précise, le système interprète une forte demande et revoit les prix à la hausse de manière anticipée.

### 2. Le grand dilemme : Réserver tôt ou parier sur la dernière minute ?

C'est la question que tout le monde se pose. Faut-il jouer la carte de la sécurité ou tenter le coup de poker ? La réponse dépend entièrement de votre destination et de la période.

*   **Option A : La réservation anticipée (Early Booking) – La sécurité**
    *   *Pourquoi ?* Les hôtels lancent souvent leurs stocks avec des tarifs d'appel attractifs pour s'assurer un socle de remplissage.
    *   *Le risque zéro :* Vous avez le plus large choix de chambres et vous évitez la flambée des prix de dernière minute.
*   **Option B : La dernière minute – Le pari risqué**
    *   *Quand est-ce que ça fonctionne ?* Pour les grandes métropoles en basse saison ou les hôtels d'affaires le week-end, les établissements préfèrent brader leurs chambres vides plutôt que de les laisser inoccupées.
    *   *Le piège :* En haute saison ou dans les zones très touristiques, attendre la dernière minute signifie souvent qu'il ne reste que les chambres les plus chères (ou plus rien du tout).

### 3. Les fausses bonnes idées et les pièges à éviter

1.  **Le mythe de la navigation privée** : Contrairement aux idées reçues, les sites de réservation n'augmentent pas leurs prix en fonction de vos recherches répétées (cookies). Les variations de prix sont globales et s'appliquent à tous les utilisateurs.
2.  **Attendre le jour J en pensant que les prix vont s'effondrer** : Si le taux d'occupation de l'hôtel est bon, l'algorithme ne baissera jamais les prix. Il continuera au contraire de les monter pour cibler les voyageurs de dernière minute "coincés".

### En résumé : La stratégie gagnante avec HotelCompare

Pour dénicher la meilleure offre sans stress, voici la marche à suivre :

*   **Anticipez** dès que vous connaissez vos dates pour les périodes de forte affluence.
*   **Surveillez** l'évolution des prix en amont pour repérer la tendance du marché.
*   **Utilisez notre comparateur** sur HotelCompare pour visualiser en un coup d'œil les différentes options et identifier le moment où le rapport qualité-prix est optimal.

**Ne subissez plus les algorithmes : apprenez à jouer avec eux pour voyager plus souvent et moins cher !**
"""
}
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