import argparse
from datetime import datetime
from stage import Stage, synthese_stages
from boutique import mise_a_jour_boutique

def mise_a_jour_stages(nom, stages, refresh = False):
    if refresh:
        
        now_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        for (event, days) in stages:
            print(f"Chargement {event}")
            Stage(event).chargement_donnees()
    else:
        now_string = "Pas de mise à jour"

    synthese_stages(nom, stages, "docs/index.html", now_string)

    if not refresh:
        print("Données non rafraichies !!!")
    

stages = [
   ('stage-d-automne-2024-u7-a-u11', ["Lundi", "Mardi", "Mercredi"]),
   ('stage-d-automne-2024-u13-a-u21', ["Jeudi", "Vendredi"])
]

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--refresh', dest='refresh', action='store_true',
                    help='refresh the data')

args = parser.parse_args()

refresh=args.refresh

mise_a_jour_stages("Automne 2024", stages, refresh)

mise_a_jour_boutique("commande-surmaillots-10-2024", refresh)