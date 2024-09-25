import argparse
from stage import UnStage, Stages
from boutique import Boutique


stages = [
   UnStage('stage-d-automne-2024-u7-a-u11', ["lundi", "mardi", "mercredi"]),
   UnStage('stage-d-automne-2024-u13-a-u21', ["jeudi", "vendredi"])
]

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--refresh', dest='refresh', action='store_true',
                    help='refresh the data')

args = parser.parse_args()

refresh=args.refresh

# mise_a_jour_stages("Automne 2024", stages, refresh)
stages_group = Stages("Automne 2024", stages)
stages_group.mise_a_jour(refresh)

#mise_a_jour_boutique("commande-surmaillots-10-2024", refresh)
boutique = Boutique("commande-surmaillots-10-2024")
boutique.mise_a_jour(refresh)