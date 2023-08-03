#tc_ocr_scraper

from dotenv import load_dotenv
import os
import discord
import pytesseract
import PIL.ImageGrab as ImageGrab
import re
import json
import prefixes_create
from discord import Color
from discord.ext import tasks

#declare discord intents
intents = discord.Intents.all()
intents.message_content = True

client = discord.Client(intents = intents)

#load the discord token and id
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#varrs needed
identifier = set()

#channel ids
pc_snipe = put your snipe channel id here
pc_bl = put your blacklist channel id here

#tc ocr scraper
@tasks.loop()
async def tc_scraper():
    global identifier
    #take a ss of tc
    #(left_x, top_y, right_x, bottom_y)
    img1 = ImageGrab.grab(bbox=(20, 590, 1140, 1020))
    #use tesseract to get text from the ss
    text = pytesseract.image_to_string(img1)
    # splits with a look ahead(misses the latest post)
    text_split = re.findall("[\s\S]*?(?=\[[0-9]{2}\:[0-9]{2}\])",text)
    #loop through each split
    for i in text_split:
        i = i.replace("\n","")
        # if the tc_message hasnt been seen yet
        if i not in str(identifier):
            #pull the usernames out of tc
            username = re.findall("(?<=\[[0-9]{2}\:[0-9]{2}\])(.*?)(?=:)",i)
            #time posted
            time = re.findall("\[[0-9]{2}\:[0-9]{2}\]",i)
            #tc_message
            if time != [] and username != []:
                tc_message = i.replace(time[0],"").replace(username[0],"")
            elif username != []:
                tc_message = i.replace(username[0],"")
            else:
                tc_message = i
            #open filters
            with open("filters.json") as json_file:
                filters = json.load(json_file)
            #weapon names from filter to cut out
            weapon_names_not = ["1","melee","rifle","shotgun","pistol","archgun"]
            #loop through filters
            for x in filters:
                #varrs needed
                prefixes = ""
                #check if the filter is an empty stat
                if filters[x]['pos1'] != "1":
                    pos1 = filters[x]['pos1']
                else:
                    pos1 = ""
                if filters[x]['pos2'] != "1":
                    pos2 = filters[x]['pos2']
                else:
                    pos2 = ""
                if filters[x]['pos3'] != "1":
                    pos3 = filters[x]['pos3']
                else:
                    pos3 = ""
                #if its not all empty +++ then 
                if pos1 != "" or pos2 != "" or pos3 != "":
                    prefixes = prefixes_create.create_prefixes(pos1, pos2, pos3)
                if filters[x]['weapon'] not in weapon_names_not:
                    weapon = filters[x]['weapon']
                else:
                    weapon = ""
                if prefixes != "":
                    prefixes = prefixes.split("\n")
                    #loop through the prefixes
                    links = re.findall("[\[{].*?[\]|}]",tc_message)
                    prices = [re.sub("[\[{].*?[\]|}]", " ",i) for i in re.findall("[\[{].*?[\]|}] *\d*[.,]?\d*k?p?w?",tc_message)]
                    for prefix in prefixes:
                        #string to check for filter
                        string_to_search = weapon.title() + " " + prefix.capitalize()
                        for link, price in zip(links, prices):
                            if string_to_search in link:
                                #string to check if the riven has been grabbed already
                                try:
                                    identifier_to_add = username[0] + string_to_search
                                except:
                                    print("failed to create identifier to add")
                                    continue
                                if identifier_to_add.lower() not in str(identifier).lower():
                                    blacklist = []
                                    #open the blacklist file
                                    with open('blacklist.txt') as blacklist_file:
                                        for line in blacklist_file:
                                            line = line.replace('\n','')
                                            blacklist.append(line.lower())
                                    if username[0].strip().lower() not in str(blacklist).lower():
                                        #send to discord
                                        channel = client.get_channel(pc_snipe)
                                        embed = discord.Embed(title=re.sub("[\[\]\{\}]", "", link) + " " + price,description="/w " + re.sub("[-]","\-",str(re.sub("[_]","\_",str(username[0]).lower().strip()))) + " can you link your " + re.sub("[\[\]\{\}]", "", link) + "\n\n" + "**Message:** " + i, color=discord.Color.yellow())
                                        embed.set_author(name= username[0])
                                        message = await channel.send(embed=embed)
                                        identifier.add(identifier_to_add)
                                    else:
                                        #send to discord
                                        channel = client.get_channel(pc_bl)
                                        embed = discord.Embed(title=re.sub("[\[\]\{\}]", "", link) + " " + price,description="/w " + re.sub("[-]","\-",str(re.sub("[_]","\_",str(username[0]).lower().strip()))) + " can you link your " + re.sub("[\[\]\{\}]", "", link) + "\n\n" + "**Message:** " + i, color=discord.Color.yellow())
                                        embed.set_author(name= username[0])
                                        message = await channel.send(embed=embed)
                                        identifier.add(identifier_to_add)

#start the bot loop
@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    print(
        f'{client.user} has connectred to Discord!'
        f'{guild.name}(id: {guild.id})'
    )
    tc_scraper.start()
client.run(TOKEN)