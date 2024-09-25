# Need to do before : pip install helloasso_api

import json

import sys
sys.path.insert(0, '../helloasso')
from model import HelloAssoToModel

from commun import DocumentHtml, JsonTools, SyntheseHelloAsso

class Evenement(object): 
    
    def __init__(self, nom, jours, billets):
        self.nom = nom
        self.jours = jours
        self.billets = billets
    
    def par_type_de_billet(self):
        return JsonTools.group_by(self.billets, key_builder=lambda value: value.nom)
    
    def tous_les_champs_specifiques(self, champs = None):
        return [champ 
                for billet in self.billets
                for champ in billet.tous_les_champs_specifiques(champs)]
    
    def charger(event: str, jours: list):
        with open(f"data/{event}.json"   , "r") as read_content: 
            json_participants = json.load(read_content)

        billets = [HelloAssoToModel.new_adhesion(json) for json in json_participants]      
        
        return Evenement(event, jours, billets)

    def effectif_le(self, jour):    
        return self.effectif_par_jour().get(jour.lower(), 0)
    
    def effectif_par_jour(self):
        par_type_billet = JsonTools.group_by(self.billets, lambda _: _.nom)
        champs_jour = [champ for champ in self.tous_les_champs_specifiques(['2 jours', '1 jour', 'jour'])]
        jours_choisis = JsonTools.group_by(champs_jour, lambda _: _.reponse)
        
        return {day.lower() : self._compter_participants(day, jours_choisis, par_type_billet) for day in self.jours}
       
    def _compter_participants(self, day, jours_choisis, par_type_billet):
        def count_with_key_criteria(data, criteria):
            return sum([len(value) for (key, value) in data.items() if criteria(key)])       

        nb = sum([len(size) for (key_day, size) in jours_choisis.items() if day.lower() in key_day.lower() ])
        tous_les_jours = count_with_key_criteria(par_type_billet, lambda key: f"{len(self.jours)} jour" in key)
        return nb + tous_les_jours
        


class DocumentStage(DocumentHtml): 
    def __init__(self) -> None:
        super().__init__()
            
    def generer_rapport(self, nom, effectif_par_jour, now_string):
        html_days = ("\n"+(" "*4*3)).join([f"<tr><td>{day}</td><td>{nb}</td></tr>" for (day, nb) in effectif_par_jour.items()])
        html = self.generer_html(f"""
            <h3>Inscription aux stages {nom}</h3>
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

        return html

class UnStage(SyntheseHelloAsso):
    def __init__(self, nom, days) -> None:
        super().__init__(nom)
        self.days = days
        
    def chargement_donnees(self):    
        print(f"Chargement {self.nom}")
        self.chargement_donnees()
        
    def chargement_donnees(self):
    
        from hello_asso import orga

        json_participants = orga.get_event_participants(self.nom)
        #print(json_participants)

        with open(f"data/{self.nom}.json", "w") as outfile:
            outfile.write(json.dumps(json_participants, indent=4))
            
    def synthese(self, now_string):
        event = Evenement.charger(self.nom, self.days)
       
        effectif_par_jour = {day: event.effectif_le(day) for day in self.days}
       
        print(f"Stage {self.nom}: ", effectif_par_jour)
        return effectif_par_jour
        
class Stages(SyntheseHelloAsso):
    def __init__(self, nom, stages) -> None:
        super().__init__(nom)
        self.output_file = "docs/index.html"
        self.stages_old =  [ (stage.nom, stage.days) for stage in stages]
        self.stages = stages
        
    def chargement_donnees(self):    
        for stage in self.stages:
            stage.chargement_donnees()
            
    def synthese(self, now_string):
       
        effectif_par_jour = self._effectif_par_jour(now_string)        
        html = DocumentStage().generer_rapport(self.nom, effectif_par_jour, now_string)
        DocumentHtml.save(self.output_file, html)
  
    def _effectif_par_jour(self, now_string):
        # Definition des jours pour les avoir dans l'ordre
        jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi']

        syntheses = [stage.synthese(now_string) for stage in self.stages]
        effectif_par_jour = {jour: sum([synthese.get(jour, 0) for synthese in syntheses]) for jour in jours}   
                
        print("Stages: ", (", ".join([stage.nom for stage in self.stages])))
        print("\n".join([f"- {day}: {nb}" for (day, nb) in effectif_par_jour.items()]))
            
        return effectif_par_jour
