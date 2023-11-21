#current_missions

#arbitration = https://api.warframestat.us/PC/arbitration/

#events = https://api.warframestat.us/PC/events/
#such as gift of the lotus and thermia fractures

#fissures = https://api.warframestat.us/PC/fissures/

#invasions = https://api.warframestat.us/PC/invasions/

#sortie = https://api.warframestat.us/PC/sortie/

#teshins shop = https://api.warframestat.us/pc/steelPath/

#baro = https://api.warframestat.us/PC/voidTrader/

import requests
import json
import re
from dateutil import parser
from datetime import datetime, timezone
import pytz
from requests_html import HTMLSession
import time
from bs4 import BeautifulSoup as bs4

#sortie
# test = requests.get('https://api.warframestat.us/PC/sortie/')
# data = dict(test.json())

# print(data['variants'][0]['missionType'],data['variants'][0]['node'],data['variants'][1]['missionType'],data['variants'][1]['node'],data['variants'][2]['missionType'],data['variants'][2]['node'])

#teshin
# test = requests.get('https://api.warframestat.us/pc/steelPath/')
# data = dict(test.json())

# print(data['currentReward']['name'])

#events
# test = requests.get('https://api.warframestat.us/PC/events/')
# data = test.json()

# new_dict = {item['description']:item for item in data}

# print_statement = ""

# for x in new_dict:
#     # print(new_dict[x]['description'])
#     for y in new_dict[x]['rewards']:
#         if y['items'] != []:
#             rewards = str(y['items'])
    
#     # print(rewards)
#     print_statement += "Event: " + str(new_dict[x]['description'])+ "\n"+ "\n" + "Rewards: "+ str(re.sub("[\[\]']","",str(rewards))) + "\n"
# print(print_statement)


#fissures
# test = requests.get('https://api.warframestat.us/PC/fissures/')
# data = test.json()

# new_dict = {item['node']:item for item in data}
# for x in new_dict:
#     if new_dict[x]['isHard'] == True:
#         if new_dict[x]['tierNum'] == 5:
#             print(new_dict[x]['node'])

#arbitrations

# test = requests.get('https://api.warframestat.us/PC/arbitration/')
# data = dict(test.json())



# print(data['node'], " ",data['typeKey'])

#invasions

# test = requests.get('https://api.warframestat.us/PC/invasions/')
# data = test.json()

# new_dict =  {item['node']:item for item in data}

# for x in new_dict:
#     #check for forma
#     if "Forma Blueprint" in new_dict[x]['attacker']['reward']['itemString']:
#         print(new_dict[x]['node'],new_dict[x]['attacker']['reward']['itemString'],new_dict[x]['desc'])
#     if "Forma Blueprint" in new_dict[x]['defender']['reward']['itemString']:
#         print(new_dict[x]['node'],new_dict[x]['defender']['reward']['itemString'],new_dict[x]['desc'])
#     #check for gold potato
#     if "Orokin Catalyst Blueprint" in new_dict[x]['attacker']['reward']['itemString']:
#         print(new_dict[x]['node'],new_dict[x]['attacker']['reward']['itemString'],new_dict[x]['desc'])
#     if "Orokin Catalyst Blueprint" in new_dict[x]['defender']['reward']['itemString']:
#         print(new_dict[x]['node'],new_dict[x]['defender']['reward']['itemString'],new_dict[x]['desc'])
#     #check for silver potato
#     if "Orokin Reactor Blueprint" in new_dict[x]['attacker']['reward']['itemString']:
#         print(new_dict[x]['node'],new_dict[x]['attacker']['reward']['itemString'],new_dict[x]['desc'])
#     if "Orokin Reactor Blueprint" in new_dict[x]['defender']['reward']['itemString']:
#         print(new_dict[x]['node'],new_dict[x]['defender']['reward']['itemString'],new_dict[x]['desc'])


# test = requests.get('https://api.warframestat.us/PC/events/')
# data = test.json()

# new_dict = {item['id']:item for item in data}
# # print(new_dict)
# print_statement = ""

# for x in new_dict:
#     # print(new_dict[x]['description'])
#     for y in new_dict[x]['rewards']:
#         if y['items'] != []:
#             rewards = str(y['items'])
#     end_date = parser.parse(new_dict[x]['expiry'])
#     print((time.mktime(end_date.timetuple())))
#     # print(rewards)
#     print_statement += "Event: **" + str(new_dict[x]['description'])+ "**\n" + "Rewards: "+ str(re.sub("[\[\]']","",str(rewards))) + "\nEnd Date: " + "<t:" + str(time.mktime(end_date.timetuple())) + ":d>\n"+ "\n"
# # print(print_statement)


# get the webpage and json
# test = requests.get('https://api.empx.cc/warframe/rivencalc/')
# data = dict(test.json())

# ips = {}

# for x in data['weapons']:
#     ips.update({x:data['weapons'][x]['can_roll_ips']})
# print(ips)

#check for ips/dispos
# with open("ips.txt") as json_file:
#     ips = json.load(json_file)

# #open dispos
# with open("rifle_dispos.txt") as json_file:
#     rifle_dispos = json.load(json_file)
# with open("pistol_dispos.txt") as json_file:
#     pistol_dispos = json.load(json_file)
# with open("melee_dispos.txt") as json_file:
#     melee_dispos = json.load(json_file)
# with open("shotgun_dispos.txt") as json_file:
#     shotgun_dispos = json.load(json_file)
# with open("archgun_dispos.txt") as json_file:
#     archgun_dispos = json.load(json_file)
# with open("kitgun_dispos.txt") as json_file:
#     kitgun_dispos = json.load(json_file)

# weapon = "burston"

# weapon = weapon.capitalize()

# can_roll = []

# dispo = ""

# if weapon in rifle_dispos:
#     for x in rifle_dispos:
#         if x == weapon:
#             if ips[weapon]['Impact'] == True:
#                 can_roll += ['Impact']
#             if ips[weapon]['Puncture'] == True:
#                 can_roll += ['Puncture']
#             if ips[weapon]['Slash'] == True:
#                 can_roll += ['Slash']
#         if weapon in x:
#             dispo += "\n" + x + " " + str(rifle_dispos[x])

# print("Dispo(s): ", dispo, "\n\nIPS: ",re.sub("[\[\],']","",str(can_roll)))
# print(re.sub("[\[\],']","",str(can_roll)),dispo)

# import grading_functions
# import translator_search

# #grab rivens from r.m
# rm_url = "https://riven.market/_modules/riven/showrivens.php?baseurl=Lw==&platform=PC&limit=500&recency=1&veiled=false&onlinefirst=false&polarity=all&rank=all&mastery=16&weapon=Any&stats=Any&neg=Any&price=99999&rerolls=-1&sort=time&direction=ASC&page=1&time=0"

# r = requests.get(rm_url)
# soup = bs4(r.content,"lxml")

# table = soup.find('div',attrs={"id":"riven-list"})

# riven_data = {}
# count = 0

# users = []

# for row in table.findAll('div',attrs={'class':"attribute seller"}):
#     user = str(row.text).replace(" ","")
#     users += [user]
# for row,x in zip(table.findAll('div', attrs={'class':"riven"}),users):
#     count += 1
#     riven_data.update({count:{'weapon':row['data-weapon'],'prefix':row['data-name'],'pos1':row['data-stat1'],'pos_val1':row['data-stat1val'],'pos2':row['data-stat2'],'pos_val2':row['data-stat2val'],'pos3':row['data-stat3'],'pos_val3':row['data-stat3val'],'neg':row['data-stat4'],'negval':row['data-stat4val'], "mr":row['data-mr'],"rank":row['data-rank'],"polarity":row['data-polarity'],"rerolls":row['data-rerolls'],"price":row['data-price'], "user":x}})

# #filter through the data
# with open("filters.json") as json_file:
#     filters = json.load(json_file)

# db_identifiers = set()

# blacklist = []

# #open the blacklist file
# with open('blacklist.txt') as blacklist_file:
#     for line in blacklist_file:
#         line = line.replace('\n','')
#         blacklist.append(line.lower())

# # print(str(blacklist).lower())
# def print_replace(data):
#     data = data.replace("_", " ")
#     data = data.replace("channeling efficiency","heavy attack efficiency")
#     data = data.replace("channeling damage", "intial combo")
#     return data


# for x in riven_data:
#     # print(type(str(riven_data[x]['user']).replace(" ","")))
#     if str(riven_data[x]['user']).lower().strip() in str(blacklist).lower().strip():
#         print("blacklist",riven_data[x]['user'])
#     else:
#         print("not blacklist",riven_data[x]['user'])

    # print(riven_data[x]['user'], riven_data[x]['weapon'])
    # #make identifier for the riven
    # identifier = str(riven_data[x]['user'])  ,str(str(riven_data[x]['weapon']).replace("_"," "))  ,str(riven_data[x]['prefix'])  ,str(riven_data[x]['price']) ,str(riven_data[x]['rank'])  ,str(riven_data[x]['mr']) ,str(riven_data[x]['polarity'])  ,str(riven_data[x]['pos_val1'])  ,str(riven_data[x]['pos1'])  ,str(riven_data[x]['pos_val2'])  ,str(riven_data[x]['pos2'])  ,str(riven_data[x]['pos_val3'])  ,str(riven_data[x]['pos3'])  ,str(riven_data[x]['negval'])  ,str(riven_data[x]['neg'])
    # #check if its in the identifier already
    # if identifier not in db_identifiers:
    #     for y in filters:
    #             #replace _ with space
    #             stat1name = str(riven_data[x]['pos1']).replace("_"," ")
    #             stat2name = str(riven_data[x]['pos2']).replace("_"," ")
    #             stat3name = str(riven_data[x]['pos3']).replace("_"," ")
    #             negstat = str(riven_data[x]['neg']).replace("_"," ")
    #             #translate riven.market backend names with the backend names I use for grading and filters
    #             stat1name = translator_search.translate_rm(stat1name)
    #             stat2name = translator_search.translate_rm(stat2name)
    #             stat3name = translator_search.translate_rm(stat3name)
    #             negstat = translator_search.translate_rm(negstat)
    #             #if stat doesnt exist make it an empty list
    #             if stat3name == "":
    #                  stat3name = []
    #             if negstat == "":
    #                  negstat = []
    #             #filter the riven
    #             if str(riven_data[x]['weapon']).replace("_"," ") in filters[y] or filters[y]['weapon'] == "1":
    #                 if str(stat1name) in filters[y]['pos1'] or str(stat1name) in filters[y]['pos2'] or str(stat1name) in filters[y]['pos3'] or filters[y]['pos1'] == "1"or filters[y]['pos2'] == "1"or filters[y]['pos3'] == "1":
    #                             if str(stat2name) in filters[y]['pos1'] or str(stat2name) in filters[y]['pos2'] or str(stat2name) in filters[y]['pos3']or filters[y]['pos1'] == "1"or filters[y]['pos2'] == "1"or filters[y]['pos3'] == "1":
    #                                 # if str(stat3name) in filters[y]['pos1'] or str(stat3name) in filters[y]['pos2'] or str(stat3name) in filters[y]['pos3']or filters[y]['pos1'] == "1"or filters[y]['pos2'] == "1"or filters[y]['pos3'] == "1":
    #                                     if str(negstat) in str(filters[y]['neg']) or filters[y]['neg'] == "1":
    #                                         grades = grading_functions.get_varriants(str(riven_data[x]['weapon']).replace("_"," "), riven_data[x]['pos_val1'], stat1name,riven_data[x]['pos_val2'], stat2name, riven_data[x]['pos_val3'], stat3name,riven_data[x]['negval'],negstat)
    #                                         pos_grade1_1 = ""
    #                                         pos_grade1_2 = ""
    #                                         pos_grade2_1 = ""
    #                                         pos_grade2_2 = ""
    #                                         pos_grade3_1 = ""
    #                                         pos_grade3_2 = ""
    #                                         neg_grade1 = ""
    #                                         neg_grade2 = ""
    #                                         # print_statement = ""
    #                                         description = ""
    #                                         #seperate the grades out
    #                                         for z in grades:
    #                                             try:
    #                                                 pos_grade1_1, pos_grade1_2 = grades[z]['pos1']
    #                                             except:
    #                                                 pos_grade1_1 = ""
    #                                                 pos_grade1_2 = ""
    #                                             try:
    #                                                 pos_grade2_1, pos_grade2_2 = grades[z]['pos2']
    #                                             except:
    #                                                 pos_grade2_1 = ""
    #                                                 pos_grade2_2 = ""
    #                                             try:
    #                                                 pos_grade3_1, pos_grade3_2 = grades[z]['pos3']
    #                                             except:
    #                                                 pos_grade3_1 = ""
    #                                                 pos_grade3_2 = ""
    #                                             try:
    #                                                 neg_grade1, neg_grade2 = grades[z]['neg']
    #                                             except:
    #                                                 neg_grade1 = ""
    #                                                 neg_grade2 = ""
    #                                             description += str(grades[z]['weapon']).title() + " "+"\n" + str(stat1name)+ " "+ str(riven_data[x]['pos_val1'])+ " "+ " ("+ str(pos_grade1_1)+ ", " + str(pos_grade1_2)+ ") " + " \n"+ str(stat2name)+ " "+ str(riven_data[x]['pos_val2']) + " "+ " ("+str(pos_grade2_1)+ ", "+ str(pos_grade2_2)+ ") " + " \n"+ str(stat3name)+ " "+ str(riven_data[x]['pos_val3'])+ " "+   " ("+str(pos_grade3_1)+ ", "+ str(pos_grade3_2) + ") " +" \n"+ str(negstat)+ " "+ str(riven_data[x]['negval']) + " "+" ("+str(neg_grade1)+ ", "+ str(neg_grade2) + ")\n" + "\n"
    #                                         print(description)
        # #add identifier to the identifiers list
        # db_identifiers.add(identifier)

test = requests.get('https://api.warframestat.us/PC/voidTrader')
data = dict(test.json())
description = ""
for x in data['inventory']:
    description += x['item'] +"\nDucats: "+ str(x['ducats']) + "\nCredits: " + str(x['credits']) + "\n\n"
print(description)