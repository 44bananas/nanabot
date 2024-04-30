#rm_scraper

import grequests
import json
import grading_functions
from datetime import date
import sqlite3
import os
import discord
import re
from discord.ext import tasks
from dotenv import load_dotenv
from discord import Color
import logging
import translator_search
from bs4 import BeautifulSoup as bs4
import bane_patch

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO, filename='rm_scraper.log', filemode='a')

#discord token and guild
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#channel ids
snipe = int(os.getenv('snipe'))
bl = int(os.getenv('bl'))

#declare discord intents
intents = discord.Intents.all()
intents.message_content = True

client = discord.Client(intents = intents)

#loop to scrape rm
@tasks.loop()
async def rm_snipe_loop():
    #open dispos
    with open("rifle_dispos.txt") as json_file:
        rifle_dispos = json.load(json_file)
    with open("pistol_dispos.txt") as json_file:
        pistol_dispos = json.load(json_file)
    with open("melee_dispos.txt") as json_file:
        melee_dispos = json.load(json_file)
    with open("shotgun_dispos.txt") as json_file:
        shotgun_dispos = json.load(json_file)
    with open("archgun_dispos.txt") as json_file:
        archgun_dispos = json.load(json_file)
    with open("kitgun_dispos.txt") as json_file:
        kitgun_dispos = json.load(json_file)
    logging.info('start of rm loop')
    url = ["https://riven.market/_modules/riven/showrivens.php?baseurl=Lw==&platform=PC&limit=250&recency=1&veiled=false&onlinefirst=false&polarity=all&rank=all&mastery=16&weapon=Any&stats=Any&neg=Any&price=99999&rerolls=-1&sort=time&direction=ASC&page=1&time=0"]
    data = grequests.map(grequests.get(u) for u in url)
    logging.info("webrequest")
    for i in data:
        try:
            data = i.text
        except:
            logging.info("data fucked", data)
            continue
        soup = bs4(data,"lxml")
        table = soup.find('div',attrs={"id":"riven-list"})
        users = []
        riven_data = {}
        count = 0
        for row in table.findAll('div',attrs={'class':"attribute seller"}):
            users += [str(row.text).replace(" ","").replace("\r\n(PC)","")]
        for row,x in zip(table.findAll('div', attrs={'class':"riven"}),users):
            count += 1
            riven_data.update({count:{'weapon':row['data-weapon'],'prefix':row['data-name'],'pos1':row['data-stat1'],'pos_val1':row['data-stat1val'],'pos2':row['data-stat2'],'pos_val2':row['data-stat2val'],'pos3':row['data-stat3'],'pos_val3':row['data-stat3val'],'neg':row['data-stat4'],'negval':row['data-stat4val'], "mr":row['data-mr'],"rank":row['data-rank'],"polarity":row['data-polarity'],"rerolls":row['data-rerolls'],"price":row['data-price'], "user":x}})
        logging.info('got all the riven data for rm')
        #filter through the data
        with open("filters.json") as json_file:
            filters = json.load(json_file)
        todays_date = date.today()
        blacklist = []
        logging.info('before the rm filter')
        for x in riven_data:
            #make identifier for the riven
            identifier = str(riven_data[x]['user']).strip()  ,str(str(riven_data[x]['weapon']).replace("_"," "))  ,str(riven_data[x]['prefix']) ,str(riven_data[x]['rank'])  ,str(riven_data[x]['mr']) ,str(riven_data[x]['polarity'])  ,str(riven_data[x]['pos_val1'])  ,str(riven_data[x]['pos1'])  ,str(riven_data[x]['pos_val2'])  ,str(riven_data[x]['pos2'])  ,str(riven_data[x]['pos_val3'])  ,str(riven_data[x]['pos3'])  ,str(riven_data[x]['negval'])  ,str(riven_data[x]['neg'])
            #replace _ with space
            stat1name, stat2name, stat3name, negstat = translator_search.translate_rm(str(riven_data[x]['pos1']).replace("_"," ")), translator_search.translate_rm(str(riven_data[x]['pos2']).replace("_"," ")), translator_search.translate_rm(str(riven_data[x]['pos3']).replace("_"," ")), translator_search.translate_rm(str(riven_data[x]['neg']).replace("_"," "))
            #if stat doesnt exist make it an empty list
            if stat3name == "":
                stat3name = []
            if negstat == "":
                negstat = []
            #check if its in the identifier already
            conrm = sqlite3.connect("rm.db")
            if str(identifier) not in str(conrm.execute("SELECT identifier FROM rivens WHERE identifier = ?",(str(identifier),)).fetchone())[2:-3]:
                for y in filters:
                    stats = [i for i in [i for i in sorted([str(stat1name).replace("_"," ").lower(),str(stat2name).replace("_"," ").lower(),str(stat3name).replace("_"," ").lower()]) if i != "[]"] if i != ""]
                    filtered = [i for i in [i for i in sorted([str(filters[y]['pos1']).lower(),str(filters[y]['pos2']).lower(),str(filters[y]['pos3']).lower()]) if i != "1"] if i != ""]
                    #filter the riven
                    if str(riven_data[x]['weapon']).replace("_"," ").lower() in filters[y]['weapon'] or filters[y]['weapon'] == "1" or (str(filters[y]['weapon']).lower() == 'melee' and str(riven_data[x]['weapon']).replace("_"," ").lower() in melee_dispos)or (str(filters[y]['weapon']).lower() == 'shotgun' and str(riven_data[x]['weapon']).replace("_"," ").lower() in shotgun_dispos)or (str(filters[y]['weapon']).lower() == 'rifle' and str(riven_data[x]['weapon']).replace("_"," ").lower() in rifle_dispos)or (str(filters[y]['weapon']).lower() == 'archgun' and str(riven_data[x]['weapon']).replace("_"," ").lower() in archgun_dispos)or (str(filters[y]['weapon']).lower() == 'pistol' and str(riven_data[x]['weapon']).replace("_"," ").lower() in pistol_dispos)or (str(filters[y]['weapon']).lower() == 'kitgun' and str(riven_data[x]['weapon']).replace("_"," ").lower() in kitgun_dispos):                        
                        if sorted(stats) == sorted(filtered) or filtered == []:
                            if str(negstat).lower() in filters[y]['neg'] or filters[y]['neg'] == "1":
                                logging.info('after the rm filter')
                                grades = grading_functions.get_varriants(str(riven_data[x]['weapon']).replace("_"," "), riven_data[x]['pos_val1'], stat1name,riven_data[x]['pos_val2'], stat2name, riven_data[x]['pos_val3'], stat3name,riven_data[x]['negval'],negstat)
                                pos_grade1_1, pos_grade1_2, pos_grade2_1, pos_grade2_2, pos_grade3_1, pos_grade3_2, neg_grade1, neg_grade2  = "", "", "", "", "", "", "", ""
                                user = re.sub("[-]","\-",str(re.sub("[_]","\_",str(riven_data[x]['user']).lower().strip())))
                                description = "/w " + user + " Hi, I'd like to buy your " + str(riven_data[x]['weapon']).title().replace("_"," ") + " " + str(riven_data[x]['prefix']) + " riven that you sell on riven.market" + "\n\n"
                                #seperate the grades out
                                if grades == {}:
                                    description += str(riven_data[x]['weapon']).replace("_"," ").title() + " "+"\n"+ str(stat1name)+ " "+ str(riven_data[x]['pos_val1'])+ " "+  " \n"+ str(stat2name)+ " "+ str(riven_data[x]['pos_val2']) + " "+ " \n"+ str(stat3name)+ " "+ str(riven_data[x]['pos_val3'])+ " " +" \n"+ str(negstat)+ " "+ str(riven_data[x]['negval']) + "\n" + "\n"
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
                                        try:
                                            stat1name, stat2name, stat3name, negstat = stat1name.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), stat2name.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), stat3name.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), negstat.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo")
                                        except:
                                            logging.info("name changing failed in grade loop")
                                        description += str(grades[z]['weapon']).title() + " "+"\n"+pos1_color + str(stat1name)+ " "+ str(bane_patch.back_to_front(str(stat1name),str(riven_data[x]['pos_val1'])))+ " "+ " ("+ str(pos_grade1_1)+ "%, " + str(pos_grade1_2)+ ") " + " \n"+pos2_color+ str(stat2name)+ " "+ str(bane_patch.back_to_front(str(stat2name),str(riven_data[x]['pos_val2']))) + " "+ " ("+str(pos_grade2_1)+ "%, "+ str(pos_grade2_2)+ ") " + " \n"+pos3_color+ str(stat3name)+ " "+ str(bane_patch.back_to_front(str(stat3name),str(riven_data[x]['pos_val3'])))+ " "+   " ("+str(pos_grade3_1)+ "%, "+ str(pos_grade3_2) + ") " +" \n"+neg_color+ str(negstat)+ " "+ str(bane_patch.back_to_front(str(negstat),str(riven_data[x]['negval']))) + " "+" ("+str(neg_grade1)+ "%, "+ str(neg_grade2) + ")\n" + "\n"
                                # print(description)
                                #open the blacklist file
                                with open('blacklist.txt') as blacklist_file:
                                    for line in blacklist_file:
                                        line = line.replace('\n','')
                                        blacklist.append(line.lower())
                                logging.info('send to rm_send_discord')
                                #check name against blacklist
                                if str(riven_data[x]['user']).lower().strip() not in str(blacklist).lower().strip():
                                    channel = client.get_channel(snipe)
                                    embed = discord.Embed(title=str(riven_data[x]['weapon']).replace("_"," ") + " " + riven_data[x]['prefix'] + " "+str(riven_data[x]['price']),url="https://riven.market/profile/"+riven_data[x]['user'], description=description, color=discord.Color.purple())
                                    embed.set_author(name= riven_data[x]['user'] + "\n" + "Filter: " + str(str(y)))
                                    embed.set_footer(text="Mastery: " + str(riven_data[x]['mr']) + " Roll Count: " + str(riven_data[x]['rerolls']) + " Polarity: " + riven_data[x]['polarity'] + " Rank: " + str(riven_data[x]['rank']))
                                    message = await channel.send(embed=embed)
                                    logging.info('sent to disocrd, message rm')
                                else:
                                    channel = client.get_channel(bl)
                                    embed = discord.Embed(title=str(riven_data[x]['weapon']).replace("_"," ") + " " + riven_data[x]['prefix'] + " "+str(riven_data[x]['price']),url="https://riven.market/profile/"+riven_data[x]['user'], description=description, color=discord.Color.purple())
                                    embed.set_author(name= riven_data[x]['user'] + "\n" + "Filter: " + str(str(y)))
                                    embed.set_footer(text="Mastery: " + str(riven_data[x]['mr']) + " Roll Count: " + str(riven_data[x]['rerolls']) + " Polarity: " + riven_data[x]['polarity'] + " Rank: " + str(riven_data[x]['rank']))
                                    message = await channel.send(embed=embed)
                                    logging.info('sent to disocrd, message rm')
            #add rivens to the db
            conrm.execute("INSERT OR IGNORE INTO rivens (usernames, weapon, prefix, price, rank, mr, polarity, rerolls, stat1name, stat1stats, stat2name, stat2stats, stat3name, stat3stats, stat4name, stat4stats, identifier, date) values( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (str(riven_data[x]['user']).strip(), str(riven_data[x]['weapon']).lower(), str(riven_data[x]['prefix']),riven_data[x]['price'], str(riven_data[x]['rank']), str(riven_data[x]['mr']), str(riven_data[x]['polarity']), str(riven_data[x]['rerolls']), str(stat1name), str(riven_data[x]['pos_val1']), str(stat2name), str(riven_data[x]['pos_val2']), str(stat3name), str(riven_data[x]['pos_val3']), str(negstat), str(riven_data[x]['negval']), str(identifier),todays_date))
            conrm.commit()

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
    rm_snipe_loop.start()
    logging.info('bot intilized')
client.run(TOKEN)