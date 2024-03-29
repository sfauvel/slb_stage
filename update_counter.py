# Need to do before : pip install helloasso_api


from helloasso_api import HaApiV5
from datetime import datetime
import json
import os

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
        request = f'{self._base_url}/{self._slug}/{route}/items?{url_params}'
        print(request)
        return self._client.call(request).json()
          

    def get_all_items_data(self, url: str, params={}) -> dict:
        page_index = 1
        page_size = 20
        
        json_data = []
        params["pageSize"] = page_size
        while True:
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
        return self.get_all_items_data(f"forms/Event/{event}", params)
    
    def get_extract_event_participants(self, event: str, jours) -> dict:
        json_participants = self.get_event_participants(event)
        participants = extract_participants(json_participants, jours)
        return Event(event, jours, participants)

    def get_shop_nb_participants(self, shop: str) -> int:
        params = {
            "pageSize": 1,
            "pageIndex": 1,
        }
        json = self.call(f"forms/Shop/{shop}", params)
        total = json["pagination"]["totalCount"]
        return total

def print_response(json_response):
    for k,v in json_response.items():
        print(f"{k}=> {v}\n")

class Event:
    def __init__(self, name, all_days, participants):
        self.name = name
        self.all_days = all_days
        self.participants = participants

class Participant:
    def __init__(self, nom, prenom, categorie, jours):
        
        self.nom=nom
        self.prenom=prenom
        self.categorie=categorie
        self.jours=jours

    def __str__(self):
        return f"{self.nom}, {self.prenom}, {self.categorie}, {self.jours}"

def print_by_day(json_data):
    print(json_data)
    data = json_data
    for d in data:
        print(f"{d['user']['firstName']} | {d['user']['lastName']} | {d['name']} | {d['payer']['email']}")

        customFields = d['customFields']
        for field in customFields:
            print(f"   {field['name']}: {field['answer']}")
        
        jours = []
        Participant(d['user']['lastName'], d['user']['firstName'], d['customFields']['Catégorie'], jours)

def extract_participants(json_data, all_days):
    data = json_data
    participants=[]
    for d in data:
        customFields = d['customFields']
        categorie = [field['answer'] for field in customFields if field['name'] == 'Catégorie'][0]

        if f"{len(all_days)} jour" in d['name']:
            jours = all_days
        else:
            jours_answer = " / ".join([field['answer'] for field in customFields if field['name'].lower() == '2 jours' or field['name'].lower() == '1 jour'])
            jours = list(dict.fromkeys(jours_answer.split(" / ")))

        participants.append(Participant(d['user']['lastName'], d['user']['firstName'], categorie, jours))

    return participants

def count_participants_by_day(event):
    all_days = event.all_days
    participants = event.participants

    for day in all_days:
        nb = len([p for p in participants if day in p.jours])
        print(f"{day}: {nb}")

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

def shop(shop, output_file):
    
    nb_ventes = orga.get_shop_nb_participants(shop)

    html = generate_html(f"""
            <div>Ventes boutique: {nb_ventes}</div>
            </br>
            <div>dernière mises à jour<br>{now_string}</div>""")
    
    with open(output_file, "w") as html_file:
        html_file.write(html)
    
def stage(stages, output_file):
    events = [orga.get_extract_event_participants(event, days) for (event, days) in stages]
    
    html_days = "\n"
    for day in [day for (event, days) in stages for day in days]:
        nb = len([p for event in events for p in event.participants if day in p.jours])
        print(f"{day}: {nb}")
        html_days += (" "*4*3) + f"<tr><td>{day}</td><td>{nb}</td></tr>\n"

    html = generate_html(f"""
            Inscription aux stages
            <table>{html_days}
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


api = HaApiV5(
        api_base='api.helloasso.com',
        client_id=os.getenv('CLIENT_ID'),
        client_secret=os.getenv('CLIENT_SECRET'),
        timeout=60
    )


now_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

slug = 'sainte-luce-basket'
orga = OrganizationApi(api, slug)

stage([
    ('stage-de-printemps-2024-u7-a-u11', ["Lundi", "Mardi", "Mercredi"]),
    ('stage-de-printemps-2024-u13-a-u20', ["Jeudi", "Vendredi"])
], "docs/index.html")

shop("commande-surmaillots", "docs/ventes-boutique.html")