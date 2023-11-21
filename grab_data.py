#grab_data

import requests
import json

# get the webpage and json
test = requests.get('https://api.empx.cc/warframe/rivencalc/')
data = dict(test.json())

ips = {}

rifle_dispos = {}
pistol_dispos = {}
melee_dispos = {}
shotgun_dispos = {}
archgun_dispos = {}
kitgun_dispos = {}

rifle_base = {}
pistol_base = {}
melee_base = {}
shotgun_base = {}
archgun_base = {}

kitgun_list = ["Sporelacer","Rattleguts","Vermisplicer","Catchmoon","Gaze","Tombfinger"]

for x in data['weapons']:
    try:
        ips.update({x:data['weapons'][x]['can_roll_ips']})
    except:
        ips.update({x:{"Impact": False, "Puncture": False, "Slash": False}})

for x in data['weapons']:
    if data['weapons'][x]['riventype'] == "Rifle":
        rifle_dispos.update(data['weapons'][x]['variants'])
    if data['weapons'][x]['riventype'] == "Pistol" and ("Primary" not in data['weapons'][x]['variants'] or "Secondary" not in data['weapons'][x]['variants']):
        pistol_dispos.update(data['weapons'][x]['variants'])
        print(data['weapons'][x]['variants'])
    if data['weapons'][x]['riventype'] == "Melee":
        melee_dispos.update(data['weapons'][x]['variants'])
    if data['weapons'][x]['riventype'] == "Shotgun":
        shotgun_dispos.update(data['weapons'][x]['variants'])
    if data['weapons'][x]['riventype'] == "Archgun":
        archgun_dispos.update(data['weapons'][x]['variants'])
    if x in kitgun_list:
        kitgun_dispos.update({x:data['weapons'][x]['variants']})

def translator(stat):
    translate_stats = {
        "Damage":"base damage / melee damage",
        "Critical Chance":"critical chance",
        "Critical Damage":"critical damage",
        "Fire Rate":"fire rate / attack speed",
        "Attack Speed":"fire rate / attack speed",
        "Initial Combo":"channeling damage",
        "Weapon Recoil":"recoil",
        "Multishot":"multishot",
        "Toxin":"toxin damage",
        "Cold":"cold damage",
        "Electric":"electric damage",
        "Heat":"heat damage",
        "Slide Attack Critical Chance":"critical chance on slide attack",
        "Finisher Damage":"finisher damage",
        "Damage to Grineer":"damage vs grineer",
        "Damage to Infested":"damage vs infested",
        "Damage to Corpus":"damage vs corpus",
        "Ammo Max":"ammo maximum",
        "Impact":"impact damage",
        "Puncture":"puncture damage",
        "Slash":"slash damage",
        "Magazine Capacity":"magazine capacity",
        "Punch Through":"punch through",
        "Status Chance":"status chance",
        "Status Duration":"status duration",
        "Heavy Attack Efficiency":"channeling efficiency",
        "Reload Speed":"reload speed",
        "Flight Speed":"projectile speed",
        "Zoom":"zoom"
    }
    try:
        return str(translate_stats[stat])
    except:
        return str(stat).lower()

for x in data['buffs']:
    if x == "Rifle":
        for y in data['buffs'][x]:
            stat_data = {translator(y): data['buffs'][x][y]}
            rifle_base.update(stat_data)
    if x == "Pistol":
        for y in data['buffs'][x]:
            stat_data = {translator(y): data['buffs'][x][y]}
            pistol_base.update(stat_data)
    if x == "Melee":
        for y in data['buffs'][x]:
            stat_data = {translator(y): data['buffs'][x][y]}
            melee_base.update(stat_data)
    if x == "Shotgun":
        for y in data['buffs'][x]:
            stat_data = {translator(y): data['buffs'][x][y]}
            shotgun_base.update(stat_data)
    if x == "Archgun":
        for y in data['buffs'][x]:
            stat_data = {translator(y): data['buffs'][x][y]}
            archgun_base.update(stat_data)

#write ips
with open("ips.txt","w")as file:
    file.write(json.dumps(ips).replace(" & ", " And "))

#write base stats
with open("rifle_base.txt","w") as file:
    file.write(json.dumps(rifle_base))
with open("pistol_base.txt","w") as file:
    file.write(json.dumps(pistol_base))
with open("melee_base.txt","w") as file:
    file.write(json.dumps(melee_base))
with open("shotgun_base.txt","w") as file:
    file.write(json.dumps(shotgun_base))
with open("archgun_base.txt","w") as file:
    file.write(json.dumps(archgun_base))

#write dispos
with open("rifle_dispos.txt","w") as file:
    file.write(json.dumps(rifle_dispos))
with open("pistol_dispos.txt","w") as file:
    file.write(json.dumps(pistol_dispos))
with open("melee_dispos.txt","w") as file:
    file.write(json.dumps(melee_dispos).replace(" & ", " And "))
with open("shotgun_dispos.txt","w") as file:
    file.write(json.dumps(shotgun_dispos))
with open("archgun_dispos.txt","w") as file:
    file.write(json.dumps(archgun_dispos))
with open("kitgun_dispos.txt","w") as file:
    file.write(json.dumps(kitgun_dispos))