#grab_info_from_wfm
import requests
from PIL import Image, ImageFont, ImageDraw
import json
import re
import translator_search
import math
import decimal

base_print_value = 230
print_value = 0
def start(user):
    user = user
    url = "https://api.warframe.market/v1/profile/"+user+"/auctions"
    data = requests.get(url).json()
    rivens_data = retrieve_rivens(data)
    def riven_img(weapon, pos_stats, neg_stat, neg_val, pol, roll_count, mr, prefix, price):
        global base_print_value
        global print_value
        price = str(price)
        weapon = weapon.lower().replace("dark_split_sword_(dual_swords)","dark_split-sword").title().replace("_"," ")
        prefix = prefix.title()
        stat1stat = pos_stats["pos0_vals"]
        stat2stat = pos_stats["pos1_vals"]
        try:
            stat3stat = pos_stats["pos2_vals"]
        except:
            stat3stat = "[]"
        try:
            if neg_val == []:
                negstat = "[]"
            else:
                negstat = neg_val
        except:
            negstat = "[]"
        stat1name_raw = pos_stats["pos0_stats"].replace("_"," ").replace("Channeling Efficiency","Heavy Attack").replace("Channeling Damage","Initial Combo")
        stat2name_raw = pos_stats["pos1_stats"].replace("_"," ").replace("Channeling Efficiency","Heavy Attack").replace("Channeling Damage","Initial Combo")
        try:
            stat3name_raw = pos_stats["pos2_stats"].replace("_"," ").replace("Channeling Efficiency","Heavy Attack").replace("Channeling Damage","Initial Combo")
        except:
            stat3name_raw = "[]"
        try:
            negname_raw = neg_stat.replace("_"," ").replace("Channeling Efficiency","Heavy Attack").replace("Channeling Damage","Initial Combo")
        except:
            negname_raw = "[]"
        #process values from wfm
        stat1stat = float(stat1stat)
        stat2stat = float(stat2stat)
        if stat3stat != '[]':
            stat3stat = float(stat3stat)
        else:
            stat3stat = 0
        if negstat != '[]':
            negstat = float(negstat)
        else:
            negstat = 0
        roll_count = int(roll_count)
        mr = int(mr)
        #process names from wfm
        if stat1name_raw == []:
            stat1name_raw = "[]"
        if stat2name_raw == []:
            stat2name_raw = "[]"
        if stat3name_raw == []:
            stat3name_raw = "[]"
        if negname_raw == []:
            negname_raw = "[]"
        #open dispos
        with open("weapon_info.json") as json_file:
            weapon_info = json.load(json_file)
        # with open("melee_dispos.txt") as json_file:
        #     melee_dispos = json.load(json_file)
        # with open("archgun_dispos.txt") as json_file:
        #     archgun_dispos = json.load(json_file)
        # with open("rifle_dispos.txt") as json_file:
        #     rifle_dispos = json.load(json_file)
        # with open("shotgun_dispos.txt") as json_file:
        #     shotgun_dispos = json.load(json_file)
        #open images used
        mad = Image.open("madaurai.png")
        vaz = Image.open("vazarin.png")
        nar = Image.open("naramon.png")
        rolled = Image.open("rolled.png")
        #check polarity and set it accordingly
        if pol == "naramon":
            pol = nar
        if pol == "vazarin":
            pol = vaz
        if pol == "madurai":
            pol = mad
        #open base images
        normal_riven = Image.open("riven.png")
        short_riven = Image.open("riven_short.png")
        long_riven = Image.open("riven_long.png")
        #get number of lines to be wrote onto riven
        number_of_lines = 0
        statnames = [stat1name_raw, stat2name_raw, stat3name_raw, negname_raw]
        statvalues = [stat1stat, stat2stat, stat3stat, negstat]
        #loop the stats and count lines needed
        for statval, statname in zip(statvalues, statnames):
            if statval == 0:
                break
            if len(str(statval) + " "+ statname) > 24:
                number_of_lines += 2
            else:
                number_of_lines += 1
        if len(weapon + prefix) < 14:
            number_of_lines += 1
        else:
            number_of_lines += 2
        #assign vars depending on length of lines
        if number_of_lines >= 7:
            base_riven = long_riven
            bottom_row = 463
        elif number_of_lines >= 6:
            base_riven = normal_riven
            bottom_row = 418
        else:
            base_riven = short_riven
            bottom_row = 382
        #function to split stat lines if its too long
        def split_or_not_stats(statname, statval,pos_neg):
            if statval == 0:
                return
            global base_print_value, print_value
            #generate the sybol after the stat value
            if statname != "Range" and statname != "Initial Combo" and statname != "Combo Duration" and statname != "Punch Through":
                p_or_m_or_s = "%"
            elif statname == "Range" or statname == "Initial Combo" or statname == "Punch Through":
                p_or_m_or_s = ""
            elif statname == "Combo Duration":
                p_or_m_or_s = "s"
            #check if it cant fit the stat on 1 line
            if len(str(statval) + " "+ statname) > 24:
                #split the stats at spaces
                split_string = statname.split(" ")
                #create that varrs needed in the while loop
                line1 = ""
                count = 0
                #run while line1 would be less then 23 chars
                while len(line1 + str(statval)) <= 23:
                    #if it'd be less then 25chars then add the next word
                    if len(line1 + split_string[count] + str(statval)) <= 23:
                        line1 += split_string[count] + " "
                        count += 1
                    #if it'd be more then 25chars break out of the while loop
                    else:
                        break
                #create line2 with rest of string
                line2 = re.sub("[\[\]',]","",str(split_string[count:]))
                #write each on the riven
                _,_,w,h = draw.textbbox((315,0),str(statval) + line1, font= stat_name_font)
                draw.text(((W-w)/2, print_value), pos_neg+str(abs(statval))+p_or_m_or_s + " " + line1, font=stat_name_font, fill=(171, 136, 204))
                print_value += 30
                base_print_value += 30
                _,_,w,h = draw.textbbox((280,0),line2, font= stat_name_font)
                draw.text(((W-w)/2, print_value), line2, font=stat_name_font, fill=(171, 136, 204))
                base_print_value += 30
            else:
                #write each on the riven
                _,_,w,h = draw.textbbox((315,0),str(statval) + statname, font= stat_name_font)
                draw.text(((W-w)/2, print_value), pos_neg+str(abs(statval))+p_or_m_or_s + " " + statname, font=stat_name_font, fill=(171, 136, 204))
                print_value += 30
                base_print_value += 30
        #apply polarity
        base_riven.paste(pol, (320,44), pol)
        #draw call
        draw = ImageDraw.Draw(base_riven)
        #fonts for roll count and name
        roll_font = ImageFont.truetype("Roboto-Medium.ttf",size=18)
        name_font = ImageFont.truetype("Roboto-Regular.ttf",size=38)
        stat_name_font = ImageFont.truetype("Roboto-Regular.ttf",size=25)
        price_font = ImageFont.truetype("Roboto-Medium.ttf",size=65)
        #create the bottom bar where mr and reroll count
        if roll_count == 0:
            draw.text((165,bottom_row),"MR " + str(mr),font=roll_font, fill = (171, 136, 204))
        elif len(str(roll_count)) == 1:
            #if rerolls = 1 digit
            base_riven.paste(rolled, (275,bottom_row-1),rolled)
            draw.text((300,bottom_row),str(roll_count),font=roll_font, fill = (171, 136, 204))
            draw.text((70,bottom_row),"MR " + str(mr),font=roll_font, fill = (171, 136, 204))
        elif len(str(roll_count)) == 2:
            #if rerolls = 2 digit
            base_riven.paste(rolled, (260,bottom_row-1),rolled)
            draw.text((285,bottom_row),str(roll_count),font=roll_font, fill = (171, 136, 204))
            draw.text((70,bottom_row),"MR " + str(mr),font=roll_font, fill = (171, 136, 204))
        elif len(str(roll_count)) == 3:
            #if rerolls = 3 digit
            base_riven.paste(rolled, (255,bottom_row-1),rolled)
            draw.text((280,bottom_row),str(roll_count),font=roll_font, fill = (171, 136, 204))
            draw.text((70,bottom_row),"MR " + str(mr),font=roll_font, fill = (171, 136, 204))
        elif len(str(roll_count)) == 4:
            #if rerolls = 4 digit
            base_riven.paste(rolled, (245,bottom_row-1),rolled)
            draw.text((270,bottom_row),str(roll_count),font=roll_font, fill = (171, 136, 204))
            draw.text((70,bottom_row),"MR " + str(mr),font=roll_font, fill = (171, 136, 204))
        #create that varrs needed in the while loop
        line1 = ""
        line2 = ""
        count = 0
        long_name = False
        prefix_part = prefix.split("-")
        #write price
        W,H = base_riven.size
        _,_,w,h = draw.textbbox((275,0),price, font= price_font)
        draw.text(((W-w)/2, 75), price, font=price_font, fill=(255, 255, 0))
        #weapon + prefix if it fits
        if len(weapon + prefix) < 14:
            line1 = weapon + " " + prefix
        #check if weapon + first part of prefix will fit
        elif len(weapon + prefix_part[0]) < 13:
            line1 = weapon + " "+ prefix_part[0] + "-"
            line2 = prefix_part[1]
            long_name = True
        #check if weapon + prefix is too long
        elif len(weapon + prefix) > 13:
            line1 = weapon
            line2 = prefix
            long_name = True
        #write weapon name/prefix
        W,H = base_riven.size
        _,_,w,h = draw.textbbox((275,0),line1, font= name_font)
        draw.text(((W-w)/2, 180), line1, font=name_font, fill=(171, 136, 204))
        #write weapon name / prefix if its too long for 1 line
        if line2 != "":
            W,H = base_riven.size
            _,_,w,h = draw.textbbox((280,0),line2, font= name_font)
            #write weapon name centered
            draw.text(((W-w)/2, 215), line2, font=name_font, fill=(171, 136, 204))
        #loop through and replace fr/as and dmg/melee dmg
        stat1name, stat2name, stat3name, negname = ["Fire Rate" if stat.lower() == "fire rate / attack speed" and weapon_info[weapon.title()]['type'] != "melee" else "Attack Speed" if stat.lower() == "fire rate / attack speed" and weapon_info[weapon.title()]['type'] == "melee" else stat for stat in ["Damage" if stat.lower() == "base damage / melee damage" and weapon_info[weapon.title()]['type'] != "melee" else "Melee Damage" if stat.lower() == "base damage / melee damage" and weapon_info[weapon.title()]['type'] == "melee" else stat for stat in [stat1name_raw, stat2name_raw, stat3name_raw, negname_raw]]]
        #translate stat names
        stat1name = translator_search.translate_riven_img(stat1name)
        stat2name = translator_search.translate_riven_img(stat2name)
        stat3name = translator_search.translate_riven_img(stat3name)
        negname = translator_search.translate_riven_img(negname)
        #check if rifle/melee so it can add (x2 for ***)
        if weapon_info[weapon.title()]['type'] == "melee":
        # if weapon.title() in str(melee_dispos):
            stat1name = translator_search.translate_riven_img_melee(stat1name)
            stat2name = translator_search.translate_riven_img_melee(stat2name)
            stat3name = translator_search.translate_riven_img_melee(stat3name)
        if weapon_info[weapon.title()]['type'] != "melee":
        # if weapon.title() in str(archgun_dispos) or weapon.title() in str(rifle_dispos) or weapon.title() in str(shotgun_dispos):
            stat1name = translator_search.translate_riven_img_rifle(stat1name)
            stat2name = translator_search.translate_riven_img_rifle(stat2name)
            stat3name = translator_search.translate_riven_img_rifle(stat3name)
        #make neg value negative so I can check in the loop below for the negative stat
        negstat = -abs(negstat)
        #loop through all the stats
        for stats in ([stat1name,stat1stat], [stat2name,stat2stat], [stat3name,stat3stat], [negname,negstat]):
            recoil_symbol = "-"
            pos_neg = "+"
            if stats[1] < 0:
                recoil_symbol = "+"
                pos_neg = "-"
            #check if name isnt too long
            if long_name != True:
                #if it isnt recoil
                print_value = base_print_value
                if str(stats[0]).title() != "Weapon Recoil":
                    split_or_not_stats(stats[0], stats[1], pos_neg)
                #if it is recoil
                else:
                    split_or_not_stats(stats[0], stats[1], recoil_symbol)
            else:
                #if its too long for 1 line
                print_value = base_print_value + 30
                #if it isnt recoil
                if str(stats[0]).title() != "Weapon Recoil":
                    split_or_not_stats(stats[0], stats[1], pos_neg)
                #if it is recoil
                else:
                    split_or_not_stats(stats[0], stats[1], recoil_symbol)
        base_print_value = 230
        print_value = 0
        base_riven = base_riven.crop((0,0,375,base_riven.size[0]))
        return(base_riven)

    list_of_images = []
    for weapon_id in rivens_data:
        img_new = Image.new("RGBA",(375,666))
        img_new.paste(riven_img(rivens_data[weapon_id]["weapon"], rivens_data[weapon_id]["pos_stats"], rivens_data[weapon_id]['neg_stat'], rivens_data[weapon_id]["neg_val"], rivens_data[weapon_id]["polarity"], rivens_data[weapon_id]["rerolls"], rivens_data[weapon_id]["mastery"], rivens_data[weapon_id]["riven_name"],rivens_data[weapon_id]["price"]),(0,0),riven_img(rivens_data[weapon_id]["weapon"], rivens_data[weapon_id]["pos_stats"], rivens_data[weapon_id]['neg_stat'], rivens_data[weapon_id]["neg_val"], rivens_data[weapon_id]["polarity"], rivens_data[weapon_id]["rerolls"], rivens_data[weapon_id]["mastery"], rivens_data[weapon_id]["riven_name"],rivens_data[weapon_id]["price"]))
        list_of_images.append(img_new)
    img_per_row = round(math.sqrt(len(list_of_images)))

    if (math.sqrt(len(list_of_images)) - math.floor(math.sqrt(len(list_of_images)))) < (math.ceil(math.sqrt(len(list_of_images))) - math.sqrt(len(list_of_images))):
        img_new = Image.new("RGBA",(375*img_per_row,560*img_per_row+560))
    else:
        img_new = Image.new("RGBA",(375*img_per_row,560*img_per_row))

    x_coor = 0
    y_coor = 0
    for riven_image in list_of_images:
        img_new.paste(riven_image,(x_coor,y_coor),riven_image)
        if x_coor == 375*img_per_row-375:
            x_coor = 0
            y_coor += 560
            continue
        x_coor += 375
    img_new.save("grid.png")
    return img_new

def retrieve_rivens(data):
    rivens = {}
    for riven in data["payload"]["auctions"]:
        if riven['is_marked_for'] != "removing":
            positive_stats = []
            positive_vals = []
            negative_stats = []
            negative_vals = []
            rolls = riven["item"]["re_rolls"]
            mr = riven["item"]["mastery_level"]
            riv_name = riven["item"]["name"]
            pol = riven["item"]["polarity"]
            if "ax_52" in riven["item"]["weapon_url_name"]:
                weap_name = "ax-52"
            elif "efv_5_jupiter" in riven["item"]["weapon_url_name"]: 
                weap_name = "efv-5_jupiter"
            else:
                weap_name = riven["item"]["weapon_url_name"]
            if riven["buyout_price"] == None:
                price = riven["starting_price"]
            else:
                price = riven["buyout_price"]
            stats = {}
            count = 0
            for stat in riven["item"]["attributes"]:
                if stat["positive"] == True:
                    stats.update({f"pos{count}_stats":stat['url_name'],f"pos{count}_vals":stat['value']})
                    positive_stats.append(stat['url_name'])
                    positive_vals.append(stat['value'])
                    count += 1
                elif stat["positive"] == False:
                    negative_stats.append(stat['url_name'])
                    negative_vals.append(stat['value'])
            try:
                rivens.update({riven["id"]:{"weapon":weap_name,"riven_name":riv_name,"rerolls":rolls,"mastery":mr,"polarity":pol,"price":price,"pos_stats":stats,"neg_stat":negative_stats[0],"neg_val":negative_vals[0]}})
            except:
                rivens.update({riven["id"]:{"weapon":weap_name,"riven_name":riv_name,"rerolls":rolls,"mastery":mr,"polarity":pol,"price":price,"pos_stats":stats,"neg_stat":negative_stats,"neg_val":negative_vals}})
    return rivens
