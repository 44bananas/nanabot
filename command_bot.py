#command bot

import discord
from discord.ext import tasks
from discord.ext import commands
from dotenv import load_dotenv
import sqlite3
import translator_search
import json
import re
import functions_for_functions
import grading_functions
import requests
from dateutil import parser, tz
import time
from discord import Color
import logging
from discord import Interaction
from discord import app_commands
import os
from pagination import Pagination
import typing
import riven_img_dynamic
import random
from PIL import Image, ImageFont, ImageDraw
import io
from pagination_file_send import Pagination_file_send

#discord token and guild
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#discord intents
intents = discord.Intents.all()
intents.message_content = True

#bot and bot command
client = discord.Client(intents = intents)
tree = app_commands.CommandTree(client)     

#rolls command
@tree.command(name = "rolls", description="Check rolls for a weapon", guild=discord.Object(id=GUILD))
async def rolls(interaction:discord.message, weapon:str):
    logging.info("start of rolls")
    #replace the and
    weapon = weapon.lower().replace("And","&").replace("and","&")
    #get lists of rolls
    with open("rolls.json") as json_file:
        rolls_list = dict(json.load(json_file))
    logging.info("start of loop through data")
    if weapon in rolls_list:
        #check if theres notes
        if str(rolls_list[weapon]['notes']) != "nan":
            notes = rolls_list[weapon]['notes']
        else:
            notes = ""
        #create the embed
        embed = discord.Embed(title=weapon.capitalize(),description= "Positive Values: **"+rolls_list[weapon]['pos_stats']+"**\n\n" + "Neg Values: **"+rolls_list[weapon]['neg_stats']+"**\n\n" +str(notes), color=discord.Color.yellow())
    else:
        embed = discord.Embed(title="ERROR", description=weapon+" Not Found", color=discord.Color.red())
    await interaction.response.send_message(embed=embed)
    logging.info("endo of rolls")

#riven img(s) given a wfm link
@tree.command(name = "wfm_grade", description="create a grade image from a wfm link", guild=discord.Object(id=GUILD))
async def wfm_grade(interaction:discord.message,url :str):
    logging.info("start of wfm_grade")
    await interaction.response.defer()

    #take that url and get the url to grab the riven info from
    url = url.split("https://warframe.market/auction/")[1]
    url = "https://api.warframe.market/v1//auctions/entry/" + url

    test = requests.get(url)
    data = dict(test.json())

    # selec the data from the json
    data = data['payload']['auction']

    riven_data = {}
    logging.info("before grabbing data")
    # check if the auction is a riven
    if data['item']['type'] == 'riven':
        #varrs needed
        pos_stats = []
        pos_values = []
        neg_stats = []
        neg_values = []
        #grab the stats
        for x in data['item']['attributes']:
            if x['positive'] == True:
                pos_stats += [x['url_name']]
                pos_values += [abs(x['value'])]
            if x['positive'] == False:
                neg_stats = str(x['url_name']).replace("_", " ")
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
        logging.info("after grabbing data")
        riven_data.update({"weapon":data['item']['weapon_url_name'], "pos1stat":pos_stat_1,"pos1val":pos_stat_1val, "pos2stat":pos_stat_2,"pos2val":pos_stat_2val, "pos3stat":pos_stat_3,"pos3val":pos_stat_3val, "negstat":neg_stats, "negval":neg_values,"rerolls":data['item']['re_rolls'],"pol":data['item']['polarity'],"mr":data['item']['mastery_level']})
    logging.info("before generating image")
    riven_images = riven_img_dynamic.riven_img(riven_data['weapon'], riven_data['pos1stat'], str(riven_data['pos1val']), riven_data['pos2stat'], str(riven_data['pos2val']), riven_data['pos3stat'], str(riven_data['pos3val']), riven_data['negstat'], str(riven_data['negval']), riven_data['pol'], str(riven_data['rerolls']), str(riven_data['mr']))
    riven_images = [i for i in riven_images.values()]
    logging.info("after generating image")
    #cycle through riven images with buttons n shit
    L = 1
    async def get_page(page: int):
        offset = (page-1) * L
        # riven_images = riven_images.values()
        for x in riven_images[offset:offset+L]:
            image = Image.open(io.BytesIO(x))
            image.save("riven_image" + str(offset) + ".png")
            embed = discord.Embed(title = str(riven_data['weapon']).replace("_"," "))
            file = discord.File("riven_image"+str(offset) + ".png", filename="image.png")
            embed.set_image(url="attachment://image.png")
        n = Pagination_file_send.compute_total_pages(len(riven_images), L)
        embed.set_footer(text=f"Riven {page} of {n}")
        return embed, n, file
    logging.info("before sending to discord")
    await Pagination_file_send(interaction, get_page).navegate()
    logging.info("end of wfm_grade")

#give me riven img given stats
@tree.command(name = "img_create", description = "imgcreate", guild=discord.Object(id=GUILD))
async def img_create(interaction:discord.message, weapon:str,stat1:str,stat1val:str, stat2:str,stat2val:str, stat3:str,stat3val:str,neg:str,negval:str,rerolls:typing.Optional[int]=random.randrange(0,1111),mr:typing.Optional[int]=random.randrange(8,16),polarity: typing.Optional[str]=random.choice(["naramon","vazarin","madurai"])):
    logging.info("start of img_create")
    embed_list = []
    files = []
    await interaction.response.defer()
    weapon = weapon.title()
    stat1name_raw = translator_search.translate(stat1).title()
    stat1stat = float(stat1val)
    stat2name_raw = translator_search.translate(stat2).title()
    stat2stat = float(stat2val)
    stat3name_raw = translator_search.translate(stat3).title()
    stat3stat = float(stat3val)
    negname_raw = translator_search.translate(neg).title()
    negstat = float(negval)
    pol = polarity.lower()
    logging.info("before generating image")
    riven_images = riven_img_dynamic.riven_img(weapon, stat1name_raw, stat1stat, stat2name_raw, stat2stat, stat3name_raw, stat3stat, negname_raw, negstat, pol, rerolls, mr)
    riven_images = [i for i in riven_images.values()]
    logging.info("after generating image")
    #cycle through riven images with buttons n shit
    L = 1
    async def get_page(page: int):
        offset = (page-1) * L
        # riven_images = riven_images.values()
        for x in riven_images[offset:offset+L]:
            image = Image.open(io.BytesIO(x))
            image.save("riven_image" + str(offset) + ".png")
            embed = discord.Embed(title = weapon)
            file = discord.File("riven_image"+str(offset) + ".png", filename="image.png")
            embed.set_image(url="attachment://image.png")
        n = Pagination_file_send.compute_total_pages(len(riven_images), L)
        embed.set_footer(text=f"Riven {page} of {n}")
        return embed, n, file
    logging.info("before sending to discord")
    await Pagination_file_send(interaction, get_page).navegate()
    logging.info("end of img_create")

#give me riven prefix name given stats
@tree.command(name = "prefixes", description = "Give the riven prefix names", guild=discord.Object(id=GUILD))
async def prefixes(interaction:discord.message, stat1:str, stat2:str, stat3:str):
    logging.info("start of prefixes")
    #if stat from user = 1 then set it to none
    if stat1 == "1":
        stat1 = ""
    if stat2 == "1":
        stat2 = ""
    if stat3 == "1":
        stat3 = ""
    logging.info("prefixes start")
    #open prefix_suffix
    with open("prefix_suffix.json") as json_file:
        prefix_suffix = json.load(json_file)
    print_message = ""
    #create a list of the stats translated
    stats = [translator_search.translate(stat1).title(),translator_search.translate(stat2).title(),translator_search.translate(stat3).title()]
    prefix = []
    suffix = []
    #get the prefixes/suffexes
    for y in stats:
        try:
            prefix.append(str(prefix_suffix[str(y).title()]['prefix']))
            suffix.append(str(prefix_suffix[str(y).title()]['suffix']))
        except:
            prefix.append("")
            suffix.append("")
            logging.info("stat not found in stats given", y)
    #check if its empty
    if prefix[0] == "" and suffix[0] == "" and prefix[1] == "" and suffix[1] == "" and prefix[2] == "" and suffix[2] == "":
        embed = discord.Embed(title="No Stats", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
    #check if its a single stat
    elif prefix[0] == "" and suffix[0] == "" and prefix[1] == "" and suffix[1] == "":
        print_message += str(prefix[2]) + "\n" + str(suffix[0]) + "\n"
    elif prefix[1] == "" and suffix[1] == "" and prefix[2] == "" and suffix[2] == "":
        print_message += str(prefix[0]) + "\n" + str(suffix[0]) + "\n"
    elif prefix[0] == "" and suffix[0] == "" and prefix[2] == "" and suffix[2] == "":
        print_message += str(prefix[1]) + "\n" + str(suffix[1]) + "\n"
    #check if its a dual stat
    elif prefix[0] == "" and suffix[0] == "":
        print_message += str(prefix[1]) + str(suffix[2]) + "\n"
        print_message += str(prefix[2]) + str(suffix[1]) + "\n"
    elif prefix[1] == "" and suffix[1] == "":
        print_message += str(prefix[0]) + str(suffix[2]) + "\n"
        print_message += str(prefix[2]) + str(suffix[0]) + "\n"
    elif prefix[2] == "" and suffix[2] == "":
        print_message += str(prefix[1]) + str(suffix[0]) + "\n"
        print_message += str(prefix[0]) + str(suffix[1]) + "\n"
    #check if all 3 arent empty
    elif (prefix[0] != "" and suffix[0] != "") and (prefix[1] != "" and suffix[1] != "") and (prefix[2] != "" and suffix[2] != ""):
        print_message += str(prefix[0]) + "-" + str(prefix[1]) + str(suffix[2]) + "\n"
        print_message += str(prefix[0]) + "-" + str(prefix[2]) + str(suffix[1]) + "\n"
        print_message += str(prefix[1]) + "-" + str(prefix[0]) + str(suffix[2]) + "\n"
        print_message += str(prefix[1]) + "-" + str(prefix[2]) + str(suffix[0]) + "\n"
        print_message += str(prefix[2]) + "-" + str(prefix[0]) + str(suffix[1]) + "\n"
        print_message += str(prefix[2]) + "-" + str(prefix[1]) + str(suffix[0]) + "\n"
    #if its not empty, add newlines
    if prefix != ["","",""]:
        print_message += "\n\n"
    #send the name in discord
    embed = discord.Embed(title="Riven Names: ",description= print_message.lower(), color=discord.Color.yellow())
    await interaction.response.send_message(embed=embed)
    logging.info("end of prefixes")

#give riven stats, given a prefix name
@tree.command(name = "riven", description = "Give the prefix, return stats", guild=discord.Object(id=GUILD))
async def riven(interaction:discord.message, name:str):
    logging.info("begining of riven")
    #open prefix_suffix
    with open("prefix_suffix.json") as json_file:
        prefix_suffix = json.load(json_file)
    #create the varriables for the stats
    first_stat = ""
    second_stat = ""
    third_stat = ""
    #grab the stat names from the prefixes/suffix
    for x in prefix_suffix:
        if prefix_suffix[x]['prefix'].lower() in name and first_stat == "":
            first_stat = x
        elif prefix_suffix[x]['prefix'].lower() in name and second_stat == "":
            second_stat = x
        if prefix_suffix[x]['suffix'].lower() in name and third_stat == "":
            third_stat = x
    #send to discord
    if first_stat != "" and second_stat != "" and third_stat != "":
        embed = discord.Embed(title="Stats for: **" + name + "**", description=first_stat +", "+ second_stat +", "+ third_stat)
        await interaction.response.send_message(embed=embed)
    elif first_stat != "" and second_stat != "":
        embed = discord.Embed(title="Stats for: **" + name+ "**", description=first_stat +", "+ second_stat)
        await interaction.response.send_message(embed=embed)
    elif first_stat != "" and third_stat != "":
        embed = discord.Embed(title="Stats for: **" + name+ "**", description=first_stat +", "+ third_stat)
        await interaction.response.send_message(embed=embed)
    elif third_stat != "" and second_stat != "":
        embed = discord.Embed(title="Stats for: **" + name+ "**", description=third_stat +", "+ second_stat)
        await interaction.response.send_message(embed=embed)
    elif first_stat != "":
        embed = discord.Embed(title="Stat for: **" + name+ "**", description=first_stat)
        await interaction.response.send_message(embed=embed)
    elif second_stat != "":
        embed = discord.Embed(title="Stat for: **" + name+ "**", description=second_stat)
        await interaction.response.send_message(embed=embed)
    elif third_stat != "":
        embed = discord.Embed(title="Stat for: **" + name+ "**", description=third_stat)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="No Stats Given or Typo: **" + name+ "**", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
    logging.info("end of riven")

#unroll search wfm
@tree.command(name = "unroll", description = "Grab 10 cheapest unroll rivens for a given weapon", guild=discord.Object(id=GUILD))
async def unroll(interaction:discord.message, weapon:str):
    await interaction.response.defer()
    embed_list = []
    logging.info("unroll command start")
    wfm_search_link = "https://api.warframe.market/v1/auctions/search?type=riven&weapon_url_name="+weapon.replace(" ", "_").replace("&","and").lower()+"&polarity=any&sort_by=price_asc"
    #url to grab from
    data = requests.get(wfm_search_link)
    #make it dict
    data = dict(data.json())
    count = 0
    number_of_returns = 10
    logging.info("unroll before loop")
    try:
        #loop through each riven
        for x in data['payload']['auctions']:
            #check if its a pc riven
            if x['platform'] == "pc":
                count += 1
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
                weapon_name = x['item']['weapon_url_name']
                wfm_url = x['id']
                rerolls = x['item']['re_rolls']
                prefix = x['item']['name']
                user = x['owner']['ingame_name']
                start_price = x['starting_price']
                bo_price = x['buyout_price']
                mr = x['item']['mastery_level']
                rank = x['item']['mod_rank']
                pol = x['item']['polarity']
                status = x['owner']['status']
                pos_stats = pos_stat1+ " "+ pos_val1+"\n"+ pos_stat2+ " "+ pos_val2 + "\n" + pos_stat3+ " "+ pos_val3 + "\n"
                neg_stats = neg_stat + " " + neg_val + "\n"
                if status == "ingame":
                    #make sure they're unrolled
                    if int(rerolls) == 0:
                        if number_of_returns > 0:
                            number_of_returns += -1
                            #send it to discord
                            embed = discord.Embed(title=weapon_name + " " + prefix + " "+str(start_price) + "-" + str(bo_price),url="https://warframe.market/auction/"+wfm_url, description="/w " + user + " Hi, I'd like to buy your " + weapon + " " + prefix + " riven that you sell on warframe.market" +"\n\nPositives:\n "+ pos_stats+"\nNegative: \n" +  neg_stats + "\n\n" + "Mastery: " + str(mr) + " Roll Count: " + str(rerolls) + " Polarity: " + pol + " Rank: " + str(rank), color=discord.Color.blue())
                            embed.set_author(name= user)
                            embed_list.append(embed)
        L = 1
        async def get_page(page: int):
            offset = (page-1) * L
            for embed in embed_list[offset:offset+L]:
                emb = embed
            n = Pagination.compute_total_pages(len(embed_list), L)
            emb.set_footer(text=f"Riven {page} of {n}")
            return emb, n
        await Pagination(interaction, get_page).navegate()
        logging.info("after loop")
    except:
        logging.info("error")
        embed = discord.Embed(title="Error", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
    logging.info("end of unroll")

#folf command
@tree.command(name = "folf", description = "woof", guild=discord.Object(id=GUILD))
async def folf(interaction:discord.message):
    logging.info("begining of folf")
    embed = discord.Embed(title="FLUFFFLUFFLOOFFLORFLFLFOLROFLFOFLFORLFOFL", color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)
    logging.info("end of folf")

#trash search wfm
@tree.command(name = "trash", description = "Grab 10 cheapest rivens for a given weapon", guild=discord.Object(id=GUILD))
async def trash(interaction:discord.message, weapon:str):
    await interaction.response.defer()
    embed_list = []
    logging.info("trash command start")
    wfm_search_link = "https://api.warframe.market/v1/auctions/search?type=riven&weapon_url_name="+weapon.replace(" ", "_").replace("&","and")+"&polarity=any&sort_by=price_asc"
    #url to grab from
    data = requests.get(wfm_search_link)
    #make it dict
    data = dict(data.json())
    count = 0
    number_of_returns = 10
    logging.info("trash before loop")
    try:
        #loop through each riven
        for x in data['payload']['auctions']:
            #check if its a pc riven
            if x['platform'] == "pc":
                count += 1
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
                weapon_name = x['item']['weapon_url_name']
                wfm_url = x['id']
                rerolls = x['item']['re_rolls']
                prefix = x['item']['name']
                user = x['owner']['ingame_name']
                start_price = x['starting_price']
                bo_price = x['buyout_price']
                mr = x['item']['mastery_level']
                rank = x['item']['mod_rank']
                pol = x['item']['polarity']
                if number_of_returns > 0:
                    number_of_returns += -1
                    #send it to discord
                    embed = discord.Embed(title=weapon_name + " " + prefix + " "+str(start_price) + "-" + str(bo_price),url="https://warframe.market/auction/"+wfm_url, description="/w " + user + " Hi, I'd like to buy your " + weapon + " " + prefix + " riven that you sell on warframe.market" +"\n\nPositives:\n"+ pos_stat1+ " "+ pos_val1+"\n"+ pos_stat2+ " "+ pos_val2 + "\n" + pos_stat3+ " "+ pos_val3+"\n\nNegative:\n" +  neg_stat+ " "+ neg_val +" \n\n" + "Mastery: " + str(mr) + " Roll Count: " + str(rerolls) + " Polarity: " + pol + " Rank: " + str(rank)+ neg_val, color=discord.Color.blue())
                    embed.set_author(name= user)
                    embed_list.append(embed)
        L = 1
        async def get_page(page: int):
            offset = (page-1) * L
            for embed in embed_list[offset:offset+L]:
                emb = embed
            n = Pagination.compute_total_pages(len(embed_list), L)
            emb.set_footer(text=f"Riven {page} of {n}")
            return emb, n
        await Pagination(interaction, get_page).navegate()
        logging.info("after loop")
    except:
        logging.info("error")
        embed = discord.Embed(title="Error", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
    logging.info("end of trash")

#check arbi
@tree.command(name = "arby", description = "Check current arbitration", guild=discord.Object(id=GUILD))
async def arby(interaction:discord.message):
    logging.info("arby start")
    url = "https://10o.io/arbitrations.json"
    test = requests.get(url)
    data = dict(test.json()[0])
    # print(data)
    tile = data['solnodedata']['tile']
    planet = data['solnodedata']['planet']
    mission = data['solnodedata']['type']
    enemy = data['solnodedata']['enemy']
    embed = discord.Embed(description="Node: **" + tile + " (" + planet + ")" + "**\nMission Type: **" + mission + "**\nFaction: **" + enemy + "**", color=discord.Color.yellow())
    await interaction.response.send_message(embed=embed)
    logging.info("arby end")

#check events
@tree.command(name = "events", description = "Check events", guild=discord.Object(id=GUILD))
async def events(interaction:discord.message):
    logging.info("events start")
    test = requests.get('https://api.warframestat.us/PC/events/')
    data = test.json()
    new_dict = {item['id']:item for item in data}
    print_statement = ""
    description = []
    for x in new_dict:
        description += [str(new_dict[x]['description'])]
        # print(new_dict[x]['description'])
        for y in new_dict[x]['rewards']:
            if y['items'] != []:
                if str(new_dict[x]['description']) != "Ghoul Purge":
                    rewards = str(y['items'])
        end_date = parser.parse(new_dict[x]['expiry']).replace(tzinfo=tz.tzlocal())
        # print(rewards)
        try: 
            print_statement += "Event: **" + str(new_dict[x]['description'])+ "**\n" + "Rewards: "+ str(re.sub("[\[\]']","",str(rewards))) + "\nEnd Date: " + "<t:" + str(int(time.mktime(end_date.timetuple()))-14400) + ">\n"+ "\n"
        except:
            print_statement += "Event: **" + str(new_dict[x]['description'])+ "**"+ "\nEnd Date: " + "<t:" + str(int(time.mktime(end_date.timetuple()))-14400) + ">\n"+ "\n"
    if  "Ghoul Purge" in str(description):
        #send it to discord
        embed = discord.Embed(description=print_statement, color=discord.Color.yellow())
        await interaction.response.send_message(embed=embed)
    elif print_statement != "":
        #send it to discord
        embed = discord.Embed(description=print_statement, color=discord.Color.yellow())
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(description="No Events", color=discord.Color.yellow())
        await interaction.response.send_message(embed=embed)
    logging.info("events end")

#check sortie
@tree.command(name = "sortie", description = "Check sortie", guild=discord.Object(id=GUILD))
async def sortie(interaction:discord.message):
    logging.info("sortie start")
    #open required files
    with open("solNodes.json") as json_file:
        solnodes = dict(json.load(json_file))
    with open("sortieData.json") as json_file:
        sortie_modifiers = dict(json.load(json_file))
    with open("missionTypes.json") as json_file:
        mission_types = dict(json.load(json_file))
    #grab worldstate data
    test = requests.get("https://content.warframe.com/dynamic/worldState.php")
    data = dict(test.json())
    #grab sortie data
    sortie = data['Sorties']
    #grab data wanted from sortie data
    node = [solnodes[x['node']]['value'] for y in [y for x in sortie for y in sortie] for x in y['Variants']]
    mission = [mission_types[x['missionType']]['value'] for y in [y for x in sortie for y in sortie] for x in y['Variants']]
    debuff = [sortie_modifiers['modifierTypes'][x['modifierType']] for y in [y for x in sortie for y in sortie] for x in y['Variants']]
    #create embed
    description = "Mission 1: **" + str(node[0]) + ", " + str(mission[0]) + "**\nDebuffs: **" + str(debuff[0]) + "\n\n**Mission 2: **" + str(node[1]) + ", " + str(mission[1]) + "\n**Debuffs: **" + str(debuff[1]) + "\n\n**Mission 3: **" + str(node[2]) + ", " + str(mission[2]) + "\n**Debuffs: **" + str(debuff[2]) + "**"
    embed = discord.Embed(title="Sortie today is: ", description= description, color=discord.Color.yellow())
    await interaction.response.send_message(embed=embed)
    logging.info("sortie end")

#check teshins weekly shop for sp
@tree.command(name = "teshin", description = "Check weekly rotating item from teshin", guild=discord.Object(id=GUILD))
async def teshin(interaction:discord.message):
    logging.info("teshin start")
    test = requests.get('https://api.warframestat.us/pc/steelPath/')
    data = dict(test.json())
    #send it to discord
    embed = discord.Embed(title="Current item rotaiton at teshin: ", description= data['currentReward']['name'], color=discord.Color.yellow())
    await interaction.response.send_message(embed=embed)
    logging.info("teshin end")

#print dispo + if it can roll ips
@tree.command(name = "dispo", description = "Give dispo and if weapon rolls ips", guild=discord.Object(id=GUILD))
async def dispo(interaction:discord.message, weapon:str):
    logging.info("dispo start")
    weapon = str(weapon).title().replace("&", "And").replace("_"," ")
    weapon = weapon.replace("Dex Furis", "Afuris").strip()
    with open("ips.txt") as json_file:
        ips = json.load(json_file)
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
    #varrs needed
    can_roll = []
    dispo = ""
    dispo_list = [rifle_dispos, pistol_dispos, melee_dispos, shotgun_dispos, archgun_dispos, kitgun_dispos]
    #weapon names to remove
    kuva_varriant = "Kuva "
    prime_varriant = " Prime"
    tenet_varriant = "Tenet "
    prisma_varriant = "Prisma "
    wraith_varriant = " Wraith"
    synoid_varriant = "Synoid "
    vandal_varriant = " Vandal"
    mk1_varriant = "Mk1-"
    sancti_varriant = "Sancti "
    carmine_varriant = "Carmine "
    telos_varriant = "Telos "
    rakta_varriant = "Rakta "
    secura_varriant = "Secura "
    vaykor_varriant = "Vaykor "
    mara_varriant = "Mara "
    weapon_list = [kuva_varriant, prime_varriant, tenet_varriant, prisma_varriant, wraith_varriant, synoid_varriant, vandal_varriant, mk1_varriant, sancti_varriant, carmine_varriant, telos_varriant, rakta_varriant, secura_varriant, vaykor_varriant, mara_varriant]
    #loop through weapons and remove the varriant names
    for x in weapon_list:
        if x in weapon:
            if weapon.replace(x, "")  in rifle_dispos or weapon.replace(x, "")  in pistol_dispos or weapon.replace(x, "")  in melee_dispos or weapon.replace(x, "")  in shotgun_dispos or weapon.replace(x, "")  in archgun_dispos or weapon.replace(x, "")  in kitgun_dispos:
                if "Gazal" not in weapon:
                    weapon = weapon.replace(x, "")
    #loop through the dispo dicts and add what can roll ips and their dispos to a list and string to send to discord
    for y in dispo_list:
        if weapon in y:
            for x in y:
                if x == weapon:
                    if weapon == "Dex Furis":
                        temp_weapon = "Afuris"
                    else:
                        temp_weapon = weapon
                    if ips[temp_weapon]['Impact'] == True:
                        can_roll += ['Impact']
                    if ips[temp_weapon]['Puncture'] == True:
                        can_roll += ['Puncture']
                    if ips[temp_weapon]['Slash'] == True:
                        can_roll += ['Slash']
                #special case for dex furis
                if x == "Dex Furis" and weapon == "Afuris":
                    dispo += "\n" + x + " " + str(y[x])
                if weapon in x:
                    #special case for skana
                    if weapon == "Skana" and x != "Dual Skana":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Dual Skana":
                        dispo += "\n" + x + " " + str(y[x])
                    #special case for dragon nikana
                    elif weapon == "Dragon Nikana":
                        dispo += "\n" + x + " " + str(y[x])
                    #special case for quanta
                    elif weapon == "Quanta" and x != "Mutalist Quanta":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Mutalist Quanta":
                        dispo += "\n" + x + " " + str(y[x])
                    #special case for cernos
                    elif weapon == "Cernos" and x != "Mutalist Cernos" and x != "Proboscis Cernos":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Mutalist Cernos":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Proboscis Cernos":
                        dispo += "\n" + x + " " + str(y[x])
                    #special case for kohmak
                    elif weapon == "Kohmak" and x != "Twin Kohmak":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Twin Kohmak":
                        dispo += "\n" + x + " " + str(y[x])
                    #special case for furis
                    elif weapon == "Furis" and x != "Afuris":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Afuris":
                        dispo += "\n" + x + " " + str(y[x])
                    #special case for lex
                    elif weapon == "Lex" and x != "Aklex":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Aklex":
                        dispo += "\n" + x + " " + str(y[x])
                    #special case for vasto
                    elif weapon == "Vasto" and x != "Akvasto":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Akvasto":
                        dispo += "\n" + x + " " + str(y[x])
                    #special case for magnus
                    elif weapon == "Magnus" and x != "Akmagnus":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Akmagnus":
                        dispo += "\n" + x + " " + str(y[x])
                    #special case for bronco
                    elif weapon == "Bronco" and x != "Akbronco":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Akbronco":
                        dispo += "\n" + x + " " + str(y[x])
                    #special case for bolto
                    elif weapon == "Bolto" and x != "Akbolto":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Akbolto":
                        dispo += "\n" + x + " " + str(y[x])
                    #special case for cestra
                    elif weapon == "Cestra" and x != "Dual Cestra" and x != "Secura Dual Cestra":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Secura Dual Cestra" or weapon == "Dual Cestra":
                        dispo += "\n" + x + " " + str(y[x])
                    #special case for stubbas
                    elif weapon == "Stubba" and x != "Kuva Twin Stubbas":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Kuva Twin Stubbas":
                        dispo += "\n" + x + " " + str(y[x])
                    #special case for grakata
                    elif weapon == "Grakata" and x != "Twin Grakatas":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Twin Grakatas":
                        dispo += "\n" + x + " " + str(y[x])
                    #special case for viper
                    elif weapon == "Viper" and x != "Twin Vipers" and x != "Twin Vipers Wraith":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Twin Vipers":
                        dispo += "\n" + x + " " + str(y[x])
                    #special cases for war/broken war
                    elif weapon == "War" and x != "Broken War":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Broken War":
                        dispo += "\n" + x + " " + str(y[x])
                    #special case for heat sword
                    elif weapon == "Heat Sword" and x != "Dual Heat Swords":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Dual Heat Swords":
                        dispo += "\n" + x + " " + str(y[x])
                    #special case for machete
                    elif weapon == "Machete" and x != "Gazal Machete":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Gazal Machete":
                        dispo += "\n" + x + " " + str(y[x])
                    #special case for krohkur
                    elif weapon == "Krohkur" and x != "Twin Krohkur":
                        dispo += "\n" + x + " " + str(y[x])
                    elif weapon == "Twin Krohkur":
                        dispo += "\n" + x + " " + str(y[x])
                    elif x != "Dragon Nikana" and x != "Twin Krohkur" and  x != "Gazal Machete" and x != "Dual Heat Swords" and x != "Broken War" and x != "Twin Vipers Wraith" and x != "Twin Vipers" and x != "Twin Grakatas" and x != "Kuva Twin Stubbas" and x != "Dual Cestra" and x != "Secura Dual Cestra" and x != "Akbolto" and x != "Akbronco" and x != "Mutalist Cernos" and x != "Proboscis Cernos" and x != "Dual Skana" and x != "Mutalist Quanta" and x != "Twin Kohmak" and x != "Afuris" and x != "Aklex" and x != "Akvasto" and x != "Akmagnus":
                        dispo += "\n" + x + " " + str(y[x])
    #check if if returns anything and send error message to discord if it didnt
    if dispo == "":
        embed = discord.Embed(description="Weapon Not Found: "+ weapon, color=discord.Color.yellow())
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(description="Dispo(s): "+ re.sub("[\{\}']","",dispo)+ "\n\nIPS: "+re.sub("[\[\],']","",str(can_roll)), color=discord.Color.yellow())
        await interaction.response.send_message(embed=embed)
    logging.info("dispo end")

#grab the data from dbs
async def grab_from_db(db_name):
    logging.info("start of grab_from_db")
    #lists of data I want
    weapon_list  = []
    stat1_list  = []
    stat2_list  = []
    stat3_list  = []
    stat4_list  = []
    prefix_list  = []
    stat1val_list  = []
    stat2val_list  = []
    stat3val_list  = []
    stat4val_list  = []
    user_list  = []
    mr_list  = []
    rollcount_list  = []
    polarity_list  = []
    rank_list  = []
    price_list  = []
    date = []
    data_lists = [weapon_list, stat1_list, stat2_list, stat3_list, stat4_list,  stat1val_list, stat2val_list, stat3val_list, stat4val_list,prefix_list,user_list, mr_list, rollcount_list, polarity_list,rank_list,price_list,date]
    #list of commands needed to grab data
    sql_command_list = ["SELECT weapon FROM rivens;","SELECT stat1name FROM rivens;","SELECT stat2name FROM rivens;","SELECT stat3name FROM rivens;","SELECT stat4name FROM rivens;","SELECT stat1stats FROM rivens;","SELECT stat2stats FROM rivens;","SELECT stat3stats FROM rivens;","SELECT stat4stats FROM rivens;","SELECT prefix FROM rivens;","SELECT usernames FROM rivens;","SELECT mr FROM rivens;","SELECT rerolls FROM rivens;","SELECT polarity FROM rivens;","SELECT rank FROM rivens;","SELECT price FROM rivens;","SELECT date FROM rivens;"]
    #run the sql commands and return the data
    for x,y in zip(data_lists,sql_command_list):
        con = sqlite3.connect(db_name,isolation_level=None)
        con.execute('pragma journal_mode=wal;')
        cur = con.cursor()
        db = cur.execute(y)
        db = db.fetchall()
        for i in db:
            x += [i]
    logging.info("end of grab_from_db")
    return weapon_list, stat1_list, stat2_list, stat3_list, stat4_list,  stat1val_list, stat2val_list, stat3val_list, stat4val_list,prefix_list,user_list, mr_list, rollcount_list, polarity_list,rank_list,price_list,date

#rm db send to discord function
async def print_rm(filtered,db_identifiers):
    list_of_embeds = []
    logging.info("start of print_rm")
    #for every riven that was filtered
    for x in filtered:
        description = ""
        identifier = re.sub("[\(\)',]","",str(filtered[x]['user'])) + re.sub("[\(\)',]","",str(filtered[x]['weapon'])) + re.sub("[\(\)',]","",str(filtered[x]['prefix'])) + re.sub("[\(\)',]","",str(filtered[x]['pos1'])) + re.sub("[\(\)',]","",str(filtered[x]['pos1val']))+re.sub("[\(\)',]","",str(filtered[x]['pos2'])) + re.sub("[\(\)',]","",str(filtered[x]['pos2val']))+re.sub("[\(\)',]","",str(filtered[x]['pos3'])) + re.sub("[\(\)',]","",str(filtered[x]['pos3val']))+re.sub("[\(\)',]","",str(filtered[x]['neg']))+re.sub("[\(\)',]","",str(filtered[x]['negval']))+ re.sub("[\(\)',]","",str(filtered[x]['mr']))+ re.sub("[\(\)',]","",str(filtered[x]['reroll']))+ re.sub("[\(\)',]","",str(filtered[x]['polarity']))+ re.sub("[\(\)',]","",str(filtered[x]['rank']))
        #if it hasnt been sent yet
        if str(identifier) not in str(db_identifiers):
            #grade it
            grades = grading_functions.get_varriants(re.sub("[\(\)',]","",str(filtered[x]['weapon'])),re.sub("[\(\)',]","",str(filtered[x]['pos1val'])),re.sub("[\(\)',]","",str(filtered[x]['pos1'])),re.sub("[\(\)',]","",str(filtered[x]['pos2val'])),re.sub("[\(\)',]","",str(filtered[x]['pos2'])),re.sub("[\(\)',]","",str(filtered[x]['pos3val'])),re.sub("[\(\)',]","",str(filtered[x]['pos3'])),re.sub("[\(\)',]","",str(filtered[x]['negval'])),re.sub("[\(\)',]","",str(filtered[x]['neg'])))
            #seperate the grades
            for y in grades:
                try:
                    pos1_color, pos_grade1_1, pos_grade1_2 = grades[y]['pos1']
                except:
                    pos1_color = ""
                    pos_grade1_1 = ""
                    pos_grade1_2 = ""
                try:
                    pos2_color,pos_grade2_1, pos_grade2_2 = grades[y]['pos2']
                except:
                    pos2_color = ""
                    pos_grade2_1 = ""
                    pos_grade2_2 = ""
                try:
                    pos3_color, pos_grade3_1, pos_grade3_2 = grades[y]['pos3']
                except:
                    pos3_color = ""
                    pos_grade3_1 = ""
                    pos_grade3_2 = ""
                try:
                    neg_color, neg_grade1, neg_grade2 = grades[y]['neg']
                except:
                    neg_color = ""
                    neg_grade1 = ""
                    neg_grade2 = ""
                user = re.sub("[_]","\_",str(re.sub("[-]","\-",str(re.sub("[\(\)',]","",str(filtered[x]['user']))))))
                description += user +  "\n"+"Date: "+ re.sub("[\(\)',]","",str(filtered[x]['date_listed'])) +"\n"+  str(grades[y]['weapon']).title() + " " + re.sub("[\(\)',]","",str(filtered[x]['prefix'])) + " " + re.sub("[\(\)',]","",str(filtered[x]['price']))+ "\n" + pos1_color+   re.sub("[\(\)',]","",str(filtered[x]['pos1']))+ " " + re.sub("[\(\)',]","",str(filtered[x]['pos1val']))+ " " + " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") "+ "\n"+ pos2_color +re.sub("[\(\)',]","",str(filtered[x]['pos2']))+ " " + re.sub("[\(\)',]","",str(filtered[x]['pos2val']))+ " " + " ("+ str(pos_grade2_1)+ "%, " + pos_grade2_2+ ") "+ "\n"+ pos3_color+re.sub("[\(\)',]","",str(filtered[x]['pos3']))+ " " + re.sub("[\(\)',]","",str(filtered[x]['pos3val']))+ " " + " ("+ str(pos_grade3_1)+ "%, " + pos_grade3_2+ ") "+ "\n"+ neg_color+re.sub("[\(\)',]","",str(filtered[x]['neg']))+ " " + re.sub("[\(\)',]","",str(filtered[x]['negval']))+ " " + " ("+ str(neg_grade1)+ "%, " + neg_grade2+ ") " + "\n"+"Mastery: " + re.sub("[\(\)',]","",str(filtered[x]['mr'])) + " Roll Count: " + re.sub("[\(\)',]","",str(filtered[x]['reroll'])) + " Polarity: " + re.sub("[\(\)',]","",str(filtered[x]['polarity'])) + " Rank: " + re.sub("[\(\)',]","",str(filtered[x]['rank']))+ "\n\n"
                db_identifiers.add(identifier)
            if description != "":
                embed = discord.Embed(title="Riven Market",description=description, color=discord.Color.purple())
                list_of_embeds.append(embed)
    logging.info("end of print_rm")
    return list_of_embeds

#wfm db send to discord function
async def print_wfm(filtered,db_identifiers):
    list_of_embeds = []
    logging.info("start of print_wfm")
    #for every riven that was filtered
    for x in filtered:
        description = ""
        identifier = re.sub("[\(\)',]","",str(filtered[x]['user'])) + re.sub("[\(\)',]","",str(filtered[x]['weapon'])) + re.sub("[\(\)',]","",str(filtered[x]['prefix'])) + re.sub("[\(\)',]","",str(filtered[x]['pos1'])) + re.sub("[\(\)',]","",str(filtered[x]['pos1val']))+re.sub("[\(\)',]","",str(filtered[x]['pos2'])) + re.sub("[\(\)',]","",str(filtered[x]['pos2val']))+re.sub("[\(\)',]","",str(filtered[x]['pos3'])) + re.sub("[\(\)',]","",str(filtered[x]['pos3val']))+re.sub("[\(\)',]","",str(filtered[x]['neg']))+re.sub("[\(\)',]","",str(filtered[x]['negval']))+ re.sub("[\(\)',]","",str(filtered[x]['mr']))+ re.sub("[\(\)',]","",str(filtered[x]['reroll']))+ re.sub("[\(\)',]","",str(filtered[x]['polarity']))+ re.sub("[\(\)',]","",str(filtered[x]['rank']))
        #if it hasnt been sent yet
        if str(identifier) not in str(db_identifiers):
            #grade it
            grades = grading_functions.get_varriants(re.sub("[\(\)',]","",str(filtered[x]['weapon'])),re.sub("[\(\)',]","",str(filtered[x]['pos1val'])),re.sub("[\(\)',]","",str(filtered[x]['pos1'])),re.sub("[\(\)',]","",str(filtered[x]['pos2val'])),re.sub("[\(\)',]","",str(filtered[x]['pos2'])),re.sub("[\(\)',]","",str(filtered[x]['pos3val'])),re.sub("[\(\)',]","",str(filtered[x]['pos3'])),re.sub("[\(\)',]","",str(filtered[x]['negval'])),re.sub("[\(\)',]","",str(filtered[x]['neg'])))
            #seperate the grades
            for y in grades:
                try:
                    pos1_color, pos_grade1_1, pos_grade1_2 = grades[y]['pos1']
                except:
                    pos1_color = ""
                    pos_grade1_1 = ""
                    pos_grade1_2 = ""
                try:
                    pos2_color,pos_grade2_1, pos_grade2_2 = grades[y]['pos2']
                except:
                    pos2_color = ""
                    pos_grade2_1 = ""
                    pos_grade2_2 = ""
                try:
                    pos3_color, pos_grade3_1, pos_grade3_2 = grades[y]['pos3']
                except:
                    pos3_color = ""
                    pos_grade3_1 = ""
                    pos_grade3_2 = ""
                try:
                    neg_color, neg_grade1, neg_grade2 = grades[y]['neg']
                except:
                    neg_color = ""
                    neg_grade1 = ""
                    neg_grade2 = ""
                user = re.sub("[_]","\_",str(re.sub("[-]","\-",str(re.sub("[\(\)',]","",str(filtered[x]['user']))))))
                description += user +  "\n"+"Date: "+ re.sub("[\(\)',]","",str(filtered[x]['date_listed'])) +"\n"+  str(grades[y]['weapon']).title() + " " + re.sub("[\(\)',]","",str(filtered[x]['prefix'])) + " " + re.sub("[\(\)',]","",str(filtered[x]['price']))+ "\n" + pos1_color+   re.sub("[\(\)',]","",str(filtered[x]['pos1']))+ " " + re.sub("[\(\)',]","",str(filtered[x]['pos1val']))+ " " + " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") "+ "\n"+ pos2_color +re.sub("[\(\)',]","",str(filtered[x]['pos2']))+ " " + re.sub("[\(\)',]","",str(filtered[x]['pos2val']))+ " " + " ("+ str(pos_grade2_1)+ "%, " + pos_grade2_2+ ") "+ "\n"+ pos3_color+re.sub("[\(\)',]","",str(filtered[x]['pos3']))+ " " + re.sub("[\(\)',]","",str(filtered[x]['pos3val']))+ " " + " ("+ str(pos_grade3_1)+ "%, " + pos_grade3_2+ ") "+ "\n"+ neg_color+re.sub("[\(\)',]","",str(filtered[x]['neg']))+ " " + re.sub("[\(\)',]","",str(filtered[x]['negval']))+ " " + " ("+ str(neg_grade1)+ "%, " + neg_grade2+ ") " + "\n"+"Mastery: " + re.sub("[\(\)',]","",str(filtered[x]['mr'])) + " Roll Count: " + re.sub("[\(\)',]","",str(filtered[x]['reroll'])) + " Polarity: " + re.sub("[\(\)',]","",str(filtered[x]['polarity'])) + " Rank: " + re.sub("[\(\)',]","",str(filtered[x]['rank']))+ "\n\n"
                db_identifiers.add(identifier)
            if description != "":
                embed = discord.Embed(title="Warframe Market",description=description, color=discord.Color.blue())
                list_of_embeds.append(embed)
    logging.info("end of print_wfm")
    return list_of_embeds

#command to search the dbs
@tree.command(name = "search", description = "Search db for rivens", guild=discord.Object(id=GUILD))
async def search(interaction: discord.message, weapon:str, stat1:str, stat2:str, stat3:str,neg:str):
    await interaction.response.defer()
    embed_list = []
    logging.info("search start")
    #translate the arguments given by the user
    arg2 = translator_search.translate(stat1)
    arg3 = translator_search.translate(stat2)
    arg4 = translator_search.translate(stat3)
    arg5 = translator_search.translate(neg).replace("any","1")
    #data input
    neg = arg5
    stats = [arg2, arg3, arg4]
    weapon = str(weapon.lower()).title().replace("_", " ").replace("&", "and")
    if weapon == "Any":
        weapon = "1"
    #grab the data
    data_wfm = await grab_from_db("wfm.db")
    data_rm = await grab_from_db("rm.db")
    #create empty set for checking if riven was sent already
    db_identifiers = set()
    #pull the data out of the list
    weapon_list = data_wfm[0]
    stat1_list = data_wfm[1]
    stat2_list = data_wfm[2]
    stat3_list = data_wfm[3]
    stat4_list = data_wfm[4]
    stat1val_list = data_wfm[5]
    stat2val_list = data_wfm[6]
    stat3val_list = data_wfm[7]
    stat4val_list = data_wfm[8]
    prefix_list = data_wfm[9]
    user_list = data_wfm[10]
    mr_list = data_wfm[11]
    rollcount_list = data_wfm[12]
    polarity_list = data_wfm[13]
    rank_list = data_wfm[14]
    price_list = data_wfm[15]
    date = data_wfm[16]
    logging.info("before filtering wfm data")
    #filter the data
    filtered = await filters_search(weapon, arg2, arg3, arg4, stats, neg, weapon_list, stat1_list, stat2_list, stat3_list, stat4_list,  stat1val_list, stat2val_list, stat3val_list, stat4val_list,prefix_list,user_list, mr_list, rollcount_list, polarity_list,rank_list,price_list,date)
    logging.info("before sending wfm rivens to be sent to discord")
    #print the data
    embed_list.extend(await print_wfm(filtered,db_identifiers))
    #pulld the data out of the list
    weapon_list = data_rm[0]
    stat1_list = data_rm[1]
    stat2_list = data_rm[2]
    stat3_list = data_rm[3]
    stat4_list = data_rm[4]
    stat1val_list = data_rm[5]
    stat2val_list = data_rm[6]
    stat3val_list = data_rm[7]
    stat4val_list = data_rm[8]
    prefix_list = data_rm[9]
    user_list = data_rm[10]
    mr_list = data_rm[11]
    rollcount_list = data_rm[12]
    polarity_list = data_rm[13]
    rank_list = data_rm[14]
    price_list = data_rm[15]
    date = data_rm[16]
    logging.info("before filtering rm data")
    #filter the data
    filtered = await filters_search(weapon, arg2, arg3, arg4, stats, neg, weapon_list, stat1_list, stat2_list, stat3_list, stat4_list,  stat1val_list, stat2val_list, stat3val_list, stat4val_list,prefix_list,user_list, mr_list, rollcount_list, polarity_list,rank_list,price_list,date)
    logging.info("before sending rm rivens to be sent to discord")
    #print the data
    embed_list.extend(await print_rm(filtered,db_identifiers))
    L = 1
    async def get_page(page: int):
        offset = (page-1) * L
        for embed in embed_list[offset:offset+L]:
            emb = embed
        n = Pagination.compute_total_pages(len(embed_list), L)
        emb.set_footer(text=f"Riven {page} of {n}")
        return emb, n
    if embed_list == []:
        #send it to discord
        embed = discord.Embed(title="None Found", color=discord.Color.yellow())
        await interaction.followup.send(embed=embed)
    else:
        await Pagination(interaction, get_page).navegate()
    logging.info("end of search")

#filter the data
async def filters_search(weapon, arg2, arg3, arg4, stats, neg, weapon_list, stat1_list, stat2_list, stat3_list, stat4_list,  stat1val_list, stat2val_list, stat3val_list, stat4val_list,prefix_list,user_list, mr_list, rollcount_list, polarity_list,rank_list,price_list,date):
    logging.info("beinging of filters_search")
    #varrs needed
    matches = {}
    count = 0
    #loop through the lists of data
    for weapon_db, stat1, stat2, stat3, stat4, stat1val, stat2val, stat3val, stat4val, prefix, user, mr, reroll, polarity, rank, price, date_listed in zip(weapon_list, stat1_list, stat2_list, stat3_list, stat4_list,  stat1val_list, stat2val_list, stat3val_list, stat4val_list,prefix_list,user_list, mr_list, rollcount_list, polarity_list,rank_list,price_list,date):
        #replace character with space
        weapon_db = str(weapon_db).replace("_"," ").title()
        #create list of pos stats
        statsdb = [stat1[0],stat2[0],stat3[0]]
        #filter the stats given by user with the stats in the db, (1 == any stat)
        if str(weapon).title() in str(weapon_db).title() or weapon == "1":
            test = all(item in statsdb for item in stats)
            if test == True:
                if neg in str(stat4).replace("_"," ") or neg == "1":
                    count += 1
                    matches.update({count:{'weapon':weapon_db,'pos1':stat1,'pos1val':stat1val,'pos2':stat2,'pos2val':stat2val,'pos3':stat3,'pos3val':stat3val,'neg':stat4,'negval':stat4val,'prefix':prefix,'user':user,'mr':mr,"reroll":reroll,"polarity":polarity,'rank':rank,'price':price,"date_listed":date_listed}})
            elif arg2 == "1" and arg3 == "1" and arg4 == "1":
                if neg in str(stat4).replace("_"," ") or neg == "1":
                    count += 1
                    matches.update({count:{'weapon':weapon_db,'pos1':stat1,'pos1val':stat1val,'pos2':stat2,'pos2val':stat2val,'pos3':stat3,'pos3val':stat3val,'neg':stat4,'negval':stat4val,'prefix':prefix,'user':user,'mr':mr,"reroll":reroll,"polarity":polarity,'rank':rank,'price':price,"date_listed":date_listed}})
            elif arg2 != "1" and arg3 == "1" and arg4 == "1":
                if arg2 in str(statsdb).lower():
                    if neg in str(stat4).replace("_"," ") or neg == "1":
                        count += 1
                        matches.update({count:{'weapon':weapon_db,'pos1':stat1,'pos1val':stat1val,'pos2':stat2,'pos2val':stat2val,'pos3':stat3,'pos3val':stat3val,'neg':stat4,'negval':stat4val,'prefix':prefix,'user':user,'mr':mr,"reroll":reroll,"polarity":polarity,'rank':rank,'price':price,"date_listed":date_listed}})
            elif arg2 == "1" and arg3 != "1" and arg4 == "1":
                if arg3 in str(statsdb).lower():
                    if neg in str(stat4).replace("_"," ") or neg == "1":
                        count += 1
                        matches.update({count:{'weapon':weapon_db,'pos1':stat1,'pos1val':stat1val,'pos2':stat2,'pos2val':stat2val,'pos3':stat3,'pos3val':stat3val,'neg':stat4,'negval':stat4val,'prefix':prefix,'user':user,'mr':mr,"reroll":reroll,"polarity":polarity,'rank':rank,'price':price,"date_listed":date_listed}})
            elif arg2 == "1" and arg3 == "1" and arg4 != "1":
                if arg4 in str(statsdb).lower():
                    if neg in str(stat4).replace("_"," ") or neg == "1":
                        count += 1
                        matches.update({count:{'weapon':weapon_db,'pos1':stat1,'pos1val':stat1val,'pos2':stat2,'pos2val':stat2val,'pos3':stat3,'pos3val':stat3val,'neg':stat4,'negval':stat4val,'prefix':prefix,'user':user,'mr':mr,"reroll":reroll,"polarity":polarity,'rank':rank,'price':price,"date_listed":date_listed}})
            elif arg2 == "1":
                stats = [arg3, arg4]
                test = all(item in statsdb for item in stats)
                if test == True:
                    if neg in str(stat4).replace("_"," ") or neg == "1":
                        count += 1
                        matches.update({count:{'weapon':weapon_db,'pos1':stat1,'pos1val':stat1val,'pos2':stat2,'pos2val':stat2val,'pos3':stat3,'pos3val':stat3val,'neg':stat4,'negval':stat4val,'prefix':prefix,'user':user,'mr':mr,"reroll":reroll,"polarity":polarity,'rank':rank,'price':price,"date_listed":date_listed}})
            elif arg3 == "1":
                stats = [arg2, arg4]
                test = all(item in statsdb for item in stats)
                if test == True:
                    if neg in str(stat4).replace("_"," ") or neg == "1":
                        count += 1
                        matches.update({count:{'weapon':weapon_db,'pos1':stat1,'pos1val':stat1val,'pos2':stat2,'pos2val':stat2val,'pos3':stat3,'pos3val':stat3val,'neg':stat4,'negval':stat4val,'prefix':prefix,'user':user,'mr':mr,"reroll":reroll,"polarity":polarity,'rank':rank,'price':price,"date_listed":date_listed}})
            if arg4 == "1":
                stats = [arg2, arg3]
                test = all(item in statsdb for item in stats)
                if test == True:
                    if neg in str(stat4).replace("_"," ") or neg == "1":
                        count += 1
                        matches.update({count:{'weapon':weapon_db,'pos1':stat1,'pos1val':stat1val,'pos2':stat2,'pos2val':stat2val,'pos3':stat3,'pos3val':stat3val,'neg':stat4,'negval':stat4val,'prefix':prefix,'user':user,'mr':mr,"reroll":reroll,"polarity":polarity,'rank':rank,'price':price,"date_listed":date_listed}})
    logging.info("end of filteres_search")
    #return all the rivens produced
    return matches

#add people to the blacklist
@tree.command(name = "blacklist", description = "Add someone to the blacklist", guild=discord.Object(id=GUILD))
async def blacklist(interaction: discord.message, user: str):
    logging.info("blacklist start")
    #open the file
    blacklist = open('blacklist.txt',"a")
    #add the name
    blacklist.write(user + '\n')
    blacklist.close()
    #send the name in discord
    embed = discord.Embed(title="Added: ",description= user+ " to the blacklist", color=discord.Color.yellow())
    await interaction.response.send_message(embed=embed)
    logging.info("blacklist end")

#check what baro has
@tree.command(name = "baro", description = "Check when baro is here/leaving and his inventory", guild=discord.Object(id=GUILD))
async def baro(interaction: discord.message):
    logging.info("begining of baro")
    test = requests.get('https://api.warframestat.us/PC/voidTrader')
    data = dict(test.json())
    description = ""
    if data['active'] == True:
        for x in data['inventory']:
            description += "**"+x['item'] +"**\nDucats: "+ str(x['ducats']) + "\nCredits: " + str(x['credits']) + "\n\n"
        embed = discord.Embed(title=data['character'] +" is here", description=description + data['character'] +" Leaves in: "+data['endString'], color=discord.Color.yellow())
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title=data['character'] +" is not here", description=data['character'] +" arvies: "+data['endString'], color=discord.Color.yellow())
        await interaction.response.send_message(embed=embed)
    logging.info("end of baro")

#remove a filter
@tree.command(name = "filterremove", description = "Remove a filter", guild=discord.Object(id=GUILD))
async def filterremove(interaction: discord.message, filter: str):
    logging.info("filterremove start")
    #varrs needed
    weapon_name_filter = []
    pos1_filter = []
    pos2_filter = []
    pos3_filter = []
    neg_filter = []
    filter_num = []
    #create lists of the stats
    with open("filters.json") as json_file:
        filters = json.load(json_file)
    for x in filters:
        filter_num += [x]
    for x in await functions_for_functions.find_by_key(filters, "weapon"):
        weapon_name_filter += [x]
    for x in await functions_for_functions.find_by_key(filters, "pos1"):
        pos1_filter += [x]
    for x in await functions_for_functions.find_by_key(filters, "pos2"):
        pos2_filter += [x]
    for x in await functions_for_functions.find_by_key(filters, "pos3"):
        pos3_filter += [x]
    for x in await functions_for_functions.find_by_key(filters, "neg"):
        y = {"neg"}
        neg_dict = dict.fromkeys(y,x)
        test = neg_dict['neg']
        test = re.sub("[{',}]","",str(test))
        neg_filter += list(test.splitlines())
    #varrs needed for filter delete
    count = 0
    filters_updated = {}
    counted_list = []
    filter_copy = filters.copy()
    #loop through filter to find and delete it
    for a, b, c, d, e, f, g in zip(weapon_name_filter, pos1_filter, pos2_filter, pos3_filter, neg_filter, filter_num, filter_copy):
        if filter == g:
            del filters[filter]
            e = str(e)
            e = re.sub("[\[\]]","",e)
            embed = discord.Embed(title="Removed filter "+ f+ ": ", description= a+" "+b+" "+c+" "+d+" negatives:"+e, color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed)
        count = int(count) + 1
        counted_list += [str(count)]
    #new dict with updated filter
    filters_updated = dict(zip(counted_list,list(filters.values())))
    #write the updated filter
    with open("filters.json", "w") as outfile:
        json.dump(filters_updated, outfile)
    logging.info("filterremove end")

#send all the filters to discord
@tree.command(name = "filterlist", description = "List filters", guild=discord.Object(id=GUILD))
async def filterlist(interaction: discord.message):
    await interaction.response.defer()
    logging.info("filterlist start")
    #declare varrs needed
    weapon_name_filter = []
    pos1_filter = []
    pos2_filter = []
    pos3_filter = []
    neg_filter = []
    filter_num = []
    embed_list = []
    L= 1
    #get lists of filters
    with open("filters.json") as json_file:
        filters = json.load(json_file)
    for x in filters:
        filter_num += [x]
    for x in await functions_for_functions.find_by_key(filters, "weapon"):
        weapon_name_filter += [x]
    for x in await functions_for_functions.find_by_key(filters, "pos1"):
        pos1_filter += [x]
    for x in await functions_for_functions.find_by_key(filters, "pos2"):
        pos2_filter += [x]
    for x in await functions_for_functions.find_by_key(filters, "pos3"):
        pos3_filter += [x]
    for x in await functions_for_functions.find_by_key(filters, "neg"):
        y = {"neg"}
        neg_dict = dict.fromkeys(y,x)
        test = neg_dict['neg']
        test = re.sub("[\[\],']","",str(test))
        neg_filter += list(test.splitlines())
    #zip through the lists
    for q, v, w, y, z, k in zip(weapon_name_filter, pos1_filter, pos2_filter, pos3_filter, neg_filter, filter_num):
        #send it to discord
        q = str(q)
        v = str(v)
        w = str(w)
        y = str(y)
        z = str(z)
        q = await functions_for_functions.print_replace(q)
        v = await functions_for_functions.print_replace(v)
        w = await functions_for_functions.print_replace(w)
        y = await functions_for_functions.print_replace(y)
        z = await functions_for_functions.print_replace(z)
        if q == "1":
            q = "any"
        embed = discord.Embed(title="Filter "+ k + ": ",description= "Weapon: " + q+"\nPositives: "+v+", "+w+", "+y+"\nNegatives: "+z, color=discord.Color.yellow())
        embed_list.append(embed)
    async def get_page(page: int):
        offset = (page-1) * L
        for embed in embed_list[offset:offset+L]:
            emb = embed
        n = Pagination.compute_total_pages(len(embed_list), L)
        emb.set_footer(text=f"Riven {page} of {n}")
        return emb, n
    await Pagination(interaction, get_page).navegate()
    logging.info("filterlist end")

#add a new filter
@tree.command(name = "filters", description = "Add a filter", guild=discord.Object(id=GUILD))
async def filters(interaction: discord.message, weapon:str, stat1:str, stat2:str, stat3:str, neg:str):
    logging.info("filters start")
    neg_stat = ""
    #open the filters
    with open("filters.json") as json_file:
        filters = json.load(json_file)
    #count how many
    for x in filters:
        number_of_filters = x
    #add 1 more for the next filter
    number_of_filters = int(number_of_filters) + 1
    #update the dict for the new filter
    arg2 = translator_search.translate(stat1)
    arg3 = translator_search.translate(stat2)
    arg4 = translator_search.translate(stat3)
    #if neg has space(ie more then 1 neg) it'll translate them
    neg_stat = [translator_search.translate_filter(x) for x in neg.split(" ")]
    #update the filter
    filters.update({str(number_of_filters):{"weapon": weapon.replace("_", " ").replace("&","and"), "pos1": arg2, "pos2": arg3, "pos3": arg4, "neg": neg_stat}})
    #write it out
    with open("filters.json", "w") as outfile:
        json.dump(filters, outfile)
    #turn them to strings
    arg1 = str(weapon)
    arg2 = str(arg2)
    arg3 = str(arg3)
    arg4 = str(arg4)
    neg_stat = str(neg_stat)
    #find and deleted specific chars
    arg1 = re.sub("[\[\]']","",arg1)
    arg2 = re.sub("[\[\]']","",arg2)
    arg3 = re.sub("[\[\]']","",arg3)
    arg4 = re.sub("[\[\]']","",arg4)
    neg_stat = re.sub("[\[\]']","",neg_stat)
    #send it to discord
    embed = discord.Embed(title="Added filter "+str(number_of_filters) + ": ", description= arg1+" "+arg2+" "+arg3+" "+arg4+" negatives:"+neg_stat, color=discord.Color.yellow())
    await interaction.response.send_message(embed=embed)
    logging.info("filters end")

#search warframe.market rivens
@tree.command(name = "searchwfm", description = "search warframe.market", guild=discord.Object(id=GUILD))
#search_wfm
async def searchwfm(interaction: discord.message, weapon:str, stat1:str, stat2:str, stat3:str, neg:str):
    await interaction.response.defer()
    L = 1
    logging.info("searchwfm start")
    #turn inputs into data I use
    weapon = str(weapon).replace("&", "and").replace(" ", "_").lower()
    stat1name = translator_search.translate_wfm_search(stat1)
    stat2name = translator_search.translate_wfm_search(stat2)
    stat3name = translator_search.translate_wfm_search(stat3)
    negname = translator_search.translate_wfm_search(neg)
    #create the weapon search
    if "1" not in weapon:
        weapon = "&weapon_url_name=" + weapon
    else:
        weapon = ""
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
    #create the neg search
    if "any" in negname:
        negname = "&negative_stats=has"
    elif "1" not in negname:
        negname = "&negative_stats=" + negname
    else:
        negname = ""
    logging.info("searchwfm link creation")
    wfm_search_link = "https://api.warframe.market/v1/auctions/search?type=riven"+weapon+stat_search+negname+"&polarity=any&sort_by=price_asc"
    #url to grab from
    data = requests.get(wfm_search_link)
    #make it dict
    data = dict(data.json())
    count = 0
    embed_list = []
    # try:
    logging.info("searchwfm start of loop of data")
    #loop through each riven
    for x in data['payload']['auctions']:
        #check if its a pc riven
        if x['platform'] == "pc":
            count += 1
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
            created = str(int(time.mktime(parser.parse(x['created']).timetuple()))-14400)
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
            #get grades
            grades = grading_functions.get_varriants(str(weapon_name).replace("_"," "), pos_val1, pos_stat1,pos_val2, pos_stat2, pos_val3, pos_stat3,neg_val,neg_stat)
            description = ""
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
                description += str(grades[z]['weapon']).title() + " "+"\n" +pos1_color+ pos_stat1+ " "+ pos_val1+ " "+ " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") " + " \n"+pos2_color+ pos_stat2+ " "+ pos_val2 + " "+ " ("+str(pos_grade2_1)+ "%, "+ pos_grade2_2+ ") " + " \n"+pos3_color+ pos_stat3+ " "+ pos_val3+ " "+   " ("+str(pos_grade3_1)+ "%, "+ pos_grade3_2 + ") " +" \n"+neg_color+ neg_stat+ " "+ neg_val + " "+" ("+str(neg_grade1)+ "%, "+ neg_grade2 + ")\n" + "\n"
            description +="Mastery: **" + str(mr) + "** Roll Count: **" + str(rerolls) + "** Polarity: **" + pol + "** Rank: **" + str(rank) + "**"
            if note != "":
                description += "\n\nDescription: " + note + "\n\nListing created on: <t:" + created + ">"
            else:
                description += "\n\nListing created on: <t:" + created + ">"
            #send it to discord
            embed = discord.Embed(title=weapon_name + " " + prefix + " "+str(start_price) + "-" + str(bo_price),url="https://warframe.market/auction/"+wfm_url, description=description, color=discord.Color.blue())
            embed.set_author(name= user)
            embed_list.append(embed)
    async def get_page(page: int):
        offset = (page-1) * L
        for embed in embed_list[offset:offset+L]:
            emb = embed
        n = Pagination.compute_total_pages(len(embed_list), L)
        emb.set_footer(text=f"Riven {page} of {n}")
        return emb, n
    if embed_list == []:
        #send it to discord
        embed = discord.Embed(title="None Found", color=discord.Color.yellow())
        await interaction.followup.send(embed=embed)
    else:
        await Pagination(interaction, get_page).navegate()
    logging.info("end of searchwfm")

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD))
    print("Ready!")
client.run(TOKEN)
