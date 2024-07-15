import argparse
from stage import chargement_donnees, synthese_stages

stages = [
   ('stage-d-ete-2024-u9-a-u11', ["Lundi", "Mardi", "Mercredi"]),
   ('stage-d-ete-2024-u13-a-u21', ["Jeudi", "Vendredi"])
]

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--refresh', dest='refresh', action='store_true',
                    help='refresh the data')

args = parser.parse_args()

refresh=args.refresh
if refresh:
    now_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    for (event, days) in stages:
        chargement_donnees(event)
else:
    now_string = "Pas de mise à jour"

synthese_stages(stages, "docs/index.html", now_string)

if not refresh:
    print("Données non rafraichies !!!")
