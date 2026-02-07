from gevent import monkey
monkey.patch_all()
import grequests
import os
from dotenv import load_dotenv
import discord
from discord import Color
from discord.ext import tasks
import json
from datetime import date
from dateutil import parser
import sqlite3
import asyncio
import time
import grader
import bane_patch
import translator_search

#discord token and guild
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#channel ids
snipe = int(os.getenv('snipe'))
bl = int(os.getenv('bl'))
funni_grades = int(os.getenv('funni_grades'))

#declare discord intents
intents = discord.Intents.all()
intents.message_content = True

client = discord.Client(intents = intents)

def description_creation(weapon, stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negname, prefix, description):
    grades = grader.grade(weapon, bane_patch.front_to_back(stat1name, str(stat1val)), stat1name.replace("_", " "), bane_patch.front_to_back(stat2name, str(stat2val)), stat2name.replace("_", " "), bane_patch.front_to_back(stat3name, str(stat3val)), stat3name.replace("_", " "), bane_patch.front_to_back(negname, str(negval)), negname.replace("_", " "), "8")    
    description += "Grades for " +  weapon.title() + " " +  prefix + "\n"
    empty_description = description
    stat1val, stat2val, stat3val, negval = bane_patch.back_to_front(stat1name, str(stat1val)), bane_patch.back_to_front(stat2name, str(stat2val)), bane_patch.back_to_front(stat3name, str(stat3val)), bane_patch.back_to_front(negname, str(negval))
    stat1stat, stat2stat, stat3stat, negstat = stat1name.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), stat2name.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), stat3name.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), negname.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo")
    for z in grades:
        if "?" in str(grades[z]) or "circle" not in str(grades[z]):
            continue
        try:
            pos1_color, pos_grade1_1, pos_grade1_2 = grades[z]['pos1']
        except:
            pos1_color, pos_grade1_1, pos_grade1_2  = "", "", ""
        try:
            pos2_color,pos_grade2_1, pos_grade2_2 = grades[z]['pos2']
        except:
            pos2_color, pos_grade2_1, pos_grade2_2 = "", "", ""
        try:
            pos3_color, pos_grade3_1, pos_grade3_2 = grades[z]['pos3']
        except:
            pos3_color, pos_grade3_1, pos_grade3_2 = "", "", ""
        try:
            neg_color, neg_grade1, neg_grade2 = grades[z]['neg']
        except:
            neg_color, neg_grade1, neg_grade2 = "", "", ""
        wiki_url = "https://warframe.fandom.com/wiki/"
        weapon_url = str(grades[z]['weapon']).title().replace(" ","_").replace("And","&")
        if "mk" in weapon_url.lower():
            weapon_url = wiki_url + "MK" +(weapon_url[2:]).title()
        else:
            weapon_url = wiki_url + weapon_url        
        description += "["+str(grades[z]['weapon']).title() + "]("+ weapon_url+")\n" +pos1_color+ stat1stat+ " "+ str(stat1val)+ " "+ " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") " + " \n"+pos2_color+ stat2stat+ " "+ str(stat2val) + " "+ " ("+str(pos_grade2_1)+ "%, "+ pos_grade2_2+ ") " 
        if stat3stat != "[]":
            description += " \n"+pos3_color+ stat3stat+ " "+ str(stat3val)+ " "+   " ("+str(pos_grade3_1)+ "%, "+ pos_grade3_2 + ") " 
        if negstat != "[]":
            description += " \n"+neg_color+ negstat+ " "+ str(negval) + " "+" ("+str(neg_grade1)+ "%, "+ neg_grade2 + ")"
        description += "\n\n"
    if description != empty_description:
        return description
    else:
        for z in grades:
            try:
                pos1_color, pos_grade1_1, pos_grade1_2 = grades[z]['pos1']
            except:
                pos1_color, pos_grade1_1, pos_grade1_2  = "", "", ""
            try:
                pos2_color,pos_grade2_1, pos_grade2_2 = grades[z]['pos2']
            except:
                pos2_color, pos_grade2_1, pos_grade2_2 = "", "", ""
            try:
                pos3_color, pos_grade3_1, pos_grade3_2 = grades[z]['pos3']
            except:
                pos3_color, pos_grade3_1, pos_grade3_2 = "", "", ""
            try:
                neg_color, neg_grade1, neg_grade2 = grades[z]['neg']
            except:
                neg_color, neg_grade1, neg_grade2 = "", "", ""
            wiki_url = "https://warframe.fandom.com/wiki/"
            weapon_url = str(grades[z]['weapon']).title().replace(" ","_").replace("And","&")
            if "mk" in weapon_url.lower():
                weapon_url = wiki_url + "MK" +(weapon_url[2:]).title()
            else:
                weapon_url = wiki_url + weapon_url            
            description += "["+str(grades[z]['weapon']).title() + "]("+ weapon_url+")\n" +pos1_color+ stat1stat+ " "+ str(stat1val)+ " "+ " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") " + " \n"+pos2_color+ stat2stat+ " "+ str(stat2val) + " "+ " ("+str(pos_grade2_1)+ "%, "+ pos_grade2_2+ ") " 
            if "[]" not in stat3stat:
                description += " \n"+pos3_color+ stat3stat+ " "+ str(stat3val)+ " "+   " ("+str(pos_grade3_1)+ "%, "+ pos_grade3_2 + ") " 
            if "[]" not in negstat:
                description += " \n"+neg_color+ negstat+ " "+ str(negval) + " "+" ("+str(neg_grade1)+ "%, "+ neg_grade2 + ")"
            description += "\n\n"
        return description

#loop to scrape wfm faster
@tasks.loop()
async def wfm_auc_save():
    url = ["https://api.warframe.market/v1/auctions"]
    header = {"Host":"api.warframe.market"}
    try:
        data = grequests.map(grequests.get(u, headers = header) for u in url)
    except:
        return
    try:
        data = dict(json.loads(data[0].text))
    except:
        return
    try:
        data = data['payload']['auctions']
    except:
        data = {}
        return
    with open("wfm_data.json",'w') as fp:
        fp.write(json.dumps(data))

#loop to scrape wfm
@tasks.loop()
async def wfm_snipe_loop():
    weapon_names = []
    with open("weapon_info.json") as json_file:
            weapon_info = json.load(json_file)
    for item in weapon_info:
        for weapons in weapon_info[item]['variants'].items():
            weapon_names.append(weapons[0].replace("Primary","").replace("Secondary","").strip())
    number_of_filters = 0
    riven_data = {}
    with open("wfm_data.json") as json_file:
        data= json.load(json_file)
    for i in data:
        # check if the auction is a riven
        if i['item']['type'] == 'riven':
            #varrs needed
            pos_stats, pos_values, neg_stats, neg_values = [], [], [], []
            #grab the stats
            for x in i['item']['attributes']:
                if x['positive'] == True:
                    pos_stats += [x['url_name']]
                    pos_values += [abs(x['value'])]
                if x['positive'] == False:
                    neg_stats, neg_values = x['url_name'], x['value']
            try:
                #seperate the stats
                pos_stat_1, pos_stat_1val, pos_stat_2, pos_stat_2val = str(pos_stats[0]).replace("_", " "), str(pos_values[0]), str(pos_stats[1]).replace("_", " "), str(pos_values[1])
            except:
                print("Failed at comment: seperate the stats", pos_stat_1, pos_stat_1val)
            #third stats if they exist
            if len(pos_stats) > 2 and len(pos_values) > 2:
                pos_stat_3, pos_stat_3val = str(pos_stats[2]).replace("_", " "), str(pos_values[2]).replace("_", " ")
            else:
                pos_stat_3, pos_stat_3val = [], []
            #add it to a dict
            number_of_filters = int(number_of_filters) + 1
            if "ax_52" in i['item']['weapon_url_name']:
                weapon = "ax-52"
            elif "vinquibus_melee" in i['item']['weapon_url_name']:
                weapon = "vinquibus melee"
            elif "vinquibus" in i['item']['weapon_url_name']:
                weapon = "vinquibus primary"
            elif "efv_5_jupiter" in i['item']['weapon_url_name']:
                weapon = "efv-5 jupiter"
            elif "efv_8_mars" in i['item']['weapon_url_name']:
                weapon = "efv-8 mars"
            elif "riot_848" in i['item']['weapon_url_name']:
                weapon = "riot-848"
            else:
                weapon = i['item']['weapon_url_name']
            riven_data.update({str(number_of_filters):{'user':i['owner']['ingame_name'],'prefix':i['item']['name'],'weapon':weapon,'bo_price':i['buyout_price'],'start_price':i['starting_price'],'mr':i['item']['mastery_level'],'prefix':i['item']['name'],'rank':i['item']['mod_rank'],'rerolls':i['item']['re_rolls'],'polarity':i['item']['polarity'],'wfm_auc':i['id'],'pos1':pos_stat_1, 'pos_val1':pos_stat_1val,'pos2':pos_stat_2,'pos_val2':pos_stat_2val,'pos3':pos_stat_3,'pos_val3':pos_stat_3val, 'neg':neg_stats, 'neg_values':neg_values}})
        #filter through the data
        with open("filters.json") as json_file:
            filters = json.load(json_file)
        todays_date = date.today()
        blacklist = []
        # select the db
        for x in riven_data:
            conwf = sqlite3.connect("wfm.db")
            #make identifier for the riven
            identifier = str(riven_data[x]['user'])  ,str(str(riven_data[x]['weapon']).replace("_"," "))  ,str(riven_data[x]['prefix'])   ,str(riven_data[x]['rank'])  ,str(riven_data[x]['mr']) ,str(riven_data[x]['polarity'])  ,str(riven_data[x]['pos_val1'])  ,str(riven_data[x]['pos1'])  ,str(riven_data[x]['pos_val2'])  ,str(riven_data[x]['pos2'])  ,str(riven_data[x]['pos_val3'])  ,str(riven_data[x]['pos3'])  ,str(riven_data[x]['neg_values'])  ,str(riven_data[x]['neg'])
            # riven_data[x]['pos_val1'], riven_data[x]['pos_val2'], riven_data[x]['pos_val3'], riven_data[x]['neg_values'] = bane_patch.front_to_back(riven_data[x]['pos1'], riven_data[x]['pos_val1']), bane_patch.front_to_back(riven_data[x]['pos2'], riven_data[x]['pos_val2']),bane_patch.front_to_back(riven_data[x]['pos3'], riven_data[x]['pos_val3']), bane_patch.front_to_back(riven_data[x]['neg'], riven_data[x]['neg_values'])  
            #check if its in the identifier already
            if str(identifier) not in str(conwf.execute("SELECT identifier FROM rivens WHERE identifier = ?",(str(identifier),)).fetchone())[2:-3]:
                stats = [i for i in [i for i in sorted([str(riven_data[x]['pos1']).replace("_"," ").lower(),str(riven_data[x]['pos2']).replace("_"," ").lower(),str(riven_data[x]['pos3']).replace("_"," ").lower()]) if i != "[]"] if i != ""]
                for y in filters:
                    filtered = [i for i in [i for i in sorted([str(filters[y]['pos1']).lower(),str(filters[y]['pos2']).lower(),str(filters[y]['pos3']).lower()]) if i != "1"] if i != ""]
                    #filter the riven
                    for item in weapon_info:
                        if str(riven_data[x]['weapon']).replace("_"," ").lower() in filters[y]['weapon'] or filters[y]['weapon'] == "1" or filters[y]['weapon'] == "any" or (str(filters[y]['weapon']).lower() == weapon_info[item]['type']):
                            if sorted(stats) == sorted(filtered) or filtered == []:
                                if str(riven_data[x]['neg']).lower().replace("_"," ") in str(filters[y]['neg']).lower() or filters[y]['neg'] == "1" or filters[y]['neg'] == "any":                                                       
                                    #get the grades of all variant
                                    description = "```/w " + str(riven_data[x]['user']) + " Hi, I'd like to buy your " + str(riven_data[x]['weapon']).title().replace("_"," ") + " " + str(riven_data[x]['prefix']) + " riven that you sell on warframe.market" + "```\n\n"
                                    description = description_creation(str(riven_data[x]['weapon']).replace("dark_split_sword_(dual_swords)","dark_split-sword").replace("_"," "), riven_data[x]['pos_val1'], str(riven_data[x]['pos1']).replace("_"," "),riven_data[x]['pos_val2'], str(riven_data[x]['pos2']).replace("_"," "), riven_data[x]['pos_val3'], str(riven_data[x]['pos3']).replace("_"," "),riven_data[x]['neg_values'],str(riven_data[x]['neg']).replace("_"," "), str(riven_data[x]['prefix']), description)
                                    #open the blacklist file
                                    with open('blacklist.txt') as blacklist_file:
                                        for line in blacklist_file:
                                            line = line.replace('\n','')
                                            blacklist.append(line.lower())
                                    #check name against blacklist
                                    if str(riven_data[x]['user']).lower() not in str(blacklist).lower():
                                        channel = client.get_channel(snipe)
                                        embed = discord.Embed(title=str(riven_data[x]['weapon']).replace("_"," ") + " " + riven_data[x]['prefix'] + " "+str(riven_data[x]['start_price']) + "-" + str(riven_data[x]['bo_price']),url="https://warframe.market/auction/"+riven_data[x]['wfm_auc'], description=description, color=discord.Color.blue())
                                        embed.set_author(name= riven_data[x]['user'] + "\n" + "Filter: " + str(str(y)))
                                        embed.set_footer(text="Mastery: " + str(riven_data[x]['mr']) + " Roll Count: " + str(riven_data[x]['rerolls']) + " Polarity: " + riven_data[x]['polarity'] + " Rank: " + str(riven_data[x]['rank']))
                                        message = await channel.send(embed=embed)
                                        break
                                    else:
                                        channel = client.get_channel(bl)
                                        embed = discord.Embed(title=str(riven_data[x]['weapon']).replace("_"," ") + " " + riven_data[x]['prefix'] + " "+str(riven_data[x]['start_price']) + "-" + str(riven_data[x]['bo_price']),url="https://warframe.market/auction/"+riven_data[x]['wfm_auc'], description=description, color=discord.Color.blue())
                                        embed.set_author(name= riven_data[x]['user'] + "\n" + "Filter: " + str(str(y)))
                                        embed.set_footer(text="Mastery: " + str(riven_data[x]['mr']) + " Roll Count: " + str(riven_data[x]['rerolls']) + " Polarity: " + riven_data[x]['polarity'] + " Rank: " + str(riven_data[x]['rank']))
                                        message = await channel.send(embed=embed)
                                        break                                        
            # riven_data[x]['pos_val1'], riven_data[x]['pos_val2'], riven_data[x]['pos_val3'], riven_data[x]['neg_values'] = bane_patch.front_to_back(riven_data[x]['pos1'], riven_data[x]['pos_val1']), bane_patch.front_to_back(riven_data[x]['pos2'], riven_data[x]['pos_val2']),bane_patch.front_to_back(riven_data[x]['pos3'], riven_data[x]['pos_val3']), bane_patch.front_to_back(riven_data[x]['neg'], riven_data[x]['neg_values'])  
            # add rivens to the db
            conwf.execute("INSERT OR IGNORE INTO rivens (usernames, weapon, prefix, price, rank, mr, polarity, rerolls, stat1name, stat1stats, stat2name, stat2stats, stat3name, stat3stats, stat4name, stat4stats, identifier, date) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (str(riven_data[x]['user']), str(riven_data[x]['weapon']), str(riven_data[x]['prefix']),riven_data[x]['start_price'], str(riven_data[x]['rank']), str(riven_data[x]['mr']), str(riven_data[x]['polarity']), str(riven_data[x]['rerolls']), str(riven_data[x]['pos1']).replace("_"," ").lower(), str(bane_patch.front_to_back(riven_data[x]['pos1'], riven_data[x]['pos_val1'])).replace("_"," ").lower(), str(riven_data[x]['pos2']).replace("_"," ").lower(), str(bane_patch.front_to_back(riven_data[x]['pos2'], riven_data[x]['pos_val2'])).replace("_"," ").lower(), str(riven_data[x]['pos3']).replace("_"," ").lower(), str(bane_patch.front_to_back(riven_data[x]['pos3'], riven_data[x]['pos_val3'])).replace("_"," ").lower(), str(riven_data[x]['neg']).replace("_"," ").lower(), str(bane_patch.front_to_back(riven_data[x]['neg'], riven_data[x]['neg_values'])).replace("_"," ").lower(), str(identifier),todays_date))
            conwf.commit()

#loop to scrape wfm faster
@tasks.loop()
async def wfm_snipe_loop_fast():
    todays_date = date.today()
    #open blacklist
    blacklist = []
    with open('blacklist.txt') as blacklist_file:
        for line in blacklist_file:
            line = line.replace('\n','')
            blacklist.append(line.lower())
    weapon_names = []
    with open("weapon_info.json") as json_file:
            weapon_info = json.load(json_file)
    for item in weapon_info:
        for weapons in weapon_info[item]['variants'].items():
            weapon_names.append(weapons[0].replace("Primary","").replace("Secondary","").replace("-"," ").strip())
    #set the faster filters
    filters = {
        "1": {"weapon": "melee", "pos1": "critical damage", "pos2": "fire rate / attack speed", "pos3": "range", "neg": ["impact damage", "puncture damage", "channeling efficiency", "critical chance on slide attack", "finisher damage"]},        
        "2": {"weapon": "1", "pos1": "critical chance", "pos2": "critical damage", "pos3": "multishot", "neg": ["impact damage", "puncture damage", "ammo maximum", "zoom", "recoil", "projectile speed", "magazine capacity"]},        
        "3": {"weapon": "melee", "pos1": "electric damage", "pos2": "fire rate / attack speed", "pos3": "range", "neg": ["impact damage", "puncture damage", "channeling efficiency", "critical chance on slide attack", "finisher damage"]}
    }
    description = ""
    link_list = []
    for f in filters:
        #turn inputs into data I use
        weapon = str(filters[f]['weapon']).replace(" ","_")
        stat1name, stat2name, stat3name = translator_search.translate_wfm_search(filters[f]['pos1']).replace(" ","_"), translator_search.translate_wfm_search(filters[f]['pos2']).replace(" ","_"), translator_search.translate_wfm_search(filters[f]['pos3']).replace(" ","_")
        #create the weapon search
        if weapon.lower() == "melee" or weapon.lower() == "shotgun" or weapon.lower() == "kitgun" or weapon.lower() == "rifle" or weapon.lower() == "pistol":
            weapon_url = ""
        elif weapon == "1":
            weapon_url = ""
        elif weapon.title() in str(weapon_names):
            weapon_url = "&weapon_url_name=" + weapon
        else:
            weapon_url = ""
        #check if user wants any of the stats null
        if "1" in stat1name:
            stat1name = ""
        if "1" in stat2name:
            stat2name = ""
        if "1" in stat3name:
            stat3name = ""
        #create the stat_search if any single stat is nothing
        if stat1name == "" :
            stat_search = "&positive_stats=" + stat2name + "," + stat3name
        if stat2name == "":
            stat_search = "&positive_stats=" + stat1name + "," + stat3name
        if stat3name == "":
            stat_search = "&positive_stats=" + stat1name + "," + stat2name
        #create the stat_search if any two stats is nothing
        if stat1name == "" and stat2name == "":
            stat_search = "&positive_stats=" + stat3name
        if stat1name == "" and stat3name == "":
            stat_search = "&positive_stats=" + stat2name
        if stat2name == "" and stat3name == "":
            stat_search = "&positive_stats=" + stat1name
        #create the stat_search if all three stats are nothing
        if stat1name =="" and stat2name == "" and stat3name == "":
            stat_search = ""
        #create the stat_search if none of the stats are nothing
        if stat1name !="" and stat2name != "" and stat3name != "":
            stat_search = "&positive_stats=" + stat1name + "," + stat2name + "," + stat3name
        for neg in filters[f]['neg']:
            #create the neg search
            if "any" in neg.replace(" ", "_"):
                negname = "&negative_stats=has"
            elif "1" not in neg:
                negname = "&negative_stats=" + neg.replace(" ", "_")
            else:
                negname = "&negative_stats=has"
            #create the api link to pull data from
            wfm_search_link = "https://api.warframe.market/v1/auctions/search?type=riven"+weapon_url+stat_search+negname+"&polarity=any&sort_by=price_asc"
            link_list.append(wfm_search_link)
    list_broken = [link_list[x:x+1] for x in range(0,len(link_list), 1)]
    for j in list_broken:
        header = {"Host":"api.warframe.market"}
        data = await asyncio.sleep(0.3, result=grequests.map(grequests.get(u, headers = header) for u in j))
        for i in data:
            try:
                data = dict(json.loads(i.text))
            except:
                continue
            # try:
            #loop through each riven
            for x in data['payload']['auctions']:
                #check if its a pc riven
                if x['platform'] == "pc":
                    #grab the pos stats
                    pos_stats = [item for item in x['item']['attributes'] if item['positive'] == True]
                    pos_stat1, pos_val1, pos_stat2, pos_val2 = str(pos_stats[0]['url_name']).replace("_"," "), str(pos_stats[0]['value']), str(pos_stats[1]['url_name']).replace("_"," "), str(pos_stats[1]['value'])
                    #seperate the pos stats and values
                    try: 
                        pos_stat3 = str(pos_stats[2]['url_name']).replace("_"," ")
                    except:
                        pos_stat3 = ""
                    try:
                        pos_val3 = str(pos_stats[2]['value'])
                    except:
                        pos_val3 = ""
                    #grab the neg stats
                    neg_stats = [item for item in x['item']['attributes'] if item['positive'] == False]
                    #sepearte the value and stat name
                    try:
                        neg_stat = str(neg_stats[0]['url_name']).replace("_"," ")
                    except:
                        neg_stat = ""
                    try:
                        neg_val = str(neg_stats[0]['value'])
                    except:
                        neg_val = ""
                    #grab the rest of the data
                    if "ax_52" in x['item']['weapon_url_name']:
                        weapon_name = "ax-52"
                    elif "vinquibus_melee" in x['item']['weapon_url_name']:
                        weapon_name = "vinquibus melee"
                    elif "vinquibus" in x['item']['weapon_url_name']:
                        weapon_name = "vinquibus primary"
                    elif "efv_5_jupiter" in x['item']['weapon_url_name']:
                        weapon_name = "efv-5 jupiter"
                    elif "efv_8_mars" in x['item']['weapon_url_name']:
                        weapon_name = "efv-8 mars"
                    elif "riot_848" in x['item']['weapon_url_name']:
                        weapon_name = "riot-848"
                    else:
                        weapon_name = x['item']['weapon_url_name']
                    created,  wfm_url, rerolls, note, prefix, user, start_price, bo_price, mr, rank, pol = str(int(time.mktime(parser.parse(x['created']).timetuple()))-18000), x['id'], x['item']['re_rolls'], x['note_raw'], x['item']['name'], x['owner']['ingame_name'],  x['starting_price'], x['buyout_price'], x['item']['mastery_level'], x['item']['mod_rank'], x['item']['polarity']
                    identifier = str(user)  ,str(str(weapon_name).replace("_"," "))  ,str(prefix)   ,str(rank)  ,str(mr) ,str(pol)  ,str(pos_val1)  ,str(pos_stat1)  ,str(pos_val2)  ,str(pos_stat2)  ,str(pos_val3)  ,str(pos_stat3)  ,str(neg_val)  ,str(neg_stat)
                    pos_val1, pos_val2, pos_val3, neg_val = bane_patch.front_to_back(pos_stat1, pos_val1), bane_patch.front_to_back(pos_stat2, pos_val2), bane_patch.front_to_back(pos_stat3, pos_val3), bane_patch.front_to_back(neg_stat, neg_val)
                    # select the db
                    conwf_fast = sqlite3.connect("wfm.db")
                    # print(identifier)
                    # try:
                    #     print(conwf_fast.execute("SELECT identifier FROM rivens WHERE identifier = ?",(str(identifier),)).fetchone()[0])
                    # except:
                    #     print('failed to do db search')
                    if str(identifier) not in str(conwf_fast.execute("SELECT identifier FROM rivens WHERE identifier = ?",(str(identifier),)).fetchone()):
                        # print(identifier,"\n\n")
                        for each in weapon_info:
                            # print(weapon_name)
                            if weapon_name.replace("_"," ").replace("(dual swords)","").strip().title() in weapon_names:
                                # print(weapon_name.replace("_"," ").replace("(dual swords)","").strip().title())
                                # print(identifier)
                                # try:
                                #     print(conwf_fast.execute("SELECT identifier FROM rivens WHERE identifier = ?",(str(identifier),)).fetchone()[0])
                                # except:
                                #     print('failed to do db search')
                                if str(weapon).title() in str(weapon_name).replace("_"," ").replace("-"," ").title() or (weapon == "melee" and weapon_info[each]['type'] == 'melee') or (weapon == "rifle" and weapon_info[each]['type'] == "rifle") or (weapon == "shotgun" and weapon_info[each]['type'] == "shotgun") or (weapon == "kitgun" and weapon_info[each]['type'] == "kitgun") or (weapon == "archgun" and weapon_info[each]['type'] == "archgun") or weapon == "1" or weapon == "any":
                                    # #get grades                                
                                    description = "```/w " + user + " Hi, I'd like to buy your " + str(weapon_name).replace("_"," ").title() + " " + str(prefix) + " riven that you sell on warframe.market" + "```\n\n"
                                    description = description_creation(weapon_name.replace("dark_split_sword_(dual_swords)","dark_split-sword").replace("_"," "), pos_val1, pos_stat1 , pos_val2, pos_stat2, pos_val3, pos_stat3, neg_val, neg_stat, prefix, description) + "Mastery: **" + str(mr) + "** Roll Count: **" + str(rerolls) + "** Polarity: **" + pol + "** Rank: **" + str(rank) + "**"
                                    if note != "":
                                        description += "\n\nDescription: " + note + "\n\nListing created on: <t:" + created + ">"
                                    else:
                                        description += "\n\nListing created on: <t:" + created + ">"
                                if description != None:
                                    #check time of listing and see if its in last hr
                                    if int(int(time.time()-int(created))) <= 3600:
                                        #blacklist filter
                                        # if str(user).lower() not in str(blacklist).lower():
                                        channel = client.get_channel(1347854250394259478)
                                        embed = discord.Embed(title=str(weapon_name).replace("_"," ").title() + " " + prefix + " "+str(start_price) + "-" + str(bo_price),url="https://warframe.market/auction/"+wfm_url, description=description, color=discord.Color.blue())
                                        message = await channel.send(embed=embed)
                                        break
                                        # else:
                                        #     channel = client.get_channel(1111360041258336347)
                                        #     embed = discord.Embed(title=str(weapon_name).replace("_"," ").title() + " " + prefix + " "+str(start_price) + "-" + str(bo_price),url="https://warframe.market/auction/"+wfm_url, description=description, color=discord.Color.blue())                                        
                                        #     message = await channel.send(embed=embed)
                                        #     break
                                    pos_val1, pos_val2, pos_val3, neg_val = bane_patch.front_to_back(pos_stat1, pos_val1), bane_patch.front_to_back(pos_stat2, pos_val2), bane_patch.front_to_back(pos_stat3, pos_val3), bane_patch.front_to_back(neg_stat, neg_val)
                                    #add rivens to the db
                                    conwf_fast.execute("INSERT OR IGNORE INTO rivens (usernames, weapon, prefix, price, rank, mr, polarity, rerolls, stat1name, stat1stats, stat2name, stat2stats, stat3name, stat3stats, stat4name, stat4stats, identifier, date) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                                (str(user), str(weapon_name), str(prefix),start_price, str(rank), str(mr), str(pol), str(rerolls), str(pos_stat1).replace("_"," ").lower(), str(pos_val1).replace("_"," ").lower(), str(pos_stat2).replace("_"," ").lower(), str(pos_val2).replace("_"," ").lower(), str(pos_stat3).replace("_"," ").lower(), str(pos_val3).replace("_"," ").lower(), str(neg_stat).replace("_"," ").lower(), str(neg_val).replace("_"," ").lower(), str(identifier),todays_date))
                                    conwf_fast.commit()
            # except:
            #     print("error on filter number: " + "nope" + wfm_search_link + description + str(i))

#used only for grade_loop so it doesn't double or more post
identifier_list = []

#check for sss/fff grades
@tasks.loop()
async def grade_loop():
    number_of_filters = 0
    riven_data = {}
    with open("wfm_data.json") as json_file:
        data= json.load(json_file)
    for i in data:
        # check if the auction is a riven
        if i['item']['type'] == 'riven':
            #varrs needed
            pos_stats, pos_values, neg_stats, neg_values = [], [], [], []
            #grab the stats
            for x in i['item']['attributes']:
                if x['positive'] == True:
                    pos_stats += [x['url_name']]
                    pos_values += [abs(x['value'])]
                if x['positive'] == False:
                    neg_stats, neg_values = x['url_name'], x['value']
            try:
                #seperate the stats
                pos_stat_1, pos_stat_1val, pos_stat_2, pos_stat_2val = str(pos_stats[0]).replace("_", " "), str(pos_values[0]), str(pos_stats[1]).replace("_", " "), str(pos_values[1])
            except:
                print("Failed at comment: seperate the stats", pos_stat_1, pos_stat_1val)
            #third stats if they exist
            if len(pos_stats) > 2 and len(pos_values) > 2:
                pos_stat_3, pos_stat_3val = str(pos_stats[2]).replace("_", " "), str(pos_values[2]).replace("_", " ")
            else:
                pos_stat_3, pos_stat_3val = [], []
            if "ax_52" in i['item']['weapon_url_name']:
                weapon = "ax-52"
            else:
                weapon = i['item']['weapon_url_name']
            #add it to a dict
            number_of_filters = int(number_of_filters) + 1
            riven_data.update({str(number_of_filters):{'user':i['owner']['ingame_name'],'prefix':i['item']['name'],'weapon':weapon,'bo_price':i['buyout_price'],'start_price':i['starting_price'],'mr':i['item']['mastery_level'],'prefix':i['item']['name'],'rank':i['item']['mod_rank'],'rerolls':i['item']['re_rolls'],'polarity':i['item']['polarity'],'wfm_auc':i['id'],'pos1':pos_stat_1, 'pos_val1':pos_stat_1val,'pos2':pos_stat_2,'pos_val2':pos_stat_2val,'pos3':pos_stat_3,'pos_val3':pos_stat_3val, 'neg':neg_stats, 'neg_values':neg_values}})
    for x in riven_data:
        # select the db
        conwf = sqlite3.connect("wfm.db")
        #make identifier for the riven
        identifier = str(riven_data[x]['user'])  ,str(str(riven_data[x]['weapon']).replace("_"," "))  ,str(riven_data[x]['prefix'])   ,str(riven_data[x]['rank'])  ,str(riven_data[x]['mr']) ,str(riven_data[x]['polarity'])  ,str(riven_data[x]['pos_val1'])  ,str(riven_data[x]['pos1'])  ,str(riven_data[x]['pos_val2'])  ,str(riven_data[x]['pos2'])  ,str(riven_data[x]['pos_val3'])  ,str(riven_data[x]['pos3'])  ,str(riven_data[x]['neg_values'])  ,str(riven_data[x]['neg'])
        if str(identifier) not in str(conwf.execute("SELECT identifier FROM rivens WHERE identifier = ?",(str(identifier),)).fetchone())[2:-3] and str(identifier) not in str(identifier_list):
            grades = grader.grade(str(riven_data[x]['weapon']).replace("dark_split_sword_(dual_swords)","dark_split-sword").replace("_"," "), riven_data[x]['pos_val1'], str(riven_data[x]['pos1']).replace("_"," "),riven_data[x]['pos_val2'], str(riven_data[x]['pos2']).replace("_"," "), riven_data[x]['pos_val3'], str(riven_data[x]['pos3']).replace("_"," "),riven_data[x]['neg_values'],str(riven_data[x]['neg']).replace("_"," "), "8")
            description = "```/w " + riven_data[x]['user'] + " Hi, I'd like to buy your " + str(riven_data[x]['weapon']).title().replace("_"," ") + " " + str(riven_data[x]['prefix']) + " riven that you sell on warframe.market" + "```\n\n"
            has_sss = False
            has_fff = False
            for z in grades:
                try:
                    pos1_color, pos_grade1_1, pos_grade1_2 = grades[z]['pos1']
                except:
                    pos1_color, pos_grade1_1, pos_grade1_2  = "", "", ""
                try:
                    pos2_color,pos_grade2_1, pos_grade2_2 = grades[z]['pos2']
                except:
                    pos2_color, pos_grade2_1, pos_grade2_2 = "", "", ""
                try:
                    pos3_color, pos_grade3_1, pos_grade3_2 = grades[z]['pos3']
                except:
                    pos3_color, pos_grade3_1, pos_grade3_2 = "", "", ""
                try:
                    neg_color, neg_grade1, neg_grade2 = grades[z]['neg']
                except:
                    neg_color, neg_grade1, neg_grade2 = "", "", ""
                pos1, pos2, pos3, neg = str(riven_data[x]['pos1']).replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), str(riven_data[x]['pos2']).replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), str(riven_data[x]['pos3']).replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), str(riven_data[x]['neg']).replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo")
                description += str(grades[z]['weapon']).title() + " "+"\n" +pos1_color+ pos1+ " "+ str(riven_data[x]['pos_val1'])+ " "+ " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") " + " \n"+pos2_color+ pos2+ " "+ str(riven_data[x]['pos_val2']) + " "+ " ("+str(pos_grade2_1)+ "%, "+ pos_grade2_2+ ") " + " \n"+pos3_color+ pos3+ " "+ str(riven_data[x]['pos_val3'])+ " "+   " ("+str(pos_grade3_1)+ "%, "+ pos_grade3_2 + ") " +" \n"+neg_color+ neg+ " "+ str(riven_data[x]['neg_values']) + " "+" ("+str(neg_grade1)+ ", "+ neg_grade2 + ")\n" + "\n"
                if pos_grade1_2 == "F grade" and pos_grade2_2 == "F grade" and pos_grade3_2 == "F grade":
                    has_fff = True
                if pos_grade1_2 == "S grade" and pos_grade2_2 == "S grade" and pos_grade3_2 == "S grade":
                    has_sss = True
            if has_fff == True or has_sss == True:
                identifier_list.append(str(identifier))
                channel = client.get_channel(funni_grades)
                embed = discord.Embed(title=str(riven_data[x]['weapon']).replace("_"," ") + " " + riven_data[x]['prefix'] + " "+str(riven_data[x]['start_price']) + "-" + str(riven_data[x]['bo_price']),url="https://warframe.market/auction/"+riven_data[x]['wfm_auc'], description=description, color=discord.Color.blue())
                embed.set_author(name= riven_data[x]['user'])
                embed.set_footer(text="Mastery: " + str(riven_data[x]['mr']) + " Roll Count: " + str(riven_data[x]['rerolls']) + " Polarity: " + riven_data[x]['polarity'] + " Rank: " + str(riven_data[x]['rank']))
                message = await channel.send(embed=embed)

#start the bot loop
@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    print(
        f'{client.user} has connected to Discord!'
        f'{guild.name}(id: {guild.id})'
    )
    wfm_auc_save.start()
    wfm_snipe_loop.start()
    # wfm_snipe_loop_fast.start()
    grade_loop.start()
client.run(TOKEN)