# Need to do before : pip install helloasso_api

import argparse
from datetime import datetime
import json

import sys
sys.path.insert(0, '../helloasso')
from model import HelloAssoToModel

class Evenement(object): 
    
    def __init__(self, nom, jours, billets):
        self.nom = nom
        self.jours = jours
        self.billets = billets
    
    def par_type_de_billet(self):
        return group_by(self.billets, key_builder=lambda value: value.nom)
    
    def tous_les_champs_specifiques(self, champs = None):
        return [champ 
                for billet in self.billets
                for champ in billet.tous_les_champs_specifiques(champs)]
    
    def charger(event: str, jours: list):
        with open(f"data/{event}.json"   , "r") as read_content: 
            json_participants = json.load(read_content)

        billets = [HelloAssoToModel.new_adhesion(json) for json in json_participants]      
        
        return Evenement(event, jours, billets)
    
    def effectif_par_jour(self):
        par_type_billet = group_by(self.billets, lambda _: _.nom)
        champs_jour = [champ for champ in self.tous_les_champs_specifiques(['2 jours', '1 jour', 'jour'])]
        jours_choisis = group_by(champs_jour, lambda _: _.reponse)
        
        def count_with_key_criteria(data, criteria):
            return sum([len(value) for (key, value) in data.items() if criteria(key)])
        
        def compter_participants(day, jours_choisis, par_type_billet):
            nb = sum([len(size) for (key_day, size) in jours_choisis.items() if day.lower() in key_day.lower() ])
            tous_les_jours = count_with_key_criteria(par_type_billet, lambda key: f"{len(self.jours)} jour" in key)
            return nb + tous_les_jours
        
        return {day : compter_participants(day, jours_choisis, par_type_billet) for day in self.jours}
       

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
    
def chargement_donnees(event):
    
    from hello_asso import orga

    json_participants = orga.get_event_participants(event)
    print(json_participants)

    with open(f"data/{event}.json", "w") as outfile:
        outfile.write(json.dumps(json_participants, indent=4))
        
def synthese_stages(stages, output_file, now_string):
   
    events = [ Evenement.charger(event, days) for (event, days) in stages]

    all_days = [day.lower() for (_, days) in stages for day in days]
    
    effectif_par_jour = []
    for day in all_days:
        nb = sum([effectif 
                  for event in events 
                  for (jour, effectif) in event.effectif_par_jour().items() 
                  if jour.lower() == day.lower()])
        effectif_par_jour.append((day, nb))
        print(f"{day}: {nb}")
        
    generer_rapport(effectif_par_jour, output_file, now_string)

        
def generer_html(body, style=""):
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

def generer_rapport(effectif_par_jour, output_file, now_string):
    html_days = ("\n"+(" "*4*3)).join([f"<tr><td>{day}</td><td>{nb}</td></tr>" for (day, nb) in effectif_par_jour])
    html = generer_html(f"""
            Inscription aux stages
            <table>
            {html_days}
            </table>
            dernière mises à jour<br>{now_string}""",
            style=f"""
                table, th, td {{
                    margin: 1em;
                    border: 1px solid black;
                    border-collapse: collapse;
                }}
                td {{
                    padding: 5px;
                    text-align: center;
                }}
                tr:nth-child(odd) {{
                    background-color: #a4c2f7;
                }}""")

    with open(output_file, "w") as html_file:
        html_file.write(html)

# def get_champ(json, champ, default = None):
#     return json[champ] if champ in json else default
    

def append_to_dict(dict, key, value):
    if not key in dict:
        dict[key] = []
    dict[key].append(value)
    
def group_by(list, value_builder=lambda data: data, key_builder=lambda key: key):
    dict = {}
    for data in list:
        value = value_builder(data)
        append_to_dict(dict, key_builder(value), value)
    return dict

def afficher_nombre_par_entree(dict):
    for k, v in dict.items():
        print(f"{k}: {len(v)}")
        
