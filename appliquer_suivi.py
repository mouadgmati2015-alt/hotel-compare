"""
Ajoute le suivi des clics (Google Analytics) sur les restaurants et lieux
de la page « Itinéraire découverte ».

À lancer UNE SEULE FOIS, depuis le dossier qui contient itineraire.py :
    python appliquer_suivi.py

Le script :
  - vérifie que chaque endroit à modifier existe exactement une fois ;
  - ne modifie RIEN s'il y a le moindre doute ;
  - garde une copie de sauvegarde : itineraire.py.bak
"""
import shutil
import sys
from pathlib import Path

FICHIER = Path("itineraire.py")

REMPLACEMENTS = [
    # 1. Chaque lieu reçoit son nom, sa catégorie et son étape
    ("function lieuHtml(x,sous){",
     "function lieuHtml(x,sous,cat,etape){"),
    ('<li class="it-lieu"><div>',
     '<li class="it-lieu" data-suivi-etab="1" data-nom="${esc(x.nom)}" '
     'data-cat="${esc(cat)}" data-etape="${esc(etape)}"><div>'),
    # 2. Les deux liens cliquables sont repérés
    ('rel="noopener nofollow">Site</a>',
     'rel="noopener nofollow" data-suivi="site">Site</a>'),
    ('rel="noopener nofollow">Carte</a>',
     'rel="noopener nofollow" data-suivi="carte">Carte</a>'),
    # 3. La catégorie et l'étape sont transmises depuis les listes
    ("function liste(titre,arr,sous,vide){",
     "function liste(titre,arr,sous,vide,cat,etape){"),
    ("lieuHtml(x,sous(x))",
     "lieuHtml(x,sous(x),cat,etape)"),
    ('"Aucun lieu remarquable trouvé sur ce tronçon.")',
     '"Aucun lieu remarquable trouvé sur ce tronçon.","visite",ville)'),
    ('"Aucun restaurant trouvé près du milieu de la journée.")',
     '"Aucun restaurant trouvé près du milieu de la journée.","dejeuner",ville)'),
    ('"Aucun restaurant trouvé dans cette ville.");',
     '"Aucun restaurant trouvé dans cette ville.","diner",ville);'),
]

# 4. Envoi de l'événement à Google Analytics quand on clique
ECOUTEUR = '''// Suivi des clics sur les lieux et restaurants (Google Analytics)
document.addEventListener("click",function(ev){
 const lien=ev.target.closest&&ev.target.closest("[data-suivi]");
 const carte=lien&&lien.closest("[data-suivi-etab]");
 if(!carte||typeof gtag!=="function")return;
 gtag("event","clic_etablissement",{type_clic:lien.getAttribute("data-suivi"),etab_nom:carte.getAttribute("data-nom"),etab_categorie:carte.getAttribute("data-cat"),etab_etape:carte.getAttribute("data-etape")});
},true);
'''
FIN_SCRIPT = "</script>\n</body>"


def main():
    if not FICHIER.exists():
        print("Je ne trouve pas itineraire.py ici. Placez-vous dans le dossier "
              "comparateur-ia, puis relancez.")
        return 1

    texte = FICHIER.read_text(encoding="utf-8")

    if "clic_etablissement" in texte:
        print("Le suivi est déjà installé. Rien à faire.")
        return 0

    for ancien, nouveau in REMPLACEMENTS + [(FIN_SCRIPT, ECOUTEUR + FIN_SCRIPT)]:
        n = texte.count(ancien)
        if n != 1:
            print(f"ARRÊT : cet endroit est présent {n} fois au lieu d'une :")
            print("   " + ancien.splitlines()[0])
            print("Aucune modification n'a été faite. Envoyez-moi ce message.")
            return 1
        texte = texte.replace(ancien, nouveau)

    shutil.copy(FICHIER, "itineraire.py.bak")
    FICHIER.write_text(texte, encoding="utf-8")
    print("Terminé. Une sauvegarde a été créée : itineraire.py.bak")
    print("Relancez maintenant votre générateur pour recréer le site.")
    return 0


if __name__ == "__main__":
    sys.exit(main())