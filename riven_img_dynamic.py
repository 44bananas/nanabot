#riven_img_dynamic

from PIL import Image, ImageFont, ImageDraw
import grading_functions
import json
import translator_search
import re
import io
import prefixes_create

#values for writing on rive
base_print_value = 230
print_value = 0

def riven_img(weapon, stat1name_raw, stat1stat, stat2name_raw, stat2stat, stat3name_raw, stat3stat, negname_raw, negstat, pol, roll_count, mr):
    global base_print_value, print_value

    #dict of rivens
    imgs = {}
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
    with open("melee_dispos.txt") as json_file:
        melee_dispos = json.load(json_file)
    with open("archgun_dispos.txt") as json_file:
        archgun_dispos = json.load(json_file)
    with open("rifle_dispos.txt") as json_file:
        rifle_dispos = json.load(json_file)
    with open("shotgun_dispos.txt") as json_file:
        shotgun_dispos = json.load(json_file)
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

    #generate grades
    grades = grading_functions.get_varriants(str(weapon).replace("_"," "), stat1stat, stat1name_raw,stat2stat, stat2name_raw, stat3stat, stat3name_raw,negstat,negname_raw)
    number_of_varriants = len(grades)
    while number_of_varriants > 0:
        #open riven base img
        normal_riven = Image.open("riven.png")
        short_riven = Image.open("riven_short.png")
        long_riven = Image.open("riven_long.png")
        try:
            pos1_color, pos_grade1_1, pos_grade1_2 = grades[str(number_of_varriants)]['pos1']
        except:
            pos1_color = ""
            pos_grade1_1 = ""
            pos_grade1_2 = ""
        try:
            pos2_color,pos_grade2_1, pos_grade2_2 = grades[str(number_of_varriants)]['pos2']
        except:
            pos2_color = ""
            pos_grade2_1 = ""
            pos_grade2_2 = ""
        try:
            pos3_color, pos_grade3_1, pos_grade3_2 = grades[str(number_of_varriants)]['pos3']
        except:
            pos3_color = ""
            pos_grade3_1 = ""
            pos_grade3_2 = ""
        try:
            neg_color, neg_grade1, neg_grade2 = grades[str(number_of_varriants)]['neg']
        except:
            neg_color = ""
            neg_grade1 = ""
            neg_grade2 = ""
        try:
            weapon_varriant = str(grades[str(number_of_varriants)]['weapon'])
        except:
            weapon_varriant = weapon
        try:
            weapon = weapon.replace("_"," ").title()
        except:
            weapon = weapon

        #if empty stats
        if pos_grade1_1 == "":
            pos_grade1_1 = 0
        if pos_grade2_1 == "":
            pos_grade2_1 = 0
        if pos_grade3_1 == "":
            pos_grade3_1 = 0

        #generate the prefix
        dict_of_stats = {stat1name_raw:pos_grade1_1,stat2name_raw:pos_grade2_1,stat3name_raw:pos_grade3_1}
        dict_of_stats = sorted(dict_of_stats,key=dict_of_stats.get,reverse=True)
        prefix = prefixes_create.create_prefixes(dict_of_stats[0],dict_of_stats[1],dict_of_stats[2]).split("\n")[0]

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
        if number_of_lines >= 8:
            base_riven = long_riven
            bottom_row = 463
        elif number_of_lines >= 6:
            base_riven = normal_riven
            bottom_row = 418
        else:
            base_riven = short_riven
            bottom_row = 382
        
        #function to split stat lines if its too long
        def split_or_not_stats(statname, statval,grade1, grade2, color,pos_neg):
            if statval == 0:
                return
            global base_print_value, print_value
            #if grade is positive add a + to the front
            if grade1 != "":
                if float(grade1) > 0:
                    grade1 = "+" + str(grade1)

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

                #write grade
                if grade1 == "" and grade2 == "":
                    draw.text((375,print_value),"?% ERROR",font=stat_name_font, fill = (252, 231, 3))

                if color == ":yellow_circle:":
                    draw.text((375,print_value),"?% ERROR",font=stat_name_font, fill = (252, 231, 3))
                
                if color == ":orange_circle:":
                    draw.text((375,print_value),str(grade1) + "% " + str(grade2),font=stat_name_font, fill = (252, 140, 3))

                if color == ":red_circle:":
                    draw.text((375,print_value),str(grade1) + "% " + str(grade2),font=stat_name_font, fill = (255, 0, 0))
                
                if color == ":green_circle:":
                    draw.text((375,print_value),str(grade1) + "% " + str(grade2),font=stat_name_font, fill = (0, 255, 0))

                base_print_value += 30
                print_value += 30
                _,_,w,h = draw.textbbox((280,0),line2, font= stat_name_font)
                draw.text(((W-w)/2, print_value), line2, font=stat_name_font, fill=(171, 136, 204))
                base_print_value += 30
            else:
                #write each on the riven
                _,_,w,h = draw.textbbox((315,0),str(statval) + statname, font= stat_name_font)
                draw.text(((W-w)/2, print_value), pos_neg+str(abs(statval))+p_or_m_or_s + " " + statname, font=stat_name_font, fill=(171, 136, 204))

                if grade1 == "" and grade2 == "":
                    draw.text((375,print_value),"?% ERROR",font=stat_name_font, fill = (252, 231, 3))

                if color == ":yellow_circle:":
                    draw.text((375,print_value),"?% ERROR",font=stat_name_font, fill = (252, 231, 3))
                
                if color == ":orange_circle:":
                    draw.text((375,print_value),str(grade1) + "% " + str(grade2),font=stat_name_font, fill = (252, 140, 3))

                if color == ":red_circle:":
                    draw.text((375,print_value),str(grade1) + "% " + str(grade2),font=stat_name_font, fill = (255, 0, 0))
                
                if color == ":green_circle:":
                    draw.text((375,print_value),str(grade1) + "% " + str(grade2),font=stat_name_font, fill = (0, 255, 0))

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

        #write varriant
        draw.text((375, base_print_value-30),weapon_varriant, font=stat_name_font, fill = (252, 231, 3))

        #create the bottom bar where mr and reroll count
        if roll_count == 0:
            draw.text((165,418),"MR " + str(mr),font=roll_font, fill = (171, 136, 204))
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
        if pos_grade1_1 == "":
            pos_grade1_1 = 0
        if pos_grade2_1 == "":
            pos_grade2_1 = 0
        if pos_grade3_1 == "":
            pos_grade3_1 = 0

        #create that varrs needed in the while loop
        line1 = ""
        line2 = ""
        count = 0
        long_name = False

        prefix_part = prefix.split("-")

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
        stat1name, stat2name, stat3name, negname = ["Fire Rate" if stat.lower() == "fire rate / attack speed" and weapon.title() not in melee_dispos else "Attack Speed" if stat.lower() == "fire rate / attack speed" and weapon.title() in melee_dispos else stat for stat in ["Damage" if stat.lower() == "base damage / melee damage" and weapon.title() not in melee_dispos else "Melee Damage" if stat.lower() == "base damage / melee damage" and weapon.title() in melee_dispos else stat for stat in [stat1name_raw, stat2name_raw, stat3name_raw, negname_raw]]]

        #translate stat names
        stat1name = translator_search.translate_riven_img(stat1name)
        stat2name = translator_search.translate_riven_img(stat2name)
        stat3name = translator_search.translate_riven_img(stat3name)
        negname = translator_search.translate_riven_img(negname)
        #check if rifle/melee so it can add (x2 for ***)
        if weapon.title() in str(melee_dispos):
            stat1name = translator_search.translate_riven_img_melee(stat1name)
            stat2name = translator_search.translate_riven_img_melee(stat2name)
            stat3name = translator_search.translate_riven_img_melee(stat3name)
        if weapon.title() in str(archgun_dispos) or weapon.title() in str(rifle_dispos) or weapon.title() in str(shotgun_dispos):
            stat1name = translator_search.translate_riven_img_rifle(stat1name)
            stat2name = translator_search.translate_riven_img_rifle(stat2name)
            stat3name = translator_search.translate_riven_img_rifle(stat3name)
            
        #make neg value negative so I can check in the loop below for the negative stat
        negstat = -abs(negstat)

        #loop through all the stats
        for stats, graded in zip([[stat1name,stat1stat], [stat2name,stat2stat], [stat3name,stat3stat], [negname,negstat]],[[pos_grade1_1, pos_grade1_2,pos1_color],[pos_grade2_1, pos_grade2_2,pos2_color],[pos_grade3_1, pos_grade3_2,pos3_color],[neg_grade1, neg_grade2,neg_color]]):
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
                    split_or_not_stats(stats[0], stats[1], graded[0], graded[1], graded[2],pos_neg)
                #if it is recoil
                else:
                    split_or_not_stats(stats[0], stats[1], graded[0], graded[1], graded[2],recoil_symbol)
            else:
                #if its too long for 1 line
                print_value = base_print_value + 30
                #if it isnt recoil
                if str(stats[0]).title() != "Weapon Recoil":
                    split_or_not_stats(stats[0], stats[1], graded[0], graded[1], graded[2],pos_neg)
                #if it is recoil
                else:
                    split_or_not_stats(stats[0], stats[1], graded[0], graded[1], graded[2],recoil_symbol)
        base_print_value = 230
        print_value = 0

        #set the image as bytes
        buf = io.BytesIO()
        base_riven.save(buf,format='png')

        #add the bytes into the dict
        imgs["{0}".format(number_of_varriants)] = buf.getvalue()

        number_of_varriants -= 1

    return imgs