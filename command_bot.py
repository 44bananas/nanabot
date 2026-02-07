#command_bot

from gevent import monkey, sleep
monkey.patch_all()

import grequests
import requests
import discord
built_python_range = range
from discord.ext import tasks
from discord.ext import commands
from dotenv import load_dotenv
from discord import Color
from discord import Interaction
from discord import app_commands
import os
import json
import typing
import grader
import translator_search
import re
import bane_patch
import prefixes_create
import pandas as pd
import functions_for_functions
from pagination import Pagination
from pagination_file_send import Pagination_file_send
import sqlite3
import time
from dateutil import parser
from io import BytesIO
import io
from PIL import Image
import img_reading_dyn
import grab_info_from_wfm

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

def description_creation(weapon, stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negname, description):
    grades = grader.grade(weapon, str(stat1val), stat1name.replace("_", " "), str(stat2val), stat2name.replace("_", " "), str(stat3val), stat3name.replace("_", " "), str(negval), negname.replace("_", " "), "8")
    prefix = prefixes_create.create_prefixes(stat1name.replace("_"," "), stat2name.replace("_"," "), stat3name.replace("_"," ")).splitlines()[0]
    description += "\n\nGrades for " +  weapon.title() + " " +  prefix + "\n"
    stat1val, stat2val, stat3val, negval = bane_patch.back_to_front(stat1name, stat1val), bane_patch.back_to_front(stat2name, stat2val), bane_patch.back_to_front(stat3name, stat3val), bane_patch.back_to_front(negname, -abs(float(negval)))
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
        wiki_url = "https://wiki.warframe.com/w/"
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
    if "orange_circle" in description or "red_circle" in description or "green_cricle" in description:
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
            wiki_url = "https://wiki.warframe.com/w/"
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

def strip_variants(weapon):
    weapon = weapon.title()
    with open("weapon_info.json") as json_file:
        weapon_info = json.load(json_file)
    weapon_list = ["Kuva ", " Prime", "Tenet ", "Prisma ", " Wraith", "Synoid ", " Vandal", "Mk1-", "Sancti ", "Carmine ", "Telos ", "Rakta ", "Secura ", "Vaykor ", "Mara "]
    for x in weapon_list:
        if x in weapon:
            for y in weapon_info:
                if weapon.replace(x, "").strip() in weapon_info[y]['variants']:
                    if "Gazal" not in weapon:
                        weapon = weapon.replace(x, "")
    return weapon

def check_ign(ign):
    users = []
    xbox = "https://content-xb1"
    psn = "https://content-ps4"
    pc = "https://content"
    url = ".warframe.com/1/dynamic/getProfileViewingData.php?n="
    data = grequests.map(grequests.get(u) for u in [pc + url + ign, psn + url + ign, xbox + url + ign])
    is_account_real = False
    for i in data:
        try:
            if "Retry PC account:" in i.text:
                is_account_real = True
                ign = i.text.replace("Retry PC account: ","")
            elif i.status_code == 400 or i.status_code == 409:
                break
            else:
                is_account_real = True
        except:
            is_account_real = False
    if ign != "":
        try:
            users.append((requests.get("https://content.warframe.com/1/dynamic/getProfileViewingData.php?n="+ign).json()['Results'][0]['AccountId']['$oid'],ign.lower()))
        except:
            return
    con = sqlite3.connect("tc_usernames.db")
    users_to_add = set([i for i in users if i not in con.execute("SELECT * FROM names").fetchall()])
    for i in users_to_add:
        con.execute("INSERT OR REPLACE INTO names (id, username) values(?, ?) ",(i[0], i[1]))
        con.commit()
    con.close()
    return

@tree.command(name="tc_search", description="search tc riven db")
async def tc_search(interaction:discord.message, user_weapon_response:str, user_pos1_response:str, user_pos2_response:str, user_pos3_response:typing.Optional[str]="", user_neg_response:typing.Optional[str]="", invisible_to_others:typing.Optional[bool]=True):
    await interaction.response.defer(ephemeral = invisible_to_others)
    embed_list = []
    riven_images = []
    base_url = "https://44bananas.uk/riven_search?"
    weapon = "weapon=" + user_weapon_response
    pos1 = "&pos1=" + user_pos1_response
    pos2 = "&pos2=" + user_pos2_response
    if user_pos3_response != "":
        pos3 = "&pos3=" + user_pos3_response
    else:
        pos3 = ""
    if user_neg_response != "":
        neg = "&neg=" + user_neg_response
    else:
        neg = ""

    response_info = requests.get(base_url+weapon+pos1+pos2+pos3+neg).json()

    for x in response_info:
        description = "``"+ response_info[x]["username"] + "`` \n\n" + response_info[x]["weapon"] + " " + response_info[x]["prefix"] + " \n\n" + response_info[x]["stat1val"] + " " + response_info[x]["stat1"] + " \n" + response_info[x]["stat2val"] + " " + response_info[x]["stat2"] + " \n" + response_info[x]["stat3val"] + " " + response_info[x]["stat3"] + " \n" + response_info[x]["negval"] + " " + response_info[x]["neg"] + " \n\n``" + response_info[x]["message"] + "`` \n\n" + response_info[x]["date"]
        embed = discord.Embed(description=description, color=discord.Color.yellow())
        embed_list.append(embed)
        riven_images.append(response_info[x]["image"])

    L = 1
    async def get_page(page: int):
        offset = (page-1) * L
        # riven_images = riven_images.values()
        for x, embed in zip(riven_images[offset:offset+L],embed_list[offset:offset+L]):
            image = Image.open(io.BytesIO(eval(x))).save("image" + str(offset) + ".jpg")
            # image.save("image" + str(offset) + ".png")
            embed = embed
            file = discord.File("image"+str(offset) + ".jpg", filename="image.jpg")
            embed.set_image(url="attachment://image.jpg")
        n = Pagination_file_send.compute_total_pages(len(riven_images), L)
        embed.set_footer(text=f"Riven {page} of {n}")
        return embed, n, file
    await Pagination_file_send(interaction, get_page).navegate()

@tree.command(name="update_weapons", description="update weapon list for dispos")
async def update_weapons(interaction:discord.message):
    weapon_info = requests.get("https://pastebin.com/raw/GCTWpQWp").json()
    with open("weapon_info.json",'w') as fp:
        fp.write(json.dumps(weapon_info))
    embed = discord.Embed(description="Weapon List Updated!",color=discord.Color.yellow())
    await interaction.response.send_message(embed=embed, ephemeral = True)

@tree.command(name = "dispo", description = "Give dispo and if weapon rolls ips")
async def dispo(interaction:discord.message, weapon:str, invisible_to_others:typing.Optional[bool]=True):
    with open("weapon_info.json") as json_file:
        weapon_info = json.load(json_file)
    weapon = strip_variants(str(weapon).title().replace("&", "And").replace("_"," ").replace("Dex Furis", "Afuris").strip())
    if weapon_info[weapon]['type'] == "bayonet":
        weapon += " Melee"
    for x in weapon_info:
        if weapon in weapon_info[x]["variants"]:
            description = "Dispo(s):\n"
            for each in weapon_info[x]["variants"]:
                description += each + " " + weapon_info[x]["variants"][each] + "\n"
            if "True" in str(weapon_info[x]["ips"]):
                        description += "\nIPS:\n"
            for each in weapon_info[x]["ips"]:
                    if weapon_info[x]["ips"][each] == True:
                            description +=  each + "\n"
    embed = discord.Embed(description=description,color=discord.Color.yellow())
    await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)

@tree.command(name="grade", description="grade riven(ex:\"torid 1.6dtc 1.52dtg 1.52dti -91.2pfs \")")
async def grade(interaction:discord.message, userinput:str, invisible_to_others:typing.Optional[bool]=True):
    def split_text(text_to_split):
        return [i for i in re.split(r"(-*\d+[.]*\d*)", text_to_split) if i != ""]
    with open("weapon_info.json") as json_file:
        weapon_info = json.load(json_file)
    string_from_user = userinput.lower().split(" ")
    try:
        if string_from_user[-2] == "-r":
            rank = string_from_user[-1]
            string_from_user = string_from_user[:-2]
        else:
            rank = "8"
    except:
        rank = "8"
    try:
        weapon = string_from_user[0].lower().replace("_"," ").replace("&","and")
    except:
        embed = discord.Embed(title="Error weapon doesn't exist: ", description=str(string_from_user)[2:-2],color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral = True)
        return
    weapon = strip_variants(weapon)
    if weapon not in str(weapon_info):
        embed = discord.Embed(title="Error weapon doesn't exist: ", description=weapon,color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral = True)
        return    
    try:
        try:
            if "recoil" in translator_search.translate_filter(split_text(string_from_user[1])[1].lower()):
                stat1 = string_from_user[1][1:]
            else:
                stat1 = string_from_user[1]
        except:
            embed = discord.Embed(title="Error in: " + string_from_user[1], color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral = True)
            return
    except:
        embed = discord.Embed(title="Error in: " + str(string_from_user)[2:-2], color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral = True)
        return
    try:
        if "recoil" in translator_search.translate_filter(split_text(string_from_user[2])[1].lower()):
            stat2 = string_from_user[2][1:]
        else:
            stat2 = string_from_user[2]
    except:
        embed = discord.Embed(title="Error in: " + string_from_user[2], color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral = True)
        return
    try:
        if (split_text(string_from_user[3])[0][0] == "-" and "recoil" not in translator_search.translate_filter(split_text(string_from_user[3])[1]).lower()) or (split_text(string_from_user[3])[0][0] != "-" and "recoil" in translator_search.translate_filter(split_text(string_from_user[3])[1]).lower()) or ("damage vs" in translator_search.translate_filter(split_text(string_from_user[3])[1]) and float(split_text(string_from_user[3])[0]) < 1):
            neg = string_from_user[3]
        else:
            if "recoil" in translator_search.translate_filter(split_text(string_from_user[3])[1].lower()):
                stat3 = string_from_user[3][1:]
            else:
                stat3 = string_from_user[3]
            try:
                if string_from_user[4][0] == "-" or ("damage vs" in translator_search.translate_filter(split_text(string_from_user[4])[1].lower()) and float(split_text(string_from_user[4])[0]) < 1) or "recoil" in translator_search.translate_filter(split_text(string_from_user[4])[1].lower()):
                    neg = string_from_user[4]
            except:
                neg = ""
    except:
        stat3 = ""
        neg = ""
    try:
        stat1, stat2= split_text(stat1), split_text(stat2)
    except:
        embed = discord.Embed(title="Error in: " + stat1 + " or " + stat2, color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral = True)
        return
    try:
        stat3 = split_text(stat3)
    except:
        stat3 = "[]"
    try:
        neg = split_text(neg)
    except:
        neg = "[]"
    try:
        stat1stat, stat1val = translator_search.translate_filter(stat1[1]), bane_patch.front_to_back(translator_search.translate_filter(stat1[1]),stat1[0])
    except:
        embed = discord.Embed(title="Error in: " + stat1, color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral = True)
        return
    try:
        stat2stat, stat2val = translator_search.translate_filter(stat2[1]), bane_patch.front_to_back(translator_search.translate_filter(stat2[1]),stat2[0])
    except:
        embed = discord.Embed(title="Error in: " + stat2, color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral = True)
        return
    try:
        stat3stat, stat3val = translator_search.translate_filter(stat3[1]).replace("]",""), bane_patch.front_to_back(translator_search.translate_filter(stat3[1]),stat3[0]).replace("[","")
    except:
        try:
            stat3stat, stat3val = translator_search.translate_filter(stat3[1]), bane_patch.front_to_back(translator_search.translate_filter(stat3[1]),stat3[0])
        except:
            stat3stat, stat3val = "[]", ""
    try:
        negstat, negval = translator_search.translate_filter(neg[1]).replace("]",""), bane_patch.front_to_back(translator_search.translate_filter(neg[1]),neg[0]).replace("[","")
    except:
        try:
            negstat, negval = translator_search.translate_filter(neg[1]), bane_patch.front_to_back(translator_search.translate_filter(neg[1]),neg[0])
        except:
            negstat, negval = "[]", ""
    if stat3val == "":
        stat3val = 0
    if negval == "":
        negval = 0
    if stat1stat == "":
        stat1stat = "[]"
    if stat2stat == "":
        stat2stat = "[]"
    if stat3stat == "":
        stat3stat = "[]"
    if negstat == "":
        negstat = "[]"
    try:
        grades = grader.grade(weapon, stat1val, stat1stat, stat2val, stat2stat, stat3val, stat3stat, negval, negstat, rank)
    except:
        embed = discord.Embed(title="Failed to grade: " + str(string_from_user)[2:-2], color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral = True)
        return
    description = ""
    stat1val, stat2val, stat3val, negval = bane_patch.back_to_front(stat1stat, stat1val), bane_patch.back_to_front(stat2stat, stat2val), bane_patch.back_to_front(stat3stat, stat3val), bane_patch.back_to_front(negstat, -abs(float(negval)))
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
        for x, y in zip([pos1_color, pos2_color, pos3_color, neg_color],[stat1, stat2, stat3, neg]):
            if "circle" not in str(x) and str(y) != '[]':
                embed = discord.Embed(title="Error in: " + y[0] + y[1],color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral = True)
                return
        prefix = prefixes_create.create_prefixes(stat1stat, stat2stat, stat3stat).splitlines()[0]
        wiki_url = "https://wiki.warframe.com/w/"
        weapon_url = str(grades[z]['weapon']).title().replace(" ","_").replace("And","&")
        if "mk" in weapon_url.lower():
            weapon_url = wiki_url + "MK" +(weapon_url[2:]).title()
        else:
            weapon_url = wiki_url + weapon_url
        stat1stat, stat2stat, stat3stat, negstat = stat1stat.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), stat2stat.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), stat3stat.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), negstat.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo")
        description += "["+str(grades[z]['weapon']).title() + "]("+ weapon_url+")\n" +pos1_color+ stat1stat+ " "+ str(stat1val)+ " "+ " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") " + " \n"+pos2_color+ stat2stat+ " "+ str(stat2val) + " "+ " ("+str(pos_grade2_1)+ "%, "+ pos_grade2_2+ ") " 
        if stat3stat != "[]":
            description += " \n"+pos3_color+ stat3stat+ " "+ str(stat3val)+ " "+   " ("+str(pos_grade3_1)+ "%, "+ pos_grade3_2 + ") " 
        if negstat != "[]":
            description += " \n"+neg_color+ negstat+ " "+ str(negval) + " "+" ("+str(neg_grade1)+ "%, "+ neg_grade2 + ")"
        description += "\n\n"
    if description != "":
        embed = discord.Embed(title="Grades for: " + weapon.title() + " " +  prefix, description=description,color=discord.Color.yellow())
        await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)
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
            wiki_url = "https://wiki.warframe.com/w/"
            weapon_url = str(grades[z]['weapon']).title().replace(" ","_").replace("And","&")
            if "mk" in weapon_url.lower():
                weapon_url = wiki_url + "MK" +(weapon_url[2:]).title()
            else:
                weapon_url = wiki_url + weapon_url
            stat1stat, stat2stat, stat3stat, negstat = stat1stat.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), stat2stat.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), stat3stat.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), negstat.replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo")
            description += "["+str(grades[z]['weapon']).title() + "]("+ weapon_url+")\n" +pos1_color+ stat1stat+ " "+ str(stat1val)+ " "+ " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") " + " \n"+pos2_color+ stat2stat+ " "+ str(stat2val) + " "+ " ("+str(pos_grade2_1)+ "%, "+ pos_grade2_2+ ") " 
            if "[]" not in stat3stat:
                description += " \n"+pos3_color+ stat3stat+ " "+ str(stat3val)+ " "+   " ("+str(pos_grade3_1)+ "%, "+ pos_grade3_2 + ") " 
            if "[]" not in negstat:
                description += " \n"+neg_color+ negstat+ " "+ str(negval) + " "+" ("+str(neg_grade1)+ "%, "+ neg_grade2 + ")"
            description += "\n\n"
        embed = discord.Embed(title="Grades for: " + weapon.title() + " " +  prefixes_create.create_prefixes(stat1stat, stat2stat, stat3stat).splitlines()[0], description=description,color=discord.Color.yellow())
        await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)

#riven grades given wfm link
@tree.command(name = "grade_wfm", description="get riven grades from a wfm link")
async def grade_wfm(interaction:discord.message, url :str, invisible_to_others:typing.Optional[bool]=True):
    #take that url and get the url to grab the riven info from
    url_click = url
    url = url.split("https://warframe.market/auction/")[1]
    url = "https://api.warframe.market/v1/auctions/entry/" + url
    try:
        test = requests.get(url)
    except:
        embed = discord.Embed(title="Not a Valid URL",color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral = True)
        return
    try:
        data = dict(test.json())
    except:
        embed = discord.Embed(title="Failed data conversion, please contact 44bananas",color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral = True)
        return
    # selec the data from the json
    try:
        data = data['payload']['auction']
    except:
        embed = discord.Embed(title="Not a Valid URL or WFM Down",color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral = True)
        return
    riven_data = {}
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
            pos_stat_3 = '[]'
            pos_stat_3val = '[]'
        pos_stat_1val, pos_stat_2val, pos_stat_3val, neg_values = bane_patch.front_to_back(pos_stat_1, pos_stat_1val), bane_patch.front_to_back(pos_stat_2, pos_stat_2val), bane_patch.front_to_back(pos_stat_3, pos_stat_3val), bane_patch.front_to_back(neg_stats, neg_values)
        if "ax_52" in data['item']['weapon_url_name']:
            weapon = "ax-52"
        elif "vinquibus_melee" in data['item']['weapon_url_name']:
            weapon = "vinquibus melee"
        elif "vinquibus" in data['item']['weapon_url_name']:
            weapon = "vinquibus primary"
        elif "efv_5_jupiter" in data['item']['weapon_url_name']:
            weapon = "efv-5 jupiter"
        elif "efv_8_mars" in data['item']['weapon_url_name']:
            weapon = "efv-8 mars"
        elif "riot_848" in data['item']['weapon_url_name']:
            weapon = "riot-848"
        else:
            weapon = data['item']['weapon_url_name']
        riven_data.update({"weapon":weapon, "pos1stat":pos_stat_1,"pos1val":pos_stat_1val, "pos2stat":pos_stat_2,"pos2val":pos_stat_2val, "pos3stat":pos_stat_3,"pos3val":pos_stat_3val, "negstat":neg_stats, "negval":neg_values,"rerolls":data['item']['re_rolls'],"pol":data['item']['polarity'],"mr":data['item']['mastery_level']})
    grades = grader.grade(riven_data['weapon'].replace("dark_split_sword_(dual_swords)","dark_split-sword").replace("_"," "), str(riven_data['pos1val']), riven_data['pos1stat'], str(riven_data['pos2val']), riven_data['pos2stat'], str(riven_data['pos3val']), riven_data['pos3stat'], str(riven_data['negval']), riven_data['negstat'], "8")
    stat1val, stat2val, stat3val, negval = bane_patch.back_to_front(riven_data['pos1stat'], str(riven_data['pos1val'])), bane_patch.back_to_front(riven_data['pos2stat'], str(riven_data['pos2val'])), bane_patch.back_to_front(riven_data['pos3stat'], str(riven_data['pos3val'])),bane_patch.back_to_front(riven_data['negstat'], str(riven_data['negval'])) 
    stat1stat, stat2stat, stat3stat, negstat = riven_data['pos1stat'],riven_data['pos2stat'],riven_data['pos3stat'],riven_data['negstat']
    description = ""
    prefix = prefixes_create.create_prefixes(stat1stat, stat2stat, stat3stat).splitlines()[0]
    stat1stat, stat2stat, stat3stat, negstat = str(stat1stat).replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), str(stat2stat).replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), str(stat3stat).replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo"), str(negstat).replace("_", " ").replace("channeling efficiency","heavy attack efficiency").replace("channeling damage", "initial combo")
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
        description += str(grades[z]['weapon']).title() + " "+"\n" +pos1_color+ stat1stat+ " "+ str(stat1val)+ " "+ " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") " + " \n"+pos2_color+ stat2stat+ " "+ str(stat2val) + " "+ " ("+str(pos_grade2_1)+ "%, "+ pos_grade2_2+ ") " 
        if stat3stat != "[]":
            description += " \n"+pos3_color+ stat3stat+ " "+ str(stat3val)+ " "+   " ("+str(pos_grade3_1)+ "%, "+ pos_grade3_2 + ") " 
        if negstat != "[]":
            description += " \n"+neg_color+ negstat+ " "+ str(negval) + " "+" ("+str(neg_grade1)+ "%, "+ neg_grade2 + ")"
        description += "\n\n"
    if description != "":
        embed = discord.Embed(title="Grades for: " + riven_data['weapon'].replace("dark_split_sword_(dual_swords)","dark_split-sword").replace("_"," ") + " " +  prefix, url= url_click, description=description,color=discord.Color.yellow())
        embed.set_footer(text="MR: " + str(riven_data["mr"]) + " Polarity: " + str(riven_data["pol"]).capitalize() + " Rerolls: " + str(riven_data['rerolls']))
        await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)
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
            description += str(grades[z]['weapon']).title() + " "+"\n" +pos1_color+ stat1stat+ " "+ str(stat1val)+ " "+ " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") " + " \n"+pos2_color+ stat2stat+ " "+ str(stat2val) + " "+ " ("+str(pos_grade2_1)+ "%, "+ pos_grade2_2+ ") " 
            if "[]" not in stat3stat:
                description += " \n"+pos3_color+ stat3stat+ " "+ str(stat3val)+ " "+   " ("+str(pos_grade3_1)+ "%, "+ pos_grade3_2 + ") " 
            if "[]" not in negstat:
                description += " \n"+neg_color+ negstat+ " "+ str(negval) + " "+" ("+str(neg_grade1)+ "%, "+ neg_grade2 + ")"
            description += "\n\n"
        embed = discord.Embed(title="Grades for: " + riven_data['weapon'].replace("dark_split_sword_(dual_swords)","dark_split-sword").replace("_"," ") + " " +  prefixes_create.create_prefixes(stat1stat, stat2stat, stat3stat).splitlines()[0], description=description,color=discord.Color.yellow(), url= url_click)
        embed.set_footer(text="MR: " + str(riven_data["mr"]) + " Polarity: " + str(riven_data["pol"]).capitalize() + " Rerolls: " + str(riven_data['rerolls']))
        await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)

#rolls command
@tree.command(name = "rolls", description="Check rolls for a weapon")
async def rolls(interaction:discord.message, weapon:str, invisible_to_others:typing.Optional[bool]=True):
    #replace the and
    weapon = weapon.lower().replace("And","&").replace("and","&")
    #get lists of rolls
    with open("rolls.json") as json_file:
        rolls_list = dict(json.load(json_file))
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
    await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)

@tree.command(name = "update_rolls", description="update the rolls doc for the bot")
async def update_rolls(interaction:discord.message):
    await interaction.response.defer(ephemeral = True)
    with open("weapon_info.json") as json_file:
        weapon_info = json.load(json_file)
    #grab the sheet
    excel_sheet = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQrEc4ZwJ4WL1FXaMaTAgMtqPQpwVMMr5vd6iE3sxFsjeiHPqhF_fl7Dxny_Spp-99XXPxYzwIXkld5/pub?output=xlsx"
    #read the sheet
    sheets = pd.read_excel(excel_sheet, sheet_name = None)
    #split the sheet
    primary = sheets['primary']
    secondary = sheets['secondary']
    melee = sheets['melee']
    archgun = sheets['archgun']
    robotic = sheets['robotic']
    sticks = sheets['stat sticks']
    #list of sheets to loop through
    list_of_sheets = [primary, secondary, melee, archgun, robotic, sticks]
    names_of_sheets = ["primary", "secondary", "melee", "archgun", "robotic", "sticks"]
    #dict of rolls
    rolls = {}
    for sheet, names in zip(list_of_sheets, names_of_sheets):
        #check number of rows to loop through
        number_of_rows = len(sheet)
        #create list of header to figure out where data is at in the doc
        header = sheet.columns.values.tolist
        column_of_info = 0
        for x in header():
            if "WEAPON" in x:
                if weapon_info[column_of_info]['type'] == "bayonet" and names == "primary":
                    weapon = column_of_info + " primary"   
                elif weapon_info[column_of_info]['type'] == "bayonet" and names == "secondary":
                    weapon = column_of_info + " secondary"
                elif weapon_info[column_of_info]['type'] == "bayonet" and names == "melee":
                    weapon = column_of_info + " melee"   
                else:
                    weapon = column_of_info
            if "POSITIVE STATS:" in x:
                pos_stats = column_of_info
            if "NEGATIVE STATS:" in x:
                neg_stats = column_of_info
            if "Notes:" in x:
                notes = column_of_info
            column_of_info += 1
        #loop through the rows
        for x in built_python_range(number_of_rows):
            rolls.update({sheet.iloc[x].iloc[weapon]:{"pos_stats":sheet.iloc[x].iloc[pos_stats], "neg_stats":sheet.iloc[x].iloc[neg_stats], "notes":sheet.iloc[x].iloc[notes]}})
    #write it out
    with open("rolls.json", "w") as outfile:
        json.dump(rolls, outfile)
    embed = discord.Embed( description="Updated Rolls Doc", color=discord.Color.yellow())
    await interaction.followup.send(embed=embed)

#add a new filter
@tree.command(name = "filters", description = "Add a filter")
async def filters(interaction: discord.message, weapon:str, stat1:str, stat2:str, stat3:typing.Optional[str]="1", neg:typing.Optional[str]="1", invisible_to_others:typing.Optional[bool]=True):
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
    arg1 = re.sub(r"[\[\]']","",arg1)
    arg2 = re.sub(r"[\[\]']","",arg2)
    arg3 = re.sub(r"[\[\]']","",arg3)
    arg4 = re.sub(r"[\[\]']","",arg4)
    neg_stat = re.sub(r"[\[\]']","",neg_stat)
    #send it to discord
    embed = discord.Embed(title="Added filter "+str(number_of_filters) + ": ", description= arg1+" "+arg2+" "+arg3+" "+arg4+" negatives:"+neg_stat, color=discord.Color.yellow())
    await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)

#send all the filters to discord
@tree.command(name = "filterlist", description = "List filters")
async def filterlist(interaction: discord.message, invisible_to_others:typing.Optional[bool]=True):
    await interaction.response.defer(ephemeral = invisible_to_others)
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
        test = re.sub(r"[\[\],']","",str(test))
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

#remove a filter
@tree.command(name = "filterremove", description = "Remove a filter")
async def filterremove(interaction: discord.message, filter: str, invisible_to_others:typing.Optional[bool]=True):
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
        test = re.sub(r"[{',}]","",str(test))
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
            e = re.sub(r"[\[\]]","",e)
            embed = discord.Embed(title="Removed filter "+ f+ ": ", description= a+" "+b+" "+c+" "+d+" negatives:"+e, color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)
        count = int(count) + 1
        counted_list += [str(count)]
    #new dict with updated filter
    filters_updated = dict(zip(counted_list,list(filters.values())))
    #write the updated filter
    with open("filters.json", "w") as outfile:
        json.dump(filters_updated, outfile)

#add people to the blacklist
@tree.command(name = "blacklist", description = "Add someone to the blacklist")
async def blacklist(interaction: discord.message, user: str, invisible_to_others:typing.Optional[bool]=True):
    #open the file
    blacklist = open('blacklist.txt',"a")
    #add the name
    blacklist.write(user + '\n')
    blacklist.close()
    #send the name in discord
    embed = discord.Embed(title="Added: ",description= user+ " to the blacklist", color=discord.Color.yellow())
    await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)

#command to get number of rivens in db
@tree.command(name="riven_count", description="Number of Rivens in Database")
async def riven_count(interaction:discord.message, invisible_to_others:typing.Optional[bool]=True):
    await interaction.response.defer(ephemeral = invisible_to_others)
    description = ""
    for x in ["wfm.db","rm.db"]:
        #open the db
        con = sqlite3.connect(x,isolation_level=None)
        con.execute('pragma journal_mode=wal;')
        cur = con.cursor()
        description += x + "\n" + str(len(cur.execute("SELECT * FROM rivens").fetchall())) + "\n\n"
    #send it to discord
    embed = discord.Embed(title="Number of Rivens", description=description, color=discord.Color.yellow())
    await interaction.followup.send(embed=embed)

#command to search the dbs
@tree.command(name = "search", description = "Search db for rivens")
async def search(interaction: discord.message, weapon:str, stat1:str, stat2:str, stat3:typing.Optional[str]='[]',neg:typing.Optional[str]='[]', invisible_to_others:typing.Optional[bool]=True):
    await interaction.response.defer(ephemeral = invisible_to_others)
    embed_list = []
    #translate the arguments given by the user
    stat1 = translator_search.translate(stat1)
    stat2 = translator_search.translate(stat2)
    stat3 = translator_search.translate(stat3)
    stat4 = translator_search.translate(neg)
    weapon_name = str(weapon).lower().replace("_", " ").replace("&", "and").replace("any", "1")
    #grab the data
    wfm = "wfm.db"
    rm = "rm.db"
    #loop through the 2 dbs
    for x in [wfm,rm]:
        #open the db
        con = sqlite3.connect(x,isolation_level=None)
        con.execute('pragma journal_mode=wal;')
        cur = con.cursor()
        #search for the data
        if stat4 == "any":
            data = cur.execute("SELECT * FROM rivens WHERE weapon = ? AND (stat1name = ? OR stat2name = ? OR stat3name = ?) AND (stat1name = ? OR stat2name = ? OR stat3name = ?) AND (stat1name = ? OR stat2name = ? OR stat3name = ?) AND stat4name != ?",(weapon_name, stat1,stat1,stat1,stat2,stat2,stat2,stat3,stat3,stat3,"[]",))
        elif stat4 == "" or stat4 == "1":
            data = cur.execute("SELECT * FROM rivens WHERE weapon = ? AND (stat1name = ? OR stat2name = ? OR stat3name = ?) AND (stat1name = ? OR stat2name = ? OR stat3name = ?) AND (stat1name = ? OR stat2name = ? OR stat3name = ?)",(weapon_name, stat1,stat1,stat1,stat2,stat2,stat2,stat3,stat3,stat3,))
        else:
            data = cur.execute("SELECT * FROM rivens WHERE weapon = ? AND (stat1name = ? OR stat2name = ? OR stat3name = ?) AND (stat1name = ? OR stat2name = ? OR stat3name = ?) AND (stat1name = ? OR stat2name = ? OR stat3name = ?) AND stat4name = ?",(weapon_name, stat1,stat1,stat1,stat2,stat2,stat2,stat3,stat3,stat3,stat4,))
        #loop through each riven found
        for riven in data:
            description = ""
            #grade each riven
            grades = grader.grade(str(riven[1]).replace("_"," "), riven[9], riven[8],riven[11], riven[10], riven[13], riven[12],riven[15],riven[14], "8")
            #loop through the grades
            for grade in grades:
                    try:
                        pos1_color, pos_grade1_1, pos_grade1_2 = grades[grade]['pos1']
                    except:
                        pos1_color = ""
                        pos_grade1_1 = ""
                        pos_grade1_2 = ""
                    try:
                        pos2_color,pos_grade2_1, pos_grade2_2 = grades[grade]['pos2']
                    except:
                        pos2_color = ""
                        pos_grade2_1 = ""
                        pos_grade2_2 = ""
                    try:
                        pos3_color, pos_grade3_1, pos_grade3_2 = grades[grade]['pos3']
                    except:
                        pos3_color = ""
                        pos_grade3_1 = ""
                        pos_grade3_2 = ""
                    try:
                        neg_color, neg_grade1, neg_grade2 = grades[grade]['neg']
                    except:
                        neg_color = ""
                        neg_grade1 = ""
                        neg_grade2 = ""
                    #create username and description for the embed
                    user = re.sub(r"[_]",r"\_",str(re.sub(r"[-]",r"\-",str(re.sub(r"[\(\)',]","",str(riven[0]))))))
                    description += user +  "\n"+"Date: "+ re.sub(r"[\(\)',]","",str(riven[17])) +"\n"+  str(grades[grade]['weapon']).title() + " " + re.sub(r"[\(\)',]","",str(riven[2])) + " " + re.sub(r"[\(\)',]","",str(riven[3]))+ "\n" + pos1_color+   re.sub(r"[\(\)',]","",str(riven[8]))+ " " + re.sub(r"[\(\)',]","",str(bane_patch.back_to_front(riven[8], riven[9])))+ " " + " ("+ str(pos_grade1_1)+ "%, " + pos_grade1_2+ ") "+ "\n"+ pos2_color +re.sub(r"[\(\)',]","",str(riven[10]))+ " " + re.sub(r"[\(\)',]","",str(bane_patch.back_to_front(riven[10], riven[11])))+ " " + " ("+ str(pos_grade2_1)+ "%, " + pos_grade2_2+ ") "+ "\n"+ pos3_color+re.sub(r"[\(\)',]","",str(riven[12]))+ " " + re.sub(r"[\(\)',]","",str(bane_patch.back_to_front(riven[12], riven[13])))+ " " + " ("+ str(pos_grade3_1)+ "%, " + pos_grade3_2+ ") "+ "\n"+ neg_color+re.sub(r"[\(\)',]","",str(riven[14]))+ " " + re.sub(r"[\(\)',]","",str(bane_patch.back_to_front(riven[14], riven[15])))+ " " + " ("+ str(neg_grade1)+ "%, " + neg_grade2+ ") " + "\n"+"Mastery: " + re.sub(r"[\(\)',]","",str(riven[5])) + " Roll Count: " + re.sub(r"[\(\)',]","",str(riven[7])) + " Polarity: " + re.sub(r"[\(\)',]","",str(riven[6])) + " Rank: " + re.sub(r"[\(\)',]","",str(riven[4]))+ "\n\n"
            #if the description has anything create the embed and add it to the embed list
            if description != "":
                embed = discord.Embed(description=description, color=discord.Color.yellow())
                embed_list.append(embed)
    #print the data
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

#search warframe.market rivens
@tree.command(name = "searchwfm", description = "search warframe.market")
async def searchwfm(interaction: discord.message, weapon:typing.Optional[str]="1", stat1:typing.Optional[str]="", stat2:typing.Optional[str]="", stat3:typing.Optional[str]="", neg:typing.Optional[str]="1", invisible_to_others:typing.Optional[bool]=True):
    await interaction.response.defer(ephemeral = invisible_to_others)
    L = 1
    #turn inputs into data I use
    weapon = str(weapon).replace("&", "and").replace(" ", "_").lower().replace("-","_")
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
    wfm_search_link = "https://api.warframe.market/v1/auctions/search?type=riven"+weapon+stat_search+negname+"&polarity=any&sort_by=price_asc"
    #url to grab from
    header = {"Host":"api.warframe.market"}
    data = requests.get(wfm_search_link, headers = header)
    #make it dict
    data = dict(data.json())
    count = 0
    embed_list = []
    if data == {'error': {'weapon_url_name': ['app.auctions.errors.item_not_exist'], 'negative_stats': ['app.form.invalid']}}:
        embed = discord.Embed(title="You can't search nothing!", color=discord.Color.yellow())
        await interaction.followup.send(embed=embed)
        return
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
                pos_stat3 = "[]"
            try:
                pos_val3 = str(pos_stats[2]['value'])
            except:
                pos_val3 = "[]"
            #grab the neg stats
            neg_stats = [item for item in x['item']['attributes'] if item['positive'] == False]
            #sepearte the value and stat name
            try:
                neg_stat = str(neg_stats[0]['url_name']).replace("_"," ")
            except:
                neg_stat = "[]"
            try:
                neg_val = str(neg_stats[0]['value'])
            except:
                neg_val = "[]"
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
            mr = x['item']['mastery_level']
            rank = x['item']['mod_rank']
            pol = x['item']['polarity']
            #get grades
            grades = grader.grade(str(weapon_name).replace("dark_split_sword_(dual_swords)","dark_split-sword").replace("_"," "), pos_val1, pos_stat1,pos_val2, pos_stat2, pos_val3, pos_stat3,neg_val,neg_stat, "8")
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
            embed = discord.Embed(title=weapon_name.replace("dark_split_sword_(dual_swords)","dark_split-sword").replace("_"," ") + " " + prefix + " "+str(start_price) + "-" + str(bo_price),url="https://warframe.market/auction/"+wfm_url, description=description, color=discord.Color.blue())
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

#search usernames
@tree.command(name = 'name_search', description="search someones name for previous igns")
async def name_search(interaction: discord.message, user:str, invisible_to_others:typing.Optional[bool]=True):
    def check_names(userlist, db, user):
        try:
            userlist.append(db.execute("SELECT * FROM names WHERE id = ?",(str(db.execute("SELECT * FROM names WHERE username = ?",(user.lower(),)).fetchall()[0][0]),)).fetchall())
        except:
            print("none found")
        try:
            return userlist[0]
        except:
            return userlist
    def check_list(list_name):
        if any(isinstance(sub, list) for sub in list_name):
            list_name = sum(list_name,[])
        return list_name
    conwfm = sqlite3.connect("usernames.db")
    contc = sqlite3.connect("tc_usernames.db")
    wfm_names = []
    tc_names = []
    wfm_names = check_names(wfm_names, conwfm, user)
    tc_names = check_names(tc_names, contc, user)
    wfm_names_new = []
    tc_names_new = []
    for x in wfm_names:
        check_names(tc_names_new, contc, x[1])
    for x in tc_names:
        check_names(wfm_names_new, conwfm, x[1])
    wfm_names, tc_names= check_list(wfm_names) +  check_list(wfm_names_new), check_list(tc_names) + check_list(tc_names_new)
    wfm_names_new = []
    tc_names_new = []
    [wfm_names_new.append(item) for item in wfm_names if item not in wfm_names_new]
    [tc_names_new.append(item) for item in tc_names if item not in tc_names_new]
    description = "WFM: \n"
    for x in wfm_names_new:
        description += x[1] + " " + x[0] + "\n"
    description += "\nTC: \n"
    for x in tc_names_new:
        description += x[1] + " " + x[0] + "\n"
    embed = discord.Embed(title= "Usernames for: " + user, description=description)
    await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)

#give me riven prefix name given stats
@tree.command(name = "prefixes", description = "Give the riven prefix names")
async def prefixes(interaction:discord.message, stat1:str, stat2:typing.Optional[str]='', stat3:typing.Optional[str]='', invisible_to_others:typing.Optional[bool]=True):
    #if stat from user = 1 then set it to none
    if stat1 == "1":
        stat1 = ""
    if stat2 == "1":
        stat2 = ""
    if stat3 == "1":
        stat3 = ""
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
    await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)

#give riven stats, given a prefix name
@tree.command(name = "riven_name", description = "Give the prefix, return stats")
async def riven_name(interaction:discord.message, name:str, invisible_to_others:typing.Optional[bool]=True):
    #open prefix_suffix
    with open("prefix_suffix.json") as json_file:
        prefix_suffix = json.load(json_file)
    #create the varriables for the stats
    first_stat = ""
    second_stat = ""
    third_stat = ""
    #grab the stat names from the prefixes/suffix
    for x in prefix_suffix:
        if prefix_suffix[x]['prefix'].lower() in name.lower() and first_stat == "":
            first_stat = x
        elif prefix_suffix[x]['prefix'].lower() in name.lower() and second_stat == "":
            second_stat = x
        if prefix_suffix[x]['suffix'].lower() in name.lower() and third_stat == "":
            third_stat = x
    #send to discord
    if first_stat != "" and second_stat != "" and third_stat != "":
        embed = discord.Embed(title="Stats for: **" + name + "**", description=first_stat +", "+ second_stat +", "+ third_stat)
        await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)
    elif first_stat != "" and second_stat != "":
        embed = discord.Embed(title="Stats for: **" + name+ "**", description=first_stat +", "+ second_stat)
        await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)
    elif first_stat != "" and third_stat != "":
        embed = discord.Embed(title="Stats for: **" + name+ "**", description=first_stat +", "+ third_stat)
        await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)
    elif third_stat != "" and second_stat != "":
        embed = discord.Embed(title="Stats for: **" + name+ "**", description=third_stat +", "+ second_stat)
        await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)
    elif first_stat != "":
        embed = discord.Embed(title="Stat for: **" + name+ "**", description=first_stat)
        await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)
    elif second_stat != "":
        embed = discord.Embed(title="Stat for: **" + name+ "**", description=second_stat)
        await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)
    elif third_stat != "":
        embed = discord.Embed(title="Stat for: **" + name+ "**", description=third_stat)
        await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)
    else:
        embed = discord.Embed(title="No Stats Given or Typo: **" + name+ "**", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)

#unroll search wfm
@tree.command(name = "unroll", description = "Grab 10 cheapest unroll rivens for a given weapon")
async def unroll(interaction:discord.message, weapon:str, invisible_to_others:typing.Optional[bool]=True):
    await interaction.response.defer(ephemeral = invisible_to_others)
    wfm_search_link = "https://api.warframe.market/v1/auctions/search?type=riven&weapon_url_name="+weapon.replace(" ", "_").replace("-","_").replace("&","and").lower()+"&polarity=any&sort_by=price_asc"
    #url to grab from
    data = requests.get(wfm_search_link)
    #make it dict
    data = dict(data.json())
    count = 0
    number_of_returns = 10
    description = ""
    try:
        #loop through each riven
        for x in data['payload']['auctions']:
            #check if its a pc riven
            if x['platform'] == "pc":
                count += 1
                #grab the rest of the data
                weapon_name = x['item']['weapon_url_name']
                wfm_url = x['id']
                rerolls = x['item']['re_rolls']
                prefix = x['item']['name']
                user = x['owner']['ingame_name']
                start_price = x['starting_price']
                bo_price = x['buyout_price']
                mr = x['item']['mastery_level']
                pol = x['item']['polarity']
                status = x['owner']['status']
                if status == "ingame":
                    #make sure they're unrolled
                    if int(rerolls) == 0:
                        if number_of_returns > 0:
                            number_of_returns += -1
                            description += "**[" + weapon_name.title().replace("_"," ") + " " + prefix + "](https://warframe.market/auction/"+ wfm_url + ") " + str(start_price) + "-" + str(bo_price) + " MR" + str(mr) + " " + pol.title() + "**\n/w " + user + " Hi, I'd like to buy your " + weapon + " " + prefix + " riven that you sell on warframe.market\n\n"
        embed = discord.Embed(title="Unroll Riven Price for " + weapon_name.title().replace("_"," ") + ": ", description=description, color=discord.Color.yellow())
        await interaction.followup.send(embed=embed)
    except:
        embed = discord.Embed(title="Error", color=discord.Color.red())
        await interaction.followup.send(embed=embed)

#trash search wfm
@tree.command(name = "trash", description = "Grab 10 cheapest rivens for a given weapon")
async def trash(interaction:discord.message, weapon:str, invisible_to_others:typing.Optional[bool]=True):
    await interaction.response.defer(ephemeral = invisible_to_others)
    wfm_search_link = "https://api.warframe.market/v1/auctions/search?type=riven&weapon_url_name="+weapon.replace("-","_").replace(" ", "_").replace("&","and")+"&polarity=any&sort_by=price_asc"
    #url to grab from
    data = requests.get(wfm_search_link)
    #make it dict
    data = dict(data.json())
    count = 0
    number_of_returns = 10
    description = ""
    try:
        #loop through each riven
        for x in data['payload']['auctions']:
            #check if its a pc riven
            if x['platform'] == "pc":
                count += 1
                #grab the rest of the data
                weapon_name = x['item']['weapon_url_name']
                wfm_url = x['id']
                rerolls = x['item']['re_rolls']
                prefix = x['item']['name']
                user = x['owner']['ingame_name']
                start_price = x['starting_price']
                bo_price = x['buyout_price']
                mr = x['item']['mastery_level']
                pol = x['item']['polarity']
                if number_of_returns > 0:
                    number_of_returns += -1
                    description += "**[" + weapon_name.title().replace("_"," ") + " " + prefix + "](https://warframe.market/auction/"+ wfm_url + ") " + str(start_price) + "-" + str(bo_price) + " MR" + str(mr) + " " + pol.title() + " Rerolls: " + str(rerolls) + "**\n/w " + user + " Hi, I'd like to buy your " + weapon + " " + prefix + " riven that you sell on warframe.market\n\n"
        embed = discord.Embed(title="Trash Riven Price for " + weapon_name.title().replace("_"," ") + ": ", description=description, color=discord.Color.yellow())
        await interaction.followup.send(embed=embed)
    except:
        embed = discord.Embed(title="Error", description="Weapon not found: " + weapon ,color=discord.Color.red())
        await interaction.followup.send(embed=embed)

#weekly top 10 prices
@tree.command(name="top", description="Check the prices of top 10 sold rivens")
async def top(interaction:discord.message, invisible_to_others:typing.Optional[bool]=True):    
    #get the data
    raw_data = requests.get("https://www-static.warframe.com/repos/weeklyRivensPC.json")
    data = raw_data.text
    itemType = [i[:-1] for i in re.findall("(?=itemType).*",data)]
    compatibility = [i[:-1] for i in re.findall("(?=compatibility).*",data)]
    rero = [i[:-1] for i in re.findall("(?=rerolled).*",data)]
    avg = [i[:-1] for i in re.findall("(?=avg).*",data)]
    stddev = [i[:-1] for i in re.findall("(?=stddev).*",data)]
    minimum =[i[:-1] for i in re.findall("(?=min).*",data)]
    maximum = [i[:-1] for i in re.findall("(?=max).*",data)]
    pop = [i[:-1] for i in re.findall("(?=pop).*",data)]
    median = re.findall("(?=median).*",data)
    dict_of_top_10 = {}
    number_top_10 = 0
    while len(dict_of_top_10) < 10:
        high = 0
        count = 0
        for item, comp, rolled, av, std, mi, ma, po, med in zip(itemType, compatibility, rero, avg, stddev, minimum, maximum, pop, median):
            test_price = float(re.findall(r"\d+",ma)[0])
            if test_price > high:
                weapon = re.findall("(?=').[^']\D*[^']",comp)
                weapon_type = item
                rerolled = rolled
                high = float(re.search(r"\d+",ma)[0])
                weapon_number = count
            if count < len(data)-1:
                count += 1
        del itemType[weapon_number], compatibility[weapon_number], rero[weapon_number], avg[weapon_number], stddev[weapon_number], minimum[weapon_number], maximum[weapon_number], pop[weapon_number], median[weapon_number]
        number_top_10 += 1
        dict_of_top_10.update({number_top_10:{"weapon":weapon[0][1:], "weapon_type":weapon_type, "max_price":high,"rerolled":rerolled}})
    description = ""
    for x in dict_of_top_10:
        if "true" in dict_of_top_10[x]['rerolled']:
            rolled = "Rolled"
        else:
            rolled = "Unrolled"
        description += "Riven: **" + str(dict_of_top_10[x]['weapon']) + "** \nPrice: **" + str(int(dict_of_top_10[x]['max_price'])) + "P** " + rolled + "\n\n"
    embed = discord.Embed(title="Top 10 Rivens By Price: ", description=description,color=discord.Color.yellow())
    await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)

#give price check on riven image
@tree.command(name="pc", description="price check")
async def pc(interaction:discord.message, image_attachted: discord.Attachment, invisible_to_others:typing.Optional[bool]=True):   
    await interaction.response.defer(ephemeral = invisible_to_others) 
    try:
        riven = img_reading_dyn.grade_riven(Image.open(BytesIO(requests.get(image_attachted.url).content)))
    except:
        embed = discord.Embed(title="Broke during OCR, take a better pic!", color=discord.Color.red())
        Image.open(BytesIO(requests.get(image_attachted.url).content)).save("riven_ocr.png")
        file = discord.File("riven_ocr.png", filename="image.png")
        embed.set_image(url="attachment://image.png")
        await interaction.followup.send(file = file, embed=embed)
        return    
    weapon = riven[0].replace(" ","_").lower()
    stat1val = riven[1]
    stat1name = riven[2].replace(" ","_").lower()
    stat2val = riven[3]
    stat2name = riven[4].replace(" ","_").lower()
    stat3val = riven[5]
    stat3name = riven[6].replace(" ","_").lower()
    negval = riven[7]
    negname = riven[8].replace(" ","_").lower()
    #check if user wants any of the stats null
    if "[]" in stat1name:
        stat1name = ""
    if "[]" in stat2name:
        stat2name = ""
    if "[]" in stat3name:
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
    if "[]" not in negname:
        negsearch = "&negative_stats=" + negname
    elif negname == "[]":
        negsearch = ""
    else:
        negsearch = "&negative_stats=has"
    wfm_search_link = "https://api.warframe.market/v1/auctions/search?type=riven&weapon_url_name="+weapon.replace("-","_")+stat_search+negsearch+"&polarity=any&sort_by=price_asc"
    #url to grab from
    header = {"Host":"api.warframe.market"}
    data = requests.get(wfm_search_link, headers = header)
    #make it dict
    data = dict(data.json())
    try:
        if data == {'error': {'weapon_url_name': ['app.auctions.errors.item_not_exist'], 'negative_stats': ['app.form.invalid']}} or data["payload"]['auctions'] == []:
            description = "```"+ stat1name + " " + stat2name + " "  + stat3name + " "  + negname + "```"
            description = description_creation(weapon, stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negname, description)
            embed = discord.Embed(title="None found!", description= description, color=discord.Color.yellow())
            Image.open(BytesIO(requests.get(image_attachted.url).content)).save("riven_ocr.png")
            file = discord.File("riven_ocr.png", filename="image.png")
            embed.set_image(url="attachment://image.png")
            await interaction.followup.send(file = file,embed=embed)
            return
    except:
        description = "```"+ stat1name + " " + stat2name + " "  + stat3name + " "  + negname + "```"
        description = description_creation(weapon, stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negname, description)
        embed = discord.Embed(title="None found!", description= description, color=discord.Color.yellow()) 
        Image.open(BytesIO(requests.get(image_attachted.url).content)).save("riven_ocr.png")
        file = discord.File("riven_ocr.png", filename="image.png")
        embed.set_image(url="attachment://image.png")
        await interaction.followup.send(file = file,embed=embed)
        return
    prices = {}
    #loop through each riven
    for x in data['payload']['auctions']:
        wfm_link = "https://warframe.market/auction/" + str(x['id'])
        if x['item']['re_rolls'] == 0:
            rolled = ":white_check_mark:"
        else:
            rolled = ":x:"
        pos_stats = [item for item in x['item']['attributes'] if item['positive'] == True]
        stat1wfm = str(pos_stats[0]['url_name'])
        stat2wfm = str(pos_stats[1]['url_name'])
        try: 
            stat3wfm = str(pos_stats[2]['url_name'])
        except:
            stat3wfm = ""
        neg_stats = [item for item in x['item']['attributes'] if item['positive'] == False]
        try:
            negwfm = str(neg_stats[0]['url_name'])
        except:
            negwfm = ""
        if sorted([stat1name, stat2name, stat3name]) == sorted([stat1wfm, stat2wfm, stat3wfm]) and negname == negwfm:            
            start_price = str(x['starting_price'])
            bo_price = str(x['buyout_price'])
            top_price = str(x['top_bid'])
            name = str(x['item']['name'])
            prices.update({x['id']:[start_price,top_price, bo_price, rolled, wfm_link]})
    if stat3val == "":
        stat3val = "[]"
    if negval == "":
        negval = "[]"
    if stat1name == "":
        stat1name = "[]"
    if stat2name == "":
        stat2name = "[]"
    if stat3name == "":
        stat3name = "[]"
    if negname == "":
        negname = "[]"
    if prices == {}:
        description = "```"+ stat1name + " " + stat2name + " "  + stat3name + " "  + negname + "```"
        description = description_creation(weapon, stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negname, description)
        embed = discord.Embed(title="None found!", description= description, color=discord.Color.yellow())
        Image.open(BytesIO(requests.get(image_attachted.url).content)).save("riven_ocr.png")
        file = discord.File("riven_ocr.png", filename="image.png")
        embed.set_image(url="attachment://image.png")
        await interaction.followup.send(file = file, embed=embed)
        return
    description = "Start | Bid | Buyout | Unrolled"
    for x in prices:
        description += "\n[" + prices[x][0] + " | " +  prices[x][1] + " | " +prices[x][2] + " | " + prices[x][3] + "](" + prices[x][4] + ")"
    description = description_creation(weapon, stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negname, description)
    Image.open(BytesIO(requests.get(image_attachted.url).content)).save("riven_ocr.png")
    file = discord.File("riven_ocr.png", filename="image.png")
    embed = discord.Embed(title="Prices for: " + riven[0] + " " + name ,description= description,  color=discord.Color.yellow())
    embed.set_image(url="attachment://image.png")
    await interaction.followup.send(file = file, embed=embed)   

#check arbi
@tree.command(name = "arby", description = "Check current arbitration")
async def arby(interaction:discord.message, invisible_to_others:typing.Optional[bool]=True):
    url = "https://10o.io/arbitrations.json"
    test = requests.get(url)
    data = dict(test.json()[0])
    # print(data)
    tile = data['solnodedata']['tile']
    planet = data['solnodedata']['planet']
    mission = data['solnodedata']['type']
    enemy = data['solnodedata']['enemy']
    embed = discord.Embed(description="Node: **" + tile + " (" + planet + ")" + "**\nMission Type: **" + mission + "**\nFaction: **" + enemy + "**", color=discord.Color.yellow())
    await interaction.response.send_message(embed=embed, ephemeral = invisible_to_others)

#wfm profile command
@tree.command(name = "wfm_img", description="Generate image of rivens listed on someones wfm profile")
async def wfm_img(interaction:discord.message, user:str, invisible_to_others:typing.Optional[bool]=True):
    await interaction.response.defer(ephemeral = invisible_to_others)
    # try:
    riven_images = [grab_info_from_wfm.start(user)]
    print(len(riven_images))
    # except:
        # embed = discord.Embed(title="Name not Found", color=discord.Color.red())
        # await interaction.followup.send(embed=embed)
    #cycle through riven images with buttons n shit
    L = 1
    async def get_page(page: int):
        offset = (page-1) * L
        # riven_images = riven_images.values()
        for x in riven_images[offset:offset+L]:
            image = x
            image.save("riven_image" + str(offset) + ".png")
            embed = discord.Embed(title = user)
            file = discord.File("riven_image"+str(offset) + ".png", filename="image.png")
            embed.set_image(url="attachment://image.png")
        n = Pagination_file_send.compute_total_pages(len(riven_images), L)
        embed.set_footer(text=f"Riven {page} of {n}")
        return embed, n, file
    await Pagination_file_send(interaction, get_page).navegate()

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")
client.run(TOKEN)