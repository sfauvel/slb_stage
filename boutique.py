from datetime import datetime
import json

import sys
sys.path.insert(0, '../helloasso')
from model import HelloAssoToModel

from commun import DocumentHtml, JsonTools, SyntheseHelloAsso

class DocumentBoutique(DocumentHtml):
    def __init__(self, nb_ventes) -> None:
        super().__init__()
        self.nb_ventes = nb_ventes
    
    def generer_rapport(self, shop, now_string):
        print(f"{shop}: {self.nb_ventes}")
        html = DocumentHtml().generer_html(f"""
                <h3>{shop}</h3>
                <div>Ventes: {self.nb_ventes}</div>
                </br>
                <div>dernière mises à jour<br>{now_string}</div>""")
        return html
    

class Boutique(SyntheseHelloAsso):
    
    def __init__(self, nom) -> None:
        super().__init__(nom)
        self.output_file = "docs/ventes-boutique.html"

    def rafraichir_donnees(self):
        from hello_asso import OrganizationApi
        super().recuperer_donnees(OrganizationApi.get_shop_participants)

    def preparer_document(self):
        nb_ventes = len(self.data) 
        return DocumentBoutique(nb_ventes)

    def charger(self):
        json_data = self.lire_json()
        billets = [HelloAssoToModel.new_item_vendu(json) for json in json_data]      
        return billets
    