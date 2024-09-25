from datetime import datetime
import json

import sys
sys.path.insert(0, '../helloasso')
from model import HelloAssoToModel

from commun import DocumentHtml, JsonTools, SyntheseHelloAsso

class DocumentBoutique(DocumentHtml):
    def __init__(self) -> None:
        super().__init__()
       
    
    def generer_rapport(self, shop, nb_ventes, now_string):
        print(f"{shop}: {nb_ventes}")
        html = DocumentHtml().generer_html(f"""
                <h3>{shop}</h3>
                <div>Ventes: {nb_ventes}</div>
                </br>
                <div>dernière mises à jour<br>{now_string}</div>""")
        return html
    

class Boutique(SyntheseHelloAsso):
    
    def __init__(self, nom) -> None:
        super().__init__(nom)
        self.output_file = "docs/ventes-boutique.html"

    def chargement_donnees(self):    
        from hello_asso import orga
        
        json_boutique = orga.get_shop_participants(self.nom)
        #print(json_boutique)
        
        with open(f"data/{self.nom}.json", "w") as outfile:
            outfile.write(json.dumps(json_boutique, indent=4))

    def synthese(self, now_string):
        data = self.charger()
        nb_ventes = len(data) 
        
        html = DocumentBoutique().generer_rapport(self.nom, nb_ventes, now_string)
        DocumentHtml.save(self.output_file, html)

    def charger(self):
        event=self.nom
        print(f"Charger {event}")
        with open(f"data/{event}.json"   , "r") as read_content: 
            json_participants = json.load(read_content)

        billets = [HelloAssoToModel.new_item_vendu(json) for json in json_participants]      
        return billets
    