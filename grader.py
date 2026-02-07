import json
import translator_search

with open("weapon_base.json") as json_file:
    weapon_base = json.load(json_file)
with open("weapon_info.json") as json_file:
    weapon_info = json.load(json_file)

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

def grade(weapon, stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat, rank):
    weapon = str(weapon).title()
    stat1name = str(stat1name).lower()
    stat2name = str(stat2name).lower()
    stat3name = str(stat3name).lower()
    negstat = str(negstat).lower()
    stat1val = (float(stat1val)/(1+float(rank)))*9
    stat2val = (float(stat2val)/(1+float(rank)))*9
    try:
        stat3val = (float(stat3val)/(1+float(rank)))*9
    except:
        stat3val = "[]"
    try:
        negval = (float(negval)/(1+float(rank)))*9
    except:
        negval = "[]"

    weapon = strip_variants(weapon)
    return get_grade(weapon, stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat)

#return grades with rm translate
def grade_rm(weapon, stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat):
    with open("weapon_info.json") as json_file:
        weapon_info = json.load(json_file)
    with open("weapon_base.json") as json_file:
        weapon_base = json.load(json_file)
    stat1name = translator_search.translates_rm(stat1name)
    stat2name = translator_search.translates_rm(stat2name)
    stat3name = translator_search.translates_rm(stat3name)
    negstat = translator_search.translates_rm(negstat)
    grades_dict = {}
    number_of_filters = 0
    for x in weapon_info:
        if weapon in weapon_info[x]["variants"] or (weapon in ["Sporelacer","Rattleguts","Vermisplicer","Catchmoon","Gaze","Tombfinger"] and weapon_info[x]['type'] == 'kitgun') or weapon_info[x]['type'] == 'bayonet':
            if weapon_info[x]["type"] != "kitgun" and weapon_info[x]["type"] != "bayonet":
                stats = weapon_base[weapon_info[x]['type']]
            elif weapon_info[x]["type"] == "bayonet":
                if "Melee" in weapon_info[x]["variants"]:
                    stats = weapon_base["melee"]
                if "Primary" in weapon_info[x]["variants"]:
                    stats = weapon_base["rifle"]
            else:                
                if "Primary" in weapon_info[x]["variants"]:
                    if "catchmoon" in weapon_info[x]["variants"] or "sporelacer" in weapon_info[x]["variants"]:
                        stats = weapon_base["shotgun"]
                    else:
                        stats = weapon_base["rifle"]
                else:
                    stats = weapon_base["pistol"]
            for variant in weapon_info[x]["variants"]:
                if weapon_info[x]["type"] == "kitgun":
                    if variant.replace("Secondary","").replace("Primary","").strip() != weapon:
                        continue
                dispo = weapon_info[x]["variants"][variant]
                grades = grade_weapon(stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat, stats, float(dispo))
                if grades != []:
                    for y in grades_dict:
                        number_of_filters = y
                    number_of_filters = int(number_of_filters) + 1
                    grades_dict.update({str(number_of_filters):{"weapon": variant.title(), "pos1": grades[0], "pos2": grades[1], "pos3": grades[2], "neg": grades[3]}})      
    return grades_dict

def get_grade(weapon, stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat):
    with open("weapon_info.json") as json_file:
        weapon_info = json.load(json_file)
    with open("weapon_base.json") as json_file:
        weapon_base = json.load(json_file)
    grades_dict = {}
    number_of_filters = 0
    for x in weapon_info:
        if weapon in weapon_info[x]["variants"] or (weapon in ["Sporelacer","Rattleguts","Vermisplicer","Catchmoon","Gaze","Tombfinger"] and weapon_info[x]['type'] == 'kitgun'):
            if weapon_info[x]["type"] != "kitgun" and weapon_info[x]["type"] != "bayonet":
                stats = weapon_base[weapon_info[x]['type']]
            elif weapon_info[x]["type"] == "bayonet":
                if "Melee" in weapon:           
                    stats = weapon_base["melee"]
                elif "Primary" in weapon:
                    stats = weapon_base["rifle"]
            else:                
                if "Primary" in weapon_info[x]["variants"]:
                    if "catchmoon" in weapon_info[x]["variants"] or "sporelacer" in weapon_info[x]["variants"]:
                        stats = weapon_base["shotgun"]
                    else:
                        stats = weapon_base["rifle"]
                else:
                    stats = weapon_base["pistol"]
            for variant in weapon_info[x]["variants"]:
                if weapon_info[x]['type'] == "bayonet" and weapon != variant:
                    continue
                if weapon_info[x]["type"] == "kitgun":
                    if variant.replace("Secondary","").replace("Primary","").strip() != weapon:
                        continue
                dispo = weapon_info[x]["variants"][variant]
                grades = grade_weapon(stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat, stats, float(dispo))
                if grades != []:
                    for y in grades_dict:
                        number_of_filters = y
                    number_of_filters = int(number_of_filters) + 1
                    grades_dict.update({str(number_of_filters):{"weapon": variant.title(), "pos1": grades[0], "pos2": grades[1], "pos3": grades[2], "neg": grades[3]}})        
    return grades_dict

def grade_weapon(stat1val, stat1name, stat2val, stat2name, stat3val, stat3name, negval, negstat,stats, dispo):
    grade1 = ""
    grade2 = ""
    grade3 = ""
    grade4 = ""
    if negstat == '[]':
        if stat3name == '[]':
            grade1 = grade_2stat_no_neg(stat1name, stat1val,stats, dispo)
            grade2 = grade_2stat_no_neg(stat2name, stat2val,stats, dispo)
            grade3 = ""
            grade4 = ""
        else:
            grade1 = grade_3stat_no_neg(stat1name, stat1val,stats, dispo)
            grade2 = grade_3stat_no_neg(stat2name, stat2val,stats, dispo)
            grade3 = grade_3stat_no_neg(stat3name, stat3val,stats, dispo)
            grade4 = ""
    else:
        if stat3name == '[]':
            grade1 = grade_2stat_neg(stat1name, stat1val,stats, dispo)
            grade2 = grade_2stat_neg(stat2name, stat2val,stats, dispo)
            grade3 = ""
            grade4 = grade_neg_2stat(negstat, abs(float(negval)),stats, dispo)
        else:
            grade1 = grade_3stat_neg(stat1name, stat1val,stats, dispo)
            grade2 = grade_3stat_neg(stat2name, stat2val,stats, dispo)
            grade3 = grade_3stat_neg(stat3name, stat3val,stats, dispo)
            grade4 = grade_neg_3stat(negstat, abs(float(negval)),stats, dispo)
    return [
        grade1,
        grade2,
        grade3,
        grade4
    ]

#return neg grade of a +2-1 riven
def grade_neg_2stat(stat_name, stat_value, stats, dispo):
    return riven_math_neg(stat_name, stat_value, stats, dispo, 0.495)

#return neg grade of a +3-1 riven
def grade_neg_3stat(stat_name, stat_value, stats, dispo):
    return riven_math_neg(stat_name, stat_value, stats, dispo, 0.75)

#return pos grade of a +2-1 riven
def grade_2stat_neg(stat_name, stat_value, stats, dispo):
    return riven_math_pos(stat_name, stat_value, stats, dispo, 1.2375)

#return pos grade of a +2-0
def grade_2stat_no_neg(stat_name, stat_value, stats, dispo):
    return riven_math_pos(stat_name, stat_value, stats, dispo, 0.99)

#return pos grade of a +3-0
def grade_3stat_no_neg(stat_name, stat_value, stats, dispo):
    return riven_math_pos(stat_name, stat_value, stats, dispo, 0.75)

#return pos grade of a +3-1
def grade_3stat_neg(stat_name, stat_value, stats, dispo):
    return riven_math_pos(stat_name, stat_value, stats, dispo, 0.9375)

def riven_math_pos(stat_name, stat_value, stats, dispo, riven_multi):
    if stat_name in stats:
        base_stat = float(stats[stat_name])
        avg_val = round(base_stat * dispo * riven_multi,1)
        grade = round((float(stat_value)-avg_val)*100/avg_val,3)
        #output grade
        return(pos_grade_output(grade))

def riven_math_neg(stat_name, stat_value, stats, dispo, riven_multi):
    if stat_name in stats:
        base_stat = float(stats[stat_name])
        avg_val = round(base_stat * dispo * riven_multi,1)
        grade = round((float(stat_value)-avg_val)*100/avg_val,3)
        #output grade
        return(neg_grade_output(grade))
    
#return neg grade
def neg_grade_output(grade):
    if grade > 0:
        grade_send = -abs(grade)
    elif grade < 0:
        grade_send = abs(grade)
    if grade == 0:
        grade_send = grade
    #output grade
    if grade <= -11.1:
        return (":yellow_circle:",grade_send, "? grade")
    if -9.5 >= grade and grade >= -11:
        return (":green_circle:",grade_send, "S grade")
    if -7.5 >= grade and grade > -9.5:
        return (":green_circle:",grade_send, "A+ grade")
    if -5.5 >= grade and grade > -7.5:
        return (":green_circle:",grade_send, "A grade")
    if -3.5 >= grade and grade > -5.5:
        return (":green_circle:",grade_send, "A- grade")
    if -1.5 >= grade and grade > -3.5:
        return (":orange_circle:",grade_send, "B+ grade")
    if 1.5 >= grade and grade > -1.5:
        return (":orange_circle:",grade_send, "B grade")
    if 3.5 >= grade and grade > 1.5:
        return (":orange_circle:",grade_send, "B- grade")
    if 5.5 >= grade and grade > 3.5:
        return (":orange_circle:",grade_send, "C+ grade")
    if 7.5 >= grade and grade > 5.5:
        return (":orange_circle:",grade_send, "C grade")
    if 9.5 >= grade and grade > 7.5:
        return (":red_circle:",grade_send, "C- grade")
    if 11.1 >= grade and grade > 9.5:
        return (":red_circle:",grade_send, "F grade")
    if grade >= 11.1:
        return (":yellow_circle:",grade_send, "? grade")

#return pos grade
def pos_grade_output(grade):
    #output grade
    if grade >= 11.1:
        return (":yellow_circle:",grade, "? grade")
    if 9.5 <= grade and grade < 11.1:
        return (":green_circle:",grade, "S grade")
    if 7.5 <= grade and grade < 9.5:
        return (":green_circle:",grade, "A+ grade")
    if 5.5 <= grade and grade < 7.5:
        return (":green_circle:",grade, "A grade")
    if 3.5 <= grade and grade < 5.5:
        return (":green_circle:",grade, "A- grade")
    if 1.5 <= grade and grade < 3.5:
        return (":orange_circle:",grade, "B+ grade")
    if -1.5 <= grade and grade < 1.5:
        return (":orange_circle:",grade, "B grade")
    if -3.5 <= grade and grade < -1.5:
        return (":orange_circle:",grade, "B- grade")
    if -5.5 <= grade and grade < -3.5:
        return (":orange_circle:",grade, "C+ grade")
    if -7.5 <= grade and grade < -5.5:
        return (":orange_circle:",grade, "C grade")
    if -9.5 <= grade and grade < -7.5:
        return (":red_circle:",grade, "C- grade")
    if -11.1 <= grade and grade < -9.5:
        return (":red_circle:",grade, "F grade")
    if grade <= -11.1:
        return (":yellow_circle:",grade, "? grade")