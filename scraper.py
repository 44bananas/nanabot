#scraper

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
from dateutil import parser, tz
import time
from datetime import datetime
import grequests
import requests
import asyncio

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO, filename='scraper.log', filemode='a')

#discord token and guild
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#channel ids
snipe = int(os.getenv('snipe'))
bl = int(os.getenv('bl'))
alerts = int(os.getenv('alerts'))
sss = int(os.getenv('sss'))
fff = int(os.getenv('fff'))

db_identifiers = set()
db_identifiers_sss_fff = set()

#declare discord intents
intents = discord.Intents.all()
intents.message_content = True

client = discord.Client(intents = intents)

#print to discord
async def rm_send_discord_no_filter(weapon, prefix, start_price, description, user,  mr, rerolls, polarity, rank, id):
    channel = client.get_channel(id)
    embed = discord.Embed(title=weapon + " " + prefix + " "+str(start_price),url="https://riven.market/profile/"+user, description=description, color=discord.Color.purple())
    embed.set_author(name= user)
    embed.set_footer(text="Mastery: " + str(mr) + " Roll Count: " + str(rerolls) + " Polarity: " + polarity + " Rank: " + str(rank))
    message = await channel.send(embed=embed)
    logging.info('sent to disocrd, message rm')

#print to discord
async def wfm_send_discord_no_filter(weapon, prefix, start_price, bo_price, wfm_url, description, user,  mr, rerolls, polarity, rank, id):
    channel = client.get_channel(id)
    embed = discord.Embed(title=weapon + " " + prefix + " "+str(start_price) + "-" + str(bo_price),url="https://warframe.market/auction/"+wfm_url, description=description, color=discord.Color.blue())
    embed.set_author(name= user)
    embed.set_footer(text="Mastery: " + str(mr) + " Roll Count: " + str(rerolls) + " Polarity: " + polarity + " Rank: " + str(rank))
    message = await channel.send(embed=embed)
    logging.info('sent to discord, message wfm')

#print to discord
async def rm_send_discord(weapon, prefix, start_price, description, user, filter_num, mr, rerolls, polarity, rank, id):
    channel = client.get_channel(id)
    embed = discord.Embed(title=weapon + " " + prefix + " "+str(start_price),url="https://riven.market/profile/"+user, description=description, color=discord.Color.purple())
    embed.set_author(name= user + "\n" + "Filter: " + str(filter_num))
    embed.set_footer(text="Mastery: " + str(mr) + " Roll Count: " + str(rerolls) + " Polarity: " + polarity + " Rank: " + str(rank))
    message = await channel.send(embed=embed)
    logging.info('sent to disocrd, message rm')

#print to discord
async def wfm_send_discord(weapon, prefix, start_price, bo_price, wfm_url, description, user, filter_num, mr, rerolls, polarity, rank, id):
    channel = client.get_channel(id)
    embed = discord.Embed(title=weapon + " " + prefix + " "+str(start_price) + "-" + str(bo_price),url="https://warframe.market/auction/"+wfm_url, description=description, color=discord.Color.blue())
    embed.set_author(name= user + "\n" + "Filter: " + str(filter_num))
    embed.set_footer(text="Mastery: " + str(mr) + " Roll Count: " + str(rerolls) + " Polarity: " + polarity + " Rank: " + str(rank))
    message = await channel.send(embed=embed)
    logging.info('sent to discord, message wfm')

#replace some text before sending to discord
async def print_replace(data):
    data = str(data).replace("_", " ")
    data = str(data).replace("channeling efficiency","heavy attack efficiency")
    data = str(data).replace("channeling damage", "initial combo")
    return data

async def filter_func(weapon_name, pos_val1, pos_stat1,pos_val2, pos_stat2, pos_val3, pos_stat3,neg_val,neg_stat, negs, mr, rerolls, pol, rank, note, created, user, prefix):
    #get grades
    grades = grading_functions.get_varriants(str(weapon_name).replace("_"," "), pos_val1, pos_stat1,pos_val2, pos_stat2, pos_val3, pos_stat3,neg_val,neg_stat)
    description = "'''/w " + user + " Hi, I'd like to buy your " + str(weapon_name).replace("_"," ").title() + " " + str(prefix) + " riven that you sell on warframe.market" + "\n\n'''"
    for z in grades:
        try:
            pos1_color, pos_grade1_1, pos_grade1_2 = grades[z]['pos1']
        except:
            pos1_color = ""
            pos_grade1_1 = ""
            pos_grade1_2 = ""
        try:
            pos2_color,pos_grade2_1, pos_grade2_2 = grades[z]['pos2']
        except:
            pos2_color = ""
            pos_grade2_1 = ""
            pos_grade2_2 = ""
        try:
            pos3_color, pos_grade3_1, pos_grade3_2 = grades[z]['pos3']
        except:
            pos3_color = ""
            pos_grade3_1 = ""
            pos_grade3_2 = ""
        try:
            neg_color, neg_grade1, neg_grade2 = grades[z]['neg']
        except:
            neg_color = ""
            neg_grade1 = ""
            neg_grade2 = ""
        pos_stat1 = await print_replace(pos_stat1)
        pos_stat2 = await print_replace(pos_stat2)
        pos_stat3 = await print_replace(pos_stat3)
        neg_stat = await print_replace(neg_stat)
        description += str(grades[z]['weapon']).title() + " "+"\n" +pos1_color+ pos_stat1+ " "+ pos_val1+ " "+ " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") " + " \n"+pos2_color+ pos_stat2+ " "+ pos_val2 + " "+ " ("+str(pos_grade2_1)+ "%, "+ pos_grade2_2+ ") " + " \n"+pos3_color+ pos_stat3+ " "+ pos_val3+ " "+   " ("+str(pos_grade3_1)+ "%, "+ pos_grade3_2 + ") " +" \n"+neg_color+ neg_stat+ " "+ neg_val + " "+" ("+str(neg_grade1)+ "%, "+ neg_grade2 + ")\n" + "\n"
    description +="Mastery: **" + str(mr) + "** Roll Count: **" + str(rerolls) + "** Polarity: **" + pol + "** Rank: **" + str(rank) + "**"
    if note != "":
        description += "\n\nDescription: " + note + "\n\nListing created on: <t:" + created + ">"
    else:
        description += "\n\nListing created on: <t:" + created + ">"
    return description

#loop to scrape wfm
@tasks.loop(seconds=10)
async def wfm_snipe_loop():
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
    logging.info('start of wfm loop')
    global db_identifiers
    number_of_filters = 0
    riven_data = {}
    # get the webpage and json
    test = requests.get('https://api.warframe.market/v1/auctions')
    data = dict(test.json())
    # selec the data from the json
    data = data['payload']['auctions']
    for i in data:
        # check if the auction is a riven
        if i['item']['type'] == 'riven':
            #varrs needed
            pos_stats = []
            pos_values = []
            neg_stats = []
            neg_values = []
            #grab the stats
            for x in i['item']['attributes']:
                if x['positive'] == True:
                    pos_stats += [x['url_name']]
                    pos_values += [abs(x['value'])]
                if x['positive'] == False:
                    neg_stats = x['url_name']
                    neg_values = x['value']
            try:
                #seperate the stats
                pos_stat_1 = str(pos_stats[0]).replace("_", " ")
                pos_stat_1val = str(pos_values[0])
                pos_stat_2 = str(pos_stats[1]).replace("_", " ")
                pos_stat_2val = str(pos_values[1])
            except:
                print("Failed at comment: seperate the stats", pos_stat_1, pos_stat_1val)
            #third stats if they exist
            if len(pos_stats) > 2 and len(pos_values) > 2:
                pos_stat_3 = str(pos_stats[2]).replace("_", " ")
                pos_stat_3val = str(pos_values[2]).replace("_", " ")
            else:
                pos_stat_3 = []
                pos_stat_3val = []
            #add it to a dict
            number_of_filters = int(number_of_filters) + 1
            riven_data.update({str(number_of_filters):{'user':i['owner']['ingame_name'],'prefix':i['item']['name'],'weapon':i['item']['weapon_url_name'],'bo_price':i['buyout_price'],'start_price':i['starting_price'],'mr':i['item']['mastery_level'],'prefix':i['item']['name'],'rank':i['item']['mod_rank'],'rerolls':i['item']['re_rolls'],'polarity':i['item']['polarity'],'wfm_auc':i['id'],'pos1':pos_stat_1, 'pos_val1':pos_stat_1val,'pos2':pos_stat_2,'pos_val2':pos_stat_2val,'pos3':pos_stat_3,'pos_val3':pos_stat_3val, 'neg':neg_stats, 'neg_values':neg_values}})
    logging.info('grabbed the wfm json data and put it in dict riven_data')
    # select the db
    con = sqlite3.connect("wfm.db")

    #filter through the data
    with open("filters.json") as json_file:
        filters = json.load(json_file)
    logging.info('start of the wfm filter')
    todays_date = date.today()
    blacklist = []
    for x in riven_data:
        #make identifier for the riven
        identifier = str(riven_data[x]['user'])  ,str(str(riven_data[x]['weapon']).replace("_"," "))  ,str(riven_data[x]['prefix'])   ,str(riven_data[x]['rank'])  ,str(riven_data[x]['mr']) ,str(riven_data[x]['polarity'])  ,str(riven_data[x]['pos_val1'])  ,str(riven_data[x]['pos1'])  ,str(riven_data[x]['pos_val2'])  ,str(riven_data[x]['pos2'])  ,str(riven_data[x]['pos_val3'])  ,str(riven_data[x]['pos3'])  ,str(riven_data[x]['neg_values'])  ,str(riven_data[x]['neg'])
        #check if its in the identifier already
        if identifier not in db_identifiers:
            for y in filters:
                #filter the riven
                if str(riven_data[x]['weapon']).replace("_"," ").lower() in filters[y]['weapon'] or filters[y]['weapon'] == "1" or (str(filters[y]['weapon']).lower() == 'melee' and str(riven_data[x]['weapon']).replace("_"," ").lower() in melee_dispos)or (str(filters[y]['weapon']).lower() == 'shotgun' and str(riven_data[x]['weapon']).replace("_"," ").lower() in shotgun_dispos)or (str(filters[y]['weapon']).lower() == 'rifle' and str(riven_data[x]['weapon']).replace("_"," ").lower() in rifle_dispos)or (str(filters[y]['weapon']).lower() == 'archgun' and str(riven_data[x]['weapon']).replace("_"," ").lower() in archgun_dispos)or (str(filters[y]['weapon']).lower() == 'pistol' and str(riven_data[x]['weapon']).replace("_"," ").lower() in pistol_dispos)or (str(filters[y]['weapon']).lower() == 'kitgun' and str(riven_data[x]['weapon']).replace("_"," ").lower() in kitgun_dispos):
                    if str(riven_data[x]['pos1']).replace("_"," ").lower() in filters[y]['pos1'] or str(riven_data[x]['pos1']).replace("_"," ").lower() in filters[y]['pos2'] or str(riven_data[x]['pos1']).replace("_"," ").lower() in filters[y]['pos3'] or filters[y]['pos1'] == "1"or filters[y]['pos2'] == "1"or filters[y]['pos3'] == "1":
                            if str(riven_data[x]['pos2']).replace("_"," ").lower() in filters[y]['pos1'] or str(riven_data[x]['pos2']).replace("_"," ").lower() in filters[y]['pos2'] or str(riven_data[x]['pos2']).replace("_"," ").lower() in filters[y]['pos3']or filters[y]['pos1'] == "1"or filters[y]['pos2'] == "1"or filters[y]['pos3'] == "1":
                                if str(riven_data[x]['pos3']).replace("_"," ").lower() in filters[y]['pos1'] or str(riven_data[x]['pos3']).replace("_"," ").lower() in filters[y]['pos2'] or str(riven_data[x]['pos3']).replace("_"," ").lower() in filters[y]['pos3']or filters[y]['pos1'] == "1"or filters[y]['pos2'] == "1"or filters[y]['pos3'] == "1":
                                    if str(riven_data[x]['neg']).replace("_"," ").lower() in filters[y]['neg'] or filters[y]['neg'] == "1":                                    
                                        logging.info('through the wfm filter')
                                        user = re.sub("[-]","\-",str(re.sub("[_]","\_",str(riven_data[x]['user']))))
                                        #get the grades of all varriants
                                        grades = grading_functions.get_varriants(str(riven_data[x]['weapon']).replace("_"," "), riven_data[x]['pos_val1'], str(riven_data[x]['pos1']).replace("_"," "),riven_data[x]['pos_val2'], str(riven_data[x]['pos2']).replace("_"," "), riven_data[x]['pos_val3'], str(riven_data[x]['pos3']).replace("_"," "),riven_data[x]['neg_values'],str(riven_data[x]['neg']).replace("_"," "))
                                        description = "'''/w " + user + " Hi, I'd like to buy your " + str(riven_data[x]['weapon']).title().replace("_"," ") + " " + str(riven_data[x]['prefix']) + " riven that you sell on warframe.market" + "\n\n'''"
                                        #seperate the grades out
                                        for z in grades:
                                            try:
                                                pos1_color, pos_grade1_1, pos_grade1_2 = grades[z]['pos1']
                                            except:
                                                pos1_color = ""
                                                pos_grade1_1 = ""
                                                pos_grade1_2 = ""
                                            try:
                                                pos2_color,pos_grade2_1, pos_grade2_2 = grades[z]['pos2']
                                            except:
                                                pos2_color = ""
                                                pos_grade2_1 = ""
                                                pos_grade2_2 = ""
                                            try:
                                                pos3_color, pos_grade3_1, pos_grade3_2 = grades[z]['pos3']
                                            except:
                                                pos3_color = ""
                                                pos_grade3_1 = ""
                                                pos_grade3_2 = ""
                                            try:
                                                neg_color, neg_grade1, neg_grade2 = grades[z]['neg']
                                            except:
                                                neg_color = ""
                                                neg_grade1 = ""
                                                neg_grade2 = ""
                                            pos1 = await print_replace(riven_data[x]['pos1'])
                                            pos2 = await print_replace(riven_data[x]['pos2'])
                                            pos3 = await print_replace(riven_data[x]['pos3'])
                                            neg = await print_replace(riven_data[x]['neg'])
                                            #add grades to the varriable
                                            description += str(grades[z]['weapon']).title() + " "+"\n" +pos1_color+ pos1+ " "+ str(riven_data[x]['pos_val1'])+ " "+ " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") " + " \n"+pos2_color+ pos2+ " "+ str(riven_data[x]['pos_val2']) + " "+ " ("+str(pos_grade2_1)+ "%, "+ pos_grade2_2+ ") " + " \n"+pos3_color+ pos3+ " "+ str(riven_data[x]['pos_val3'])+ " "+   " ("+str(pos_grade3_1)+ "%, "+ pos_grade3_2 + ") " +" \n"+neg_color+ neg+ " "+ str(riven_data[x]['neg_values']) + " "+" ("+str(neg_grade1)+ ", "+ neg_grade2 + ")\n" + "\n"
                                        #open the blacklist file
                                        with open('blacklist.txt') as blacklist_file:
                                            for line in blacklist_file:
                                                line = line.replace('\n','')
                                                blacklist.append(line.lower())
                                        logging.info("send to wfm_send_discord")
                                        #check name against blacklist
                                        if str(riven_data[x]['user']).lower() not in str(blacklist).lower():
                                            await wfm_send_discord(str(riven_data[x]['weapon']).replace("_"," "), riven_data[x]['prefix'], riven_data[x]['start_price'], riven_data[x]['bo_price'], riven_data[x]['wfm_auc'], description, riven_data[x]['user'], str(y), riven_data[x]['mr'], riven_data[x]['rerolls'], riven_data[x]['polarity'], riven_data[x]['rank'],snipe)
                                        else:
                                            await wfm_send_discord(str(riven_data[x]['weapon']).replace("_"," "), riven_data[x]['prefix'], riven_data[x]['start_price'], riven_data[x]['bo_price'], riven_data[x]['wfm_auc'], description, riven_data[x]['user'], str(y), riven_data[x]['mr'], riven_data[x]['rerolls'], riven_data[x]['polarity'], riven_data[x]['rank'],bl)
            #add identifier to the identifiers list
            db_identifiers.add(identifier)
        #add rivens to the db
        con.execute("INSERT OR IGNORE INTO rivens (usernames, weapon, prefix, price, rank, mr, polarity, rerolls, stat1name, stat1stats, stat2name, stat2stats, stat3name, stat3stats, stat4name, stat4stats, identifier, date) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (str(riven_data[x]['user']), str(riven_data[x]['weapon']), str(riven_data[x]['prefix']),riven_data[x]['start_price'], str(riven_data[x]['rank']), str(riven_data[x]['mr']), str(riven_data[x]['polarity']), str(riven_data[x]['rerolls']), str(riven_data[x]['pos1']).replace("_"," ").lower(), str(riven_data[x]['pos_val1']).replace("_"," ").lower(), str(riven_data[x]['pos2']).replace("_"," ").lower(), str(riven_data[x]['pos_val2']).replace("_"," ").lower(), str(riven_data[x]['pos3']).replace("_"," ").lower(), str(riven_data[x]['pos_val3']).replace("_"," ").lower(), str(riven_data[x]['neg']).replace("_"," ").lower(), str(riven_data[x]['neg_values']).replace("_"," ").lower(), str(identifier),todays_date))
        con.commit()

#loop to scrape rm
@tasks.loop(seconds=10)
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
    global db_identifiers
    logging.info('start of rm loop')
    #grab rivens from r.m
    rm_url = "https://riven.market/_modules/riven/showrivens.php?baseurl=Lw==&platform=PC&limit=250&recency=1&veiled=false&onlinefirst=false&polarity=all&rank=all&mastery=16&weapon=Any&stats=Any&neg=Any&price=99999&rerolls=-1&sort=time&direction=ASC&page=1&time=0"

    r = requests.get(rm_url)
    logging.info('requested the data')
    soup = bs4(r.content,"lxml")
    table = soup.find('div',attrs={"id":"riven-list"})

    users = []
    riven_data = {}
    count = 0

    for row in table.findAll('div',attrs={'class':"attribute seller"}):
        users += [str(row.text).replace(" ","")]

    for row,x in zip(table.findAll('div', attrs={'class':"riven"}),users):
        count += 1
        riven_data.update({count:{'weapon':row['data-weapon'],'prefix':row['data-name'],'pos1':row['data-stat1'],'pos_val1':row['data-stat1val'],'pos2':row['data-stat2'],'pos_val2':row['data-stat2val'],'pos3':row['data-stat3'],'pos_val3':row['data-stat3val'],'neg':row['data-stat4'],'negval':row['data-stat4val'], "mr":row['data-mr'],"rank":row['data-rank'],"polarity":row['data-polarity'],"rerolls":row['data-rerolls'],"price":row['data-price'], "user":x}})
    logging.info('got all the riven data for rm')
    #filter through the data
    with open("filters.json") as json_file:
        filters = json.load(json_file)

    todays_date = date.today()

    blacklist = []

    # select the db
    con = sqlite3.connect("rm.db")
    logging.info('before the rm filter')
    for x in riven_data:
        #make identifier for the riven
        identifier = str(riven_data[x]['user']).strip()  ,str(str(riven_data[x]['weapon']).replace("_"," "))  ,str(riven_data[x]['prefix']) ,str(riven_data[x]['rank'])  ,str(riven_data[x]['mr']) ,str(riven_data[x]['polarity'])  ,str(riven_data[x]['pos_val1'])  ,str(riven_data[x]['pos1'])  ,str(riven_data[x]['pos_val2'])  ,str(riven_data[x]['pos2'])  ,str(riven_data[x]['pos_val3'])  ,str(riven_data[x]['pos3'])  ,str(riven_data[x]['negval'])  ,str(riven_data[x]['neg'])
        #replace _ with space
        stat1name = str(riven_data[x]['pos1']).replace("_"," ")
        stat2name = str(riven_data[x]['pos2']).replace("_"," ")
        stat3name = str(riven_data[x]['pos3']).replace("_"," ")
        negstat = str(riven_data[x]['neg']).replace("_"," ")
        #translate riven.market backend names with the backend names I use for grading and filters
        stat1name = translator_search.translate_rm(stat1name)
        stat2name = translator_search.translate_rm(stat2name)
        stat3name = translator_search.translate_rm(stat3name)
        negstat = translator_search.translate_rm(negstat)
        #if stat doesnt exist make it an empty list
        if stat3name == "":
            stat3name = []
        if negstat == "":
            negstat = []
        #check if its in the identifier already
        if identifier not in db_identifiers:
            for y in filters:
                    #filter the riven
                    if str(riven_data[x]['weapon']).replace("_"," ").lower() in filters[y]['weapon'] or filters[y]['weapon'] == "1" or (str(filters[y]['weapon']).lower() == 'melee' and str(riven_data[x]['weapon']).replace("_"," ").lower() in melee_dispos)or (str(filters[y]['weapon']).lower() == 'shotgun' and str(riven_data[x]['weapon']).replace("_"," ").lower() in shotgun_dispos)or (str(filters[y]['weapon']).lower() == 'rifle' and str(riven_data[x]['weapon']).replace("_"," ").lower() in rifle_dispos)or (str(filters[y]['weapon']).lower() == 'archgun' and str(riven_data[x]['weapon']).replace("_"," ").lower() in archgun_dispos)or (str(filters[y]['weapon']).lower() == 'pistol' and str(riven_data[x]['weapon']).replace("_"," ").lower() in pistol_dispos)or (str(filters[y]['weapon']).lower() == 'kitgun' and str(riven_data[x]['weapon']).replace("_"," ").lower() in kitgun_dispos):
                        if str(stat1name) in filters[y]['pos1'] or str(stat1name) in filters[y]['pos2'] or str(stat1name) in filters[y]['pos3'] or filters[y]['pos1'] == "1"or filters[y]['pos2'] == "1"or filters[y]['pos3'] == "1":
                                    if str(stat2name) in filters[y]['pos1'] or str(stat2name) in filters[y]['pos2'] or str(stat2name) in filters[y]['pos3']or filters[y]['pos1'] == "1"or filters[y]['pos2'] == "1"or filters[y]['pos3'] == "1":
                                        if str(stat3name) in filters[y]['pos1'] or str(stat3name) in filters[y]['pos2'] or str(stat3name) in filters[y]['pos3']or filters[y]['pos1'] == "1"or filters[y]['pos2'] == "1"or filters[y]['pos3'] == "1":
                                            if str(negstat).lower() in filters[y]['neg'] or filters[y]['neg'] == "1":
                                                logging.info('after the rm filter')
                                                grades = grading_functions.get_varriants(str(riven_data[x]['weapon']).replace("_"," "), riven_data[x]['pos_val1'], stat1name,riven_data[x]['pos_val2'], stat2name, riven_data[x]['pos_val3'], stat3name,riven_data[x]['negval'],negstat)
                                                pos_grade1_1 = ""
                                                pos_grade1_2 = ""
                                                pos_grade2_1 = ""
                                                pos_grade2_2 = ""
                                                pos_grade3_1 = ""
                                                pos_grade3_2 = ""
                                                neg_grade1 = ""
                                                neg_grade2 = ""
                                                user = re.sub("[-]","\-",str(re.sub("[_]","\_",str(riven_data[x]['user']).lower().strip())))
                                                description = "'''/w " + user + " Hi, I'd like to buy your " + str(riven_data[x]['weapon']).title().replace("_"," ") + " " + str(riven_data[x]['prefix']) + " riven that you sell on riven.market" + "\n\n'''"
                                                #seperate the grades out
                                                if grades == {}:
                                                    # print(str(riven_data[x]['weapon']).replace("_"," ").title(), str(stat1name)+ " "+ str(riven_data[x]['pos_val1']), str(stat2name)+ " "+ str(riven_data[x]['pos_val2']), str(stat3name)+ " "+ str(riven_data[x]['pos_val3']), str(negstat)+ " "+ str(riven_data[x]['negval']), user)
                                                    description += str(riven_data[x]['weapon']).replace("_"," ").title() + " "+"\n"+ str(stat1name)+ " "+ str(riven_data[x]['pos_val1'])+ " "+  " \n"+ str(stat2name)+ " "+ str(riven_data[x]['pos_val2']) + " "+ " \n"+ str(stat3name)+ " "+ str(riven_data[x]['pos_val3'])+ " " +" \n"+ str(negstat)+ " "+ str(riven_data[x]['negval']) + "\n" + "\n"
                                                else:
                                                    for z in grades:
                                                        try:
                                                            pos1_color, pos_grade1_1, pos_grade1_2 = grades[z]['pos1']
                                                        except:
                                                            pos1_color = ""
                                                            pos_grade1_1 = ""
                                                            pos_grade1_2 = ""
                                                        try:
                                                            pos2_color,pos_grade2_1, pos_grade2_2 = grades[z]['pos2']
                                                        except:
                                                            pos2_color = ""
                                                            pos_grade2_1 = ""
                                                            pos_grade2_2 = ""
                                                        try:
                                                            pos3_color, pos_grade3_1, pos_grade3_2 = grades[z]['pos3']
                                                        except:
                                                            pos3_color = ""
                                                            pos_grade3_1 = ""
                                                            pos_grade3_2 = ""
                                                        try:
                                                            neg_color, neg_grade1, neg_grade2 = grades[z]['neg']
                                                        except:
                                                            neg_color = ""
                                                            neg_grade1 = ""
                                                            neg_grade2 = ""
                                                        stat1name = await print_replace(stat1name)
                                                        stat2name = await print_replace(stat2name)
                                                        stat3name = await print_replace(stat3name)
                                                        negstat = await print_replace(negstat)
                                                        description += str(grades[z]['weapon']).title() + " "+"\n"+pos1_color + str(stat1name)+ " "+ str(riven_data[x]['pos_val1'])+ " "+ " ("+ str(pos_grade1_1)+ "%, " + str(pos_grade1_2)+ ") " + " \n"+pos2_color+ str(stat2name)+ " "+ str(riven_data[x]['pos_val2']) + " "+ " ("+str(pos_grade2_1)+ "%, "+ str(pos_grade2_2)+ ") " + " \n"+pos3_color+ str(stat3name)+ " "+ str(riven_data[x]['pos_val3'])+ " "+   " ("+str(pos_grade3_1)+ "%, "+ str(pos_grade3_2) + ") " +" \n"+neg_color+ str(negstat)+ " "+ str(riven_data[x]['negval']) + " "+" ("+str(neg_grade1)+ "%, "+ str(neg_grade2) + ")\n" + "\n"
                                                #open the blacklist file
                                                with open('blacklist.txt') as blacklist_file:
                                                    for line in blacklist_file:
                                                        line = line.replace('\n','')
                                                        blacklist.append(line.lower())
                                                logging.info('send to rm_send_discord')
                                                #check name against blacklist
                                                if str(riven_data[x]['user']).lower().strip() not in str(blacklist).lower().strip():
                                                    await rm_send_discord(str(riven_data[x]['weapon']).replace("_"," "), riven_data[x]['prefix'], riven_data[x]['price'], description, riven_data[x]['user'], str(y), riven_data[x]['mr'], riven_data[x]['rerolls'], riven_data[x]['polarity'], riven_data[x]['rank'],snipe)
                                                else:
                                                    await rm_send_discord(str(riven_data[x]['weapon']).replace("_"," "), riven_data[x]['prefix'], riven_data[x]['price'], description, riven_data[x]['user'], str(y), riven_data[x]['mr'], riven_data[x]['rerolls'], riven_data[x]['polarity'], riven_data[x]['rank'],bl)
            #add identifier to the identifiers list
            db_identifiers.add(identifier)
        #add rivens to the db
        con.execute("INSERT OR IGNORE INTO rivens (usernames, weapon, prefix, price, rank, mr, polarity, rerolls, stat1name, stat1stats, stat2name, stat2stats, stat3name, stat3stats, stat4name, stat4stats, identifier, date) values( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (str(riven_data[x]['user']).strip(), str(riven_data[x]['weapon']).lower(), str(riven_data[x]['prefix']),riven_data[x]['price'], str(riven_data[x]['rank']), str(riven_data[x]['mr']), str(riven_data[x]['polarity']), str(riven_data[x]['rerolls']), str(stat1name), str(riven_data[x]['pos_val1']), str(stat2name), str(riven_data[x]['pos_val2']), str(stat3name), str(riven_data[x]['pos_val3']), str(negstat), str(riven_data[x]['negval']), str(identifier),todays_date))
        con.commit()

#loop to scrape wfm
@tasks.loop()
async def wfm_snipe_loop_fast():
    logging.info("start of wfm_snipe_loop")
    global db_identifiers
    #open blacklist
    blacklist = []
    with open('blacklist.txt') as blacklist_file:
        for line in blacklist_file:
            line = line.replace('\n','')
            blacklist.append(line.lower())
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
    #set the faster filters
    filters = {
        "1": {"weapon": "1", "pos1": "critical chance", "pos2": "critical damage", "pos3": "toxin damage", "neg": ["impact damage", "puncture damage", "channeling efficiency", "critical chance on slide attack", "finisher damage", "ammo maximum", "zoom", "recoil", "projectile speed", "magazine capacity"]},
        "2": {"weapon": "1", "pos1": "critical chance", "pos2": "critical damage", "pos3": "base damage / melee damage", "neg": ["impact damage", "puncture damage", "channeling efficiency", "critical chance on slide attack", "finisher damage", "ammo maximum", "zoom", "recoil", "projectile speed", "magazine capacity"]},
        "3": {"weapon": "melee", "pos1": "critical damage", "pos2": "fire rate / attack speed", "pos3": "range", "neg": ["impact damage", "puncture damage", "channeling efficiency", "critical chance on slide attack", "finisher damage"]},
        "4": {"weapon": "cronus", "pos1": "critical damage", "pos2": "base damage / melee damage", "pos3": "slash damage", "neg": ["impact damage"]},
        "5": {"weapon": "1", "pos1": "critical chance", "pos2": "critical damage", "pos3": "multishot", "neg": ["impact damage", "puncture damage", "ammo maximum", "zoom", "recoil", "projectile speed", "magazine capacity"]},
        "6": {"weapon": "1", "pos1": "toxin damage", "pos2": "critical damage", "pos3": "multishot", "neg": ["impact damage", "puncture damage", "ammo maximum", "zoom", "recoil", "projectile speed", "magazine capacity"]}
    }
    description = ""
    link_list = []
    # filter_list = []
    logging.info("before creating the links")
    for f in filters:
        #turn inputs into data I use
        weapon = str(filters[f]['weapon']).replace(" ","_")
        stat1name = translator_search.translate_wfm_search(filters[f]['pos1']).replace(" ","_")
        stat2name = translator_search.translate_wfm_search(filters[f]['pos2']).replace(" ","_")
        stat3name = translator_search.translate_wfm_search(filters[f]['pos3']).replace(" ","_")
        #create the weapon search
        if weapon.lower() == "melee" or weapon.lower() == "shotgun" or weapon.lower() == "kitgun" or weapon.lower() == "rifle" or weapon.lower() == "pistol":
            weapon_url = ""
        elif weapon == "1":
            weapon_url = ""
        elif weapon.title() in str(rifle_dispos) or weapon.title() in str(shotgun_dispos) or weapon.title() in str(pistol_dispos) or weapon.title() in str(melee_dispos) or weapon.title() in str(archgun_dispos) or weapon.title() in str(kitgun_dispos):
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
            logging.info("wfm_link: "+ str(wfm_search_link))
            link_list.append(wfm_search_link)
    list_broken = [link_list[x:x+3] for x in range(0,len(link_list), 3)]
    for j in list_broken:
        data = await asyncio.sleep(1, result=grequests.map(grequests.get(u) for u in j))
        for i in data:
            try:
                data = dict(json.loads(i.text))
            except:
                logging.info("data fucked", data)
            try:
                #loop through each riven
                for x in data['payload']['auctions']:
                    #check if its a pc riven
                    if x['platform'] == "pc":
                        #grab the pos stats
                        pos_stats = [item for item in x['item']['attributes'] if item['positive'] == True]
                        pos_stat1 = str(pos_stats[0]['url_name']).replace("_"," ")
                        pos_val1 = str(pos_stats[0]['value'])
                        pos_stat2 = str(pos_stats[1]['url_name']).replace("_"," ")
                        pos_val2 = str(pos_stats[1]['value'])
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
                        created = str(int(time.mktime(parser.parse(x['created']).timetuple()))-18000)
                        weapon_name = x['item']['weapon_url_name']
                        wfm_url = x['id']
                        rerolls = x['item']['re_rolls']
                        note = x['note_raw']
                        prefix = x['item']['name']
                        user = x['owner']['ingame_name']
                        start_price = x['starting_price']
                        bo_price = x['buyout_price']
                        description_note = x['note']
                        mr = x['item']['mastery_level']
                        rank = x['item']['mod_rank']
                        pol = x['item']['polarity']
                        identifier = str(user)  ,str(str(weapon_name).replace("_"," "))  ,str(prefix)   ,str(rank)  ,str(mr) ,str(pol)  ,str(pos_val1)  ,str(pos_stat1)  ,str(pos_val2)  ,str(pos_stat2)  ,str(pos_val3)  ,str(pos_stat3)  ,str(neg_val)  ,str(neg_stat)
                        if identifier not in db_identifiers:
                            if str(weapon).title() in str(weapon_name).replace("_"," ").title() or str(weapon).title() in str(weapon_name).replace("_"," ").title() or str(weapon).title() in str(weapon_name).replace("_"," ").title() or str(weapon).title() in str(weapon_name).replace("_"," ").title() or str(weapon).title() in str(weapon_name).replace("_"," ").title():
                                description = await filter_func(weapon_name, pos_val1, pos_stat1,pos_val2, pos_stat2, pos_val3, pos_stat3,neg_val,neg_stat, filters[f]['neg'], mr, rerolls, pol, rank, note, created, user, prefix)
                            elif weapon == "melee" and str(weapon_name).replace("_"," ").title() in melee_dispos:
                                description = await filter_func(weapon_name, pos_val1, pos_stat1,pos_val2, pos_stat2, pos_val3, pos_stat3,neg_val,neg_stat, filters[f]['neg'], mr, rerolls, pol, rank, note, created, user, prefix)
                            elif weapon == "rifle" and str(weapon_name).replace("_"," ").title() in rifle_dispos:
                                description = await filter_func(weapon_name, pos_val1, pos_stat1,pos_val2, pos_stat2, pos_val3, pos_stat3,neg_val,neg_stat, filters[f]['neg'], mr, rerolls, pol, rank, note, created, user, prefix)
                            elif weapon == "shotgun" and str(weapon_name).replace("_"," ").title() in shotgun_dispos:
                                description = await filter_func(weapon_name, pos_val1, pos_stat1,pos_val2, pos_stat2, pos_val3, pos_stat3,neg_val,neg_stat, filters[f]['neg'], mr, rerolls, pol, rank, note, created, user, prefix)
                            elif weapon == "kitgun" and str(weapon_name).replace("_"," ").title() in kitgun_dispos:
                                description = await filter_func(weapon_name, pos_val1, pos_stat1,pos_val2, pos_stat2, pos_val3, pos_stat3,neg_val,neg_stat, filters[f]['neg'], mr, rerolls, pol, rank, note, created, user, prefix)
                            elif weapon == "archgun" and str(weapon_name).replace("_"," ").title() in archgun_dispos:
                                description = await filter_func(weapon_name, pos_val1, pos_stat1,pos_val2, pos_stat2, pos_val3, pos_stat3,neg_val,neg_stat, filters[f]['neg'], mr, rerolls, pol, rank, note, created, user, prefix)
                            elif weapon == "1":
                                description = await filter_func(weapon_name, pos_val1, pos_stat1,pos_val2, pos_stat2, pos_val3, pos_stat3,neg_val,neg_stat, filters[f]['neg'], mr, rerolls, pol, rank, note, created, user, prefix)
                            if description != None:
                                #check time of listing and see if its in last hr
                                if int(int(time.time()-int(created))) <= 3600:
                                    #blacklist filter
                                    if str(user).lower() not in str(blacklist).lower():
                                        channel = client.get_channel(snipe)
                                        embed = discord.Embed(title=str(weapon_name).replace("_"," ").title() + " " + prefix + " "+str(start_price) + "-" + str(bo_price),url="https://warframe.market/auction/"+wfm_url, description=description, color=discord.Color.blue())
                                        # embed.set_author(name="Filter: " + f)
                                        message = await channel.send(embed=embed)
                                    else:
                                        channel = client.get_channel(bl)
                                        embed = discord.Embed(title=str(weapon_name).replace("_"," ").title() + " " + prefix + " "+str(start_price) + "-" + str(bo_price),url="https://warframe.market/auction/"+wfm_url, description=description, color=discord.Color.blue())
                                        # embed.set_author(name="Filter: " + f)
                                        message = await channel.send(embed=embed)
                            db_identifiers.add(identifier)
            except:
                logging.info("error on filter number: ", "nope", wfm_search_link, description, i)
            logging.info("after loop through data")

async def get_url_data(url, session):
    r = await session.request('GET', url=f'{url}')
    data = dict(await r.json())

    return data

#loop to check apis
@tasks.loop(minutes=20)
async def check_api():
    logging.info("check_api start")
    #check fissures
    test = requests.get('https://api.warframestat.us/PC/fissures/')
    data = test.json()
    new_dict = {item['node']:item for item in data}
    for x in new_dict:
        if new_dict[x]['isHard'] == True:
            if new_dict[x]['tierNum'] == 5:
                if "Taveuni" in new_dict[x]['node']:
                    channel = client.get_channel(alerts)
                    embed = discord.Embed(description=new_dict[x]['node']  + "\nTime Left: " + new_dict[x]['eta'])
                    message = await channel.send(embed=embed)
    #check invasions
    test = requests.get('https://api.warframestat.us/PC/invasions/')
    data = test.json()
    description = ""
    new_dict =  {item['node']:item for item in data}
    for x in new_dict:
        #check for forma
        if "Forma Blueprint" in new_dict[x]['attacker']['reward']['itemString']:
            description += "Node: **" + new_dict[x]['node'] + "**\nReward: **" + new_dict[x]['attacker']['reward']['itemString'] + "**\nDescription: **" + new_dict[x]['desc'] + "**\n\n"
        if "Forma Blueprint" in new_dict[x]['defender']['reward']['itemString']:
            description += "Node: **" + new_dict[x]['node'] + "**\nReward: **" + new_dict[x]['defender']['reward']['itemString'] + "**\nDescription: **" + new_dict[x]['desc'] + "**\n\n"
        #check for gold potato
        if "Orokin Catalyst Blueprint" in new_dict[x]['attacker']['reward']['itemString']:
            description += "Node: **" + new_dict[x]['node'] + "**\nReward: **" + new_dict[x]['attacker']['reward']['itemString'] + "**\nDescription: **" + new_dict[x]['desc'] + "**\n\n"
        if "Orokin Catalyst Blueprint" in new_dict[x]['defender']['reward']['itemString']:
            description += "Node: **" + new_dict[x]['node'] + "**\nReward: **" + new_dict[x]['defender']['reward']['itemString'] + "**\nDescription: **" + new_dict[x]['desc'] + "**\n\n"
        #check for silver potato
        if "Orokin Reactor Blueprint" in new_dict[x]['attacker']['reward']['itemString']:
            description += "Node: **" + new_dict[x]['node'] + "**\nReward: **" + new_dict[x]['attacker']['reward']['itemString'] + "**\nDescription: **" + new_dict[x]['desc'] + "**\n\n"
        if "Orokin Reactor Blueprint" in new_dict[x]['defender']['reward']['itemString']:
            description += "Node: **" + new_dict[x]['node'] + "**\nReward: **" + new_dict[x]['defender']['reward']['itemString'] + "**\nDescription: **" + new_dict[x]['desc'] + "**\n\n"
    #send to discord if there is any
    if description != "":
        channel = client.get_channel(alerts)
        embed = discord.Embed(description=description)
        message = await channel.send(embed=embed)
    logging.info("check api end")


#loop to scrape wfm
@tasks.loop(seconds=10)
async def wfm_fff_sss_loop():
    logging.info('start of wfm sss-fff loop')
    global db_identifiers_sss_fff
    number_of_filters = 0
    riven_data = {}
    # get the webpage and json
    test = requests.get('https://api.warframe.market/v1/auctions')
    data = dict(test.json())
    # selec the data from the json
    data = data['payload']['auctions']
    for i in data:
        # check if the auction is a riven
        if i['item']['type'] == 'riven':
            #varrs needed
            pos_stats = []
            pos_values = []
            neg_stats = []
            neg_values = []
            #grab the stats
            for x in i['item']['attributes']:
                if x['positive'] == True:
                    pos_stats += [x['url_name']]
                    pos_values += [abs(x['value'])]
                if x['positive'] == False:
                    neg_stats = x['url_name']
                    neg_values = x['value']
            try:
                #seperate the stats
                pos_stat_1 = str(pos_stats[0]).replace("_", " ")
                pos_stat_1val = str(pos_values[0])
                pos_stat_2 = str(pos_stats[1]).replace("_", " ")
                pos_stat_2val = str(pos_values[1])
            except:
                print("Failed at comment: seperate the stats", pos_stat_1, pos_stat_1val)
            #third stats if they exist
            if len(pos_stats) > 2 and len(pos_values) > 2:
                pos_stat_3 = str(pos_stats[2]).replace("_", " ")
                pos_stat_3val = str(pos_values[2]).replace("_", " ")
            else:
                pos_stat_3 = []
                pos_stat_3val = []
            #add it to a dict
            number_of_filters = int(number_of_filters) + 1
            riven_data.update({str(number_of_filters):{'user':i['owner']['ingame_name'],'prefix':i['item']['name'],'weapon':i['item']['weapon_url_name'],'bo_price':i['buyout_price'],'start_price':i['starting_price'],'mr':i['item']['mastery_level'],'prefix':i['item']['name'],'rank':i['item']['mod_rank'],'rerolls':i['item']['re_rolls'],'polarity':i['item']['polarity'],'wfm_auc':i['id'],'pos1':pos_stat_1, 'pos_val1':pos_stat_1val,'pos2':pos_stat_2,'pos_val2':pos_stat_2val,'pos3':pos_stat_3,'pos_val3':pos_stat_3val, 'neg':neg_stats, 'neg_values':neg_values}})
    logging.info('grabbed the wfm json data and put it in dict riven_data')
    for x in riven_data:
        should_send_to_fff = False
        should_send_to_sss = False
        #make identifier for the riven
        identifier = str(riven_data[x]['user'])  ,str(str(riven_data[x]['weapon']).replace("_"," "))  ,str(riven_data[x]['prefix'])   ,str(riven_data[x]['rank'])  ,str(riven_data[x]['mr']) ,str(riven_data[x]['polarity'])  ,str(riven_data[x]['pos_val1'])  ,str(riven_data[x]['pos1'])  ,str(riven_data[x]['pos_val2'])  ,str(riven_data[x]['pos2'])  ,str(riven_data[x]['pos_val3'])  ,str(riven_data[x]['pos3'])  ,str(riven_data[x]['neg_values'])  ,str(riven_data[x]['neg'])
        #check if its in the identifier already
        if identifier not in db_identifiers:                                
            logging.info('through the wfm filter')
            user = re.sub("[-]","\-",str(re.sub("[_]","\_",str(riven_data[x]['user']))))
            #get the grades of all varriants
            grades = grading_functions.get_varriants(str(riven_data[x]['weapon']).replace("_"," "), riven_data[x]['pos_val1'], str(riven_data[x]['pos1']).replace("_"," "),riven_data[x]['pos_val2'], str(riven_data[x]['pos2']).replace("_"," "), riven_data[x]['pos_val3'], str(riven_data[x]['pos3']).replace("_"," "),riven_data[x]['neg_values'],str(riven_data[x]['neg']).replace("_"," "))
            description = "'''/w " + user + " Hi, I'd like to buy your " + str(riven_data[x]['weapon']).title().replace("_"," ") + " " + str(riven_data[x]['prefix']) + " riven that you sell on warframe.market" + "\n\n'''"
            #seperate the grades out
            for z in grades:
                try:
                    pos1_color, pos_grade1_1, pos_grade1_2 = grades[z]['pos1']
                except:
                    pos1_color = ""
                    pos_grade1_1 = ""
                    pos_grade1_2 = ""
                try:
                    pos2_color,pos_grade2_1, pos_grade2_2 = grades[z]['pos2']
                except:
                    pos2_color = ""
                    pos_grade2_1 = ""
                    pos_grade2_2 = ""
                try:
                    pos3_color, pos_grade3_1, pos_grade3_2 = grades[z]['pos3']
                except:
                    pos3_color = ""
                    pos_grade3_1 = ""
                    pos_grade3_2 = ""
                try:
                    neg_color, neg_grade1, neg_grade2 = grades[z]['neg']
                except:
                    neg_color = ""
                    neg_grade1 = ""
                    neg_grade2 = ""
                pos1 = await print_replace(riven_data[x]['pos1'])
                pos2 = await print_replace(riven_data[x]['pos2'])
                pos3 = await print_replace(riven_data[x]['pos3'])
                neg = await print_replace(riven_data[x]['neg'])
                if "S grade" in pos_grade1_2 and "S grade" in pos_grade2_2 and "S grade" in pos_grade3_2:
                    should_send_to_sss = True
                    #add grades to the varriable
                    description += str(grades[z]['weapon']).title() + " "+"\n" +pos1_color+ pos1+ " "+ str(riven_data[x]['pos_val1'])+ " "+ " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") " + " \n"+pos2_color+ pos2+ " "+ str(riven_data[x]['pos_val2']) + " "+ " ("+str(pos_grade2_1)+ "%, "+ pos_grade2_2+ ") " + " \n"+pos3_color+ pos3+ " "+ str(riven_data[x]['pos_val3'])+ " "+   " ("+str(pos_grade3_1)+ "%, "+ pos_grade3_2 + ") " +" \n"+neg_color+ neg+ " "+ str(riven_data[x]['neg_values']) + " "+" ("+str(neg_grade1)+ "%, "+ neg_grade2 + ")\n" + "\n"
                if "F grade" in pos_grade1_2 and "F grade" in pos_grade2_2 and "F grade" in pos_grade3_2:
                    should_send_to_fff = True
                    #add grades to the varriable
                    description += str(grades[z]['weapon']).title() + " "+"\n" +pos1_color+ pos1+ " "+ str(riven_data[x]['pos_val1'])+ " "+ " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") " + " \n"+pos2_color+ pos2+ " "+ str(riven_data[x]['pos_val2']) + " "+ " ("+str(pos_grade2_1)+ "%, "+ pos_grade2_2+ ") " + " \n"+pos3_color+ pos3+ " "+ str(riven_data[x]['pos_val3'])+ " "+   " ("+str(pos_grade3_1)+ "%, "+ pos_grade3_2 + ") " +" \n"+neg_color+ neg+ " "+ str(riven_data[x]['neg_values']) + " "+" ("+str(neg_grade1)+ "%, "+ neg_grade2 + ")\n" + "\n"
            if should_send_to_fff == True:
                await wfm_send_discord_no_filter(str(riven_data[x]['weapon']).replace("_"," "), riven_data[x]['prefix'], riven_data[x]['start_price'], riven_data[x]['bo_price'], riven_data[x]['wfm_auc'], description, riven_data[x]['user'], riven_data[x]['mr'], riven_data[x]['rerolls'], riven_data[x]['polarity'], riven_data[x]['rank'],fff)
            if should_send_to_sss == True:
                await wfm_send_discord_no_filter(str(riven_data[x]['weapon']).replace("_"," "), riven_data[x]['prefix'], riven_data[x]['start_price'], riven_data[x]['bo_price'], riven_data[x]['wfm_auc'], description, riven_data[x]['user'], riven_data[x]['mr'], riven_data[x]['rerolls'], riven_data[x]['polarity'], riven_data[x]['rank'],sss)
            #add identifier to the identifiers list
            db_identifiers_sss_fff.add(identifier)
    logging.info("end of the wfm fff-sss loop")

@tasks.loop(seconds=10)
async def rm_sss_fff_loop():
    global db_identifiers_sss_fff
    logging.info('start of rm loop')
    #grab rivens from r.m
    rm_url = "https://riven.market/_modules/riven/showrivens.php?baseurl=Lw==&platform=PC&limit=500&recency=1&veiled=false&onlinefirst=false&polarity=all&rank=all&mastery=16&weapon=Any&stats=Any&neg=Any&price=99999&rerolls=-1&sort=time&direction=ASC&page=1&time=0"
    r = requests.get(rm_url)
    soup = bs4(r.content,"lxml")
    table = soup.find('div',attrs={"id":"riven-list"})
    users = []
    riven_data = {}
    count = 0
    for row in table.findAll('div',attrs={'class':"attribute seller"}):
        users += [str(row.text).replace(" ","")]
    for row,x in zip(table.findAll('div', attrs={'class':"riven"}),users):
        count += 1
        riven_data.update({count:{'weapon':row['data-weapon'],'prefix':row['data-name'],'pos1':row['data-stat1'],'pos_val1':row['data-stat1val'],'pos2':row['data-stat2'],'pos_val2':row['data-stat2val'],'pos3':row['data-stat3'],'pos_val3':row['data-stat3val'],'neg':row['data-stat4'],'negval':row['data-stat4val'], "mr":row['data-mr'],"rank":row['data-rank'],"polarity":row['data-polarity'],"rerolls":row['data-rerolls'],"price":row['data-price'], "user":x}})
    logging.info('got all the riven data for rm')
    logging.info('before the rm filter')
    for x in riven_data:
        should_send_to_fff = False
        should_send_to_sss = False
        #make identifier for the riven
        identifier = str(riven_data[x]['user']).strip()  ,str(str(riven_data[x]['weapon']).replace("_"," "))  ,str(riven_data[x]['prefix']) ,str(riven_data[x]['rank'])  ,str(riven_data[x]['mr']) ,str(riven_data[x]['polarity'])  ,str(riven_data[x]['pos_val1'])  ,str(riven_data[x]['pos1'])  ,str(riven_data[x]['pos_val2'])  ,str(riven_data[x]['pos2'])  ,str(riven_data[x]['pos_val3'])  ,str(riven_data[x]['pos3'])  ,str(riven_data[x]['negval'])  ,str(riven_data[x]['neg'])
        #replace _ with space
        stat1name = str(riven_data[x]['pos1']).replace("_"," ")
        stat2name = str(riven_data[x]['pos2']).replace("_"," ")
        stat3name = str(riven_data[x]['pos3']).replace("_"," ")
        negstat = str(riven_data[x]['neg']).replace("_"," ")
        #translate riven.market backend names with the backend names I use for grading and filters
        stat1name = translator_search.translate_rm(stat1name)
        stat2name = translator_search.translate_rm(stat2name)
        stat3name = translator_search.translate_rm(stat3name)
        negstat = translator_search.translate_rm(negstat)
        #if stat doesnt exist make it an empty list
        if stat3name == "":
            stat3name = []
        if negstat == "":
            negstat = []
        #check if its in the identifier already
        if identifier not in db_identifiers:
            logging.info('after the rm filter')
            grades = grading_functions.get_varriants(str(riven_data[x]['weapon']).replace("_"," "), riven_data[x]['pos_val1'], stat1name,riven_data[x]['pos_val2'], stat2name, riven_data[x]['pos_val3'], stat3name,riven_data[x]['negval'],negstat)
            pos_grade1_1 = ""
            pos_grade1_2 = ""
            pos_grade2_1 = ""
            pos_grade2_2 = ""
            pos_grade3_1 = ""
            pos_grade3_2 = ""
            neg_grade1 = ""
            neg_grade2 = ""
            user = re.sub("[-]","\-",str(re.sub("[_]","\_",str(riven_data[x]['user']).lower().strip())))
            description = "'''/w " + user + " Hi, I'd like to buy your " + str(riven_data[x]['weapon']).title().replace("_"," ") + " " + str(riven_data[x]['prefix']) + " riven that you sell on riven.market" + "\n\n'''"
            #seperate the grades out
            if grades == {}:
                # print(str(riven_data[x]['weapon']).replace("_"," ").title(), str(stat1name)+ " "+ str(riven_data[x]['pos_val1']), str(stat2name)+ " "+ str(riven_data[x]['pos_val2']), str(stat3name)+ " "+ str(riven_data[x]['pos_val3']), str(negstat)+ " "+ str(riven_data[x]['negval']), user)
                description += str(riven_data[x]['weapon']).replace("_"," ").title() + " "+"\n"+ str(stat1name)+ " "+ str(riven_data[x]['pos_val1'])+ " "+  " \n"+ str(stat2name)+ " "+ str(riven_data[x]['pos_val2']) + " "+ " \n"+ str(stat3name)+ " "+ str(riven_data[x]['pos_val3'])+ " " +" \n"+ str(negstat)+ " "+ str(riven_data[x]['negval']) + "\n" + "\n"
            else:
                for z in grades:
                    try:
                        pos1_color, pos_grade1_1, pos_grade1_2 = grades[z]['pos1']
                    except:
                        pos1_color = ""
                        pos_grade1_1 = ""
                        pos_grade1_2 = ""
                    try:
                        pos2_color,pos_grade2_1, pos_grade2_2 = grades[z]['pos2']
                    except:
                        pos2_color = ""
                        pos_grade2_1 = ""
                        pos_grade2_2 = ""
                    try:
                        pos3_color, pos_grade3_1, pos_grade3_2 = grades[z]['pos3']
                    except:
                        pos3_color = ""
                        pos_grade3_1 = ""
                        pos_grade3_2 = ""
                    try:
                        neg_color, neg_grade1, neg_grade2 = grades[z]['neg']
                    except:
                        neg_color = ""
                        neg_grade1 = ""
                        neg_grade2 = ""
                    stat1name = await print_replace(stat1name)
                    stat2name = await print_replace(stat2name)
                    stat3name = await print_replace(stat3name)
                    negstat = await print_replace(negstat)
                    if "S grade" in pos_grade1_2 and "S grade" in pos_grade2_2 and "S grade" in pos_grade3_2:
                        should_send_to_sss = True
                        #add grades to the varriable
                        description += str(grades[z]['weapon']).title() + " "+"\n"+pos1_color + str(stat1name)+ " "+ str(riven_data[x]['pos_val1'])+ " "+ " ("+ str(pos_grade1_1)+ "%, " + str(pos_grade1_2)+ ") " + " \n"+pos2_color+ str(stat2name)+ " "+ str(riven_data[x]['pos_val2']) + " "+ " ("+str(pos_grade2_1)+ "%, "+ str(pos_grade2_2)+ ") " + " \n"+pos3_color+ str(stat3name)+ " "+ str(riven_data[x]['pos_val3'])+ " "+   " ("+str(pos_grade3_1)+ "%, "+ str(pos_grade3_2) + ") " +" \n"+neg_color+ str(negstat)+ " "+ str(riven_data[x]['negval']) + " "+" ("+str(neg_grade1)+ "%, "+ str(neg_grade2) + ")\n" + "\n"
                    if "F grade" in pos_grade1_2 and "F grade" in pos_grade2_2 and "F grade" in pos_grade3_2:
                        should_send_to_fff = True
                        #add grades to the varriable
                        description += str(grades[z]['weapon']).title() + " "+"\n"+pos1_color + str(stat1name)+ " "+ str(riven_data[x]['pos_val1'])+ " "+ " ("+ str(pos_grade1_1)+ "%, " + str(pos_grade1_2)+ ") " + " \n"+pos2_color+ str(stat2name)+ " "+ str(riven_data[x]['pos_val2']) + " "+ " ("+str(pos_grade2_1)+ "%, "+ str(pos_grade2_2)+ ") " + " \n"+pos3_color+ str(stat3name)+ " "+ str(riven_data[x]['pos_val3'])+ " "+   " ("+str(pos_grade3_1)+ "%, "+ str(pos_grade3_2) + ") " +" \n"+neg_color+ str(negstat)+ " "+ str(riven_data[x]['negval']) + " "+" ("+str(neg_grade1)+ "%, "+ str(neg_grade2) + ")\n" + "\n"
            logging.info('send to rm_send_discord')
            if should_send_to_fff == True:
                await rm_send_discord_no_filter(str(riven_data[x]['weapon']).replace("_"," "), riven_data[x]['prefix'], riven_data[x]['price'], description, riven_data[x]['user'], riven_data[x]['mr'], riven_data[x]['rerolls'], riven_data[x]['polarity'], riven_data[x]['rank'],fff)
            if should_send_to_sss == True:
                await rm_send_discord_no_filter(str(riven_data[x]['weapon']).replace("_"," "), riven_data[x]['prefix'], riven_data[x]['price'], description, riven_data[x]['user'], riven_data[x]['mr'], riven_data[x]['rerolls'], riven_data[x]['polarity'], riven_data[x]['rank'],sss)
            #add identifier to the identifiers list
            db_identifiers_sss_fff.add(identifier)

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
    wfm_snipe_loop.start()
    rm_snipe_loop.start()
    logging.info('bot intilized')
client.run(TOKEN)
