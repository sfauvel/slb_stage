# Need to do before : pip install helloasso_api


from helloasso_api import HaApiV5
from datetime import datetime
import json
import os
import re

#  class Event:
#      def __init__(self, name, all_days, effectif_par_jour):
#          self.name = name
#          self.all_days = all_days
#          self.effectif_par_jour = effectif_par_jour
 
#  class Participant:
#      def __init__(self, nom, prenom, categorie, jours):
         
#          self.nom=nom
#          self.prenom=prenom
#          self.categorie=categorie
#          self.jours=jours
 
#      def __str__(self):
#          return f"{self.nom}, {self.prenom}, {self.categorie}, {self.jours}"
 
#  class Stats:
#      def __init__(self, json):
#          self.json = json
     
#      def billets(self):
#          return [Billet.build(json) for json in self.json]
     
#      def par_type_de_billet(self):
#          return group_by(self.billets(), key_builder=lambda value: value.nom)
     
#      def tous_les_champs_specifiques(self, champs = None):
#          return [champ 
#                  for billet in self.billets() if len(billet.champs_specifiques) > 0 
#                  for champ in billet.champs_specifiques if champs is None or champ['name'].lower() in champs]
     
#  class Utilisateur:
#      def __init__(self, nom, prenom) -> None:
#          self.nom = nom
#          self.prenom = prenom
         
#      def build(json):
#          return Utilisateur(json['firstName'], json['lastName'])
     
#  class Billet:
#      def __init__(self, nom, utilisateur, champs_specifiques):
#          self.nom = nom
#          self.utilisateur = utilisateur
#          self.champs_specifiques = champs_specifiques
     
#      def build(json):
#          return Billet(json['name'], Utilisateur.build(json['user']), get_champ(json, 'customFields', []))
     
 
class OrganizationApi(object):
    
    def __init__(self, client, slug):
        self._base_url = "/v5/organizations"
        self._client = client
        self._slug = slug

    def get_by_slug(self) -> dict:
        return self._client.call(f"{self._base_url}/{self._slug}").json()


    def items(self, slug: str) -> dict:
        return self._client.call(f"{self._base_url}/{self._slug}").json()

    def call(self, route, params={}):
        url_params = "&".join([f"{key}={value}" for (key, value) in params.items()])
        request = f'{self._base_url}/{self._slug}/{route}?{url_params}'
        print(request)
        return self._client.call(request).json()
          

    def get_all_items_data(self, url: str, params={}, max_page=1000) -> dict:
        page_index = 1
        page_size = 30
        
        json_data = []
        params["pageSize"] = page_size
        while max_page > 0:
            max_page -= 1
            params["pageIndex"] = page_index
            json = self.call(url, params)
            
            json_data = json_data + json["data"]
            if (len(json["data"]) < page_size):
                break
            page_index += 1
        return json_data

    def get_event_participants(self, event: str) -> dict:
        params = {
            "withDetails": "true",
            "sortOrder": "Desc",
            "sortField": "Date"
        }
        return self.get_all_items_data(f"forms/Event/{event}/items", params)
    
    def get_memberships(self, event: str, max_page) -> dict:
        params = {
            "withDetails": "true",
            "sortOrder": "Desc",
            "sortField": "Date"
        }
        return self.get_all_items_data(f"forms/Membership/{event}/items", params, max_page)
 
    # def get_stats(self, event: str) -> Stats:
    #     # json_participants = self.get_event_participants(event)

    #     # with open(f"{event}.json", "w") as outfile:
    #     #     outfile.write(json.dumps(json_participants, indent=4))
            
    #     with open(f"{event}.json"   , "r") as read_content: 
    #         json_participants = json.load(read_content)

    #     return Stats(json_participants)
    
    def get_extract_event_participants(self, event: str, jours) -> dict:
    
        stat = self.get_stats(event)
        
        def get_one_key(data, criteria):
            key = get_at_most_one_key(data, criteria)
            assert(key is not None)
            return key
                
        def get_at_most_one_key(data, criteria, default_key=None):
            keys = [key for key in data.keys() if criteria(key)]
            assert(len(keys) <= 1)
            if (len(keys) == 1):
                return keys[0]
            else:
                return default_key
        
        def count_with_key_criteria(data, criteria):
            return sum([len(value) for (key, value) in data.items() if criteria(key)])
        

        def compter_participants(day, jours_choisis, par_type_billet):
            nb = sum([len(size) for (key_day, size) in jours_choisis.items() if day.lower() in key_day.lower() ])
            tous_les_jours = count_with_key_criteria(par_type_billet, lambda key: f"{len(jours)} jour" in key)
            return nb + tous_les_jours
        
        ##### >>
        print(">>>>>>>>>")
        par_type_billet = group_by(stat.billets(), lambda _: _.nom)
        afficher_nombre_par_entree(par_type_billet)
        
        champs_jour = [champ for champ in stat.tous_les_champs_specifiques(['2 jours', '1 jour', 'jour'])]
        jours_choisis = group_by(champs_jour, lambda _: _['answer'])
        
        effectif_par_jour = {day : compter_participants(day, jours_choisis, par_type_billet) for day in jours}
        
        print(effectif_par_jour)
        print("<<<<<<<<<")
        ##### <<
    
        print(f"=== {event} ===")
   
        return Event(event, jours, effectif_par_jour)

    def get_shop_nb_participants(self, shop: str) -> int:
        params = {
            "pageSize": 1,
            "pageIndex": 1,
        }
        json = self.call(f"forms/Shop/{shop}", params)
        total = json["pagination"]["totalCount"]
        return total

# def print_response(json_response):
#     for k,v in json_response.items():
#         print(f"{k}=> {v}\n")

# def print_by_day(json_data):
#     print(json_data)
#     data = json_data
#     for d in data:
#         print(f"{d['user']['firstName']} | {d['user']['lastName']} | {d['name']} | {d['payer']['email']}")

#         customFields = d['customFields']
#         for field in customFields:
#             print(f"   {field['name']}: {field['answer']}")
        
#         jours = []
#         Participant(d['user']['lastName'], d['user']['firstName'], d['customFields']['Catégorie'], jours)

# def generate_html(body, style=""):
#     return f"""<html>
#     <head>
#         <meta name="viewport" content="width=device-width, initial-scale=1">
#         <style>
#         {style}
#         </style>
#     </head>
#     <body>
#         {body}
#     </body>
# </html>
# """

  
    
api = HaApiV5(
        api_base='api.helloasso.com',
        client_id=os.getenv('CLIENT_ID'),
        client_secret=os.getenv('CLIENT_SECRET'),
        timeout=60
    )


now_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

slug = 'sainte-luce-basket'
orga = OrganizationApi(api, slug)

