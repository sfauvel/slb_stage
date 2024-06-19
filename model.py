# Need to do before : pip install helloasso_api



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
     
     
     
class Utilisateur:
    def __init__(self, nom, prenom) -> None:
        self.nom = nom
        self.prenom = prenom
         
     
class Payeur:
    def __init__(self, nom, prenom, mail) -> None:
        self.nom = nom
        self.prenom = prenom
        self.mail = mail

class Item:
    def __init__(self, nom, montant):
        self.nom = nom
        self.montant = montant

class Option:
    def __init__(self, nom, montant):
        self.nom = nom
        self.montant = montant

class Commande:
    def __init__(self, nom):
        self.nom = nom

class Adhesion:
    def __init__(self, nom, payeur, commande, utilisateur, montant, options, champs_specifiques):
        self.payeur = payeur
        self.nom = nom
        self.commande = commande
        self.utilisateur = utilisateur
        self.montant = montant
        self.options = options
        self.champs_specifiques = champs_specifiques
        
class Paiement:
    def __init__(self, payeur, date, montant, items, commande):
        self.payeur = payeur
        self.commande = commande
        self.date = date
        self.montant = montant
        self.items = items

class ChampSpecifique:
    def __init__(self, nom, reponse):
        self.nom = nom
        self.reponse = reponse
        


class HelloAssoToModel:
    def new_payeur(data):
        return Payeur(data["lastName"], data["firstName"], data["email"])
    
    def new_item(data):
        return Item(
            data["name"] if "name" in data else None, 
            data["amount"])
    
    def new_commande(data):
        return Commande(data["formSlug"])
    
    def new_utilisateur(data): 
        return Utilisateur(data['firstName'], data['lastName'])
    
    def new_custom_field(data):
        return ChampSpecifique(data["name"], data["answer"])
    
    
    def new_option(data):
        return Option(data["name"], data["amount"])
    
    def new_adhesion(data):
        return Adhesion(
            data["name"],
            HelloAssoToModel.new_payeur(data["payer"]), 
            HelloAssoToModel.new_commande(data["order"]),
            HelloAssoToModel.new_utilisateur(data["user"]),
            data["amount"], 
            [HelloAssoToModel.new_option(item) for item in data["options"]] if "options" in data else [],
            [HelloAssoToModel.new_custom_field(item) for item in data["customFields"]],
        )
    
    def new_paiement(data):
        
        return Paiement(
            HelloAssoToModel.new_payeur(data["payer"]),
            data["date"],
            data["amount"],
            [HelloAssoToModel.new_item(item) for item in data["items"]],
            HelloAssoToModel.new_commande(data["order"]),
        )