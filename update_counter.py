# Need to do before : pip install helloasso_api


from helloasso_api import HaApiV5
from datetime import datetime
import json
import os

class OrganizationApi(object):
    def __init__(self, client, slug):
        self._client = client
        self._slug = slug

    def get_by_slug(self) -> dict:
        return self._client.call(f"/v5/organizations/{self._slug}").json()


    def items(self, slug: str) -> dict:
        return self._client.call(f"/v5/organizations/{self._slug}").json()


    def get_event_participants(self, event: str) -> dict:
        return self._client.call(f"/v5/organizations/{self._slug}/forms/Event/{event}/items?pageIndex=1&pageSize=20&withDetails=true&sortOrder=Desc&sortField=Date").json()

    def get_extract_event_participants(self, event: str, jours) -> dict:
        json_participants = self.get_event_participants(event)
        participants = extract_participants(json_participants, jours)
        return Event(event, jours, participants)


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

def print_by_day(json_response):
    print(json_response)
    data = json_response["data"]
    for d in data:
        print(f"{d['user']['firstName']} | {d['user']['lastName']} | {d['name']} | {d['payer']['email']}")

        customFields = d['customFields']
        for field in customFields:
            print(f"   {field['name']}: {field['answer']}")
        
        jours = []
        Participant(d['user']['lastName'], d['user']['firstName'], d['customFields']['Catégorie'], jours)

def extract_participants(json_response, all_days):
    data = json_response["data"]
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





api = HaApiV5(
        api_base='api.helloasso.com',
        client_id=os.getenv('CLIENT_ID'),
        client_secret=os.getenv('CLIENT_SECRET'),
        timeout=60
    )


now_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

slug = 'sainte-luce-basket'
orga = OrganizationApi(api, slug)
#json_orga = orga.get_by_slug()
#print(json_orga)
#print_response(json_orga)

event_1 = orga.get_extract_event_participants('stage-d-hiver-2024-u7-a-u11', ["Lundi", "Mardi", "Mercredi"])
participants_1 = event_1.participants
event_2 = orga.get_extract_event_participants('stage-d-hiver-2024-u13-a-u20', ["Jeudi", "Vendredi"])
participants_2 = event_2.participants


#print("\n".join([str(participant) for participant in participants_1 + participants_2]))
#count_participants_by_day(event_1 + event_2)
#str_particpants = str(json_participants).replace("Stage d'hiver 2024 U7 à U11", "Stage dhiver 2024 U7 à U11").replace("Personne à prévenir en cas d'urgence", "Personne à prévenir en cas durgence").replace("'",'"').replace("False","'False'")
#print(str_particpants)

html_days = "\n"
for day in (event_1.all_days + event_2.all_days):
    nb = len([p for p in event_1.participants if day in p.jours]) + len([p for p in event_2.participants if day in p.jours])
    print(f"{day}: {nb}")
    html_days += (" "*4*3) + f"<tr><td>{day}</td><td>{nb}</td></tr>\n"


html = f"""
<html>
    <head>
        <style>
            body {
                font-size: 3em;
            }
            table, th, td {
                font-size: 1em;
                margin: 1em;
                border: 1px solid black;
                border-collapse: collapse;
            }
            td {
                padding: 5px;
                text-align: center;
            }
            tr:nth-child(odd) {
                background-color: #a4c2f7;
            }
            @media (max-width: 600px) {
                
                table {
                    width: 90%;  
                }
            }
        </style>
    </head>
    <body>
        Inscription aux stages
        <table>{html_days}
        </table>
        dernière mises à jour<br>{now_string}
    </body>
</html>
"""

with open("docs/index.html", "w") as html_file:
    html_file.write(html)
