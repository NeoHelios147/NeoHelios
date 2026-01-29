
#___Single Attack sequence_____________________________________________________________________________________________________________________________________________________________________________________________


import random as rd
import numpy as np

def attacks(attaquant,arme,defenseur):
    a=arme.model*arme.attack[0]
    if arme.attack[1]!=0:
        r=0
        for i in range(arme.attack[1]):
            r+=rd.randint(1,int(arme.attack[2][1]))
        a+=r
    if arme.stock.blast==1:
        a+=defenseur.model//5
    return [a,0,0,[0,0],[0,0],[0,0]]



def hits(A,attaquant,arme,defenseur):
    if arme.stock.torrent==1:
        return [A[0],A[0],0,0,0]
    rolls=[rd.randint(1,6) for i in range(int(A[0]))]
    BS=max_min_modif_HW(arme.BS,arme.modificateurs[0],defenseur.modificateurs[0])
    h,w=0,0
    rolls,h,w=subhits(rolls,h,w,arme,BS)
    if int(arme.reroll[0])!=0:
        rerolls=[rd.randint(1,6) for i in range(len(rolls)) if rolls[i]<=int(arme.reroll[0])]
        rerolls,h,w=subhits(rerolls,h,w,arme,BS)
    return [A[0],h,w,[0,0],[0,0],[0,0]]



def wounds(H,attaquant,arme,defenseur):
    rolls=[rd.randint(1,6) for i in range(int(H[1]))]
    WOUND=calc_wound(arme,defenseur)
    WOUND=max_min_modif_HW(WOUND,arme.modificateurs[1],defenseur.modificateurs[1])
    w,mw=H[2],0
    rolls,w,mw=subwounds(rolls,w,mw,arme,WOUND)
    if int(arme.reroll[1])!=0 or arme.stock.twin_linked==1:
        reroll=int(arme.reroll[1])
        if reroll<6 and arme.stock.twin_linked==1:
            reroll=6
        rerolls=[rd.randint(1,6) for i in range(len(rolls)) if rolls[i]<=reroll]
        rerolls,w,mw=subwounds(rerolls,w,mw,arme,WOUND)
    return [H[0],H[1],w,[0,mw],[0,0],[0,0]]



def unsaved_wounds(W,attaquant,arme,defenseur):
    rolls=[rd.randint(1,6) for i in range(W[2])]
    SAVE=defenseur.save+arme.ap
    SAVE=max_min_modif_save(SAVE,defenseur.modificateurs[2])
    SAVE=min(SAVE,defenseur.invu)
    uw=0
    rolls,uw=subsave(rolls,uw,SAVE)
    if int(defenseur.reroll)!=0 :
        reroll=int(defenseur.reroll)
        rerolls=[rd.randint(1,6) for i in range(len(rolls)) if rolls[i]<=reroll]
        rerolls,uw=subsave(rerolls,uw,SAVE)
    return [W[0],W[1],W[2],[uw,W[3][1]],[0,0],[0,0]]



def damage(UW, attaquant, arme, defenseur):
    # NORMAL DAMAGE
    LDW = subdamage(UW[3][0], attaquant, arme, defenseur)
    if defenseur.fnp[0] < 7 or defenseur.modificateurs[3] != 0:
        LDW = subfnp(LDW, defenseur.fnp[0], defenseur.modificateurs[3])

    mort = [0, defenseur.pv]
    dw, mort = damage_overspill(LDW, defenseur, mort)

    # MORTAL DAMAGE (NO CAPPING)
    LDMW = subdamage(UW[3][1], attaquant, arme, defenseur)
    if defenseur.fnp[0] < 7 or defenseur.fnp[1] < 7:
        fnp = min(defenseur.fnp[0], defenseur.fnp[1])
        LDMW = subfnp(LDMW, fnp, 0)

    dmw = sum(LDMW)

    return [UW[0], UW[1], UW[2], UW[3], [dw, dmw], mort]




#___Sort dice_____________________________________________________________________________________________________________________________________________________________________________________________


def subhits(L,h,w,arme,BS):
    Vi=[]
    for i in range(len(L)):
        if int(arme.stock.crit)<=L[i]:
            if arme.stock.sustained_hits!=0:
                h+=arme.stock.sustained_hits
            if arme.stock.lethal_hits==0:
                h+=1
            else:
                w+=1
            Vi.append(i)
    for i in range(len(Vi)):
        L.pop(Vi[-1-i])
    Vi=[]        
    for i in range(len(L)):
        if L[i]<int(arme.stock.crit) and BS<=L[i]:
            h+=1
            Vi.append(i)
    for i in range(len(Vi)):
        L.pop(Vi[-1-i])
    return L,h,w


def subwounds(L, w, mw, arme, WOUND):
    Vi = []

    # DEVASTATING / ANTI first
    for i in range(len(L)):
        if L[i] >= arme.stock.anti:
            if arme.stock.devastating_wounds:
                mw += 1
            else:
                w += 1
            Vi.append(i)

    for i in reversed(Vi):
        L.pop(i)

    Vi = []

    # NORMAL WOUNDS
    for i in range(len(L)):
        if L[i] >= WOUND:
            w += 1
            Vi.append(i)

    for i in reversed(Vi):
        L.pop(i)

    return L, w, mw

def subsave(L,uw,save):
    Vi=[]  
    for i in range(len(L)):
        if L[i]<save:
            uw+=1
            Vi.append(i)
    for i in range(len(Vi)):
        L.pop(Vi[-1-i])
    return L,uw



def subdamage(N,attaquant,arme,defenseur):
    L=[]
    for i in range(N):
        if arme.damage[1]==0:
            L.append(arme.damage[0])
        elif arme.damage[1]!=0:
            L.append(arme.damage[0]+rd.randint(1,int(arme.damage[2][1])))
    return L


def subfnp(LD,fnp,modif):
    L=[]
    for D in LD:
        rolls=[rd.randint(1,6)-modif for i in range(D)]
        d=0
        for roll in rolls:
            if roll<fnp :
                d+=1
        L.append(d)
    return L

def damage_overspill(LD,defenseur,mort):
    D=0
    pv=mort[1]
    m=mort[0]
    for d in LD:
        if d==pv:
            D+=d
            m+=1
        elif d<pv:
            D+=d
            pv=pv-d
        elif pv<d:
            D+=pv
            m+=1
            pv=defenseur.pv
    return D,[m,pv]




#___Utilities_____________________________________________________________________________________________________________________________________________________________________________________________


def max_min_modif_HW(base,modif_attack,modif_defenseur):
    modif=-modif_attack+modif_defenseur
    B=base+modif
    B=max(2,B)
    B=max(base-1,B)
    B=min(base+1,B)
    return B

def max_min_modif_save(base,modif_defenseur):
    B=base+modif_defenseur
    B=max(2,B)
    B=min(7,B)
    B=max(base-1,B)
    B=min(base+1,B)
    return B

def calc_wound(arme,defenseur):
    if arme.force/defenseur.endurance<=0.5:
        return 6
    if defenseur.endurance/arme.force<=0.5:
        return 2
    if arme.force/defenseur.endurance<1:
        return 5
    if defenseur.endurance/arme.force<1:
        return 3
    else:
        return 4



    

#___datasheet classe_____________________________________________________________________________________________________________________________________________________________________________________________


def single_attack_sequence(attaquant,arme,defenseur):
    A=attacks(attaquant,arme,defenseur)
    if A[0]==0:
        return A
    H=hits(A,attaquant,arme,defenseur)
    if H[1]==0 and H[2]==0:
        return H
    W=wounds(H,attaquant,arme,defenseur)
    UW=unsaved_wounds(W,attaquant,arme,defenseur)
    D=damage(UW,attaquant,arme,defenseur)
    return D

def one_unit_sequence(attaquant,defenseur):
    L=[]
    m=[]
    if len(attaquant.weapons)==0:
        return print("no weapons equipped")
    for weapon in attaquant.weapons:
        DM=single_attack_sequence(attaquant,attaquant.weapons[weapon],defenseur)
        L.append(DM[4])
        m.append(DM[5][0])
    return L,m

        
#___Affichage des stats_____________________________________________________________________________________________________________________________________________________________________________________________

import matplotlib.pyplot as plt
import copy

NMC=10000

def stat(Fighters, NMC):
    if Fighters.defender is None or not Fighters.attacker:
        return None

    

    total_wounds = []
    total_mortal_wounds = []
    total_models_killed = []
    wiped = 0

    for _ in range(NMC):
        defender = copy.deepcopy(Fighters.defender)
        attackers = {k: copy.deepcopy(v) for k, v in Fighters.attacker.items()}
    
        wounds = 0
        mortals = 0
        models_killed = 0

        for attacker in attackers.values():
            dmg, kills = one_unit_sequence(attacker, defender)

            wounds += sum(d[0] for d in dmg)
            mortals += sum(d[1] for d in dmg)
            models_killed += sum(kills)

        total = wounds + mortals

        if total >= Fighters.defender.model * Fighters.defender.pv:
            wiped += 1

        total_wounds.append(wounds)
        total_mortal_wounds.append(mortals)
        total_models_killed.append(models_killed)

    # --- PLOT ---
    plt.clf()
    plt.close("all")

    fig, ax = plt.subplots(1, 2, figsize=(15, 4))

    # --- NORMAL WOUNDS ---
    ax[0].hist(total_wounds, bins="rice", alpha=0.7)
    ax[0].axvline(np.mean(total_wounds), linestyle="--", linewidth=2)
    ax[0].axvspan(
        np.mean(total_wounds) - np.std(total_wounds),
        np.mean(total_wounds) + np.std(total_wounds),
        alpha=0.2
    )
    ax[0].set_title(
    f"Normal wounds\n"
    f"Avg = {np.mean(total_wounds):.2f} ± {np.std(total_wounds):.2f}"
    )
    ax[0].set_xlabel("Wounds")
    ax[0].set_ylabel("Frequency")

    # --- MORTAL WOUNDS ---
    ax[1].hist(total_mortal_wounds, bins="rice", alpha=0.7)
    ax[1].axvline(np.mean(total_mortal_wounds), linestyle="--", linewidth=2)
    ax[1].axvspan(
    np.mean(total_mortal_wounds) - np.std(total_mortal_wounds),
    np.mean(total_mortal_wounds) + np.std(total_mortal_wounds),
    alpha=0.2
    )
    ax[1].set_title(
    f"Mortal wounds\n"
    f"Avg = {np.mean(total_mortal_wounds):.2f} ± {np.std(total_mortal_wounds):.2f}"
    )
    ax[1].set_xlabel("Mortal wounds")
    ax[1].set_ylabel("Frequency")


    import uuid

    image_path = f"static/stat_{uuid.uuid4().hex}.png"

    plt.tight_layout()
    plt.savefig(image_path)
    plt.close()

    # --- RETURN STRUCTURED DATA ---
    return {
        "image": "/" + image_path,
        "wipe_chance": 100 * wiped / NMC,
        "avg_wounds": np.mean(total_wounds),
        "std_wounds": np.std(total_wounds),
        "avg_mortals": np.mean(total_mortal_wounds),
        "std_mortals": np.std(total_mortal_wounds),
        "avg_models_killed": np.mean(total_models_killed),
        "std_models_killed": np.std(total_models_killed),
    }


#___Datasheet_____________________________________________________________________________________________________________________________________________________________________________________________


Factions={}

class faction:
    def __init__(self,nom,major_faction):
         self.nom=nom
         self.datasheet={}
         Factions[nom]=[self,"datasheets/"+str(major_faction)+"/"+str(nom)+".xlsx"]

    def add_datasheet(self,nom,D):
        self.datasheet[nom]=datasheet(D[0],D[1],self)
        self.datasheet[nom].profileDef(D[2],D[3],D[4],D[5],[D[6],D[7],D[8],D[9]],[D[10],D[11]],D[12])

    def add_weapon(self,nom,A):
        nom_datasheet=A[1]
        MC=[A[i] for i in range(17,25)]
        self.datasheet[nom_datasheet].Ajout_armes(nom,arme(nom,self.datasheet[nom_datasheet],MC,A[2]))
        self.datasheet[nom_datasheet].weapons[nom].profileAtt(A[3],[A[4],A[5],A[6]],A[7],A[8],[A[9],A[10],A[11]],[A[12],A[13]],[A[14],A[15]])
        
    def afficher_faction(self):
        print(self.nom)
        print("la faction comporte :")
        for data in list(self.datasheet.keys()):
            print(self.datasheet[data].nom)
        
class datasheet:
    def __init__(self,nom,nmodel,Faction):
        self.nom=nom
        self.model=nmodel
        self.weapons={}
        #Faction.add_datasheet(nom,self)

    def update_model(self,n):
        self.model=n

    def profileDef (self,endu,save,invu,pv,modif,fnp, reroll):
        self.endurance=endu
        self.save=save
        self.invu=invu
        self.pv=pv
        self.modificateurs=list(modif)
        self.fnp=list(fnp)
        self.reroll=reroll

    def Ajout_armes(self,nom,armes):
        self.weapons[nom]=armes
    
    def afficher_datasheet(self):
        print(vars(self))
        print("Armes pour la datasheet :")
        for weapon in self.weapons:
            print(weapon)

class arme(datasheet):
    typ_var={"binaires":["blast", "torrent", "lethal_hits", "lance", "twin_linked", "devastating_wounds"],"variable":["anti","sustained_hits","crit"]}
    
    def __init__(self,nom,profile,MC,nmodel):
        self.nom=nom
        #profile.Ajout_armes(self)
        self.stock=mot_clés(self,MC[0],MC[1],MC[2],MC[3],MC[4],MC[5],MC[6])
        self.model=nmodel
    
    def profileAtt(self,BS,attack,force,ap,damage,modif,reroll):
        self.BS=BS
        self.attack=list(attack)
        self.force=force
        self.ap=ap
        self.damage=list(damage)
        self.modificateurs=list(modif)
        self.reroll=list(reroll)

    def update_model(self,n):
        self.model=n

    def update_mot_clés(self,MC):
        self.stock=MC

    def afficher_weapon(self):
        print(vars(self))

    def afficher_mot_clés(self):
        L = []
        for mot in vars(self.stock).keys():
            if mot in self.typ_var["binaires"]:
                if getattr(self.stock, mot) == 1:
                    L.append(mot)
            elif mot in self.typ_var["variable"]:
                val = getattr(self.stock, mot)
                if mot in ("anti", "crit"):
                    if val != 6:
                        L.append(f"{mot}{val}")
                else:
                    if val != 0:
                        L.append(f"{mot}{val}")
        return L


class mot_clés(arme):
    typ_var={"binaires":["blast", "torrent", "lethal_hits", "lance", "twin_linked", "devastating_wounds"],"variable":["anti","sustained_hits","crit"]}

    def __init__(self,arme,blast=0,torrent=0,lethal_hits=0,sustained_hits=0,anti=6,twin_linked=0,lance=0,devastating_wounds=0,crit=6):
        self.blast=blast
        self.torrent=torrent
        self.lethal_hits=lethal_hits
        self.anti=anti
        self.sustained_hits=sustained_hits
        self.twin_linked=twin_linked
        self.lance=lance
        self.devastating_wounds=devastating_wounds
        self.crit=crit
        self.arme=arme
        

    def modif_mot_clés(self,mot):
        if mot in self.typ_var["binaires"]:
            if mot=="blast":
                if self.blast==1:
                    self.blast=0
                else:
                    self.blast=1
            elif mot=="torrent":
                if self.torrent==1:
                    self.torrent=0
                else:
                    self.torrent=1
            elif mot=="lethal_hits":
                if self.lethal_hits==1:
                    self.lethal_hits=0
                else:
                    self.lethal_hits=1
            elif mot=="lance":
                if self.lance==1:
                    self.lance=0
                else:
                    self.lance=1
            elif mot=="twin_linked":
                if self.twin_linked==1:
                    self.twin_linked=0
                else:
                    self.twin_linked=1
            elif mot=="devastating_wounds":
                if self.devastating_wounds==1:
                    self.devastating_wounds=0
                else:
                    self.devastating_wounds=1
            
        elif mot in self.typ_var["variable"]:
            if mot=="anti":
                self.anti+=1
                if 6<self.anti:
                    self.anti=2
            if mot=="crit":
                self.crit+=1
                if 6<self.crit:
                    self.crit=2
            if mot=="sustained_hits":
                self.sustained_hits+=1
                if 4<self.sustained_hits:
                    self.sustained_hits=0

        self.arme.update_mot_clés(mot_clés)

class fighters:
    def __init__(self):
        self.attacker={}
        self.defender=None

    def define_defender(self,datasheet):
        self.defender=datasheet
        
    def add_attacker(self,datasheet):
        self.attacker[datasheet.nom]=copy.deepcopy(datasheet)
        self.attacker[datasheet.nom].weapons={}

    def add_weapon_fighter(self,unit,weapon):
        self.attacker[unit].weapons[weapon.nom]=copy.deepcopy(weapon)

    def remove_attacker(self,datasheet):
        self.attacker.pop(datasheet.nom)

    def remove_weapon_fighter(self,unit,weapon):
        self.attacker[unit].weapons.pop(weapon.nom)
        
    def select_attacker(self, datasheet_name):
        if datasheet_name in self.attacker:
            self.selected_attacker = datasheet_name


#___Factions initialisation_____________________________________________________________________________________________________________________________________________________________________________________________

# Imperium
space_marines = faction("Space Marines","imperium")
blood_angels = faction("Blood Angels","imperium")
dark_angels = faction("Dark Angels","imperium")
space_wolves = faction("Space Wolves","imperium")
black_templars = faction("Black Templars","imperium")
deathwatch = faction("Deathwatch","imperium")
grey_knights = faction("Grey Knights","imperium")
adeptus_custodes = faction("Adeptus Custodes","imperium")
astra_militarum = faction("Astra Militarum","imperium")
adepta_sororitas = faction("Adepta Sororitas","imperium")
adeptus_mechanicus = faction("Adeptus Mechanicus","imperium")
imperial_knights = faction("Imperial Knights","imperium")
agents_of_the_imperium = faction("Agents of the Imperium","imperium")

# Chaos
chaos_space_marines = faction("Chaos Space Marines","chaos")
death_guard = faction("Death Guard","chaos")
thousand_sons = faction("Thousand Sons","chaos")
world_eaters = faction("World Eaters","chaos")
Emporors_children = faction("Emporors Children","chaos")
chaos_daemons = faction("Chaos Daemons","chaos")
chaos_knights = faction("Chaos Knights","chaos")

# Xenos
aeldari = faction("Aeldari","xenos")
drukhari = faction("Drukhari","xenos")
harlequins = faction("Harlequins","xenos")
necrons = faction("Necrons","xenos")
orks = faction("Orks","xenos")
tau_empire = faction("T'au Empire","xenos")
tyranids = faction("Tyranids","xenos")
genestealer_cults = faction("Genestealer Cults","xenos")
leagues_of_votann = faction("Leagues of Votann","xenos")

#Custom

Favorites = faction("Favorites","custom")
Defense_Standard = faction("Defense Standard","custom")

#___Import excel_____________________________________________________________________________________________________________________________________________________________________________________________


import pandas as pd


def import_datasheet(file_path,faction):
    df_sheet1 = pd.read_excel(file_path, sheet_name="Datasheet")
    df_sheet2 = pd.read_excel(file_path, sheet_name="Armes")


    Datasheet = df_sheet1.values.tolist()
    Armes = df_sheet2.values.tolist()

    for row in Datasheet:
        faction.add_datasheet(row[0],list(row))
    for row in Armes:
        faction.add_weapon(row[0],row)

        
def get_faction_file_path(faction_str):
    data = Factions.get(faction_str)
    if not data:
        return None
    return data[1], data[0]


#___App_____________________________________________________________________________________________________________________________________________________________________________________________

Fighters=fighters()

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")




@app.route("/import_datasheet_route", methods=["POST"])
def import_datasheet_route():
    data = request.get_json()
    faction_str = data.get("faction")

    if not faction_str:
        return jsonify({"error": "No faction provided"}), 400

    result = get_faction_file_path(faction_str)

    if result is None:
        return jsonify({"error": "Unknown faction"}), 400

    file_path, faction = result
    import_datasheet(file_path, faction)

    return jsonify({
        "message": f"Datasheet imported for {faction.nom}"
    })

@app.route("/get_faction_tree")
def get_faction_tree():
    tree = {}

    for faction_name, (faction_obj, path) in Factions.items():
        # Only include imported factions
        if not faction_obj.datasheet:
            continue

        # Determine major faction from path
        if "imperium" in path:
            major = "Imperium"
        elif "chaos" in path:
            major = "Chaos"
        elif "custom" in path:
            major = "Custom"
        else:
            major = "Xenos"


        tree.setdefault(major, {})
        tree[major][faction_name] = {}

        for ds_name, ds in faction_obj.datasheet.items():
            tree[major][faction_name][ds_name] = list(ds.weapons.keys())

    return jsonify(tree)

@app.route("/set_defender", methods=["POST"])
def set_defender():
    data = request.get_json()

    faction_name = data.get("faction")
    datasheet_name = data.get("datasheet")

    if not faction_name or not datasheet_name:
        return jsonify({"error": "Missing faction or datasheet"}), 400

    faction_data = Factions.get(faction_name)
    if faction_data is None:
        return jsonify({"error": "Unknown faction"}), 400

    faction_obj = faction_data[0]
    datasheet = faction_obj.datasheet.get(datasheet_name)

    if datasheet is None:
        return jsonify({"error": "Unknown datasheet"}), 400

    Fighters.define_defender(datasheet)

    return jsonify({
        "name": datasheet.nom,
        "models": datasheet.model,
        "endurance": datasheet.endurance,
        "save": datasheet.save,
        "invul": datasheet.invu,
        "wounds": datasheet.pv,
        "fnp": datasheet.fnp,
        "modifiers": datasheet.modificateurs
    })

@app.route("/add_attacker", methods=["POST"])
def add_attacker():
    data = request.get_json()

    faction_name = data.get("faction")
    datasheet_name = data.get("datasheet")

    if not faction_name or not datasheet_name:
        return jsonify({"error": "Missing faction or datasheet"}), 400

    faction_data = Factions.get(faction_name)
    if faction_data is None:
        return jsonify({"error": "Unknown faction"}), 400

    faction_obj = faction_data[0]
    datasheet = faction_obj.datasheet.get(datasheet_name)

    if datasheet is None:
        return jsonify({"error": "Unknown datasheet"}), 400

    Fighters.add_attacker(datasheet)

    return jsonify({
        "name": datasheet.nom,
        "models": datasheet.model
    })



@app.route("/update_defender_models", methods=["POST"])
def update_defender_models():
    data = request.get_json()
    n = data.get("models")

    if Fighters.defender is None:
        return jsonify({"error": "No defender set"}), 400

    try:
        n = int(n)
        if n < 1:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid model number"}), 400

    # REQUIRED: use the datasheet method
    Fighters.defender.update_model(n)

    return jsonify({
        "models": Fighters.defender.model
    })

@app.route("/get_attackers")
def get_attackers():
    attackers = []

    for name, ds in Fighters.attacker.items():
        attackers.append({
            "name": ds.nom,
            "models": ds.model,
            "weapons": list(ds.weapons.keys())
        })

    return jsonify(attackers)

@app.route("/remove_attacker", methods=["POST"])
def remove_attacker():
    data = request.get_json()
    datasheet_name = data.get("datasheet")

    if not datasheet_name:
        return jsonify({"error": "Missing datasheet"}), 400

    attacker = Fighters.attacker.get(datasheet_name)
    if attacker is None:
        return jsonify({"error": "Attacker not found"}), 400

    Fighters.remove_attacker(attacker)

    return jsonify({"removed": datasheet_name})

@app.route("/add_weapon_attacker", methods=["POST"])
def add_weapon_attacker():
    data = request.get_json()

    unit_name = data.get("unit")
    weapon_name = data.get("weapon")

    if not unit_name or not weapon_name:
        return jsonify({"error": "Missing unit or weapon"}), 400

    attacker = Fighters.attacker.get(unit_name)
    if attacker is None:
        return jsonify({"error": "Attacker not found"}), 400

    # Find the weapon in original faction datasheets
    weapon_obj = None
    for faction_obj, _ in Factions.values():
        if unit_name in faction_obj.datasheet:
            ds = faction_obj.datasheet[unit_name]
            weapon_obj = ds.weapons.get(weapon_name)
            break

    if weapon_obj is None:
        return jsonify({"error": "Weapon not found"}), 400

    Fighters.add_weapon_fighter(unit_name, weapon_obj)

    return jsonify({
        "unit": unit_name,
        "weapon": weapon_name
    })

@app.route("/select_attacker", methods=["POST"])
def select_attacker():
    data = request.get_json()
    name = data.get("datasheet")

    if name not in Fighters.attacker:
        return jsonify({"error": "Attacker not found"}), 400

    Fighters.select_attacker(name)

    attacker = Fighters.attacker[name]

    return jsonify({
        "name": attacker.nom,
        "weapons": [
            {
            "name": w.nom,
            "models": w.model,
            "BS": w.BS,
            "attack": w.attack,
            "strength": w.force,
            "ap": w.ap,
            "damage": w.damage,
            "keywords": w.afficher_mot_clés()
        }
        for w in attacker.weapons.values()
    ]
})



@app.route("/run_simulation", methods=["POST"])
def run_simulation():
    data = request.get_json()
    nmc = int(data.get("nmc", 0))

    if nmc < 1:
        return jsonify({"error": "Invalid NMC"}), 400

    # ✅ CLONE combat state for this run
    fighters_copy = copy.deepcopy(Fighters)

    result = stat(fighters_copy, nmc)
    if result is None:
        return jsonify({"error": "Simulation failed"}), 400

    return jsonify({
        "image": result["image"],
        "message1": f"Chance to wipe defender: {result['wipe_chance']:.1f}%",
        "message2": (
            f"Models killed: {result['avg_models_killed']:.2f} ± "
            f"{result['std_models_killed']:.2f}"
        )
    })

@app.route("/update_weapon_models", methods=["POST"])
def update_weapon_models():
    data = request.json
    unit_name = data["unit"]
    weapon_name = data["weapon"]
    n = int(data["models"])

    attacker = Fighters.attacker.get(unit_name)
    if attacker is None:
        return jsonify({"error": "Attacker not found"}), 400

    weapon = attacker.weapons.get(weapon_name)
    if weapon is None:
        return jsonify({"error": "Weapon not found"}), 400

    weapon.update_model(n)

    return jsonify({"success": True, "models": weapon.model})



if __name__ == "__main__":
    app.run(debug=True)


