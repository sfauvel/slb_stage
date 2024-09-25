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
    def __init__(self, effectif_par_jour) -> None:
        super().__init__()
        self.effectif_par_jour = effectif_par_jour
            
    def generer_rapport(self, nom, now_string):
        html_days = ("\n"+(" "*4*3)).join([f"<tr><td>{day}</td><td>{nb}</td></tr>" for (day, nb) in self.effectif_par_jour.items()])
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
        
    def rafraichir_donnees(self):
        from hello_asso import OrganizationApi
        super().recuperer_donnees(OrganizationApi.get_event_participants)
    
    def charger(self):
        
        json_data = self.lire_json()
        billets = [HelloAssoToModel.new_adhesion(json) for json in json_data]      
        
        return Evenement(self.nom, self.days, billets)
    
    def effectif_par_jour(self):
        effectif = {day: self.data.effectif_le(day) for day in self.days}
       
        print(f"Stage {self.nom}: ", effectif)
        return effectif
        
class Stages(SyntheseHelloAsso):
    def __init__(self, nom, stages) -> None:
        super().__init__(nom)
        self.output_file = "docs/index.html"
        self.stages_old =  [ (stage.nom, stage.days) for stage in stages]
        self.stages = stages
        
    def rafraichir_donnees(self):
        for stage in self.stages:
            stage.rafraichir_donnees()
            
    def charger(self):
        for stage in self.stages:
            stage.data = stage.charger()
        
    def preparer_document(self):
        return DocumentStage(self.effectif_par_jour())
       
    def effectif_par_jour(self):
        # Definition des jours pour les avoir dans l'ordre
        jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi']

        effectif_stages = [stage.effectif_par_jour() for stage in self.stages]
        effectif_par_jour = {jour: sum([effectifs.get(jour, 0) for effectifs in effectif_stages]) for jour in jours}   
                
        print("Stages: ", (", ".join([stage.nom for stage in self.stages])))
        print("\n".join([f"- {day}: {nb}" for (day, nb) in effectif_par_jour.items()]))
            
        return effectif_par_jour
