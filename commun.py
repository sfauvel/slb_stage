
from datetime import datetime
import json

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
        self.data = None

    # Récupération des données et stockage dans un fichier json
    def rafraichir_donnees(self):
        pass

    # Charge les données depuis le fichier json
    def charger(self):
        pass

    # Retourne un document (DocumentHtml) qui servira à la génération du fichier final
    def preparer_document(self):
        pass


    def mise_a_jour(self, refresh = False):
        # Récupération depuis HelloAsso vers un fichier json
        if refresh:
            print(f"Chargement {self.nom}")
            now_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.rafraichir_donnees()
        else:
            now_string = "Pas de mise à jour"

        # Chargement des données depuis les fichiers json

        self.data = self.charger()

        document = self.preparer_document()
        self.creer_rapport(document, now_string)

        if not refresh:
            print("Données non rafraichies !!!")

    def lire_json(self):
        print(f"Charger {self.nom}")
        with open(f"data/{self.nom}.json"   , "r") as read_content:
            json_data = json.load(read_content)
        return json_data

    def creer_rapport(self, document, now_string):
        html = document.generer_rapport(self.nom, now_string)
        DocumentHtml.save(self.output_file, html)

    def recuperer_donnees(self, fonction_recuperation):
        print(f"Chargement {self.nom}")

        from hello_asso import OrganizationApi
        data_getter = OrganizationApi.get_event_participants

        from hello_asso import orga

        json_data = fonction_recuperation(orga, self.nom)
        #print(json_data)

        with open(f"data/{self.nom}.json", "w") as outfile:
            outfile.write(json.dumps(json_data, indent=4))
