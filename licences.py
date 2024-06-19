# Need to do before : pip install helloasso_api

import inspect
import json
import os
import re
from model import Adhesion, Paiement
from model import HelloAssoToModel

    
def paiements(json_file: str, json_adhesion_file: str):
    nombre_paiements = 0
    with open(json_file, "r") as read_content: 
        data = json.load(read_content)
        nombre_paiements += paiements_from_data(data)
        
    with open(json_adhesion_file, "r") as read_content: 
        data = json.load(read_content)
        nombre_paiements += adhesions_from_data(data)
    
    print(f"Nombre de paiements:{nombre_paiements}")
    

def display_paiement(paiement):
    if isinstance(paiement.montant_deduit, Montant):
        texte_mutation= f" + {paiement.montant_deduit.mutation: >2}€" if paiement.montant_deduit.mutation is not None else " +  0€"
        texte_fraterie= f" + {paiement.montant_deduit.fraterie: >4}€" if paiement.montant_deduit.fraterie is not None else " +    0€"
        return f"{paiement.categorie:<8} {paiement.montant_deduit.montant: >6}€ + {paiement.montant_deduit.assurance: >5}€{texte_mutation}{texte_fraterie} {paiement.payeur.mail:<30} {paiement.description}"
    else:
        return f"{paiement.montant_deduit} {paiement.payeur.mail} {paiement.description}"

def get_categorie(categories, annee_naissance, annee_reference=2024):
    categorie = annee_reference - int(annee_naissance) + 1
    if categorie >= 21:
        return "Sénior"
    
    if f"U{categorie}" not in categories:
        categorie += 1
    if f"U{categorie}" not in categories:
        categorie += 1
        
    return f"U{categorie}"

TARIFS = {
    "U7": 100,
    "U9": 120,
    "U11": 130,
    "U13": 140,
    "U15": 150,
    "U18": 160,
    "U21": 180,
    "Sénior": 180,
    "Loisir": 110,
    "Bénévoles joueurs": 60,
    "Bénévoles non joueur": 30,
}
CATEGORIES=TARIFS.keys()

class Adhesion2024_2025(Adhesion):
    def __init__(self, nom, payeur, commande, utilisateur, montant, options, champs_specifiques):
        super().__init__(nom, payeur, commande, utilisateur, montant, options, champs_specifiques)
        
        self.date_naissance=next(filter(lambda x: x.nom=="Date de naissance", champs_specifiques)).reponse
        (self.jour, self.mois, self.annee_naissance) = self.date_naissance.split("/")
        
        self.description = f"{self.nom} - {self.utilisateur.nom} {self.utilisateur.prenom} {self.date_naissance}"
        self.erreurs = []
        
        self.categorie = get_categorie(CATEGORIES, self.annee_naissance)
        
        assurance = sum([o.montant for o in options if o.nom.startswith("Assurance")])
        self.montant_deduit = Montant.deduire(TARIFS, -7.5, self.categorie, montant, assurance)
        
    def new(data):
        adhesion = HelloAssoToModel.new_adhesion(data)
        return Adhesion2024_2025(adhesion.nom, adhesion.payeur, adhesion.commande, adhesion.utilisateur, adhesion.montant, adhesion.options, adhesion.champs_specifiques)

class Paiement2024_2025(Paiement):
    def __init__(self, payeur, date, montant, items, commande):
        super().__init__(payeur, date, montant, items, commande)
        self.description = items[0].nom
        self.montant = self.items[0].montant
        
        self.erreurs = []
        if len(self.items) != 1:
            self.erreurs.append(f"Un seul item attendu, {len(self.items)} présent(s) sur {self.description}")
        
        self._extract_preinscription(self.description)
                
        self.categorie = get_categorie(CATEGORIES, self.annee_naissance)
        self.montant_deduit = Montant.deduire(TARIFS, -15, self.categorie, self.montant)
        
    def is_a(data):
        paiement = HelloAssoToModel.new_paiement(data)
        return paiement.commande.nom == "default"
        
    def _extract_preinscription(self, description):
        # Avec '(.+) (.+)' le prénom ne peut pas contenir d'espace
        preinscription = re.match("Paiement e-Licence pour préinscription (\d+) de (.+) (.+) (\d\d)/(\d\d)/(\d\d\d\d)", description)
        
        if preinscription:                            
            (self.licence,self.nom,self.prenom,self.jour,self.mois,self.annee_naissance) = preinscription.groups()
        else:
            self.erreurs.append(f"Description non conforme: {self.description}")
    
    def new(data):
        paiement = HelloAssoToModel.new_paiement(data)
        return Paiement2024_2025(paiement.payeur, paiement.date, paiement.montant, paiement.items, paiement.commande)
    
class Montant:
    def __init__(self, montant, assurance, mutation, fraterie):
        self.montant = montant
        self.assurance = assurance
        self.mutation = mutation
        self.fraterie = fraterie
    
    def deduire(tarif, tarif_fraterie, categorie, montant, assurance = None):
        
        if assurance is None:
            (montant, assurance) = Montant._deduire_assurance(montant)
            
        montant = montant/100
        assurance = assurance/100
            
        tarif_mutation = 60
        is_mutation = False
        is_fraterie = False

        tarifs = [tarif["Sénior"], tarif["Loisir"], tarif["Bénévoles joueurs"], tarif["Bénévoles non joueur"]] if categorie == "Sénior" else [tarif[categorie], tarif["Bénévoles joueurs"]]
        def is_tarif_existant(montant):
            return montant in tarifs
        
        if not is_tarif_existant(montant):
            if is_tarif_existant(montant-tarif_mutation):
                (montant, assurance, tarif_mutation, None)
            elif is_tarif_existant(montant-tarif_fraterie):
                (montant, assurance, None, tarif_fraterie)
            elif is_tarif_existant(montant-tarif_mutation-tarif_fraterie):
                (montant, assurance, tarif_mutation, tarif_fraterie)
            else:
                # return f"ERREUR: {categorie} {montant} (au lieu de l'un des tarifs {tarifs}) {mail} {name}"
                return f"ERREUR: {categorie} {montant} (au lieu de l'un des tarifs {tarifs})"
            
        return Montant(montant, assurance, None, None)
    
    def _deduire_assurance(montant):
        assurances = [217, 627, 217+36, 627+36]
        for assurance in assurances:
            if (montant-assurance) % 100 == 0:
                montant -= assurance
                return (montant, assurance)
            
        return (montant, 0)
    
def adhesions_from_data(data):
    tarif_fraterie = -7.5
    adhesions = [Adhesion2024_2025.new(d) for d in data]
    print(rapport_inscription(tarif_fraterie, adhesions))
    return len(adhesions)

def paiements_from_data(data):
    tarif_fraterie = -15
    paiements = [Paiement2024_2025.new(d) for d in data if Paiement2024_2025.is_a(d)]
    print(rapport_inscription(tarif_fraterie, paiements))
    return len(paiements)

def rapport_inscription(tarif_fraterie, inscription):
    inscription.sort(key = lambda p: p.payeur.mail)
    textes = [rapport(TARIFS, adhesion, tarif_fraterie) for adhesion in inscription]
    return "\n".join(textes)

def rapport(TARIFS, paiement, tarif_fraterie):
    if paiement.erreurs:
        return "ERREUR: - " + "\n        - ".join([erreur for erreur in paiement.erreurs])
        
    return display_paiement(paiement)

def chargement_donnees(json_file, json_adhesion_file):
    from hello_asso import OrganizationApi, HaApiV5
    api = HaApiV5(
            api_base='api.helloasso.com',
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET'),
            timeout=60
        )

    slug = 'sainte-luce-basket'
    orga = OrganizationApi(api, slug)
    
    data = orga.get_all_items_data("payments", {"from": "2024-06-01"}, max_page=5)
    with open(json_file, "w") as outfile:
        outfile.write(json.dumps(data, indent=4))
    
    event="adhesion-2024-2025"
    data = orga.get_memberships(event, max_page=5)
    with open(json_adhesion_file, "w") as outfile:
        outfile.write(json.dumps(data, indent=4))
    
json_file="data/payments.json"
json_adhesion_file="data/adhesions.json"

refresh=False
if refresh:
    chargement_donnees(json_file, json_adhesion_file)
    
paiements(json_file, json_adhesion_file)

if not refresh:
    print("Données non rafraichies !!!")