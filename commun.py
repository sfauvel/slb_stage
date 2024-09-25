
from datetime import datetime

class JsonTools:
    def append_to_dict(dict, key, value):
        if not key in dict:
            dict[key] = []
        dict[key].append(value)
        
    def group_by(list, value_builder=lambda data: data, key_builder=lambda key: key):
        dict = {}
        for data in list:
            value = value_builder(data)
            JsonTools.append_to_dict(dict, key_builder(value), value)
        return dict
    
class DocumentHtml(object): 
    def generer_html(self, body, style=""):
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
    
    def save(output_file, content):
        with open(output_file, "w") as filename:
            filename.write(content)
            
class SyntheseHelloAsso(object):
    def __init__(self, nom) -> None:
        self.nom = nom
    
    def chargement_donnees(self):
        pass
    
    def synthese(self, now_string):
        pass
    
    def mise_a_jour(self, refresh = False):   

        if refresh:
            print(f"Chargement {self.nom}")
            now_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.chargement_donnees()
        else:
            now_string = "Pas de mise à jour"

        self.synthese(now_string)

        if not refresh:
            print("Données non rafraichies !!!")

