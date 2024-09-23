from datetime import datetime
import json

import sys
sys.path.insert(0, '../helloasso')
from model import HelloAssoToModel

def mise_a_jour_boutique(shop, refresh = False):   

    if refresh:
        from hello_asso import orga
        print(f"Refresh {shop}")
        now_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        json_boutique = orga.get_shop_participants(shop)
        print(json_boutique)
        with open(f"data/{shop}.json", "w") as outfile:
            outfile.write(json.dumps(json_boutique, indent=4))
    else:
        now_string = "Pas de mise à jour"

    data = shop_charger(shop)
    nb_ventes = len(data) 
    generer_rapport(shop, nb_ventes, f"docs/ventes-boutique.html", now_string)

    if not refresh:
        print("Données non rafraichies !!!")

def shop_charger(event: str):
    print(f"Charger {event}")
    with open(f"data/{event}.json"   , "r") as read_content: 
        json_participants = json.load(read_content)

    billets = [HelloAssoToModel.new_item_vendu(json) for json in json_participants]      
    return billets
    #return Evenement(event, jours, billets)
    
# Idem stage.py. Mutaliser ?
def generate_html(body, style=""):
    return f"""<html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
        {style}
        </style>
    </head>
    <body>
        {body}
    </body>
</html>
"""

def generer_rapport(shop, nb_ventes, output_file, now_string):
    print(f"{shop}: {nb_ventes}")
    html = generate_html(f"""
            <div>Ventes boutique: {nb_ventes}</div>
            </br>
            <div>dernière mises à jour<br>{now_string}</div>""")
    
    with open(output_file, "w") as html_file:
        html_file.write(html)

